from requests.exceptions import RequestException


class CriticalConnectionError(RequestException):
    """Означает проблемы на стороне клиента"""


class CriticalProxyError(RequestException):
    """Означает то что прокси нерабочие"""