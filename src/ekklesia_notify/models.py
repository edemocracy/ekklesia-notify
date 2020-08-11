from enum import Enum
from typing import Any, Dict, Union, Optional
from pydantic import BaseModel


class Message(BaseModel):
    sender: Optional[str]
    sign: bool = True
    encrypt: bool = True


class MessageResponse(BaseModel):
    msg_id: str


class FreeformMessageTransport(Message):
    subject: str
    content: str


class TemplatedMessageTransport(Message):
    template: str
    variables: Dict[str, Any]

    class Config:
        schema_extra = {
            "example": {
                "sender": "example_app",
                "sign": True,
                "encrypt": False,
                "template": "example_notification",
                "variables": {
                    "subject": "An example notification",
                    "date": "2020-08-22"
                },
                "recipient_info": "<encrypted string>"
            }
        }


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

    recipient_info: Union[str, Dict[str, Any]]
