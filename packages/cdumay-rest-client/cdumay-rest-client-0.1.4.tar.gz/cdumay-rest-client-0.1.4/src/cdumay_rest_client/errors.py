#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
from cdumay_error import Error, NotImplemented, ValidationError, NotFound, \
    ErrorSchema


class NotModified(Error):
    """Not Modified"""
    MSGID = "HTTP-22313"
    CODE = 304


class Unauthorized(Error):
    """Unauthorized"""
    MSGID = "HTTP-28015"
    CODE = 401


class PaymentRequired(Error):
    """Payment Required"""
    MSGID = "HTTP-23516"
    CODE = 402


class Forbidden(Error):
    """Forbidden"""
    MSGID = "HTTP-29860"
    CODE = 403


class MethodNotAllowed(Error):
    """Method Not Allowed"""
    MSGID = "HTTP-00324"
    CODE = 405


class NotAcceptable(Error):
    """Not Acceptable"""
    MSGID = "HTTP-30133"
    CODE = 406


class ProxyAuthenticationRequired(Error):
    """Proxy Authentication Required"""
    MSGID = "HTTP-32405"
    CODE = 407


class RequestTimeout(Error):
    """Request Time-out"""
    MSGID = "HTTP-13821"
    CODE = 408


class Conflict(Error):
    """Conflict"""
    MSGID = "HTTP-21124"
    CODE = 409


class Gone(Error):
    """Gone"""
    MSGID = "HTTP-15611"
    CODE = 410


class MisdirectedRequest(Error):
    """Misdirected Request"""
    MSGID = "HTTP-24099"
    CODE = 421


class InternalServerError(Error):
    """Internal Server Error"""
    MSGID = "HTTP-02752"
    CODE = 500


class ProxyError(Error):
    """Proxy Error"""
    MSGID = "HTTP-09927"
    CODE = 502


class ServiceUnavailable(Error):
    """Service Unavailable"""
    MSGID = "HTTP-26820"
    CODE = 503


class GatewayTimeout(Error):
    """Gateway Time-out"""
    MSGID = "HTTP-04192"
    CODE = 504


HTTP_STATUS_CODES = {
    304: NotModified,
    400: ValidationError,
    401: Unauthorized,
    402: PaymentRequired,
    403: Forbidden,
    404: NotFound,
    405: MethodNotAllowed,
    406: NotAcceptable,
    407: ProxyAuthenticationRequired,
    408: RequestTimeout,
    409: Conflict,
    410: Gone,
    421: MisdirectedRequest,
    500: InternalServerError,
    501: NotImplemented,
    502: ProxyError,
    503: ServiceUnavailable,
    504: GatewayTimeout
}


def from_status(status, message=None, extra=None):
    """ Try to create an error from status code

    :param int status: HTTP status
    :param str message: Body content
    :param dict extra: Additional info
    :return: An error
    :rtype: cdumay_rest_client.errors.Error
    """
    if status in HTTP_STATUS_CODES:
        return HTTP_STATUS_CODES[status](message=message, extra=extra)
    else:
        return Error(
            code=status, message=message if message else "Unknown Error",
            extra=extra
        )


def from_response(response, url):
    """ Try to create an error from a HTTP response

    :param request.Response response: HTTP response
    :param str url: URL attained
    :return: An error
    :rtype: cdumay_rest_client.errors.Error
    """
    # noinspection PyBroadException
    try:
        data = response.json()
        if not isinstance(data, dict):
            return from_status(
                response.status_code, response.text,
                extra=dict(url=url, response=response.text)
            )

        code = data.get('code', response.status_code)
        if code in HTTP_STATUS_CODES:
            return HTTP_STATUS_CODES[code](**ErrorSchema().load(data))
        else:
            return Error(**ErrorSchema().load(data))
    except Exception:
        return from_status(
            response.status_code, response.text,
            extra=dict(url=url, response=response.text)
        )
