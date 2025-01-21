from flask import Flask, jsonify
import asyncio
from bot import WritingBot
from config import BOT_TOKEN
import os

app = Flask(__name__)
bot = None  # 宣告 bot 變數，稍後初始化

@app.route('/', methods=['POST'])  # 處理 POST 請求
async def handle_request():
    if not bot:
        return jsonify({"error": "Bot not initialized"}), 503 # 服務尚未啟動

    # 這裡處理來自 Render 的請求，例如觸發機器人執行特定任務
    try:
        # 假設 Render 會傳送 JSON 格式的請求
        request_data = request.get_json()
        # 根據請求內容執行機器人相關操作
        # ... (例如：await bot.some_method(request_data)) ...

        # 回傳結果
        return jsonify({"message": "Request processed successfully"}), 200

    except Exception as e:
        print(f"Error handling request: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health') #健康檢查端點
def health_check():
    if bot:
        return "Bot is running", 200
    else:
        return "Bot is not running", 503

async def start_bot():
    global bot
    bot = WritingBot()
    try:
        await bot.start(BOT_TOKEN)
        print("Bot started successfully")
    except Exception as e:
        print(f"Error starting bot: {e}")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    asyncio.run(start_bot()) # 在背景啟動機器人
    app.run(host='0.0.0.0', port=port, debug=False) # 啟動 Flask 應用程式
