from random import randint
from eliot import log_call, start_task
from fastapi import FastAPI
from ekklesia_notify.models import FreeformMessage, TemplatedMessage
from ekklesia_notify import configure_logging
from ekklesia_notify.transport.logging_dummy import LoggingDummyTransport
from ekklesia_notify.transport.matrix import MatrixTransport

configure_logging()

app = FastAPI()

TRANSPORT = MatrixTransport


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
        transport = TRANSPORT()
        await transport.connect()
        await transport.send_freeform_message(msg)
        await transport.disconnect()

    #for transport in transports:
    #   msg = decrypt_recipient(msg)
    #   await transport.send_freeform_message(msg)

    return {'msg_id': randint(0, 10000)}
