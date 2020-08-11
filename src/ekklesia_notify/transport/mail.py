from typing import Any, Dict, List
from eliot import start_action, Message
from ekklesia_notify.lib.mail import login, make_client, send
from ekklesia_notify.lib.templating import render_template
from ekklesia_notify.models import FreeformMessage, TemplatedMessage
from ekklesia_notify.setting_models import ClientSettings
from ekklesia_notify.transport import Recipient, Transport


class MailRecipient(Recipient):
    to: List[str]


class MailTransport(Transport):

    def __init__(self, transport_name="mail") -> None:
        self.transport_name = transport_name

    async def connect(self):
        self.cl = make_client()
        await login(self.cl)
        Message.log(transport="mail", state="ready")

    async def send_freeform_message(self, msg: FreeformMessage, recipient: MailRecipient, client_settings):
        with start_action(action_type="send_freeform_message", transport="mail", **msg.dict()):
            for to_addr in recipient['to'][:10]:
                await send(self.cl, to_addr, msg.subject, msg.content)

    async def send_templated_message(self, msg: TemplatedMessage, recipient: MailRecipient, client_settings: ClientSettings):
        lines = render_template(msg, self.transport_name, client_settings).splitlines()

        subject = lines[0]
        body = "\n".join(lines[1:]).strip()

        with start_action(action_type="send_templated_message", transport="mail", **msg.dict()):
            for to_addr in recipient['to'][:10]:
                await send(self.cl, to_addr, subject, body)

    async def disconnect(self):
        self.cl.close()
        Message.log(transport="mail", state="shutdown")

