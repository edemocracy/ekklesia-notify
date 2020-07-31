from ekklesia_notify.models import FreeformMessage, TemplatedMessage


class Transport:
    async def connect(self):
        raise NotImplementedError()

    async def send_freeform_message(self, msg: FreeformMessage):
        raise NotImplementedError()

    async def send_templated_message(self, msg: TemplatedMessage):
        raise NotImplementedError()

    async def disconnect(self):
        raise NotImplementedError()
