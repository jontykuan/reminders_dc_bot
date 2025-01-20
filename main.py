import asyncio
from bot import WritingBot
from config import BOT_TOKEN

async def main():
    bot = WritingBot()
    await bot.start(BOT_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())