from reprise.motif import Motif


class Vault:
    def __init__(self, directory) -> None:
        self.directory = directory

    def add_motif(self, content: str) -> Motif:
        motif = Motif(content)
        motif.save(self.directory)
        return motif
