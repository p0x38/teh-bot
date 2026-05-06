import asyncio
import csv
import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Tier:
    key: str
    min_level: int
    max_level: int | None


_TIERS: list[Tier] = []


async def load_tiers():
    def _load():
        base_dir = os.path.dirname(os.path.dirname(__file__))
        path = os.path.join(base_dir, "assets", "tiers.csv")

        tiers: list[Tier] = []

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                if row["key"].startswith("#"):
                    continue

                max_level = row["max_level"].strip()

                tiers.append(
                    Tier(
                        key=row["key"],
                        min_level=int(row["min_level"]),
                        max_level=int(max_level) if max_level else None,
                    )
                )

        return tiers

    global _TIERS
    _TIERS = await asyncio.to_thread(_load)


@lru_cache(maxsize=256)
def get_tier(level: int) -> str:
    if not _TIERS:
        raise RuntimeError("Tiers not loaded. Call load_tiers() first.")

    for tier in _TIERS:
        if tier.max_level is None:
            if level >= tier.min_level:
                return tier.key
        elif tier.min_level <= level <= tier.max_level:
            return tier.key

    return "mythic"


def xp_for_level(level: int) -> int:
    return 5 * (level ** 2) + 50 * level + 100
