from awsassume.assume_role_executor import AssumeRoleExecutor
from awsassume.assume_role_executor_factory import AssumeRoleExecutorFactory
from awsassume.command_executor import CommandExecutor
from awsassume.command_line_args import CommandLineArgs
from awsassume.data_models import CliArgs, Credentials
from awsassume.environment_variable import EnvironmentVariable


def main():
    cli_args: CliArgs = CommandLineArgs().get_cli_args()

    assume_role_executor: AssumeRoleExecutor = AssumeRoleExecutorFactory.get_executor(cli_args)

    credentials: Credentials = assume_role_executor.execute()

    if cli_args.command is None:
        print('# AWS assumed role credentials:')
        EnvironmentVariable.display_credentials_to_be_exported(credentials, cli_args.region_name)

        print()

        print('# Execute the following command to export the AWS assumed role credentials to environment variables.')

        command_to_eval = EnvironmentVariable.generate_command_to_export_credentials(credentials, cli_args.region_name)
        print(command_to_eval)
    else:
        env_var_with_credentials = EnvironmentVariable.get_env_var_with_credentials(credentials, cli_args.region_name)

        CommandExecutor.execute(cli_args.command, env_var_with_credentials)
