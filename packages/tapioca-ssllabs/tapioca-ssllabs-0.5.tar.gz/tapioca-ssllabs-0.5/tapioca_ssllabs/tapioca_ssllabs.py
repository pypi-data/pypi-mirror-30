# coding: utf-8

from tapioca import (
    TapiocaAdapter, generate_wrapper_from_adapter, JSONAdapterMixin)
from tapioca.exceptions import ResponseProcessException

from .resource_mapping import RESOURCE_MAPPING
from .exceptions import InvocationErrorException, ClientOverloadedException, InternalServerErrorException, \
    ServiceUnavailableException, ServiceOverloadedException


class SslLabsClientAdapter(JSONAdapterMixin, TapiocaAdapter):

    api_root = 'https://api.ssllabs.com/api/{version}/'
    resource_mapping = RESOURCE_MAPPING

    def get_api_root(self, api_params):
        version = api_params.get('version', 'v2')  # default https
        return self.api_root.format(version=version)

    def get_request_kwargs(self, api_params, *args, **kwargs):
        params = super(SslLabsClientAdapter, self).get_request_kwargs(
            api_params, *args, **kwargs)

        return params

    def get_iterator_list(self, response_data):
        return response_data

    def get_iterator_next_request_kwargs(self, iterator_request_kwargs,
                                         response_data, response):
        pass

    def process_response(self, response):
        if response.status_code == 400:
            data = self.response_to_native(response)
            raise ResponseProcessException(InvocationErrorException, data)

        elif response.status_code == 429:
            raise ResponseProcessException(ClientOverloadedException)

        elif response.status_code == 500:
            raise ResponseProcessException(InternalServerErrorException)

        elif response.status_code == 503:
            raise ResponseProcessException(ServiceUnavailableException)

        elif response.status_code == 529:
            raise ResponseProcessException(ServiceOverloadedException)

        data = self.response_to_native(response)

        return data


SslLabs = generate_wrapper_from_adapter(SslLabsClientAdapter)
