import boto3

from abc import ABC, abstractmethod

from awsassume.data_models import AssumedRoleResponse


class SecurityTokenService(ABC):

    def __init__(self, region_name: str = None) -> None:
        self.client = boto3.client('sts', region_name=region_name)

    @abstractmethod
    def assume_role(self) -> AssumedRoleResponse:
        pass
