from unittest.mock import patch

import pytest

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

    @patch("reprise.service.openai_generate_cloze_deletion")
    def test_add_default_cloze_deletion(self, mock_generate, session):
        # Mock the OpenAI API call to return a specific mask tuple
        mock_generate.return_value = [[2, 5], [7, 10]]

        motif = motif_factory(session=session).create(content="Test motif content")
        assert len(motif.cloze_deletions) == 0

        service = Service(session)
        cloze_deletion = service.generate_cloze_deletion(motif.uuid)

        # Verify the OpenAI client was called with the motif content
        mock_generate.assert_called_once_with(motif.content)

        # Verify the cloze deletion was created with the mocked mask tuples
        assert cloze_deletion is not None
        assert cloze_deletion.mask_tuples == [[2, 5], [7, 10]]
        assert cloze_deletion.motif_uuid == motif.uuid

        # Check that the motif now has the cloze deletion
        session.refresh(motif)
        assert len(motif.cloze_deletions) == 1
        assert motif.cloze_deletions[0].mask_tuples == [[2, 5], [7, 10]]

    @patch("reprise.service.openai_generate_cloze_deletion")
    def test_add_default_cloze_deletion_fallback(self, mock_generate, session):
        # Mock the OpenAI API call to raise an exception
        mock_generate.side_effect = Exception("API Error")

        motif = motif_factory(session=session).create()
        assert len(motif.cloze_deletions) == 0

        service = Service(session)

        # Now we expect the exception to be raised
        with pytest.raises(Exception) as excinfo:
            service.generate_cloze_deletion(motif.uuid)

        assert "API Error" in str(excinfo.value)
