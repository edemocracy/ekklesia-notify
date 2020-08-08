import asyncio
from typing import Any, Dict, List
from eliot import start_action, Message
from nio.client.async_client import AsyncClient
from ekklesia_notify.models import FreeformMessage, TemplatedMessage
from ekklesia_notify.transport import Recipient, Transport
from ekklesia_notify.lib.matrix import after_first_sync, get_or_create_direct_room, make_client, send, login
from ekklesia_notify.lib.templating import render_template


BODY_TEMPLATE = '''
**{subject}**

{content}
'''.strip()


class MatrixRecipient(Recipient):
    matrix_ids: List[str]


class MatrixTransport(Transport):

    cl: AsyncClient

    def __init__(self, transport_name: str = "matrix") -> None:
        self.transport_name = transport_name

    async def connect(self):
        self.cl = cl = make_client()
        await login(cl)
        asyncio.create_task(cl.sync_forever(timeout=30000, full_state=True))
        await after_first_sync(cl)
        Message.log(transport="matrix", state="ready")

    async def _send_messages(self, recipient: MatrixRecipient, body):
        for mxid in recipient['matrix_ids']:
            with start_action(action_type="communicate", transport="matrix", mxid=mxid):
                room_id = await get_or_create_direct_room(self.cl, mxid)
                await send(self.cl, room_id, body)

    async def send_freeform_message(self, msg: FreeformMessage, recipient: MatrixRecipient, client_settings):
        with start_action(action_type="send_freeform_message", transport="matrix", **msg.dict()):
            body = BODY_TEMPLATE.format(**msg.dict())
            await self._send_messages(recipient, body)

    async def send_templated_message(self, msg: TemplatedMessage, recipient: MatrixRecipient, client_settings):
        with start_action(action_type="send_templated_message", transport="matrix", **msg.dict()):
            body = render_template(msg, self.transport_name, client_settings)
            await self._send_messages(recipient, body)

    async def disconnect(self):
        Message.log(transport="matrix", state="shutdown")
