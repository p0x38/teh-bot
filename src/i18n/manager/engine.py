import random

from ..types import I18nContext, MutationContext
from .context import ContextManager
from .mutation import FluentMutationEngine
from .personality import PersonalityManager
from .rules import RuleManager


class BehaviorEngine:
    def __init__(
        self,
        context_manager: ContextManager,
        personality_manager: PersonalityManager,
        rule_manager: RuleManager,
        mutation_engine: FluentMutationEngine,
        # plugin_manager: PluginManager
    ):
        self.context_manager = context_manager
        self.personality_manager = personality_manager
        self.rule_manager = rule_manager
        self.mutation_engine = mutation_engine
        # self.plugin_manager = plugin_manager

    def process(self, text: str, key: str, ctx: I18nContext) -> str:
        ctx = self.context_manager.enrich(ctx)
        ctx = self.personality_manager.resolve(ctx)

        text = self.rule_manager.apply(text, key, ctx)

        mctx = MutationContext(
            tone=str(ctx.personality.type),
            emotion=str(ctx.emotion),
            seed=random.randint(1, 16),
            mutation=ctx.mutation,
            user_id=ctx.user_id
        )

        text = self.mutation_engine.apply(text, mctx)

        # transforms = self.plugin_manager.get_transforms()

        # transform = getattr(ctx, "transforms", None)
        # if transform in transforms:
        #     text = transforms[transform](text)

        return text
