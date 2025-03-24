from reprise.service import Service
from tests.factories import cloze_deletion_factory, motif_factory


class TestService:
    def test_reprise(self, session):
        motif_factory(session=session).create_batch(10)

        service = Service(session)
        reprisals = service.reprise()

        assert len(reprisals) == 5

    def test_reprise_reprises_second_set(self, session):
        motifs = motif_factory(session=session).create_batch(10)

        service = Service(session)

        service.reprise()
        set_1_uuid = motifs[0].reprisals[0].set_uuid
        reprisals = service.reprise()

        assert len(reprisals) == 5
        set_2_uuid = reprisals[0].set_uuid
        assert set_2_uuid != set_1_uuid

    def test_reprise_gets_cloze_deletions(self, session):
        motifs = motif_factory(session=session).create_batch(5)
        for motif in motifs:
            cloze_deletion_factory(session=session).create(motif=motif)

        service = Service(session)
        reprisals = service.reprise()
        for reprisal in reprisals:
            assert reprisal.cloze_deletion is not None
