import os

from reprise.motif import Motif


class Vault:
    def __init__(self) -> None:
        self.directory = os.path.expanduser(os.getenv("VAULT_DIRECTORY"))

    def add_motif(self, content: str) -> Motif:
        motif = Motif(content)
        motif.save(self.directory)
        return motif
