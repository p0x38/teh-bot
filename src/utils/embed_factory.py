from __future__ import annotations

from datetime import datetime
from typing import Any

from discord import Color, Embed
from pytz import UTC

from .id import generate_id


class CustomEmbed(Embed):
    def __init__(
        self,
        *,
        color: int | Color | None = None,
        title: Any | None = None,
        url: Any | None = None,
        description: Any | None = None,
        timestamp: datetime | None = None,
        **kwargs
    ):
        super().__init__(
            color=color,
            title=title,
            url=url,
            description=description,
            timestamp=timestamp or datetime.now(UTC),
            **kwargs
        )
        self.unique_id: str = generate_id(8)


class EmbedFactory:
    def __init__(self, ctx, default_color: Color | None = None):
        self.ctx = ctx
        self.default_color = default_color or Color.blurple()

    def create(
        self,
        title: str | None = None,
        description: str | None = None,
        *,
        color: Color | None = None
    ) -> CustomEmbed:
        embed = CustomEmbed(
            title=title,
            description=description,
            color=color or self.default_color
        )

        footer_parts = [f"id:{embed.unique_id}"]

        if self.ctx.trace_id:
            footer_parts.append(f"trace:{self.ctx.trace_id}")

        embed.set_footer(text=" • ".join(footer_parts))

        return embed
