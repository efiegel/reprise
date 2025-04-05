from datetime import datetime, timedelta
from email.utils import formatdate

import requests

from .db import database_session
from .service import Service
from .settings import (
    MAILGUN_API_KEY,
    MAILGUN_DOMAIN,
    MAILGUN_RECIPIENT,
)

delivery_time = datetime.now() + timedelta(seconds=2)
rfc2822_date = formatdate(delivery_time.timestamp(), localtime=True)
email_subject_date = delivery_time.strftime("%Y-%m-%d %H:%M")

with database_session() as session:
    service = Service(session)
    reprisals = service.reprise()

    motif_content = []
    for reprisal in reprisals:
        motif_content.append(reprisal.motif.content)

    email_body = "\n".join(motif_content)
    response = requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        auth=("api", MAILGUN_API_KEY),
        data={
            "from": f"Reprise <postmaster@{MAILGUN_DOMAIN}>",
            "to": MAILGUN_RECIPIENT,
            "subject": f"Reprise {email_subject_date}",
            "text": email_body,
            "o:deliverytime": rfc2822_date,
        },
    )

    if response.status_code == 200:
        print("Email scheduled successfully!")
    else:
        print(f"Failed to schedule email: {response.text}")
