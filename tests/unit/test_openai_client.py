from unittest.mock import MagicMock, patch

import pytest

from reprise.openai_client import (
    find_word_indices,
    generate_cloze_deletions,
)


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
        # Setup mock chat completions
        mock_completion = MagicMock()
        mock_completion.choices = [
            MagicMock(
                message=MagicMock(
                    content='{"cloze_deletion_sets": [["sky", "blue"], ["is"]]}'
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_completion

        # Test the function
        result = generate_cloze_deletions("The sky is blue")

        # Verify the result
        assert len(result) == 2
        assert result[0] == [[4, 6], [11, 14]]
        assert result[1] == [[8, 9]]
        mock_client.chat.completions.create.assert_called_once()

    @patch("reprise.openai_client.OPENAI_API_KEY", None)
    def test_generate_cloze_deletions_no_api_key(self):
        # Test when API key is not provided
        with pytest.raises(ValueError) as excinfo:
            generate_cloze_deletions("The sky is blue")
        assert "OpenAI API key is required" in str(excinfo.value)

    @patch("reprise.openai_client.client")
    @patch("reprise.openai_client.OPENAI_API_KEY", "fake-api-key")
    def test_generate_cloze_deletions_invalid_json(self, mock_client):
        # Setup mock response with invalid JSON
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=MagicMock(content="invalid json"))]
        mock_client.chat.completions.create.return_value = mock_completion

        # Test the function
        with pytest.raises(ValueError) as excinfo:
            generate_cloze_deletions("The sky is blue")
        assert "Invalid JSON" in str(excinfo.value)

    @patch("reprise.openai_client.client")
    @patch("reprise.openai_client.OPENAI_API_KEY", "fake-api-key")
    def test_generate_cloze_deletions_missing_cloze_deletion_sets(self, mock_client):
        # Setup mock response with missing cloze_deletion_sets key
        mock_completion = MagicMock()
        mock_completion.choices = [
            MagicMock(message=MagicMock(content='{"other_key": "value"}'))
        ]
        mock_client.chat.completions.create.return_value = mock_completion

        # Test the function
        with pytest.raises(ValueError) as excinfo:
            generate_cloze_deletions("The sky is blue")
        assert "missing required 'cloze_deletion_sets' field" in str(excinfo.value)

    @patch("reprise.openai_client.client")
    @patch("reprise.openai_client.OPENAI_API_KEY", "fake-api-key")
    def test_generate_cloze_deletions_invalid_cloze_deletion_sets(self, mock_client):
        # Setup mock response with invalid cloze_deletion_sets format
        mock_completion = MagicMock()
        mock_completion.choices = [
            MagicMock(message=MagicMock(content='{"cloze_deletion_sets": 123}'))
        ]
        mock_client.chat.completions.create.return_value = mock_completion

        # Test the function
        with pytest.raises(ValueError) as excinfo:
            generate_cloze_deletions("The sky is blue")
        assert "Invalid cloze_deletion_sets format" in str(excinfo.value)

    @patch("reprise.openai_client.client")
    @patch("reprise.openai_client.OPENAI_API_KEY", "fake-api-key")
    def test_generate_cloze_deletions_no_matches(self, mock_client):
        # Setup mock response with words that don't exist in the text
        mock_completion = MagicMock()
        mock_completion.choices = [
            MagicMock(
                message=MagicMock(content='{"cloze_deletion_sets": [["red", "green"]]}')
            )
        ]
        mock_client.chat.completions.create.return_value = mock_completion

        # Test the function
        with pytest.raises(ValueError) as excinfo:
            generate_cloze_deletions("The sky is blue")
        assert "No valid mask tuples found" in str(excinfo.value)

    @patch("reprise.openai_client.client")
    @patch("reprise.openai_client.OPENAI_API_KEY", "fake-api-key")
    def test_generate_cloze_deletions_api_error(self, mock_client):
        # Setup mock to raise an exception
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        # Test the function
        with pytest.raises(Exception) as excinfo:
            generate_cloze_deletions("The sky is blue")
        assert "API Error" in str(excinfo.value)

    @patch("reprise.openai_client.client")
    @patch("reprise.openai_client.OPENAI_API_KEY", "fake-api-key")
    def test_generate_cloze_deletions_key_error(self, mock_client):
        # Setup a mock that produces valid JSON but will cause KeyError during processing
        mock_completion = MagicMock()
        # This will pass validation but cause a TypeError when accessing word in find_word_indices
        mock_completion.choices = [
            MagicMock(message=MagicMock(content='{"cloze_deletion_sets": [["blue"]]}'))
        ]
        mock_client.chat.completions.create.return_value = mock_completion

        # Mock find_word_indices to raise KeyError
        with patch("reprise.openai_client.find_word_indices") as mock_find:
            mock_find.side_effect = KeyError("Test KeyError")

            # Test the function
            with pytest.raises(ValueError) as excinfo:
                generate_cloze_deletions("The sky is blue")
            assert "Error extracting data from OpenAI response" in str(excinfo.value)

    @patch("reprise.openai_client.client")
    @patch("reprise.openai_client.OPENAI_API_KEY", "fake-api-key")
    def test_generate_cloze_deletions_with_n_max(self, mock_client):
        """Test the generate_cloze_deletions function with the n_max parameter."""
        # Setup mock chat completions
        mock_completion = MagicMock()
        mock_completion.choices = [
            MagicMock(
                message=MagicMock(
                    content='{"cloze_deletion_sets": [["sky"], ["blue"], ["is"]]}'
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_completion

        # Test the function with n_max=5
        result = generate_cloze_deletions("The sky is blue", n_max=5)

        # Verify the result has 3 sets (the model decided to use fewer than n_max)
        assert len(result) == 3
        assert result[0] == [[4, 6]]
        assert result[1] == [[11, 14]]
        assert result[2] == [[8, 9]]

        # Check that n_max was properly passed in the API call
        call_args = mock_client.chat.completions.create.call_args[1]
        messages = call_args["messages"]
        assert "up to 5 sets" in messages[0]["content"]
        assert "maximum 5" in messages[1]["content"]
