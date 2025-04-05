from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from reprise.dispatcher import MailgunDispatcher
from reprise.settings import MAILGUN_API_KEY, MAILGUN_DOMAIN, MAILGUN_RECIPIENT


class TestMailgunDispatcher:
    @pytest.fixture
    def mock_requests(self):
        with patch("requests.post") as mock_post:
            yield mock_post

    @pytest.fixture
    def mock_service(self):
        with patch("reprise.dispatcher.Service") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.reprise.return_value = []
            yield mock_instance

    def test_send_to_mailgun_calls_mailgun_api(self, mock_requests):
        dispatcher = MailgunDispatcher()
        content = "Test email content"
        delivery_time = datetime.now()

        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.return_value = mock_response

        # Execute
        dispatcher._send_to_mailgun(content, delivery_time)

        # Verify
        mock_requests.assert_called_once()
        call_args = mock_requests.call_args[1]
        assert call_args["auth"] == ("api", MAILGUN_API_KEY)
        assert call_args["data"]["from"] == f"Reprise <postmaster@{MAILGUN_DOMAIN}>"
        assert call_args["data"]["to"] == MAILGUN_RECIPIENT
        assert call_args["data"]["text"] == content

    def test_send_to_mailgun_failure(self, mock_requests):
        dispatcher = MailgunDispatcher()
        content = "Test email content"
        delivery_time = datetime.now()

        # Mock failed response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Server error"
        mock_requests.return_value = mock_response

        # Execute and verify exception
        with pytest.raises(Exception) as exc_info:
            dispatcher._send_to_mailgun(content, delivery_time)
        assert "Failed to schedule email: Server error" in str(exc_info.value)

    def test_schedule(self, mock_service, mock_requests):
        # Setup
        dispatcher = MailgunDispatcher()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.return_value = mock_response

        # Execute
        dispatcher.schedule()

        # Verify
        mock_service.reprise.assert_called_once()
        mock_requests.assert_called_once()
