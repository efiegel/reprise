from unittest.mock import patch

import pytest

from reprise.service import Service
from tests.factories import cloze_deletion_factory, motif_factory
from tests.utils import mock_chat_completion_response


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

    def test_generate_cloze_deletion(self, mock_openai_client, session):
        mock_openai_client.return_value = mock_chat_completion_response(
            '{"cloze_deletion_sets": [["George Washington"], ["George", "president"]]}'
        )

        motif_content = "George Washington was the first president"
        motif = motif_factory(session=session).create(content=motif_content)
        assert len(motif.cloze_deletions) == 0

        service = Service(session)
        cloze_deletions = service.cloze_delete_motif(motif.uuid, n_max=2)

        # Verify the cloze deletion was created with the mocked mask tuples
        assert len(cloze_deletions) == 2
        assert cloze_deletions[0].mask_tuples == [[0, 16]]
        assert cloze_deletions[0].motif_uuid == motif.uuid
        assert cloze_deletions[1].mask_tuples == [[0, 5], [32, 40]]
        assert cloze_deletions[1].motif_uuid == motif.uuid

        # Check that the motif now has both cloze deletions
        session.refresh(motif)
        assert len(motif.cloze_deletions) == 2
        # The order might not be guaranteed, so we'll check both possibilities
        mask_tuples_list = [cd.mask_tuples for cd in motif.cloze_deletions]
        assert [[0, 16]] in mask_tuples_list
        assert [[0, 5], [32, 40]] in mask_tuples_list

    @patch("reprise.openai_client.client.chat.completions.create")
    def test_generate_cloze_deletion_fallback(self, mock_openai, session):
        # Mock the OpenAI API call to raise an exception
        mock_openai.side_effect = Exception("API Error")

        motif = motif_factory(session=session).create()
        assert len(motif.cloze_deletions) == 0

        service = Service(session)

        # Now we expect the exception to be raised
        with pytest.raises(Exception) as excinfo:
            service.cloze_delete_motif(motif.uuid, n_max=1)

        assert "API Error" in str(excinfo.value)
