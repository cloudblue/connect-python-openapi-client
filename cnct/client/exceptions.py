from requests.exceptions import HTTPError as RequestHttpError


class NotFoundError(AttributeError):
    pass


class APIError(Exception):
    def __init__(self, status_code, error_code, errors):
        self.status_code = status_code
        self.error_code = error_code
        self.errors = errors

    def __repr__(self):
        return f'<APIError {self.status_code}: {self.error_code}>'

    def __str__(self):
        errors = ','.join(self.errors)
        return f'{self.error_code}: {errors}'


class HttpError(RequestHttpError):
    pass
