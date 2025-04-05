from datetime import datetime, timedelta
from email.utils import formatdate

import requests

from reprise.db import database_session
from reprise.formatters import simple_formatter
from reprise.service import Service
from reprise.settings import (
    MAILGUN_API_KEY,
    MAILGUN_DOMAIN,
    MAILGUN_RECIPIENT,
)


class MailgunDispatcher:
    def __init__(self):
        pass

    def schedule(self):
        with database_session() as session:
            service = Service(session)
            reprisals = service.reprise()
            content = simple_formatter(reprisals)

            delivery_time = datetime.now() + timedelta(seconds=2)
            self._send_to_mailgun(content, delivery_time)

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


if __name__ == "__main__":
    dispatcher = MailgunDispatcher()
    dispatcher.schedule()
