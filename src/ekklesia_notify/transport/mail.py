import asyncio
from eliot import start_action, Message
from nio.client.async_client import AsyncClient
from ekklesia_notify.lib.mail import login, make_client, send
from ekklesia_notify.models import FreeformMessage, TemplatedMessage
from ekklesia_notify.transport import Transport


class MailTransport(Transport):

    async def connect(self):
        self.cl = make_client()
        login(self.cl)
        Message.log(transport="mail", state="ready")

    async def send_freeform_message(self, msg: FreeformMessage):
        with start_action(transport="mail", msg_type="freeform", **msg.dict()):
            send(self.cl, msg.subject, msg.recipient, msg.content)

    async def send_templated_message(self, msg: TemplatedMessage):
        with start_action(transport="mail", msg_type="templated", **msg.dict()):
            pass

    async def disconnect(self):
        self.cl.close()
        Message.log(transport="mail", state="shutdown")

