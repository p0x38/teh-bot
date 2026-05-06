import asyncio
import os
from typing import TypeVar, cast

from discord import Forbidden, HTTPException, Intents, MissingApplicationID
from discord.app_commands import CommandSyncFailure, TranslationError
from discord.ext import commands
from discord.ext.commands import (
    ExtensionAlreadyLoaded,
    ExtensionFailed,
    ExtensionNotFound,
    NoEntryPointError,
)

from .config_loader import global_config
from .contexts.context import TehContext
from .databases import Database
from .help.help import TehHelp
from .i18n import translator
from .i18n.emotion_mapper import process_emotion, resolve_emotion
from .i18n.mapper import toI18nContext
from .leveling.tiers import load_tiers
from .leveling.xp import XPManager
from .logger import log
from .utils import AsyncTTLCache
from .utils.embed_factory import EmbedFactory
from .utils.trace_context import trace_id_var
from .utils.tracing import generate_trace_id

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


ContextT = TypeVar("ContextT", bound=commands.Context)


class TehBot(commands.AutoShardedBot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=commands.when_mentioned_or(global_config.get("bot_prefix", "!")),
            intents=Intents.all(),
            help_command=TehHelp(),
            **kwargs,
        )
        self.translator = translator
        self.log = log
        self.db = Database()
        self.xp = XPManager()
        self.cache = AsyncTTLCache(default_ttl=60 * 10)

    def compute_burst_intensity(self, timestamps: list[float]) -> float:
        if len(timestamps) < 2:
            return 0.0

        intervals = [
            timestamps[i] - timestamps[i - 1]
            for i in range(1, len(timestamps))
        ]

        avg = sum(intervals) / len(intervals)

        if avg <= 0:
            return 1.0

        intensity = min(1.0, 1 / avg)
        return intensity

    async def get_context(self, origin, *, cls: type[ContextT] = TehContext) -> ContextT:
        ctx = cast(ContextT, await super().get_context(origin, cls=cls))

        if isinstance(ctx, TehContext):
            ctx.trace_id = trace_id_var.get(None)
            # guild_settings = await self.db.get_guild_settings(ctx.guild.id)

            # enabled_rule_plugins = set(guild_settings.data.get("enabled_rule_plugins", []))

            profile = await self.db.get_user_profile(ctx.author.id)

            user_locale = profile.locale
            guild_locale = getattr(ctx.guild, "preferred_locale", None) if ctx.guild else None

            ctx.locale = user_locale or guild_locale or "en"

            ctx.embeds = EmbedFactory(ctx)

            ctx.i18n = await toI18nContext(ctx, profile.data or {})

        return ctx

    async def list_py_files(self, path: str):
        return await asyncio.to_thread(
            lambda: [f for f in os.listdir(path) if f.endswith(".py") and not f.startswith("__")]
        )

    async def setup_hook(self) -> None:
        self.log.info("Boot sequence start...")

        await self._boot_phrase()
        await self._load_phase()
        await self._ready_phase()

        self.log.info("Startup complete.")

    async def _boot_phrase(self):
        self.log.info("[Phase/BOOT] Initializing core systems...")
        cog_path = os.path.join(os.path.dirname(__file__), "cogs")

        tasks = await asyncio.gather(
            self.list_py_files(cog_path), self.db.initialize(), self.translator.load(), load_tiers()
        )

        self._cog_files = tasks[0]
        self.log.info("[Phase/BOOT] Core systems ready.")

    async def _load_phase(self):
        self.log.info("[Phase/LOAD] Loading extensions...")

        sem = asyncio.Semaphore(5)

        async def load_ext(fname: str):
            async with sem:
                name = f"src.cogs.{fname[:-3]}"
                try:
                    await self.load_extension(name)
                    return (fname, True, None)
                except (
                    ExtensionAlreadyLoaded,
                    ExtensionFailed,
                    ExtensionNotFound,
                    NoEntryPointError,
                ) as e:
                    return (fname, False, e)

        results = await asyncio.gather(*(load_ext(f) for f in self._cog_files))

        for fname, ok, err in results:
            if ok:
                self.log.info(f"[Phase/LOAD] Loaded extension [cyan]{fname}[/cyan]")
            else:
                self.log.warning(f"[Phase/LOAD] Failed to load extension {fname}: {err}")

    async def _ready_phase(self):
        self.log.info("[Phase/READY] Syncing commands...")

        try:
            synced = await self.tree.sync()
            self.log.info(f"Synced [bold green]{len(synced)}[/] commands.")
        except (
            HTTPException,
            CommandSyncFailure,
            Forbidden,
            MissingApplicationID,
            TranslationError,
        ) as e:
            self.log.error(f"Slash sync failed: {e}")

    async def on_ready(self):
        if self.user:
            translator.set_identity(name=self.user.name)
        self.log.info(f"[bold yellow]{self.user} is now online and ready![/bold yellow]")

    async def on_command_error(self, ctx: commands.Context, e: commands.CommandError):
        if hasattr(ctx.command, "on_error"):
            return

        cog = ctx.cog
        if cog and cog._get_overridden_method(cog.cog_command_error) is not None:
            return

        # locale = getattr(ctx.guild, "preferred_locale", "en-US")
        # p = ctx.clean_prefix

        description = ""

        self.log.exception(f"Command failed: {ctx.command} -> {e}")

        match e:
            case commands.CommandNotFound():
                description = "that command not found"
            case commands.ConversionError(converter=converter, original=original):
                description = (
                    f"some converter called {converter.__class__.__name__} "
                    f"failed to convert for {original.__class__.__name__} "
                    "exception"
                )
            case commands.MissingRequiredArgument(param=param):
                description = (
                    f"you have missed some required argument called {param.name} for the command"
                )
            case commands.MissingRequiredAttachment(param=param):
                description = (
                    "you have missed some required attachment "
                    f"for some paramater called {param.name}"
                )
            case commands.ArgumentParsingError():
                description = "i can't understand that"
            case commands.UnexpectedQuoteError():
                description = "u don't need that quote"
            case commands.InvalidEndOfQuotedStringError():
                description = "i think you forgot to change some into quote"
            case commands.ExpectedClosingQuoteError():
                description = "i think you forgot to add quote"
            case commands.BadArgument():
                description = "i don't fricking know that"
            case commands.BadUnionArgument(param=param):
                description = (
                    f"that stupid param called {param.name} is mad at you because of bad unioning"
                )
            case commands.BadLiteralArgument(param=param):
                description = (
                    f"that stupid param called {param.name} "
                    "is mad at you because of literally doing bad option"
                )
            case commands.PrivateMessageOnly():
                description = "you can use that in DM dumbass"
            case commands.NoPrivateMessage():
                description = "you can't use that in DM dumbass"
            case (commands.CheckFailure(), commands.CheckAnyFailure()):
                description = "i won't do it ever"
            case commands.DisabledCommand():
                description = "well, i can't do it..."
            case commands.CommandInvokeError(original=original):
                description = (
                    f"welp. something thrown at me. (i think it's {original.__class__.__name__})"
                )
            case commands.TooManyArguments():
                description = "too full..."
            case commands.CommandOnCooldown(retry_after=retry_after):
                description = f"can u not spam for {int(retry_after)} seconds please"
            case commands.MaxConcurrencyReached(number=number):
                description = f"welp, you can't use since we got {number} of peoples"
            case commands.NotOwner():
                description = "you're not my owner, get out"
            case commands.MessageNotFound():
                description = "i can't see that bro"
            case commands.MemberNotFound():
                description = "who's that"
            case commands.GuildNotFound():
                description = "where's it then"
            case commands.UserNotFound():
                description = "i don't even know who was that >:("
            case commands.ChannelNotFound():
                description = "welp, i can't use that channel"
            case commands.ChannelNotReadable():
                description = "i can't check that channel :("
            case commands.ThreadNotFound():
                description = "i can't look to that bruh"
            case commands.BadColourArgument():
                description = "what does that color means"
            case commands.RoleNotFound():
                description = "what that role called"
            case commands.BadInviteArgument():
                description = "huh"
            case commands.MissingPermissions(missing_permissions=missing):
                description = f"you can't use since you don't have {' '.join(missing)}"
            case commands.BotMissingPermissions(missing_permissions=missing):
                description = f"nah i can't since i don't have {' '.join(missing)}"
            case _:
                description = f"unhandled exception raised: {e.__class__.__name__}"

        await ctx.send(f"```\n{description}\n```")

    async def on_command(self, ctx: TehContext):
        trace_id = generate_trace_id()
        ctx.bind_trace(trace_id)

        state = await self.db.get_emotion_state(ctx.author.id)

        state = await process_emotion(self.db, ctx.author.id)

        emotion = resolve_emotion(state)

        ctx.i18n.emotion = emotion

        ctx.trace_id = trace_id

        self.log.info(
            f"[{trace_id}] Command start: {ctx.command} by {ctx.author} "
            f"(annoyance={state.annoyance:.2f})"
        )

    async def on_command_completion(self, ctx: TehContext):
        ctx.release_trace()

        self.log.info(f"[{ctx.trace_id}] Command completed: {ctx.command}")
