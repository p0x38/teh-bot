import textwrap
from collections.abc import Mapping

from discord.ext import commands


class TehHelp(commands.HelpCommand):
    def __init__(self):
        super().__init__()
        self.paginator = commands.Paginator(prefix="```", suffix="```")

    def _reset(self):
        self.paginator.clear()

    def get_prefix(self):
        return self.context.clean_prefix

    def get_locale(self) -> str:
        return getattr(self.context, "locale", "en")

    def get_my_name(self):
        return self.context.me.display_name

    def _wrap(self, text: str, width: int = 90) -> list[str]:
        return textwrap.wrap(
            text,
            width=width,
            break_long_words=False,
            replace_whitespace=False,
        )

    def _line(self, text: str, indent: int = 0):
        prefix = " " * indent
        for i, line in enumerate(self._wrap(text, 90)):
            self.paginator.add_line(prefix + line if i == 0 else " " * indent + line)

    def _add_header(self, title: str):
        self.paginator.add_line(f"=== {title} ===")

    def _add_spacer(self):
        self.paginator.add_line("")

    def t(self, key: str, **kwargs) -> str:
        translator = self.context.bot.translator  # type: ignore
        return translator.t(self.get_locale(), key, self.context, **kwargs)

    def cmd_desc(self, cmd: commands.Command) -> str:
        key = f"help:{cmd.name}.description"
        text = self.t(key, fallback=cmd.short_doc or cmd.help)

        return text

    async def send_pages(self):
        destination = self.get_destination()

        for page in self.paginator.pages:
            await destination.send(page)

        self._reset()

    async def send_bot_help(
        self,
        mapping: Mapping[commands.Cog | None, list[commands.Command]]
    ):
        p = self.get_prefix()
        bname = self.get_my_name()

        self._add_header(self.t("help:menu-title", bot=bname, prefix=p))
        self._add_spacer()

        self._add_header(self.t("help:trending-title"))
        self._add_spacer()

        trending = await self.context.bot.db.get_trending_commands(  # type: ignore
            self.context.guild.id if self.context.guild else 0,
            limit=5
        )

        if not trending:
            self._line(self.t("help:trending-empty"))
        else:
            for name, count in trending:
                cmd = self.context.bot.get_command(name)
                if cmd:
                    self._line(f"{cmd.qualified_name} - {count} uses", indent=2)

        self._add_spacer()

        for cog, cmds in mapping.items():
            filtered = await self.filter_commands(cmds, sort=True)
            if not filtered:
                continue

            cog_name = getattr(cog, "qualified_name", "No category")

            self._line(f"[ {cog_name} ]")
            self._add_spacer()

            for cmd in filtered:
                desc = self.cmd_desc(cmd)
                self._line(f"{p}{cmd.name} - {desc}", indent=2)

            self._add_spacer()

        self.paginator.add_line(self.t("help:footer-usage-without-name", prefix=p))
        await self.send_pages()

    async def send_group_help(self, group: commands.Group):
        p = self.get_prefix()

        self._add_header(f"GROUP: {group.qualified_name}")
        self._line(self.t("help:prefix-text", prefix=p))
        self._line(self.t("help:description-text", v=group.help or self.t("help:no-description")))
        self._add_spacer()

        filtered = await self.filter_commands(group.commands, sort=True)

        if not filtered:
            self.paginator.add_line(self.t("help:group-empty"))
        else:
            for command in filtered:
                label = "GROUP" if isinstance(command, commands.Group) else "CMD"
                self._line(
                    f"[{label}] {p}{command.qualified_name} - {command.short_doc}",
                    indent=2
                )

        self._add_spacer()
        self.paginator.add_line(
            self.t(
                "help:footer-usage-with-name",
                prefix=p,
                name=group.qualified_name
            )
        )
        await self.send_pages()

    async def send_command_help(self, command: commands.Command):
        p = self.get_prefix()

        self._add_header(f"COMMAND: {command.qualified_name}")

        signature = self.get_command_signature(command)
        self._line(self.t('help:command-usage', prefix=p, signature=signature))

        if command.aliases:
            self._line(self.t('help:command-aliases', aliases=', '.join(command.aliases)))

        if command.cooldown:
            self._line(
                self.t(
                    "help:command-cooldown",
                    rate=command.cooldown.rate,
                    per=f"{command.cooldown.per:.0f}"
                )
            )

        self._add_spacer()

        self._line(
            self.cmd_desc(command)
        )

        await self.send_pages()
