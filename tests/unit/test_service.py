from reprise.service import Service
from tests.factories import motif_factory


class TestService:
    def test_reprise_motifs(self, session):
        motif_factory(session=session).create_batch(10)

        service = Service(session)
        reprised_motifs = service.reprise_motifs()

        assert len(reprised_motifs) == 5
        set_uuid = reprised_motifs[0].reprisals[0].set_uuid
        for motif in reprised_motifs:
            assert len(motif.reprisals) == 1
            assert motif.reprisals[0].set_uuid == str(set_uuid)

    def test_reprise_motifs_reprises_second_set(self, session):
        motifs = motif_factory(session=session).create_batch(10)

        service = Service(session)

        service.reprise_motifs()
        set_1_uuid = motifs[0].reprisals[0].set_uuid
        reprised_motifs = service.reprise_motifs()

        assert len(reprised_motifs) == 5
        set_2_uuid = reprised_motifs[0].reprisals[0].set_uuid
        assert set_2_uuid != set_1_uuid
        for motif in reprised_motifs:
            assert len(motif.reprisals) == 1
            assert motif.reprisals[0].set_uuid == str(set_2_uuid)
