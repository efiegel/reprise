from reprise.db import Citation, Motif


class MotifRepository:
    def __init__(self, session):
        self.session = session

    def add_motif(self, content: str, citation: Citation = None) -> Motif:
        motif = Motif(content=content, citation=citation)
        self.session.add(motif)
        self.session.flush()
        return motif

    def get_motif(self, uuid: str) -> Motif:
        return self.session.query(Motif).filter_by(uuid=uuid).one_or_none()

    def get_motifs(self) -> list[Motif]:
        return self.session.query(Motif).all()

    def update_motif_content(self, uuid: str, content: dict) -> Motif:
        motif = self.get_motif(uuid)
        motif.content = content
        self.session.flush()
        return motif

    def delete_motif(self, uuid: str) -> None:
        motif = self.get_motif(uuid)
        self.session.delete(motif)
        self.session.flush()

    def add_citation(self, motif_uuid: str, citation: Citation) -> Motif:
        motif = self.get_motif(motif_uuid)
        motif.citation = citation
        self.session.flush()
        return motif


class CitationRepository:
    def __init__(self, session):
        self.session = session

    def get_citation(self, uuid: str) -> Citation:
        return self.session.query(Citation).filter_by(uuid=uuid).one_or_none()

    def get_citations(self) -> list[Citation]:
        return self.session.query(Citation).all()

    def add_citation(self, title: str) -> Citation:
        citation = Citation(title=title)
        self.session.add(citation)
        self.session.flush()
        return citation

    def get_citation_by_title(self, title: str) -> Citation:
        return self.session.query(Citation).filter_by(title=title).one_or_none()
