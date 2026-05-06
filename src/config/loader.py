import asyncio

import aiofiles
import orjson
from pydantic import ValidationError

from .schema import BotSettings


async def load_settings(path: str) -> BotSettings:
    try:
        async with aiofiles.open(path, "rb") as f:
            content = await f.read()

        data = await asyncio.to_thread(orjson.loads, content)
        return BotSettings.model_validate(data)
    except FileNotFoundError:
        return BotSettings()
    except orjson.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON: {e}") from e
    except ValidationError as e:
        raise RuntimeError(f"Config validation error: {e}") from e
