from enum import Enum
from typing import Any, Dict, Union
from pydantic import BaseModel


class Message(BaseModel):
    sender: str
    sign: bool = True
    encrypt: bool = True


class FreeformMessageTransport(Message):
    subject: str
    content: str


class TemplatedMessageTransport(Message):
    template: str
    variables: Dict[str, Any]


class FreeformMessage(FreeformMessageTransport):
    """
    Message with arbitrary content specified by sender.
    Connectors that don't support a separate subject should add it to the content,
    starting with the subject.
    """
    recipient_info: Union[str, Dict[str, Any]]

    class Config:
        schema_extra = {
            "example": {
                "sender": "example_app",
                "sign": True,
                "encrypt": False,
                "subject": "test message",
                "content": "Just a test.\n\nTester",
                "recipient_info": {
                    "matrix": {"matrix_ids": ["@recipient:example.com"]},
                    "mail": {"to": ["recipient@example.com"]}
                }
            }
        }

class TemplatedMessage(TemplatedMessageTransport):
    """
    Message with a predefined subject and content that may be modified by some variables.
    """
    recipient_info: str
