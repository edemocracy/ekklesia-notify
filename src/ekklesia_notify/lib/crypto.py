import json
from base64 import b64decode
from typing import Union
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import nacl.secret
from eliot import log_call, start_action
from ekklesia_notify.models import RecipientInfo
from ekklesia_notify.settings import nacl_keys, aes_keys


def decrypt_nacl(sender, crypted):
    key = b64decode(nacl_keys[sender])
    box = nacl.secret.SecretBox(key)
    decrypted = box.decrypt(b64decode(crypted))
    return decrypted.decode("utf8")


def decrypt_aes_gcm(sender, crypted):
    key = b64decode(aes_keys[sender])
    crypted_bytes = b64decode(crypted)
    nonce = crypted_bytes[:12]
    ciphertext = crypted_bytes[12:]
    with start_action(action_type="aes_gcm_decrypt"):
        aesgcm = AESGCM(key)
        decrypted = aesgcm.decrypt(nonce, ciphertext, None)
    return decrypted.decode("utf8")


@log_call
def decode_recipient_info(recipient_info: Union[RecipientInfo, str], sender: str) -> RecipientInfo:
    # plain JSON variant, Pydantic already converted this
    if isinstance(recipient_info, RecipientInfo):
        return recipient_info

    algo, crypted = recipient_info.strip().split(":")

    if algo == "nacl":
        decrypted = decrypt_nacl(sender, crypted)
    elif algo == "aesgcm":
        decrypted = decrypt_aes_gcm(sender, crypted)
    else:
        raise NotImplementedError()

    from_json = json.loads(decrypted)
    return RecipientInfo(**from_json)


