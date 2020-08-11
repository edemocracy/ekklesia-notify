import json
from base64 import b64decode
from typing import Union
from eliot import log_call
import nacl.secret
from ekklesia_notify.models import RecipientInfo
from ekklesia_notify.settings import nacl_keys


@log_call
def decrypt_nacl(sender, crypted):
    key = b64decode(nacl_keys[sender])
    box = nacl.secret.SecretBox(key)
    decrypted = box.decrypt(crypted)
    return decrypted.decode("utf8")


@log_call
def decode_recipient_info(recipient_info: Union[RecipientInfo, str], sender: str) -> RecipientInfo:
    # plain JSON variant, Pydantic already converted this
    if isinstance(recipient_info, RecipientInfo):
        return recipient_info

    algo, crypted = recipient_info.strip().split(":")

    if algo == "nacl":
        decrypted = decrypt_nacl(sender, b64decode(crypted))
    else:
        raise NotImplementedError()

    from_json = json.loads(decrypted)
    return RecipientInfo(**from_json)


