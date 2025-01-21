from flask import Flask
import threading
import asyncio
from bot import WritingBot
from config import BOT_TOKEN
import os

app = Flask(__name__)

bot = WritingBot()

# Flask 路由設定（簡單的健康檢查）
@app.route("/")
def health_check():
    return "Bot is running!", 200

# 啟動 Flask
def run_flask():
    app.run(host="0.0.0.0", port=10000)  # 確保在環境中使用正確的 PORT 設定

# 啟動 Discord Bot
async def run_bot():
    await bot.start(BOT_TOKEN)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    asyncio.run(run_bot())
