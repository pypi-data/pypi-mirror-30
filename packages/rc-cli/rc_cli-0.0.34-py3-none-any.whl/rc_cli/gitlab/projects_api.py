from urllib.parse import urljoin

import requests

from ..emoji import KEYBOARD
from ..logger import Logger


class ProjectsApi(Logger):
    def __init__(self, config, api_url):
        super().__init__(config)
        self.projects_api_url = urljoin(api_url, 'projects/')

    def create_project(self, form_data, headers):
        """
        Create a project.

        Known Responses:
        201 (created): if project creation was successful

        :param form_data: request body (see gitlab for details)
        :param headers: Dictionary with `PRIVATE-TOKEN` entry
        :return: (response_data, response_code)
        """
        self._verbose('Creating project {} {}'.format(form_data, KEYBOARD))
        r = requests.post(self.projects_api_url, data=form_data, headers=headers)
        data = r.json()
        self._request_log('POST', self.projects_api_url, r.status_code, data)
        return data, r.status_code

    def unprotect_branch(self, project_id, branch_name, headers):
        """
        Unprotect a branch.

        Known Responses:
        404 (not found): if branch is not a protected branch
        204 (no content): if successful

        :param project_id: Project in which to unprotect the branch in
        :param branch_name: branch name to unprotect
        :param headers: Dictionary with `PRIVATE-TOKEN` entry
        :return: (response_data, response_code)
        """
        self._verbose('Unprotecting branch {}'.format(branch_name))
        unprotect_branch_url = urljoin(self.projects_api_url,
                                       '{}/protected_branches/{}'.format(project_id, branch_name))
        self._verbose(unprotect_branch_url)
        r = requests.delete(unprotect_branch_url, headers=headers)
        data = r.json() if r.status_code == requests.codes.not_found else ''
        self._request_log('DELETE', unprotect_branch_url, r.status_code, data)
        return data, r.status_code

    def protect_branch(self, project_id, form_data, headers):
        """
        Protect a branch.

        Known Responses:
        201 (created): if branch creation was successfully
        409 (conflicted): if branch is already protected

        :param project_id:
        :param form_data:
        :param headers: Dictionary with `PRIVATE-TOKEN` entry
        :return: (response_data, response_code)
        """
        self._verbose('Protecting branch {}'.format(form_data))
        protect_branch_url = urljoin(self.projects_api_url, '{}/protected_branches'.format(project_id))
        r = requests.post(protect_branch_url, data=form_data, headers=headers)
        data = r.json()
        self._request_log('POST', protect_branch_url, r.status_code, data)
        return data, r.status_code

    def add_member(self, project_id, form_data, headers):
        """
        Add a member.

        Known Responses:
        201 (created): if member was added successfully

        :param project_id: Project to update
        :param form_data: request body to send (see gitlab for details)
        :param headers: Dictionary with `PRIVATE-TOKEN` entry
        :return: (response_data, response_code)
        """
        self._verbose('Adding project member {} {} {}'.format(project_id, form_data, KEYBOARD))
        project_member_url = urljoin(self.projects_api_url, '{}/members'.format(project_id))
        r = requests.post(project_member_url, data=form_data, headers=headers)
        data = r.json()
        self._request_log('POST', project_member_url, r.status_code, data)
        return data, r.status_code

    def default_branch(self, project_id, branch_default, headers):
        """
        Set a projects default branch.

        Known Responses:
        200 (ok): if successful

        :param project_id: Project to update
        :param branch_default: Branch to set as default
        :param headers: Dictionary with `PRIVATE-TOKEN` entry
        :return: (response_data, response_code)
        """
        self._verbose('Setting project {} default branch to {}'.format(project_id, branch_default))
        project_edit_url = urljoin(self.projects_api_url, str(project_id))
        form_data = {
            'default_branch': branch_default
        }
        r = requests.put(project_edit_url, data=form_data, headers=headers)
        data = r.json()
        self._request_log('PUT', project_edit_url, r.status_code, data)
        return data, r.status_code

    def get_protected_branches(self, project_id, headers):
        """
        Get a list of protected branches.

        Known Responses:
        200 (ok): if successful

        :param project_id: Project to update.
        :return: (response_data, response_code)
        """
        self._verbose('Getting project {} protected branches'.format(project_id))
        protected_branches_url = urljoin(self.projects_api_url, '{}/protected_branches'.format(project_id))
        r = requests.get(protected_branches_url, headers=headers)
        data = r.json()
        self._request_log('GET', protected_branches_url, r.status_code, data)
        return data, r.status_code

    def get_branches(self, project_id, headers):
        """
        Get a list of branches for the project.

        :param project_id:
        :return:
        """
        self._verbose('Getting project {} branches'.format(project_id))
        branches_url = urljoin(self.projects_api_url, '{}/repository/branches'.format(project_id))
        r = requests.get(branches_url, headers=headers)
        data = r.json()
        self._request_log('GET', branches_url, r.status_code, data)
        return data, r.status_code
