from tapioca.exceptions import ClientError, ServerError


class AppscannerClientError(ClientError):
    pass


class AppscannerServerError(ServerError):
    pass
