from typing import Annotated, List
from pydantic import BaseSettings, SecretStr, Field
from pydantic.networks import EmailStr, AnyHttpUrl
from pydantic.types import DirectoryPath, FilePath


Port = Annotated[int, Field(strict=True, gt=0, lt=65536)]
MatrixId = Annotated[str, Field(regex="@[a-z0-9./_=\-]+:.+")]


class EkklesiaNotifySettings(BaseSettings):
    class Config:
        env_prefix = 'ekklesia_notify_'


class ClientSettings(EkklesiaNotifySettings):
    """Settings for clients using this service."""
    password: SecretStr
    default_sender: str
    allowed_senders: List[str]
    allowed_templates: List[str]


class MatrixTransportSettings(EkklesiaNotifySettings):
    """Settings for the matrix transport"""
    device_id: str
    homeserver: AnyHttpUrl
    mxid: MatrixId
    password: SecretStr
    session_details_file: FilePath
    store_dir: DirectoryPath


class MailTransportSettings(EkklesiaNotifySettings):
    """Settings for the mail transport"""
    cert_p12: FilePath
    cert_password: SecretStr
    sender: EmailStr
    smtp_password: SecretStr
    smtp_port: Port
    smtp_server: str
    smtp_user: str


class TransportSettings(EkklesiaNotifySettings):
    """Settings for transports that are used to send out notifications."""
    mail: MailTransportSettings
    matrix: MatrixTransportSettings


class EkklesiaNotifySettings(EkklesiaNotifySettings):
    """Top-level settings object"""

    nacl_keys: dict[str, SecretStr]
    aes_keys: dict[str, SecretStr]
    transport_settings: TransportSettings
    clients: dict[str, ClientSettings]
    recipient_info_transport_examples: dict
    template_dir: DirectoryPath
