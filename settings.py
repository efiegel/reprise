import os

from dotenv import load_dotenv

load_dotenv()

VAULT_DIRECTORY = os.path.expanduser(os.getenv("VAULT_DIRECTORY", ""))
