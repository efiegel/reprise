from datetime import datetime
from email.utils import formatdate
from typing import List

import requests

from reprise.db import database_session
from reprise.formatters import simple_formatter
from reprise.repository import ReprisalScheduleRepository
from reprise.service import Service
from reprise.settings import (
    MAILGUN_API_KEY,
    MAILGUN_DOMAIN,
    MAILGUN_RECIPIENT,
)


class MailgunDispatcher:
    def __init__(self):
        pass

    def schedule(self, target_times: List[datetime] = None):
        with database_session() as session:
            service = Service(session)
            schedule_repo = ReprisalScheduleRepository(session)

            # Get existing schedules
            existing_schedules = schedule_repo.get_reprisal_schedules()

            # Schedule for times that don't have coverage
            for target_time in target_times:
                # Check if there's already a schedule within 30 minutes of this time
                has_coverage = any(
                    abs((s.scheduled_for - target_time).total_seconds()) < 1800
                    for s in existing_schedules
                )

                if not has_coverage:
                    reprisals = service.reprise()
                    if reprisals:  # Only proceed if we got some reprisals
                        content = simple_formatter(reprisals)
                        self._send_to_mailgun(content, target_time)
                        schedule_repo.add_reprisal_schedule(
                            reprisals[0].set_uuid, target_time
                        )

    def _send_to_mailgun(self, content: str, delivery_time: datetime) -> None:
        subject = f"Reprise {delivery_time.strftime('%Y-%m-%d %H:%M')}"
        delivery_time_str = formatdate(delivery_time.timestamp(), localtime=True)

        response = requests.post(
            f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
            auth=("api", MAILGUN_API_KEY),
            data={
                "from": f"Reprise <postmaster@{MAILGUN_DOMAIN}>",
                "to": MAILGUN_RECIPIENT,
                "subject": subject,
                "text": content,
                "o:deliverytime": delivery_time_str,
            },
        )

        if response.status_code != 200:
            raise Exception(f"Failed to schedule email: {response.text}")
