from uuid import uuid4

from reprise.service import Service
from tests.factories import motif_factory


class TestService:
    def test_reprise_motifs(self, session):
        motif_factory(session=session).create_batch(10)

        service = Service(session)

        set_uuid = uuid4()
        reprised_motifs = service.reprise_motifs(set_uuid)

        assert len(reprised_motifs) == 5
        for motif in reprised_motifs:
            assert len(motif.reprisals) == 1
            assert motif.reprisals[0].set_uuid == str(set_uuid)
