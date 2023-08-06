from botocore.exceptions import ClientError

from awsassume.data_models import AssumeRoleArgs
from awsassume.security_token_service import SecurityTokenService
from awsassume.data_models import AssumedRoleResponse


class AssumeRole(SecurityTokenService):

    def __init__(self, assume_role_args: AssumeRoleArgs) -> None:
        super().__init__(assume_role_args.region_name)

        self.assume_role_args: AssumeRoleArgs = assume_role_args

    def assume_role(self) -> AssumedRoleResponse:
        try:
            response: AssumedRoleResponse = self.client.assume_role(RoleArn=self.assume_role_args.role_arn,
                                                                    RoleSessionName=self.assume_role_args.role_session_name)
        except ClientError:
            raise
        else:
            return response
