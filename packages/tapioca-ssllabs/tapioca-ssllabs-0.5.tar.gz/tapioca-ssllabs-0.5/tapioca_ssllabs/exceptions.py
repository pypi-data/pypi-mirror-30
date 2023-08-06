# coding: utf-8

import json
from tapioca.exceptions import ServerError, ClientError


class InvocationErrorException(ClientError):

    def __init__(self, message='', client=None):
        if client:
            errors = client.errors().data
            if isinstance(errors, list) and len(errors) > 0:
                message = errors[0].get('message', message)
        super(InvocationErrorException, self).__init__(message, client=client)


class ClientOverloadedException(ClientError):

    def __init__(self, message='', client=None):
        super(ClientOverloadedException, self).__init__(message, client=client)


class InternalServerErrorException(ServerError):

    def __init__(self, message='', client=None):
        super(InternalServerErrorException, self).__init__(message, client=client)


class ServiceUnavailableException(ServerError):

    def __init__(self, message='', client=None):
        super(ServiceUnavailableException, self).__init__(message, client=client)


class ServiceOverloadedException(ServerError):

    def __init__(self, message='', client=None):
        super(ServiceOverloadedException, self).__init__(message, client=client)

