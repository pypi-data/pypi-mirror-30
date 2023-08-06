from urllib.parse import urljoin

import requests

from ..emoji import KEYBOARD
from ..logger import Logger


class UsersApi(Logger):
    def __init__(self, config, api_url):
        super().__init__(config)
        self.users_api_url = urljoin(api_url, 'users/')

    def search_user_by_username(self, username, headers):
        """
        Search for user by username

        Known Responses:
        200 (ok): if successful

        :param username: username to search for
        :param headers: Dictionary with `PRIVATE-TOKEN` entry
        :return: (response_data, response_code)
        """
        self._verbose('Searching for users with username {} {}'.format(username, KEYBOARD))
        search_users_url = urljoin(self.users_api_url, '?username={}'.format(username))
        r = requests.get(search_users_url, headers=headers)
        data = r.json()
        self._request_log('GET', search_users_url, r.status_code, data)
        return data, r.status_code
