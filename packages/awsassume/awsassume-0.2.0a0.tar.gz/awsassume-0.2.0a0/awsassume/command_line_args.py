import argparse

from typing import Any

from awsassume.data_models import CliArgs


class CommandLineArgs(object):
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(description='Execute AWS CLI commands after assuming role')

        required_args: Any = self.parser.add_argument_group('required arguments')
        required_args.add_argument('-a', '--role-arn', required=True, help='The ARN of the role to assume')
        required_args.add_argument('-n', '--role-session-name', required=True, help='An identifier for the assumed role session')

        self.parser.add_argument('--no-cache', required=False, action='store_true', help='Disable caching of the assumed role response')
        self.parser.add_argument('-r', '--region', required=False, help='The region to be associated with the client')
        self.parser.add_argument('-c', '--command', required=False, nargs=argparse.REMAINDER, help='The AWS CLI command to execute after assuming role')

    def get_cli_args(self) -> CliArgs:

        parsed_cli_args: argparse.Namespace = self.parser.parse_args()

        cli_args = CliArgs(role_arn=parsed_cli_args.role_arn,
                           role_session_name=parsed_cli_args.role_session_name,
                           command=parsed_cli_args.command,
                           region_name=parsed_cli_args.region,
                           no_cache=parsed_cli_args.no_cache)

        return cli_args
