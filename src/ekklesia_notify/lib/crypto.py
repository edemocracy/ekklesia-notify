import json
from base64 import b64decode
from eliot import log_call
import nacl.secret
from ekklesia_notify.settings import nacl_keys


@log_call
def decrypt_nacl(sender, crypted):
    key = b64decode(nacl_keys[sender])
    box = nacl.secret.SecretBox(key)
    decrypted = box.decrypt(crypted)
    return decrypted.decode("utf8")


@log_call
def decode_recipient_info(recipient_info, sender):
    if isinstance(recipient_info, dict):
        return recipient_info

    algo, crypted = recipient_info.split(":")

    if algo == "nacl":
        decrypted = decrypt_nacl(sender, b64decode(crypted))
    else:
        raise NotImplementedError()

    return json.loads(decrypted)


