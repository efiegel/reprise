from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from reprise.db import ReprisalSchedule
from reprise.dispatcher import MailgunDispatcher
from reprise.settings import MAILGUN_API_KEY, MAILGUN_DOMAIN, MAILGUN_RECIPIENT
from tests.factories import (
    motif_factory,
    reprisal_factory,
    reprisal_schedule_factory,
)


class TestMailgunDispatcher:
    @pytest.fixture
    def mock_mailgun_api(self):
        with patch("requests.post") as mock_post:
            mock_response = mock_post.return_value
            mock_response.status_code = 200
            yield mock_post

    def test_send_to_mailgun_calls_mailgun_api(self, mock_mailgun_api):
        dispatcher = MailgunDispatcher()
        content = "Test email content"
        delivery_time = datetime.now()

        # Execute
        dispatcher._send_to_mailgun(content, delivery_time)

        # Verify
        mock_mailgun_api.assert_called_once()
        call_args = mock_mailgun_api.call_args[1]
        assert call_args["auth"] == ("api", MAILGUN_API_KEY)
        assert call_args["data"]["from"] == f"Reprise <postmaster@{MAILGUN_DOMAIN}>"
        assert call_args["data"]["to"] == MAILGUN_RECIPIENT
        assert call_args["data"]["text"] == content

    def test_send_to_mailgun_failure(self, mock_mailgun_api):
        mock_mailgun_api.return_value.status_code = 500
        mock_mailgun_api.return_value.text = "Server error"

        dispatcher = MailgunDispatcher()
        content = "Test email content"
        delivery_time = datetime.now()

        # Execute and verify exception
        with pytest.raises(Exception) as exc_info:
            dispatcher._send_to_mailgun(content, delivery_time)
        assert "Failed to schedule email: Server error" in str(exc_info.value)

    def test_schedule(self, session, mock_mailgun_api):
        motif_factory(session=session).create_batch(5)

        # Create test times (9am and 5pm for next 3 days)
        now = datetime.now()
        target_times = []
        for i in range(3):
            target_times.append(now.replace(hour=9, minute=0) + timedelta(days=i))
            target_times.append(now.replace(hour=17, minute=0) + timedelta(days=i))

        # Execute
        dispatcher = MailgunDispatcher()
        dispatcher.schedule(target_times)

        # Verify
        assert mock_mailgun_api.call_count == 6  # Called for each time
        schedules = session.query(ReprisalSchedule).all()
        assert len(schedules) == 6

    def test_schedule_skips_existing_times(self, session, mock_mailgun_api):
        motif_factory(session=session).create()

        # Create an existing schedule
        target_time = datetime.now()
        reprisal = reprisal_factory(session=session).create()
        reprisal_schedule_factory(session=session).create(
            reprisal_set_uuid=reprisal.set_uuid,
            scheduled_for=target_time + timedelta(minutes=5),
        )

        # Execute
        dispatcher = MailgunDispatcher()
        dispatcher.schedule([target_time], schedule_buffer=timedelta(minutes=10))

        # Verify skipped due to existing schedule
        mock_mailgun_api.assert_not_called()
        schedules = session.query(ReprisalSchedule).all()
        assert len(schedules) == 1
