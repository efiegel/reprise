import random
from uuid import uuid4

from sqlalchemy.orm import Session

from reprise.db import Reprisal
from reprise.repository import MotifRepository, ReprisalRepository


class Service:
    reprisal_count = 5

    def __init__(self, session: Session):
        self.session = session
        self.motif_repository = MotifRepository(session)
        self.reprisal_repository = ReprisalRepository(session)

    def reprise(self) -> list[Reprisal]:
        motifs = self.motif_repository.get_motifs()
        reprisal_max = max([len(motif.reprisals) for motif in motifs])
        reprisal_min = min([len(motif.reprisals) for motif in motifs])

        reprisals = []
        set_uuid = uuid4()
        for motif in motifs:
            # randomly select from cloze deletions if available
            # this means that the algorithm will never return the original motif
            if motif.cloze_deletions:
                cloze_deletion = random.choice(motif.cloze_deletions)

            if len(motif.reprisals) < reprisal_max or reprisal_max == reprisal_min:
                reprisal = self.reprisal_repository.add_reprisal(
                    motif.uuid,
                    str(set_uuid),
                    cloze_deletion.uuid if motif.cloze_deletions else None,
                )
                self.session.refresh(motif)
                reprisals.append(reprisal)

                if len(reprisals) == self.reprisal_count:
                    break

        return reprisals
