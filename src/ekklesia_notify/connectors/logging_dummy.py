from ekklesia_notify.models import FreeformMessage, TemplatedMessage
from ekklesia_notify.connectors.connector import Connector


class LoggingDummyConnector(Connector):

    async def send_freeform_message(msg: FreeformMessage):
        raise NotImplementedError()

    async def send_templated_message(msg: TemplatedMessage):
        raise NotImplementedError()
