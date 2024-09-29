from reprise.motif import Motif


class Vault:
    def __init__(self, directory) -> None:
        self.directory = directory

    def add_motif(self, content: str, citations: list) -> Motif:
        motif = Motif(content, citations)
        motif.save(f"{self.directory}/motifs")
        return motif
