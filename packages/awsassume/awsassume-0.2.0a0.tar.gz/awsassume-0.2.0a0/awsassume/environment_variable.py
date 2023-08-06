import os

from typing import Dict

from awsassume.data_models import Credentials


class EnvironmentVariable(object):

    ACCESS_KEY_ID_KEY = 'AWS_ACCESS_KEY_ID'
    SECRET_ACCESS_KEY_KEY = 'AWS_SECRET_ACCESS_KEY'
    SESSION_TOKEN_KEY = 'AWS_SESSION_TOKEN'
    DEFAULT_REGION_KEY = 'AWS_DEFAULT_REGION'

    @staticmethod
    def display_credentials_to_be_exported(credentials: Credentials, region_name: str = None) -> None:

        print(f'# {EnvironmentVariable.ACCESS_KEY_ID_KEY}={credentials.access_key_id}')
        print(f'# {EnvironmentVariable.SECRET_ACCESS_KEY_KEY}={credentials.secret_access_key}')
        print(f'# {EnvironmentVariable.SESSION_TOKEN_KEY}={credentials.session_token}')

        if region_name is not None:
            print(f'# {EnvironmentVariable.DEFAULT_REGION_KEY}={region_name}')

    @staticmethod
    def generate_command_to_export_credentials(credentials: Credentials, region_name: str = None) -> str:

        export_access_key_id = f'export {EnvironmentVariable.ACCESS_KEY_ID_KEY}="{credentials.access_key_id}"'
        export_secret_access_key = f'export {EnvironmentVariable.SECRET_ACCESS_KEY_KEY}="{credentials.secret_access_key}"'
        export_session_token = f'export {EnvironmentVariable.SESSION_TOKEN_KEY}="{credentials.session_token}"'

        command = f'{export_access_key_id}; {export_secret_access_key}; {export_session_token}'

        if region_name is not None:
            export_default_region = f'export {EnvironmentVariable.DEFAULT_REGION_KEY}="{region_name}"'

            command = f'{command}; {export_default_region}'

        return command

    @staticmethod
    def get_env_var_with_credentials(credentials: Credentials, region_name: str = None) -> Dict[str, str]:
        env_var_copy = os.environ.copy()

        env_var_copy[EnvironmentVariable.ACCESS_KEY_ID_KEY] = credentials.access_key_id
        env_var_copy[EnvironmentVariable.SECRET_ACCESS_KEY_KEY] = credentials.secret_access_key
        env_var_copy[EnvironmentVariable.SESSION_TOKEN_KEY] = credentials.session_token

        if region_name is not None:
            env_var_copy[EnvironmentVariable.DEFAULT_REGION_KEY] = region_name

        return env_var_copy
