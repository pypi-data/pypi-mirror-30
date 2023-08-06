import requests

from six.moves import urllib
from yamlsettings.extensions.base import YamlSettingsExtension


class RequestsExtension(YamlSettingsExtension):
    """Open URLs with the request library

    """
    protocols = ['http', 'https']

    @classmethod
    def conform_query(cls, query):
        """Don't conform the query, must pass as received"""
        return query

    @staticmethod
    def rebuild_url(scheme, path, fragment, username,
                    password, hostname, port, query):
        """Rebuild the netloc value"""
        netloc = "@".join(filter(None, [
            ":".join(
                filter(None, [
                    username,
                    password,
                ])
            ),
            ":".join(
                filter(None, [
                    hostname,
                    str(port or ''),
                ])
            )
        ]))

        return urllib.parse.urlunsplit([
            scheme,
            netloc,
            path,
            query,
            fragment,
        ])

    @classmethod
    def load_target(cls, scheme, path, fragment, username,
                    password, hostname, port, query,
                    load_method, **kwargs):
        """Load Target via requests"""
        url = cls.rebuild_url(scheme, path, fragment, username,
                              password, hostname, port, query)
        expected_status_code = kwargs.pop('expected_status_code', 200)
        raise_on_status = kwargs.pop('raise_on_status', True)

        resp = requests.get(url, **kwargs)
        if resp.status_code != expected_status_code:
            if raise_on_status and resp.status_code != 404:
                raise RuntimeError(resp.status_code)
            else:
                raise IOError

        return load_method(resp.content)
