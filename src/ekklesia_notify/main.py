from typing import Optional, Any, Dict
from fastapi import FastAPI
from random import randint
from ekklesia_notify.models import FreeformMessage, TemplatedMessage


app = FastAPI()


@app.get('/')
def api_info():
    return {'info': 'Ekklesia Notification service. Have a look at /docs to see how the messaging API can be used.'}



@app.post('/templated_message')
async def send_templated_message(msg: TemplatedMessage):
    print(msg)
    return {'msg_id': randint(0, 10000)}


@app.post('/freeform_message')
async def send_freeform_message(msg: FreeformMessage):
    print(msg)
    for connector in connectors:
        await connector.send_freeform_message(msg)

    return {'msg_id': randint(0, 10000)}
