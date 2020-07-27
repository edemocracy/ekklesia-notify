from ekklesia_notify.models import FreeformMessage, TemplatedMessage


class Connector:
    async def send_freeform_message(msg: FreeformMessage):
        raise NotImplementedError()

    async def send_templated_message(msg: TemplatedMessage):
        raise NotImplementedError()
