from abc import ABC, abstractmethod

from awsassume.data_models import Credentials


class AssumeRoleExecutor(ABC):

    @abstractmethod
    def execute(self) -> Credentials:
        pass
