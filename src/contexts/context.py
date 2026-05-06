from contextvars import Token
from typing import TYPE_CHECKING
from uuid import UUID

from discord.ext import commands

from ..i18n.types import I18nContext
from ..utils.embed_factory import EmbedFactory
from ..utils.trace_context import trace_id_var

if TYPE_CHECKING:
    from src.bot import TehBot


class TehContext(commands.Context):
    bot: "TehBot"

    trace_id: UUID | None = None
    _trace_token: Token[UUID | None] | None = None
    locale: str = "en"
    embeds: EmbedFactory

    i18n: I18nContext

    def bind_trace(self, trace_id: UUID):
        self.trace_id = trace_id
        self._trace_token = trace_id_var.set(trace_id)

    def release_trace(self):
        if self._trace_token is not None:
            trace_id_var.reset(self._trace_token)
            self._trace_token = None

    async def embed(
        self,
        title: str | None = None,
        description: str | None = None,
        **kwargs
    ):
        embed = self.embeds.create(
            title=title,
            description=description,
            **kwargs
        )
        return await self.send(embed=embed)

    def t(self, key: str, **kwargs) -> str:
        return self.bot.translator.t(self.locale, key, self.i18n, **kwargs)
