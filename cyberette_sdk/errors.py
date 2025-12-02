class SDKError(Exception):
    pass


class AuthenticationError(SDKError):
    pass


class ServerError(SDKError):
    pass
