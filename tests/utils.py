from unittest.mock import MagicMock


def mock_chat_completion_response(content: str):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content=content))]
    return mock_response
