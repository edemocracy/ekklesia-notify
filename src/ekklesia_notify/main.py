from random import randint
import secrets
from eliot import start_task
from ulid import ULID
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from ekklesia_notify.lib.crypto import decode_recipient_info
from ekklesia_notify.models import FreeformMessage, Message, MessageResponse, TemplatedMessage
from ekklesia_notify import configure_logging
from ekklesia_notify.setting_models import ClientSettings
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


def identify_client(credentials: HTTPBasicCredentials = Depends(security)) -> ClientSettings:
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

    return ClientSettings(**client_settings)


@app.get('/')
def api_info():
    return {'info': 'Ekklesia Notification service. Have a look at /docs to see how the messaging API can be used.'}


@app.post('/templated_message', response_model=MessageResponse)
async def send_templated_message(msg: TemplatedMessage, client_settings: ClientSettings = Depends(identify_client)):

    with start_task(task="send_templated_message") as task:

        recipient_info = decode_recipient_info(msg.recipient_info, msg.sender or client_settings.default_sender)

        for transport_id, recipient in recipient_info.items():
            transport = TRANSPORTS[transport_id]
            await transport.connect()
            await transport.send_templated_message(msg, recipient, client_settings)
            await transport.disconnect()

        msg_id = str(ULID())
        task.add_success_fields(msg_id=msg_id)

    return MessageResponse(msg_id=msg_id)


@app.post('/freeform_message', response_model=MessageResponse)
async def send_freeform_message(msg: FreeformMessage, client_settings: ClientSettings = Depends(identify_client)):

    with start_task(task="send_freeform_message") as task:

        recipient_info = decode_recipient_info(msg.recipient_info, msg.sender or client_settings.default_sender)

        for transport_id, recipient in recipient_info.items():
            transport = TRANSPORTS[transport_id]
            await transport.connect()
            await transport.send_freeform_message(msg, recipient, client_settings)
            await transport.disconnect()

        msg_id = str(ULID())
        task.add_success_fields(msg_id=msg_id)

    return MessageResponse(msg_id=msg_id)
