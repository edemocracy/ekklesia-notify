from typing import Annotated, List, Pattern
from pydantic import BaseModel, BaseSettings, SecretStr, Field
from pydantic.networks import EmailStr, HttpUrl
from pydantic.types import DirectoryPath, FilePath


Port = Annotated[int, Field(strict=True, gt=0, lt=65536)]
MatrixId = Annotated[str, Field(regex="@[a-z0-9./_=\-]+:.+")]


class ClientSettings(BaseSettings):
    """Settings for clients using this service."""
    password: SecretStr
    default_sender: str
    allowed_senders: List[str]
    allowed_templates: List[str]


class MatrixTransportSettings(BaseSettings):
    """Settings for the matrix transport"""
    device_id: str
    homeserver: HttpUrl
    mxid: MatrixId
    password: SecretStr
    session_details_file: FilePath
    store_dir: DirectoryPath


class MailTransportSettings(BaseSettings):
    """Settings for the mail transport"""
    cert_p12: FilePath
    cert_password: SecretStr
    sender: EmailStr
    smtp_password: SecretStr
    smtp_port: Port
    smtp_server: str
    smtp_user: str


class TransportSettings(BaseSettings):
    """Settings for transports that are used to send out notifications."""
    mail: MailTransportSettings
    matrix: MatrixTransportSettings


class EkklesiaNotifySettings(BaseSettings):
    """Top-level settings object"""

    nacl_keys: dict[str, SecretStr]
    aes_keys: dict[str, SecretStr]
    transport_settings: TransportSettings
    clients: dict[str, ClientSettings]
    recipient_info_transport_examples: dict
    template_dir: DirectoryPath

    class Config:
        env_prefix = 'ekklesia_notify_'
