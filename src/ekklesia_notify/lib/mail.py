from email.mime.text import MIMEText
from email.utils import formatdate

from cryptography.hazmat import backends
from cryptography.hazmat.primitives.serialization import pkcs12
from eliot import log_call
from endesive import email
from aiosmtplib import SMTP

from ekklesia_notify.settings import transport_settings

settings = transport_settings['mail']

HEADER_TEMPLATE = '''
Subject: {subject}
From: {sender}
To: {to}
Date: {date}
Auto-Submitted: auto-generated
'''


def load_smime_p12():
    with open(settings["cert_p12"], 'rb') as fp:
        return pkcs12.load_key_and_certificates(
            fp.read(), settings["cert_password"].encode("utf8"), backends.default_backend()
        )


def make_client() -> SMTP:
    return SMTP(settings["smtp_server"], settings["smtp_port"])


async def login(cl):
    await cl.connect()
    await cl.starttls()
    await cl.login(settings["smtp_user"], settings["smtp_password"])


@log_call
async def send(cl: SMTP, recipient: str, subject: str, body: str) -> None:

    headers = HEADER_TEMPLATE.format(
        subject=subject, sender=settings["sender"], to=recipient, date=formatdate(localtime=True)
    )

    mime_text = MIMEText(body, "plain")
    p12 = load_smime_p12()
    signed = email.sign(mime_text.as_bytes(), p12[0], p12[1], p12[2], 'sha512')

    body = signed.decode("ascii")
    content = (headers + body).strip()

    await cl.sendmail(settings["sender"], recipient, content)
