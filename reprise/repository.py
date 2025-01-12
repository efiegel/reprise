from reprise.db import Motif


def add_motif(content: str, citation: str) -> Motif:
    motif = Motif.create(content=content, citation=citation)
    motif.save()
    return motif


def get_motifs():
    motifs = Motif.select()
    motifs_list = [{"uuid": motif.uuid, "content": motif.content} for motif in motifs]
    return motifs_list
