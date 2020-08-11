from typing import List
from pydantic import BaseModel


class ClientSettings(BaseModel):
    password: str
    default_sender: str
    allowed_senders: List[str]
    allowed_templates: List[str]
