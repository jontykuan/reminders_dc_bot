import asyncio
from bot import WritingBot
from config import DISCORD_TOKEN

async def main():
    bot = WritingBot()
    await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())