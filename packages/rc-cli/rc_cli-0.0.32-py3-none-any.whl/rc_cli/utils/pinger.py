import sys

import requests

from ..phase import Phase


class Pinger(Phase):
    def __init__(self, config, directory):
        super().__init__(config, directory)

    def execute(self):
        if not self._validate():
            self._warn('Please address issues with `roseconfig.json`. Ping command relies on field `gitlab.url`.')

        try:
            config_json = self.config_json()
        except FileNotFoundError:
            self._error('Could not find `roseconfig.json`')
            sys.exit(1)

        gitlab = config_json.get('gitlab', None)
        if gitlab is None:
            self._error('`roseconfig.json` is missing `gitlab` field')
            sys.exit(1)
        url = gitlab.get('url', None)
        if url is None:
            self._error('`roseconfig.json` is missing `gitlab.url` field')
            sys.exit(1)

        r = requests.get(url)

        message = 'Received response {}'.format(r.status_code)
        if r.status_code == requests.codes.ok:
            self._success(message)
        else:
            self._error(message)
