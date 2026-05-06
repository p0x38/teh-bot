import random

from discord import Message

from src.utils import AsyncTTLCache


class XPManager:
    def __init__(self):
        self.xp_cooldown = 30
        self.xp_range = (5, 15)
        self._cooldowns = AsyncTTLCache(default_ttl=self.xp_cooldown)

    async def try_gain_xp(self, message: Message) -> int | None:
        if message.author.bot:
            return None

        if not message.guild:
            return None

        key = f"xp:{message.guild.id}:{message.author.id}"

        if await self._cooldowns.get(key):
            return None

        content = message.clean_content
        if not content.strip():
            return None

        xp = random.randint(self.xp_range[0], self.xp_range[1]) + (
            len(content.split(" ")) // 3) + (len(content) // 3)

        await self._cooldowns.set(key, True, ttl=self.xp_cooldown)

        return xp
