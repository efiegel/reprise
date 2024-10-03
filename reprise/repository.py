from reprise.db import Motif


def add_motif(content: str, citation: str) -> Motif:
    motif = Motif.create(content=content, citation=citation)
    motif.save()
    return motif
