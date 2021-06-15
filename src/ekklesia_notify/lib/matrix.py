import json
import os
import sys
import asyncio
from nio import AsyncClientConfig, MatrixRoom, RoomMessageText, AsyncClient, LoginResponse

from eliot import log_call, start_action, Message
import markdown
from nio.event_builders.state_events import EnableEncryptionBuilder
from nio.responses import RoomCreateResponse

import ekklesia_notify.settings

settings = ekklesia_notify.settings.settings.transport_settings.matrix


def make_client():
    client_config = AsyncClientConfig(encryption_enabled=True)
    return AsyncClient(
        settings.homeserver,
        settings.mxid,
        device_id=settings.device_id,
        config=client_config,
        store_path=settings.store_dir
    )


@log_call
def write_details_to_disk(resp: LoginResponse) -> None:
    """Writes login details to disk so that we can restore our session later
        without logging in again and creating a new device ID.
        Arguments:
            resp {LoginResponse} -- the successful client login response.
        """
    with open(settings.session_details_file, "w") as f:
        json.dump({"access_token": resp.access_token, "device_id": resp.device_id, "user_id": resp.user_id}, f)


@log_call
async def login(cl) -> None:
    """Log in either using the global variables or (if possible) using the
    session details file.
    """
    # Restore the previous session if we can
    # See the "restore_login.py" example if you're not sure how this works
    session_details_file = settings.session_details_file

    if os.path.exists(session_details_file) and os.path.isfile(session_details_file):
        try:
            with open(session_details_file, "r") as f:
                config = json.load(f)
                cl.access_token = config['access_token']
                cl.user_id = config['user_id']
                cl.device_id = config['device_id']

                # This loads our verified/blacklisted devices and our keys
                cl.load_store()
                print(f"Logged in using stored credentials: {cl.user_id} on {cl.device_id}")

        except IOError as err:
            print(f"Couldn't load session from file. Logging in. Error: {err}")
        except json.JSONDecodeError:
            print("Couldn't read JSON file; overwriting")

    # We didn't restore a previous session, so we'll log in with a password
    if not cl.user_id or not cl.access_token or not cl.device_id:
        # this calls the login method defined in AsyncClient from nio
        resp = await cl.login(settings.password.get_secret_value())

        if isinstance(resp, LoginResponse):
            print("Logged in using a password; saving details to disk")
            write_details_to_disk(resp)
        else:
            print(f"Failed to log in: {resp}")
            sys.exit(1)


async def after_first_sync(cl: AsyncClient):
    with start_action(action_type="after_first_sync") as action:
        await cl.synced.wait()
        resp = await cl.joined_rooms()
        action.add_success_fields(joined_rooms=resp.rooms, cl_rooms=cl.rooms)


async def message_callback(room: MatrixRoom, event: RoomMessageText) -> None:
    print(f"Message received in room {room.display_name}\n" f"{room.user_name(event.sender)} | {event.body}")


async def send(cl: AsyncClient, room_id: str, body: str):
    formatted_body = markdown.markdown(body)

    with start_action(action_type="send", room_id=room_id, cl_rooms=cl.rooms) as action:
        resp = await cl.room_send(
            room_id=room_id,
            message_type="m.room.message",
            ignore_unverified_devices=True,
            content={
                "msgtype": "m.text",
                "body": body,
                "format": "org.matrix.custom.html",
                "formatted_body": formatted_body
            }
        )
        action.add_success_fields(response=resp)


@log_call
def find_room_id(cl, mxid):
    for room_id, room in cl.rooms.items():
        if mxid in room.users:
            return room_id


@log_call
async def get_or_create_direct_room(cl: AsyncClient, mxid: str) -> str:

    room_id = find_room_id(cl, mxid)

    if room_id:
        Message.log(msg="using existing room", room=room_id)
        return room_id

    with start_action(action_type="create_direct_room", recipient=mxid) as action:
        resp = await cl.room_create(
            name="Benachrichtigungen",
            topic="Hier gibts Benachrichtigungen",
            federate=False,
            invite=[mxid],
            initial_state=[EnableEncryptionBuilder().as_dict()]
        )
        if isinstance(resp, RoomCreateResponse):
            action.add_success_fields(response=resp)
        else:
            raise Exception("failed to create room")

    room_id = resp.room_id

    with start_action(action_type="join_room", room=room_id):
        await cl.join(room_id)

    return room_id


async def message_to_recipient(body: str, recipient: str):
    cl = make_client()
    await login(cl)
    asyncio.create_task(cl.sync_forever(timeout=30000, full_state=True))
    await after_first_sync(cl)
    room_id = await get_or_create_direct_room(cl, recipient)
    await send(cl, room_id, body)
