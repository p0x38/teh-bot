import random

from ..types import MutationContext, MutationRule


class FluentMutationEngine:
    def __init__(
        self,
        # plugin_manager: PluginManager | None = None
    ):
        self.rules: list[MutationRule] = []
        # self.plugin_manager = plugin_manager

    def register(self, rule: MutationRule):
        self.rules.append(rule)

    def register_rules(self, rules: list[MutationRule]):
        self.rules.extend(rules)

    def apply(self, text: str, ctx: MutationContext) -> str:
        rng = random.Random(ctx.seed)

        active_rules = []

        for rule in self.rules:
            if rule.min_entropy <= ctx.entropy <= rule.max_entropy:
                weight = rule.priority * ctx.entropy
                active_rules.append((weight, rule))

        active_rules.sort(key=lambda x: x[0])

        for _, rule in active_rules:
            text = rule.fn(text, ctx, ctx.entropy, rng)

        return text
