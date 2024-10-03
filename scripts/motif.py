from reprise.db import database_context
from reprise.vault import Vault
from settings import VAULT_DIRECTORY

if __name__ == "__main__":
    text = input("add motif: ")
    citations = input("citations (optional, comma-separated): ").split(",") or []

    vault = Vault(VAULT_DIRECTORY)
    with database_context():
        vault.add_motif(text, citations)
