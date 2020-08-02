import asyncio
from typing import List
from eliot import start_action, Message
from ekklesia_notify.lib.mail import login, make_client, send
from ekklesia_notify.models import FreeformMessage, TemplatedMessage
from ekklesia_notify.transport import Recipient, Transport


class MailRecipient(Recipient):
    to: List[str]


class MailTransport(Transport):

    async def connect(self):
        self.cl = make_client()
        login(self.cl)
        Message.log(transport="mail", state="ready")

    async def send_freeform_message(self, msg: FreeformMessage, recipient: MailRecipient):
        with start_action(action_type="send_freeform_message", transport="mail", **msg.dict()):
            for to_addr in recipient['to'][:10]:
                send(self.cl, to_addr, msg.subject, msg.content)

    async def send_templated_message(self, msg: TemplatedMessage):
        with start_action(transport="mail", msg_type="templated", **msg.dict()):
            pass

    async def disconnect(self):
        self.cl.close()
        Message.log(transport="mail", state="shutdown")

