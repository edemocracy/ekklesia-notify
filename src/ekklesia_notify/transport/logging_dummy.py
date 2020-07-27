import asyncio
import random
from eliot import log_call, start_action, Message
from ekklesia_notify.models import FreeformMessage, TemplatedMessage
from ekklesia_notify.transport import Transport


class LoggingDummyTransport(Transport):

    async def connect(self):
        Message.log(transport="logging dummy", state="ready")

    async def _sleep(self):
        sleeptime = 2 * random.random()
        with start_action(action="sleeping", seconds=sleeptime):
            await asyncio.sleep(sleeptime)

    async def send_freeform_message(self, msg: FreeformMessage):
        with start_action(transport="LoggingDummy", msg_type="freeform", **msg.dict()):
            await self._sleep()

    @log_call
    async def send_templated_message(self, msg: TemplatedMessage):
        with start_action(transport="LoggingDummy", msg_type="templated", **msg.dict()):
            await self._sleep()

    async def disconnect(self):
        Message.log(msg="logging dummy transport is going to sleep")
