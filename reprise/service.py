from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from reprise.db import Motif
from reprise.repository import MotifRepository, ReprisalRepository


class Service:
    reprisal_motif_count = 5

    def __init__(self, session: Session):
        self.session = session
        self.motif_repository = MotifRepository(session)
        self.reprisal_repository = ReprisalRepository(session)

    def reprise_motifs(self, set_uuid: UUID = uuid4()) -> list[Motif]:
        motifs = self.motif_repository.get_motifs()
        reprisal_max = max([len(motif.reprisals) for motif in motifs])
        reprisal_min = min([len(motif.reprisals) for motif in motifs])

        reprised_motifs = []
        for motif in motifs:
            if len(motif.reprisals) < reprisal_max or reprisal_max == reprisal_min:
                reprised_motifs.append(motif)
                self.reprisal_repository.add_reprisal(motif.uuid, str(set_uuid))
                self.session.refresh(motif)

                if len(reprised_motifs) == self.reprisal_motif_count:
                    break

        return reprised_motifs
