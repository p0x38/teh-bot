from collections.abc import Callable

from .types import I18nContext, RulesDict

ReplaceFunc = Callable[[I18nContext], str]


rules: RulesDict = {
    "global": {
        "greeting": [
            {
                "match": lambda ctx: ctx.hour < 5,
                "replace": "Are you still awake?",
                "priority": 10
            }
        ]
    }
}
