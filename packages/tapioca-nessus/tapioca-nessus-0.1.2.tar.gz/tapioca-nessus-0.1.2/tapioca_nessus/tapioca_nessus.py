# coding: utf-8

from tapioca import (
    TapiocaAdapter, generate_wrapper_from_adapter, JSONAdapterMixin)

from requests.auth import HTTPBasicAuth


from .resource_mapping import RESOURCE_MAPPING


class NessusClientAdapter(JSONAdapterMixin, TapiocaAdapter):
    api_root = 'https://localhost:8834'
    resource_mapping = RESOURCE_MAPPING

    def get_request_kwargs(self, api_params, *args, **kwargs):
        params = super(NessusClientAdapter, self).get_request_kwargs(
            api_params, *args, **kwargs)


        params['auth'] = HTTPBasicAuth(
            api_params.get('user'), api_params.get('password'))


        return params

    def get_iterator_list(self, response_data):
        return response_data

    def get_iterator_next_request_kwargs(self, iterator_request_kwargs,
                                         response_data, response):
        pass


Nessus = generate_wrapper_from_adapter(NessusClientAdapter)
