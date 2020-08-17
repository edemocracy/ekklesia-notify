from typing import TypedDict
from ekklesia_notify.models import FreeformMessage, TemplatedMessage


class Recipient(TypedDict):
    pass


class SendFailed(Exception):
    pass


class Transport:

    async def connect(self):
        raise NotImplementedError()

    async def send_freeform_message(self, msg: FreeformMessage, recipient: Recipient, client_settings):
        raise NotImplementedError()

    async def send_templated_message(self, msg: TemplatedMessage, recipient: Recipient, client_settings):
        raise NotImplementedError()

    async def disconnect(self):
        raise NotImplementedError()
