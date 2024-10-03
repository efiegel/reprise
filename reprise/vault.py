from reprise.motif import Motif
from reprise.repository import add_motif as add_motif_to_db


class Vault:
    def __init__(self, directory) -> None:
        self.directory = directory

    def add_motif(self, content: str, citations: list) -> Motif:
        add_motif_to_db(content, citations[0])
        motif = Motif(content, citations)
        motif.save(f"{self.directory}/motifs")
        return motif
