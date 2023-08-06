from awsassume.assume_role_executor import AssumeRoleExecutor
from awsassume.data_models import AssumedRoleResponse, AssumedRoleResponseCredentials, Credentials
from awsassume.security_token_service import SecurityTokenService


class AssumeRoleNoCacheExecutor(AssumeRoleExecutor):

    def __init__(self, security_token_service: SecurityTokenService) -> None:
        self.security_token_service = security_token_service

    def execute(self) -> Credentials:
        response: AssumedRoleResponse = self.security_token_service.assume_role()

        response_credentials: AssumedRoleResponseCredentials = response['Credentials']
        credentials = Credentials(access_key_id=response_credentials['AccessKeyId'],
                                  secret_access_key=response_credentials['SecretAccessKey'],
                                  session_token=response_credentials['SessionToken'],
                                  expiration=response_credentials['Expiration'])

        return credentials
