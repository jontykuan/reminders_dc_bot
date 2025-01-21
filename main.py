from flask import Flask, jsonify
import asyncio
from bot import WritingBot
from config import BOT_TOKEN
import os

app = Flask(__name__)
bot = None  # 宣告 bot 變數，稍後初始化

async def main():
    port = int(os.environ.get("PORT"))  # Get the port from environment variable
    bot = WritingBot()
    await bot.start(BOT_TOKEN, port)  # Ensure your bot's start method supports port

if __name__ == "__main__":
    asyncio.run(main())