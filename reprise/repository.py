from reprise.db import Motif


class MotifRepository:
    def __init__(self, session):
        self.session = session

    def add_motif(self, content: str, citation: str) -> Motif:
        motif = Motif(content=content, citation=citation)
        self.session.add(motif)
        self.session.commit()
        return motif

    def get_motif(self, uuid: str) -> Motif:
        return self.session.query(Motif).filter_by(uuid=uuid).one_or_none()

    def get_motifs(self) -> list[Motif]:
        return self.session.query(Motif).all()

    def update_motif_content(self, uuid: str, content: dict) -> Motif:
        motif = self.get_motif(uuid)
        motif.content = content
        self.session.commit()
        return motif

    def delete_motif(self, uuid: str) -> None:
        motif = self.get_motif(uuid)
        self.session.delete(motif)
        self.session.commit()
