from typing import TypedDict
from ekklesia_notify.models import FreeformMessage, TemplatedMessage


class Recipient(TypedDict):
    pass


class Transport:
    async def connect(self):
        raise NotImplementedError()

    async def send_freeform_message(self, msg: FreeformMessage, recipient: Recipient):
        raise NotImplementedError()

    async def send_templated_message(self, msg: TemplatedMessage, recipient: Recipient):
        raise NotImplementedError()

    async def disconnect(self):
        raise NotImplementedError()
