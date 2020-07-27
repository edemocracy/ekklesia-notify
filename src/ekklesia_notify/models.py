from typing import Any, Dict
from pydantic import BaseModel


class Message(BaseModel):
    sender: str
    keep: bool = True
    sign: bool = True
    encrypt: bool = True

class FreeformMessage(Message):
    """
    Message with arbitrary content specified by sender.
    Connectors that don't support a separate subject should add it to the content,
    starting with the subject.
    """
    subject: str
    content: str


class TemplatedMessage(Message):
    """
    Message with a predifined subject and content that may be modified by some variables.
    """
    template: str
    variables: Dict[str, Any]
