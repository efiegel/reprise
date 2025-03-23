from reprise.db import Citation, ClozeDeletion, Motif, Reprisal


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

    def get_motifs_with_cloze_deletions(self) -> list[Motif]:
        return self.session.query(Motif).join(Motif.cloze_deletions).all()  # inner join

    def get_motifs_paginated(self, page: int, page_size: int) -> list[Motif]:
        offset = (page - 1) * page_size
        return (
            self.session.query(Motif)
            .order_by(Motif.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

    def get_motifs_count(self) -> int:
        return self.session.query(Motif).count()

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


class ReprisalRepository:
    def __init__(self, session):
        self.session = session

    def add_reprisal(
        self, motif_uuid: str, set_uuid: str, cloze_deletion_uuid: str = None
    ) -> Reprisal:
        reprisal = Reprisal(
            motif_uuid=motif_uuid,
            set_uuid=set_uuid,
            cloze_deletion_uuid=cloze_deletion_uuid,
        )
        self.session.add(reprisal)
        self.session.flush()
        return reprisal


class ClozeDeletionRepository:
    def __init__(self, session):
        self.session = session

    def add_cloze_deletion(self, motif_uuid: str, mask_tuples: list) -> ClozeDeletion:
        cloze_deletion = ClozeDeletion(motif_uuid=motif_uuid, mask_tuples=mask_tuples)
        self.session.add(cloze_deletion)
        self.session.flush()
        return cloze_deletion
