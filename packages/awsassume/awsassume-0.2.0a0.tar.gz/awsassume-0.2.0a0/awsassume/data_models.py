from datetime import datetime
from enum import auto, Enum
from typing import Any, Dict, List, NamedTuple


class AssumeRoleArgs(NamedTuple):
    role_arn: str
    role_session_name: str
    region_name: str = None


class AssumeRoleType(Enum):
    DEFAULT = auto()


AssumedRoleResponse = Dict[str, Any]


AssumedRoleResponseCredentials = Dict[str, Any]


class CliArgs(NamedTuple):
    role_arn: str
    role_session_name: str
    command: List[str] = []
    region_name: str = None
    no_cache: bool = False


class Credentials(NamedTuple):
    access_key_id: str
    secret_access_key: str
    session_token: str
    expiration: datetime


class ResponseCacheArgs(NamedTuple):
    role_arn: str
    role_session_name: str
    region_name: str = None
    assume_role_type: AssumeRoleType = AssumeRoleType.DEFAULT
