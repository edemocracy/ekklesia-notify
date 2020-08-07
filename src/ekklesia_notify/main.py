from random import randint
import secrets
from eliot import start_task
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from ekklesia_notify.lib.crypto import decode_recipient_info
from ekklesia_notify.models import FreeformMessage, TemplatedMessage
from ekklesia_notify import configure_logging
from ekklesia_notify.transport.logging_dummy import LoggingDummyTransport
from ekklesia_notify.transport.mail import MailTransport
from ekklesia_notify.transport.matrix import MatrixTransport
from ekklesia_notify.settings import clients

configure_logging()

app = FastAPI()

security = HTTPBasic()

TRANSPORTS = {
    'mail': MailTransport(),
    'matrix': MatrixTransport(),
    'logging': LoggingDummyTransport()
}


def identify_client(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    client_settings = clients.get(credentials.username, {})
    expected_password = client_settings.get("password", "wrong username")
    if client_settings:
        password_correct = secrets.compare_digest(credentials.password, expected_password)
    else:
        password_correct = secrets.compare_digest("invalid", expected_password)

    if not password_correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorrect username or password",
            headers={"WWW-Authenticate": "Basic"})

    return credentials.username



@app.get('/')
def api_info():
    return {'info': 'Ekklesia Notification service. Have a look at /docs to see how the messaging API can be used.'}


@app.post('/templated_message')
async def send_templated_message(msg: TemplatedMessage, client_name: str = Depends(identify_client)):

    with start_task(task="send_templated_message"):
        transport = TRANSPORT()
        await transport.connect()
        await transport.send_templated_message(msg)
        await transport.disconnect()

    return {'msg_id': randint(0, 10000)}


@app.post('/freeform_message')
async def send_freeform_message(msg: FreeformMessage, client_name: str = Depends(identify_client)):

    with start_task(task="send_freeform_message"):

        recipient_info = decode_recipient_info(msg.recipient_info, msg.sender)

        for transport_id, recipient in recipient_info.items():
            transport = TRANSPORTS[transport_id]
            await transport.connect()
            await transport.send_freeform_message(msg, recipient)
            await transport.disconnect()

    return {'msg_id': randint(0, 10000)}
