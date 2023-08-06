from typing import Any, Dict, List, NamedTuple  # NOQA
import requests  # NOQA

from bs4 import BeautifulSoup  # type: ignore
from six.moves.urllib.parse import quote

VisibilityTuple = NamedTuple('Visibility', [('owner', str), ('public', bool),
                                            ('readers', List[str]),
                                            ('reader_domains', List[str])])
"""The visibility of a population or population model"""


class Visibility(VisibilityTuple):

    @staticmethod
    def from_json(json):  # type: (Dict[str, Any]) -> Visibility
        return Visibility(json['owner'], json['public'], json['readers'],
                          json['reader_domains'])


class CallableEndpoint(object):
    """A helper class to make it easy to mock out HTTP calls.

    Call like:
        endpoint = CallableEndpoint('http://test.com/base', session)
        endpoint.logpdf_rows.post(json=request)
    and it will issue:
        session.post('http://test.com/base/logpdf_rows', json=request)

    Unlike just using requests, this will automatically raise on HTTP error
    codes. If for some reason you need that to not happen I'd be ok adding a
    `autoraise` parameter to the methods.
    """

    def __init__(
            self,
            url,  # type: str
            session  # type: requests.Session
    ):  # type: (...) -> None
        self.url = url
        self._session = session

    def get(self, *args, **kwargs):
        resp = self._session.get(self.url, *args, **kwargs)
        _raise_for_error(resp)
        return resp

    def post(self, *args, **kwargs):
        resp = self._session.post(self.url, *args, **kwargs)
        _raise_for_error(resp)
        return resp

    def patch(self, *args, **kwargs):
        resp = self._session.patch(self.url, *args, **kwargs)
        _raise_for_error(resp)
        return resp

    def delete(self, *args, **kwargs):
        resp = self._session.delete(self.url, *args, **kwargs)
        _raise_for_error(resp)
        return resp

    def sub_url(self, sub_path):
        """Return a new CallableEndpoint with `sub_path` appended to the URL.
        """
        new_url = self.url + '/' + quote(sub_path)
        return CallableEndpoint(new_url, self._session)

    # This isn't just an attempt to make a cute API. It'd be less strange to
    # always use `sub_url()`, but python's mock can't mock based on args, so
    # you couldn't mock `ce.sub_url('select')` and `ce.sub_url('logpdf_rows')`
    # separately. This gets around that by letting you mock `ce.select` and
    # `ce.logpdf_rows`.
    def __getattr__(self, attr):
        return self.sub_url(attr)


def _raise_for_error(response):
    """Raise an error if response indicates an HTTP error code.

    Like requests.raise_for_status(), but additionally tries to raise a
    more sensible error if we can parse out what happened from the response.

    Raises:
        NoSuchGeneratorError: If the response was a 404
        ValueError: If the request was bad due to user error, e.g. bad columns
            or too large a sample size
        HTTPError: If the response is any other 4XX or 5XX error
    """
    # TODO(asilvers): This may turn some other 404s into NoSuchGeneratorErrors
    # if, say, we start building bad URLs and 404ing due to structural issues
    # in the requests. We should work out a signalling this exact case in the
    # body of the 404 to get rid of that ambiguity.
    if response.status_code == 404:
        raise NoSuchGeneratorError
    if response.status_code == 401:
        raise AuthenticationError(
            'You are not authenticated to EDP. Do you have a token from '
            'https://betaplatform.empirical.com/tokens?')
    if response.status_code == 403:
        raise PermissionDeniedError(
            'You do not have access to the requested resource on EDP.')
    if response.status_code == 400:
        # Some errors return nice json for us
        try:
            respjson = response.json()
            error = respjson['error']
        except ValueError:
            # But if not, raise a ValueError and hope that there was some
            # useful text in the HTML. It's better than swallowing the response
            # text which is what `raise_for_status` does. Try and find the
            # response text that normally gets printed in a <p>, but fall back
            # if we fail.
            p = BeautifulSoup(response.content, 'html5lib').body.find('p')
            exc = ValueError(p.text) if p else ValueError(response.content)
            # Disable implicit exception chaining since users don't care that
            # the JSON failed to parse.
            exc.__cause__ = None  # type: ignore
            raise exc
        if error == 'MODEL_NOT_BUILT':
            raise ModelNotBuiltError('This model has not finished building.')
        if error == 'N_TOO_LARGE':
            raise ValueError('Request\'s \'n\' was too large.')
        if error == 'NO_SUCH_COLUMN':
            raise ValueError('No such column in %s: %s' %
                             (respjson['field'], respjson['columns']))
        # Got JSON but we're not handling its error code. Still better than
        # raising a 400.
        raise ValueError(respjson)
    response.raise_for_status()


class EdpError(Exception):
    pass


class NoSuchGeneratorError(EdpError):
    pass


class ModelNotBuiltError(EdpError):
    pass


class PermissionDeniedError(EdpError):
    pass


class AuthenticationError(EdpError):
    pass
