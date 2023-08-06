import errno
import os
import pickle
import re

from awsassume.data_models import AssumedRoleResponse, ResponseCacheArgs


class ResponseCache(object):
    cache_directory = f'{os.path.expanduser("~")}/.awsassume/cache'

    def __init__(self) -> None:
        try:
            os.makedirs(ResponseCache.cache_directory)
        except OSError as ex:
            if ex.errno != errno.EEXIST:
                raise

    def set_response_to_cache(self, response_cache_args: ResponseCacheArgs, assumed_role_response: AssumedRoleResponse) -> None:
        try:
            with open(self.get_cache_full_path(response_cache_args), 'wb') as file:
                pickle.dump(assumed_role_response, file)
        except OSError:
            raise

    def get_response_from_cache(self, response_cache_args: ResponseCacheArgs) -> AssumedRoleResponse:
        assumed_role_response: AssumedRoleResponse = None

        try:
            with open(self.get_cache_full_path(response_cache_args), 'rb') as file:
                assumed_role_response = pickle.load(file)
        except FileNotFoundError:
            pass
        except OSError:
            raise

        return assumed_role_response

    def delete_cache_file(self, response_cache_args: ResponseCacheArgs) -> None:
        try:
            os.remove(self.get_cache_full_path(response_cache_args))
        except OSError:
            raise

    def get_cache_full_path(self, response_cache_args: ResponseCacheArgs) -> str:
        full_path = f'{ResponseCache.cache_directory}/{self.get_cache_name(response_cache_args)}'

        return full_path

    def get_cache_name(self, response_cache_args: ResponseCacheArgs) -> str:
        cache_name: str = None

        matched_arn = re.match('arn:aws:iam::([0-9]{12}):role/([0-9a-zA-Z+=,.@\-_]{1,64})', response_cache_args.role_arn)
        if matched_arn:
            role_session_name_section = response_cache_args.role_session_name
            role_arn_section = f'{matched_arn.group(1)}_{matched_arn.group(2)}'

            region_name_section: str = 'default'
            if response_cache_args.region_name is not None:
                region_name_section = response_cache_args.region_name

            cache_name = f'{role_session_name_section}__{role_arn_section}__{region_name_section}__{response_cache_args.assume_role_type.name}'

        return cache_name
