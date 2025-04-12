import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Mailgun Settings
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
MAILGUN_RECIPIENT = os.getenv("MAILGUN_RECIPIENT")
