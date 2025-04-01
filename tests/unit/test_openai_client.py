from unittest.mock import patch

import pytest

from reprise.openai_client import (
    find_word_indices,
    generate_cloze_deletions,
)
from tests.utils import mock_chat_completion_response


class TestOpenAIClient:
    @pytest.mark.parametrize(
        "text, words_to_mask, expected_indices",
        [
            ("The sky is blue", ["blue"], [[11, 14]]),
            (
                "The sky is blue and the grass is green",
                ["sky", "green"],
                [[4, 6], [33, 37]],
            ),
            ("The blue sky is blue", ["blue"], [[4, 7], [16, 19]]),
            ("The Sky is blue", ["Sky"], [[4, 6]]),
            ("The sky is blue", ["red"], []),
            ("The sky is blue", [], []),
            ("", ["word"], []),
            ("skylark skies sky", ["sky"], [[14, 16]]),
            ("The sky is blue and the blue sky is nice", ["blue sky"], [[24, 31]]),
            ("The problem: sky is very blue.", ["sky", "blue"], [[13, 15], [25, 28]]),
            ("The time complexity is O(n log n)", ["O(n log n)"], [[23, 32]]),
        ],
    )
    def test_find_word_indices_parametrized(
        self, text, words_to_mask, expected_indices
    ):
        """Test find_word_indices with various inputs using parametrization."""
        result = find_word_indices(text, words_to_mask)
        assert result == expected_indices

    @patch("reprise.openai_client.client")
    @patch("reprise.openai_client.OPENAI_API_KEY", "fake-api-key")
    def test_generate_cloze_deletions_success(self, mock_client):
        mock_client.chat.completions.create.return_value = (
            mock_chat_completion_response(
                '{"cloze_deletion_sets": [["sky", "blue"], ["is"]]}'
            )
        )

        result = generate_cloze_deletions("The sky is blue")

        assert len(result) == 2
        assert result[0] == [[4, 6], [11, 14]]
        assert result[1] == [[8, 9]]
        mock_client.chat.completions.create.assert_called_once()

    @patch("reprise.openai_client.OPENAI_API_KEY", None)
    def test_generate_cloze_deletions_no_api_key(self):
        with pytest.raises(ValueError) as excinfo:
            generate_cloze_deletions("The sky is blue")
        assert "OpenAI API key is required" in str(excinfo.value)

    @patch("reprise.openai_client.client")
    @patch("reprise.openai_client.OPENAI_API_KEY", "fake-api-key")
    def test_generate_cloze_deletions_error_handling(self, mock_client):
        test_cases = [
            # Invalid JSON
            mock_chat_completion_response("invalid json"),
            # Missing cloze_deletion_sets key
            mock_chat_completion_response('{"other_key": "value"}'),
            # Invalid cloze_deletion_sets format
            mock_chat_completion_response('{"cloze_deletion_sets": 123}'),
            # Words that don't exist in text
            mock_chat_completion_response(
                '{"cloze_deletion_sets": [["red", "green"]]}'
            ),
            # API error
            Exception("API Error"),
        ]

        for case in test_cases:
            if isinstance(case, Exception):
                mock_client.chat.completions.create.side_effect = case
            else:
                mock_client.chat.completions.create.return_value = case

            with pytest.raises(Exception):
                generate_cloze_deletions("The sky is blue")

    @patch("reprise.openai_client.client")
    @patch("reprise.openai_client.OPENAI_API_KEY", "fake-api-key")
    def test_generate_cloze_deletions_with_n_max(self, mock_client):
        """Test the generate_cloze_deletions function with the n_max parameter."""
        mock_client.chat.completions.create.return_value = (
            mock_chat_completion_response(
                '{"cloze_deletion_sets": [["sky"], ["blue"], ["is"]]}'
            )
        )

        result = generate_cloze_deletions("The sky is blue", n_max=5)

        # Verify the result has 3 sets (the model decided to use fewer than n_max)
        assert len(result) == 3
        assert result[0] == [[4, 6]]
        assert result[1] == [[11, 14]]
        assert result[2] == [[8, 9]]

        # Ensure that n_max was properly passed in the API call
        call_args = mock_client.chat.completions.create.call_args[1]
        messages = call_args["messages"]
        assert "up to 5 sets" in messages[0]["content"]
        assert "maximum 5" in messages[1]["content"]
