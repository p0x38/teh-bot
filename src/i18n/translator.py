import asyncio
import os
import random
from collections.abc import Callable

from fluent.runtime import FluentBundle, FluentResource
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .manager.context import ContextManager
from .manager.engine import BehaviorEngine
from .manager.mutation import FluentMutationEngine
from .manager.personality import PersonalityManager
from .manager.rules import RuleManager
from .mutations import (
    chaotic_punctuation,
    emotion_filter,
    formal_compression,
    rare_glitch,
    spacing_distortion,
)
from .rules import rules
from .types import I18nContext, MutationContext, MutationRule


class LocaleReloadHandler(FileSystemEventHandler):
    def __init__(self, translator: "Translator"):
        self.translator = translator

    def on_modified(self, event) -> None:
        if str(event.src_path).endswith(".ftl"):
            self.translator.request_reload()


class Translator:
    def __init__(self):
        self.bundles: dict[str, FluentBundle] = {}
        self.locale_index: dict[str, str] = {}
        self.available_locales: set[str] = set()

        self._reload_pending = False
        self._lock = asyncio.Lock()

        self.base_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "assets", "locales"
        )

        self.bot_name = "TehBot"

        self.mutation_engine = FluentMutationEngine()
        self.behavior = BehaviorEngine(
            context_manager=ContextManager(),
            personality_manager=PersonalityManager(),
            rule_manager=RuleManager(rules),
            mutation_engine=self.mutation_engine
        )

    def resolve_key(self, bundle: FluentBundle, key: str) -> str | None:
        if bundle.has_message(key):
            return key

        if ":" in key:
            namespace, base = key.split(":", 1)

            candidates = [
                f"{namespace}-{base}",
                base,
                key
            ]

            for c in candidates:
                if bundle.has_message(c):
                    return c

        return None

    def resolve_message(self, bundle, fluent_id: str):
        message = bundle.get_message(fluent_id)
        return message.value if message and message.value else None

    def degrade(self, key: str, cmd=None, fallback=None) -> str:
        if fallback:
            return fallback

        if cmd:
            if getattr(cmd, "short_doc", None):
                return cmd.short_doc
            if getattr(cmd, "help", None):
                return cmd.help

        return f"! {key}"

    def request_reload(self):
        self._reload_pending = True

    async def watch_reload_loop(self):
        while True:
            if self._reload_pending:
                async with self._lock:
                    self._reload_pending = False
                    await asyncio.to_thread(self._load_locales)
                    self.build_locale_index()
            await asyncio.sleep(10)

    def start_watcher(self):
        handler = LocaleReloadHandler(self)

        observer = Observer()
        observer.schedule(handler, self.base_path, recursive=True)
        observer.start()

    def normalize_locale(self, loc: str) -> str:
        return loc.replace("-", "_").lower()

    def score_locale(self, requested: str, available: str) -> int:
        req = self.normalize_locale(requested)
        av = self.normalize_locale(available)

        req_lang, req_region = (req.split("_") + [None])[:2]
        av_lang, av_region = (av.split("_") + [None])[:2]

        score = 0

        if req == av:
            return 100

        if req_lang == av_lang:
            score += 60

        if req_region and av_region and req_region == av_region:
            score += 30

        if req_region and av_region and req_region[:2] == av_region[:2]:
            score += 10

        if av_lang == "en":
            score += 5

        return score

    def select_best_locale(self, requested: str) -> str:
        best = "en"
        best_score = -1

        for avail in self.available_locales:
            score = self.score_locale(requested, avail)

            if score > best_score:
                best_score = score
                best = avail

        return best

    def build_locale_index(self):
        locales = list(self.bundles.keys())
        self.available_locales = set(locales)

        sample_requests = set(locales) | {locale.split("_")[0] for locale in locales} | {"en"}

        index = {}

        for req in sample_requests:
            lower_req = req.lower()
            best_locale = None
            best_score = -1

            for avail in locales:
                lower_avail = avail.lower()
                score = self.score_locale(lower_req, lower_avail)

                if score > best_score:
                    best_score = score
                    best_locale = avail

            if best_locale:
                index[req] = best_locale

        self.locale_index = index

    def as_rule(self, fn: Callable[[str, MutationContext], str]) -> MutationRule:
        def wrapped(text: str, ctx: MutationContext, proprity: float, rng: random.Random) -> str:  # noqa: ARG001
            return fn(text, ctx)

        return MutationRule(fn=wrapped)

    async def load(self):
        await asyncio.to_thread(self._load_locales)

        self.mutation_engine.register_rules([
            self.as_rule(chaotic_punctuation),
            self.as_rule(formal_compression),
            self.as_rule(emotion_filter),
            self.as_rule(rare_glitch),
            self.as_rule(spacing_distortion),
        ])

        self.build_locale_index()

    def resolve_bundle(self, lang: str) -> FluentBundle | None:
        lang = self.normalize_locale(lang)

        if lang in self.locale_index:
            return self.bundles.get(self.locale_index[lang])

        best = self.select_best_locale(lang)
        return self.bundles.get(best) or self.bundles.get("en")

    def set_identity(self, name: str):
        self.bot_name = name

    def _load_locales(self):
        if not os.path.exists(self.base_path):
            return
        for locale_dir in os.listdir(self.base_path):
            dir_path = os.path.join(self.base_path, locale_dir)
            if not os.path.isdir(dir_path):
                continue

            bundle = FluentBundle([locale_dir])

            for root, _, files in os.walk(dir_path):
                for file in files:
                    if file.endswith(".ftl"):
                        file_path = os.path.join(root, file)
                        with open(file_path, encoding="utf-8") as f:
                            resource = FluentResource(f.read())

                        bundle.add_resource(resource)

            self.bundles[locale_dir] = bundle

    def to_mutation_ctx(self, ctx: I18nContext, seed: int) -> MutationContext:
        return MutationContext(
            tone=ctx.personality.type,
            emotion=ctx.emotion,
            seed=seed,
            mutation=ctx.mutation,
            user_id=ctx.user_id,
        )

    def t(self, lang: str, key: str, ctx: I18nContext | None = None, **kwargs) -> str:
        bundle = self.resolve_bundle(lang)

        if not bundle:
            return f"{{{lang}: {key}}}"

        fluent_id = self.resolve_key(bundle, key)

        if not fluent_id:
            return self.degrade(key, fallback=kwargs.get("fallback"))

        message = self.resolve_message(bundle, fluent_id)

        if not message:
            return self.degrade(key, fallback=kwargs.get("fallback"))

        args = kwargs.copy()
        args.setdefault("bot_name", self.bot_name)

        if ctx:
            args.update({
                "emotion": ctx.emotion.value if hasattr(ctx.emotion, "value") else ctx.emotion,
                "tone": ctx.personality.type.value
                if hasattr(ctx.personality.type, "value")
                else ctx.personality.type,
                "intensity": ctx.personality.intensity,
                "is_new_user": ctx.is_new_user,
                "level": ctx.level,
                "is_admin": ctx.is_admin,
                "is_guild": ctx.is_guild,
                "is_dm": ctx.is_dm,
                "hour": ctx.hour,
                "streak": ctx.streak,
                "seed": random.randint(1, 16),
            })

        raw, _ = bundle.format_pattern(message, args)
        raw = str(raw)

        if ctx:
            raw = self.behavior.process(raw, key, ctx)

        return str(raw)


translator = Translator()
