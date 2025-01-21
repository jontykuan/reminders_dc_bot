import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
LLMSTUDIO_BASE_URL = "http://124.10.85.93:1234/v1"  # Default LM Studio endpoint
LLMSTUDIO_MODEL = "phi-4"  # Your local model name