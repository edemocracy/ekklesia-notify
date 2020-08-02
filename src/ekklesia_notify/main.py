import json
from random import randint
from eliot import log_call, start_task
from fastapi import FastAPI
from ekklesia_notify.models import FreeformMessage, TemplatedMessage
from ekklesia_notify import configure_logging
from ekklesia_notify.transport import Recipient
from ekklesia_notify.transport.logging_dummy import LoggingDummyTransport
from ekklesia_notify.transport.mail import MailTransport
from ekklesia_notify.transport.matrix import MatrixTransport

configure_logging()

app = FastAPI()

TRANSPORTS = {
    'mail': MailTransport(),
    'matrix': MatrixTransport(),
    'logging': LoggingDummyTransport()
}


@app.get('/')
def api_info():
    return {'info': 'Ekklesia Notification service. Have a look at /docs to see how the messaging API can be used.'}


@app.post('/templated_message')
async def send_templated_message(msg: TemplatedMessage):

    with start_task(task="send_templated_message"):
        transport = TRANSPORT()
        await transport.connect()
        await transport.send_templated_message(msg)
        await transport.disconnect()

    return {'msg_id': randint(0, 10000)}


@log_call
def decode_recipient_info(recipient_info, sender):
    if isinstance(recipient_info, dict):
        return recipient_info

    from nacl import pwhash, secret, utils
    import base64

    ops = pwhash.argon2i.OPSLIMIT_SENSITIVE
    mem = pwhash.argon2i.MEMLIMIT_SENSITIVE
    kdf = pwhash.argon2i.kdf

    password = b"matrix"
    salt, ciphertext = [base64.b64decode(d) for d in recipient_info.split(":")]

    key = kdf(secret.SecretBox.KEY_SIZE, password, salt, opslimit=ops, memlimit=mem)
    box = secret.SecretBox(key)
    received = box.decrypt(ciphertext)
    decoded = received.decode('utf-8')

    return json.loads(decoded)


@app.post('/freeform_message')
async def send_freeform_message(msg: FreeformMessage):

    with start_task(task="send_freeform_message"):

        recipient_info = decode_recipient_info(msg.recipient_info, msg.sender)

        for transport_id, recipient in recipient_info.items():
            transport = TRANSPORTS[transport_id]
            await transport.connect()
            await transport.send_freeform_message(msg, recipient)
            await transport.disconnect()

    return {'msg_id': randint(0, 10000)}
