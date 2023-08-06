from awsassume.data_models import AssumedRoleResponse, ResponseCacheArgs
from awsassume.response_cache import ResponseCache


class ResponseCacheAdapter(object):

    def __init__(self, response_cache_args: ResponseCacheArgs) -> None:
        self.response_cache_args = response_cache_args

        self.response_cache = ResponseCache()

    def set_response_to_cache(self, assumed_role_response: AssumedRoleResponse) -> None:
        self.response_cache.set_response_to_cache(self.response_cache_args, assumed_role_response)

    def get_response_from_cache(self) -> AssumedRoleResponse:
        return self.response_cache.get_response_from_cache(self.response_cache_args)

    def delete_cache_file(self) -> None:
        self.response_cache.delete_cache_file(self.response_cache_args)
