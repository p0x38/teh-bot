import random

from ..types import I18nContext, RulesDict


class RuleManager:
    def __init__(self, rules: RulesDict):
        self.rules = rules

    def get_rules(self, key: str, locale: str):
        base = key.split(":")[-1]
        lang = locale.split("_")[0]

        global_rules = self.rules.get("global", {}).get(key) or self.rules.get("global", {}).get(
            base
        )

        local_rules = self.rules.get(lang, {}).get(key) or self.rules.get(lang, {}).get(base)

        return (local_rules or []) + (global_rules or [])

    def apply(self, text: str, key: str, ctx: I18nContext) -> str:
        rules = self.get_rules(key, ctx.locale)

        matched = []
        for r in rules:
            try:
                match_fn = r.get("match")
                if match_fn and match_fn(ctx):
                    matched.append(r)
            except Exception:
                continue

        if not matched:
            return text

        highest = max(r.get("priority", 0) for r in matched)
        top = [r for r in matched if r.get("priority", 0) == highest]

        weights = [r.get("weight", 1.0) for r in top]
        chosen = random.choices(top, weights=weights, k=1)[0]

        replace = chosen["replace"]
        return str(replace(ctx) if callable(replace) else replace)
