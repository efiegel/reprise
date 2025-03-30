from unittest.mock import MagicMock, patch

import pytest

from reprise.openai_client import generate_cloze_deletion


class TestOpenAIClient:
    @patch("reprise.openai_client.client")
    @patch("reprise.openai_client.OPENAI_API_KEY", "fake-api-key")
    def test_generate_cloze_deletion_success(self, mock_client):
        # Setup mock chat completions
        mock_completion = MagicMock()
        mock_completion.choices = [
            MagicMock(message=MagicMock(content='{"mask_tuples": [[3, 7], [10, 14]]}'))
        ]
        mock_client.chat.completions.create.return_value = mock_completion

        # Test the function
        result = generate_cloze_deletion("The sky is blue")

        # Verify the result
        assert result == [[3, 7], [10, 14]]
        mock_client.chat.completions.create.assert_called_once()

    @patch("reprise.openai_client.OPENAI_API_KEY", None)
    def test_generate_cloze_deletion_no_api_key(self):
        # Test when API key is not provided
        with pytest.raises(ValueError) as excinfo:
            generate_cloze_deletion("The sky is blue")
        assert "OpenAI API key is required" in str(excinfo.value)

    @patch("reprise.openai_client.client")
    @patch("reprise.openai_client.OPENAI_API_KEY", "fake-api-key")
    def test_generate_cloze_deletion_invalid_json(self, mock_client):
        # Setup mock response with invalid JSON
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=MagicMock(content="invalid json"))]
        mock_client.chat.completions.create.return_value = mock_completion

        # Test the function
        with pytest.raises(ValueError) as excinfo:
            generate_cloze_deletion("The sky is blue")
        assert "Invalid JSON" in str(excinfo.value)

    @patch("reprise.openai_client.client")
    @patch("reprise.openai_client.OPENAI_API_KEY", "fake-api-key")
    def test_generate_cloze_deletion_missing_mask_tuples(self, mock_client):
        # Setup mock response with missing mask_tuples key
        mock_completion = MagicMock()
        mock_completion.choices = [
            MagicMock(message=MagicMock(content='{"other_key": "value"}'))
        ]
        mock_client.chat.completions.create.return_value = mock_completion

        # Test the function
        with pytest.raises(ValueError) as excinfo:
            generate_cloze_deletion("The sky is blue")
        assert "missing required 'mask_tuples' field" in str(excinfo.value)

    @patch("reprise.openai_client.client")
    @patch("reprise.openai_client.OPENAI_API_KEY", "fake-api-key")
    def test_generate_cloze_deletion_invalid_mask_tuples(self, mock_client):
        # Setup mock response with invalid mask_tuples format
        mock_completion = MagicMock()
        mock_completion.choices = [
            MagicMock(message=MagicMock(content='{"mask_tuples": "not a list"}'))
        ]
        mock_client.chat.completions.create.return_value = mock_completion

        # Test the function
        with pytest.raises(ValueError) as excinfo:
            generate_cloze_deletion("The sky is blue")
        assert "Invalid mask_tuples format" in str(excinfo.value)

    @patch("reprise.openai_client.client")
    @patch("reprise.openai_client.OPENAI_API_KEY", "fake-api-key")
    def test_generate_cloze_deletion_out_of_range(self, mock_client):
        # Setup mock response with out-of-range indices
        mock_completion = MagicMock()
        mock_completion.choices = [
            MagicMock(message=MagicMock(content='{"mask_tuples": [[20, 30]]}'))
        ]
        mock_client.chat.completions.create.return_value = mock_completion

        # Test the function with shorter text
        with pytest.raises(ValueError) as excinfo:
            generate_cloze_deletion("short")
        assert "No valid mask tuples found" in str(excinfo.value)

    @patch("reprise.openai_client.client")
    @patch("reprise.openai_client.OPENAI_API_KEY", "fake-api-key")
    def test_generate_cloze_deletion_api_error(self, mock_client):
        # Setup mock to raise an exception
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        # Test the function
        with pytest.raises(Exception) as excinfo:
            generate_cloze_deletion("The sky is blue")
        assert "API Error" in str(excinfo.value)
