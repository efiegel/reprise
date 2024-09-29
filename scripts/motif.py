import os

from dotenv import load_dotenv

from reprise.vault import Vault

load_dotenv()

VAULT_DIRECTORY = os.path.expanduser(os.getenv("VAULT_DIRECTORY", ""))


if __name__ == "__main__":
    text = input("add motif: ")
    citations = input("citations (optional, comma-separated): ").split(",") or []

    vault = Vault(VAULT_DIRECTORY)
    vault.add_motif(text, citations)
