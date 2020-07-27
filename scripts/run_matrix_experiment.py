import asyncio
from ekklesia_notify.lib.matrix import get_or_create_direct_room, login, message_to_recipient, send, after_first_sync, make_client


loop = asyncio.get_event_loop()
loop.set_debug(True)
cl = make_client()


async def main():
    await login(cl)
    asyncio.create_task(cl.sync_forever(timeout=30000, full_state=True))
    #room_id = "!GjKKengyQMFtwweFRq:matrix.org" # mytestroom
    #room_id  ="!RrbGmwkePLWftzHgTM:matrix.org" # test-unencrypted
    await after_first_sync(cl)
    #await message_to_recipient("hi", 'escap')
    #await asyncio.gather(*(send(cl, room_id, f"hi{ii}") for ii in range(3)))
    #await send(cl, room_id, "fertig")


asyncio.get_event_loop().run_until_complete(main())
