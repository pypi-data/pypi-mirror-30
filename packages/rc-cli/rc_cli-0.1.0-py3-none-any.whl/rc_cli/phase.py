import json
import pathlib

import click

from .emoji import MEMO, PENCIL
from .logger import Logger


class Phase(Logger):
    def __init__(self, config, directory):
        super().__init__(config)
        self.base = pathlib.Path.cwd().joinpath(directory)

        # Look up name mangling.
        self.config = config
        self.__config_path = None
        self.__config_json = None

    def config_path(self):
        """
        Returns the Path object to `roseconfig.json`.

        :return: Path object to `roseconfig.json`
        """
        if self.__config_path is None:
            self.__config_path = self.base.joinpath('roseconfig.json')
        return self.__config_path

    def config_json(self):
        """
        Returns the json dictionary of `roseconfig.json`

        :return: Dictionary of `roseconfig.json`
        """
        if self.__config_json is None:
            with click.open_file(self.config_path().as_posix(), 'r') as f:
                self.__config_json = json.load(f)
        return self.__config_json

    def _validate(self):
        """
        Returns True if `roseconfig.json` exist, has token, and has group.

        :return: True if `roseconfig.json` is valid
        """
        config_path = self.config_path()
        if config_path.exists():
            self._verbose('{} already exists. {}'.format(config_path.as_posix(), MEMO))
            valid = self.__validate_gitlab() and self.__validate_workspaces()
        else:
            self._error('`roseconfig.json` does not exist. Please run `rc init` to begin.')
            valid = False

        click.echo()  # Print newline for clarity.
        return valid

    def __validate_gitlab(self):
        """
        Verify the gitlab field of `roseconfig.json`.

        :return: True if valid. False otherwise.
        """
        config_json = self.config_json()
        valid = True

        gitlab_obj = config_json.get('gitlab', {})
        if gitlab_obj == {}:
            self._warn('The `roseconfig.json` is missing the field `gitlab`')
            valid = False
        url = gitlab_obj.get('url', None)
        if url is None:
            self._warn('Please provide a `gitlab.url`')
            valid = False
        token = gitlab_obj.get('token', None)
        if token is None or token == '':
            token_url = 'https://docs.gitlab.com/ce/user/profile/personal_access_tokens.html#creating-a-personal-access-token'
            self._warn('Please follow {} and provide a token with api scope as `gitlab.token`'.format(token_url))
            valid = False
        return valid and self.__validate_gitlab_group(gitlab_obj.get('group', {}))

    def __validate_gitlab_group(self, group_obj):
        """
        Verify if the gitlab.group is valid.

        :param group_obj: Group dictionary object to verify
        :return: True if the gitlab.group is valid. False otherwise.
        """
        valid = True
        if group_obj == {}:
            self._warn('Please provide `gitlab.group` field {}'.format(PENCIL))
            valid = False
        name = group_obj.get('name', None)
        if name is None:
            self._warn('Please provide a `gitlab.group.name` field {}'.format(PENCIL))
            valid = False

        visibility = group_obj.get('visibility', '')
        if not self.__verify_visibility(visibility):
            self._warn(
                'Please provide a valid `gitlab.group.visibility` field [public, private, internal] {}'.format(
                    PENCIL))
            valid = False

        lfs_enabled = group_obj.get('lfs_enabled', None)
        if not isinstance(lfs_enabled, bool):
            self._warn('Please provide a boolean for `gitlab.group.lfs_enabled` field {}'.format(PENCIL))
            valid = False

        request_access_enabled = group_obj.get('request_access_enabled', None)
        if not isinstance(request_access_enabled, bool):
            self._warn('Please provide a boolean for `gitlab.group.request_access_enabled` field {}'.format(PENCIL))
            valid = False
        return valid

    def __validate_workspaces(self):
        """
        Validate that a workspaces in `roseconfig.json` is correctly configured.

        :return: True if correct. False otherwise.
        """
        config_json = self.config_json()
        valid = True

        workspaces = config_json.get('workspaces', None)
        if workspaces is None:
            self._warn('Workspaces is missing from `roseconfig.json` {}'.format(PENCIL))
            valid = False
        elif workspaces == []:
            self._warn('Workspaces is empty {}'.format(PENCIL))
            valid = False
        else:
            for index, workspace in enumerate(workspaces):
                name = workspace.get('name', None)
                path = workspace.get('path', None)
                visibility = workspace.get('visibility', '')
                lfs_enabled = workspace.get('lfs_enabled', None)
                request_access_enabled = workspace.get('request_access_enabled', None)

                if name is None:
                    self._warn('Workspace {} is missing name'.format(index))
                    valid = False
                if path is None:
                    self._warn('Workspace {} is missing path'.format(index))
                    valid = False
                if not self.__verify_visibility(visibility):
                    self._warn('Workspace {} has invalid visibility'.format(index))
                    valid = False
                if not isinstance(lfs_enabled, bool):
                    self._warn('Workspace {} requires boolean for lfs_enabled field'.format(index))
                    valid = False
                if not isinstance(request_access_enabled, bool):
                    self._warn('Workspace {} requires boolean for request_access_enabled field'.format(index))
                    valid = False
        return valid

    def __verify_visibility(self, visibility):
        """
        Verify if the visibility argument is one of public, private, or internal.

        :param visibility: String to verify as a valid visibility type.
        :return: True if valid. False otherwise
        """
        return visibility in ['public', 'private', 'internal']
