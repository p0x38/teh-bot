from ..types import I18nContext


class ContextManager:
    def enrich(self, ctx: I18nContext) -> I18nContext:
        if ctx.mutation is None:
            ctx.mutation = 0.0
        return ctx
