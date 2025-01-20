import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="DISCORD_TOKEN.env")

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
LLMSTUDIO_BASE_URL = "http://192.168.1.186:1234/v1"  # Default LM Studio endpoint
LLMSTUDIO_MODEL = "phi-4"  # Your local model name