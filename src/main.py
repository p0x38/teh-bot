import asyncio
import os

from dotenv import load_dotenv

from .bot import TehBot
from .logger import log


async def main():
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")

    if not token:
        log.error("No DISCORD_TOKEN found in .env file.")
        return

    bot = TehBot()

    try:
        log.info("Starting bot framework...")
        await bot.start(token)
    except KeyboardInterrupt:
        log.info("Shutting down...")
    finally:
        await bot.close()


def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except RuntimeError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
