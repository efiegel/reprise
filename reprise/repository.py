from .db import Motif


class MotifRepository:
    def __init__(self, session):
        self.session = session

    def add_motif(self, content: str, citation: str) -> Motif:
        motif = Motif(content=content, citation=citation)
        self.session.add(motif)
        self.session.commit()
        return motif

    def get_motifs(self):
        motifs = self.session.query(Motif).all()
        return [{"uuid": m.uuid, "content": m.content} for m in motifs]
