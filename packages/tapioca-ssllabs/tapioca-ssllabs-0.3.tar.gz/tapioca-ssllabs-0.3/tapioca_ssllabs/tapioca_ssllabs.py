# coding: utf-8

from tapioca import (
    TapiocaAdapter, generate_wrapper_from_adapter, JSONAdapterMixin)

from .resource_mapping import RESOURCE_MAPPING


class SsllabsClientAdapter(JSONAdapterMixin, TapiocaAdapter):
    api_root = 'https://api.ssllabs.com/api/{version}/'
    resource_mapping = RESOURCE_MAPPING

    def get_api_root(self, api_params):
        version = api_params.get('version', 'v3')  # default https
        return self.api_root.format(version=version)

    def get_request_kwargs(self, api_params, *args, **kwargs):
        params = super(SsllabsClientAdapter, self).get_request_kwargs(
            api_params, *args, **kwargs)

        return params

    def get_iterator_list(self, response_data):
        return response_data

    def get_iterator_next_request_kwargs(self, iterator_request_kwargs,
                                         response_data, response):
        pass


Ssllabs = generate_wrapper_from_adapter(SsllabsClientAdapter)
