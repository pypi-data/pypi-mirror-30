from awsassume.assume_role import AssumeRole
from awsassume.assume_role_cache_executor import AssumeRoleCacheExecutor
from awsassume.assume_role_executor import AssumeRoleExecutor
from awsassume.assume_role_no_cache_executor import AssumeRoleNoCacheExecutor
from awsassume.data_models import AssumeRoleArgs, AssumeRoleType, CliArgs, ResponseCacheArgs
from awsassume.response_cache_adapter import ResponseCacheAdapter
from awsassume.security_token_service import SecurityTokenService


class AssumeRoleExecutorFactory(object):

    @staticmethod
    def get_executor(cli_args: CliArgs) -> AssumeRoleExecutor:

        assume_role_args = AssumeRoleArgs(role_arn=cli_args.role_arn, role_session_name=cli_args.role_session_name, region_name=cli_args.region_name)
        security_token_service: SecurityTokenService = AssumeRole(assume_role_args)

        assume_role_executor: AssumeRoleExecutor = None
        if cli_args.no_cache is True:
            assume_role_executor = AssumeRoleNoCacheExecutor(security_token_service)
        else:
            response_cache_args = ResponseCacheArgs(role_arn=cli_args.role_arn,
                                                    role_session_name=cli_args.role_session_name,
                                                    region_name=cli_args.region_name,
                                                    assume_role_type=AssumeRoleType.DEFAULT)

            response_cache_adapter = ResponseCacheAdapter(response_cache_args)
            assume_role_executor = AssumeRoleCacheExecutor(security_token_service, response_cache_adapter)

        return assume_role_executor
