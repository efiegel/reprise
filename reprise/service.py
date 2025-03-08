from sqlalchemy.orm import Session

from reprise.db import Motif
from reprise.repository import MotifRepository, ReprisalRepository


class Service:
    reprisal_motif_count = 5

    def __init__(self, session: Session):
        self.session = session
        self.motif_repository = MotifRepository(session)
        self.reprisal_repository = ReprisalRepository(session)

    def reprise_motifs(self) -> list[Motif]:
        motifs = self.motif_repository.get_motifs()
        reprisal_max = max([len(motif.reprisals) for motif in motifs])
        reprisal_min = min([len(motif.reprisals) for motif in motifs])

        reprised_motifs = []
        for motif in motifs[: self.reprisal_motif_count]:
            if len(motif.reprisals) < reprisal_max or reprisal_max == reprisal_min:
                reprised_motifs.append(motif)
                self.reprisal_repository.add_reprisal(motif.uuid)
                self.session.refresh(motif)

        return reprised_motifs
