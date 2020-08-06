from random import randint
from eliot import start_task
from fastapi import FastAPI
from ekklesia_notify.lib.crypto import decode_recipient_info
from ekklesia_notify.models import FreeformMessage, TemplatedMessage
from ekklesia_notify import configure_logging
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
