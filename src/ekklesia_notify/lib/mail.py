from email.mime.text import MIMEText
from email.utils import formatdate

from cryptography.hazmat import backends
from cryptography.hazmat.primitives.serialization import pkcs12
from eliot import log_call
from endesive import email
from smtplib import SMTP

from ekklesia_notify.mail_settings import *


HEADER_TEMPLATE = '''
Subject: {subject}
From: {sender}
To: {to}
Date: {date}
Auto-Submitted: auto-generated
'''

def load_smime_p12():
    with open(CERT_P12, 'rb') as fp:
        return pkcs12.load_key_and_certificates(fp.read(), CERT_PASSWORD.encode("utf8"), backends.default_backend())


def make_client() -> SMTP:
    return SMTP(SMTP_SERVER, SMTP_PORT)


def login(cl):
    cl.ehlo()
    cl.starttls()
    cl.login(SMTP_USER, SMTP_PASSWORD)


@log_call
def send(cl: SMTP, recipient: str, subject: str, body: str) -> None:

    headers = HEADER_TEMPLATE.format(
        subject=subject,
        sender=SENDER,
        to=recipient,
        date=formatdate(localtime=True))

    mime_text = MIMEText(body, "plain")
    p12 = load_smime_p12()
    signed = email.sign(mime_text.as_bytes(), p12[0], p12[1], p12[2], 'sha512')

    body = signed.decode("ascii")
    content = (headers + body).strip()

    cl.sendmail(SENDER, recipient, content)


