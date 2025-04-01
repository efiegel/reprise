from unittest.mock import MagicMock


def mock_chat_completion_response(mock_openai_client: MagicMock, content: str) -> None:
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content=content))]
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_client.return_value = mock_client
