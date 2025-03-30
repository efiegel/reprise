import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI API Settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Use the 4o-mini model
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
