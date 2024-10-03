from reprise.db import database_context
from reprise.repository import add_motif

if __name__ == "__main__":
    text = input("add motif: ")
    citation = input("citation name (optional): ") or None
    with database_context():
        add_motif(text, citation)
