from ..types import I18nContext, PersonalityToneType


class PersonalityManager:
    def resolve(self, ctx: I18nContext) -> I18nContext:
        p = ctx.personality

        if ctx.is_admin:
            p.intensity = "low"

        if ctx.emotion == "mad":
            p.type = PersonalityToneType.CHAOTIC

        return ctx
