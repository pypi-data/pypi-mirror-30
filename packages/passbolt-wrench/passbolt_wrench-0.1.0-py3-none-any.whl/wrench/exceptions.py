from requests import Response


class WrenchError(Exception):
    ...


class InputValidationError(WrenchError):
    ...


class HttpRequestError(WrenchError):
    def __init__(self, response: Response) -> None:
        self.response = response


class FingerprintMismatchError(WrenchError):
    ...
