from urllib.parse import urljoin

import requests

from ..emoji import KEYBOARD
from ..logger import Logger


class GroupsApi(Logger):
    def __init__(self, config, api_url):
        super().__init__(config)
        self.groups_api_url = urljoin(api_url, 'groups/')

    def search_groups(self, group_name, headers):
        """
        Search for groups with group_name.

        Known Responses:
        200 (ok): if successful
        401 (unauthorized): if invalid token

        :param group_name: Name of group to search for
        :param headers: Dictionary with `PRIVATE-TOKEN` entry
        :return: (response_data, response_code)
        """
        self._verbose('Getting groups with name {} {}'.format(group_name, KEYBOARD))
        form_data = {'search': group_name}
        r = requests.get(self.groups_api_url, data=form_data, headers=headers)
        data = r.json()
        self._request_log('GET', self.groups_api_url, r.status_code, data)
        return data, r.status_code

    def get_subgroups(self, group_id, headers):
        """
        Get subgroups within the group_id.

        Known Responses:
        200 (ok): if successful

        :param group_id: group_id to search for
        :param headers: Dictionary with `PRIVATE-TOKEN` entry
        :return: (response_data, response_code)
        """
        self._verbose('Getting subgroups for group {} {}'.format(group_id, KEYBOARD))
        subgroup_api_url = urljoin(self.groups_api_url, '{}/subgroups'.format(group_id))
        r = requests.get(subgroup_api_url, headers=headers)
        data = r.json()
        self._request_log('GET', subgroup_api_url, r.status_code, data)
        return data, r.status_code

    def create_group(self, form_data, headers):
        """
        Create group.

        Known Responses:
        201 (created): if successful

        :param form_data: request body to send
        :param headers: Dictionary with `PRIVATE-TOKEN` entry
        :return: (response_data, response_code)
        """
        self._verbose('Creating group {} {}'.format(form_data.get('name'), KEYBOARD))
        r = requests.post(self.groups_api_url, data=form_data, headers=headers)
        data = r.json()
        self._request_log('POST', self.groups_api_url, r.status_code, data)
        return data, r.status_code

    def get_group_projects(self, group_id, headers):
        """
        Get group_id projects.

        Known Responses:
        200 (ok): if successful

        :param group_id: group_id to search for
        :param headers: Dictionary with `PRIVATE-TOKEN` entry
        :return: (response_data, response_code)
        """
        self._verbose('Getting projects in group {} {}'.format(group_id, KEYBOARD))
        group_project_url = urljoin(self.groups_api_url, '{}/projects'.format(group_id))
        r = requests.get(group_project_url, data={'simple': True}, headers=headers)
        data = r.json()
        self._request_log('GET', group_project_url, r.status_code, data)
        return data, r.status_code

    def get_group_members(self, group_id, headers):
        """
        Get members of the group.

        Known Responses:
        200 (ok): if successful


        :param group_id: group_id to search for
        :param headers: Dictionary with `PRIVATE-TOKEN` entry
        :return: (response_data, response_code)
        """
        self._verbose('Getting group members for group {} {}'.format(group_id, KEYBOARD))
        group_member_url = urljoin(self.groups_api_url, '{}/members'.format(group_id))
        r = requests.get(group_member_url, headers=headers)
        data = r.json()
        self._request_log('GET', group_member_url, r.status_code, data)
        return data, r.status_code
