import json
import sys
from urllib.parse import urlparse, urljoin, urlunsplit

import click
import requests
from git import Repo

from ..emoji import PENCIL, KEYBOARD, MEMO
from ..gitlab.groups_api import GroupsApi
from ..phase import Phase


class Initializer(Phase):
    def __init__(self, config, directory, url):
        super().__init__(config, directory)
        self.group_url = url

    def execute(self):
        """
        Initializes the rc workspace.

        :return: None
        """
        self._verbose('Creating workspace {}'.format(KEYBOARD))
        status = self.__create_workspace()
        if not status:
            sys.exit(1)
        self._verbose('Created workspace {} {}'.format(self.base.as_posix(), MEMO))
        status = self.__create_config_json()

        if status:
            self._success('Workspace initialized @ {}'.format(self.base.as_posix()))
            self._success('Please configure `roseconfig.json` and run `rc build`')
            sys.exit(0)
        else:
            self._error('There was an issue writing `roseconfig.json`')
            sys.exit(1)

    def __create_workspace(self):
        """
        Creates a RoseCloud Directory specified.
        It will not overwrite any existing directory.

        :return: None
        """
        try:
            # If directory is unix style '/etc', then working_directory is '/etc'
            # regardless of where current working directory is.
            self.base.mkdir(parents=True, exist_ok=True)
            return True
        except FileExistsError as e:
            self._error(str(e))
            return False

    def __create_config_json(self):
        """
        Create a roseconfig.json file in the workspace.
        If it exists, nothing will be done.

        :return: None
        """
        config_path = self.config_path()
        if not config_path.exists():
            self._verbose('{} does not exist. Creating roseconfig.json. {}'
                          .format(config_path.as_posix(), PENCIL))

            if self.group_url is None:
                config_json = self.__handle_new_workspace()
            else:
                config_json = self.__handle_from_url()

            with click.open_file(config_path.as_posix(), 'w') as f:
                f.write(json.dumps(config_json, indent=2))
            return True
        else:
            self._validate()
            return False

    def __handle_new_workspace(self):
        """
        Handle construction of `roseconfig.json` from scratch.

        :return: roseconfig.json
        """
        gitlab_url = click.prompt(click.style('Gitlab URL', fg='magenta'), type=str,
                                  default='https://ada.csse.rose-hulman.edu')
        gitlab_token = click.prompt(click.style('Gitlab Private Token', fg='magenta'), type=str,
                                    default='',
                                    show_default=False)
        group_name = click.prompt(click.style('Group name', fg='magenta'), type=str)
        group_description = click.prompt(click.style('Group description', fg='magenta'), type=str,
                                         default='', show_default='')
        group_visibility = click.prompt(click.style('Group visibility [public/private/internal]', fg='magenta'),
                                        type=click.Choice(['public', 'private', 'internal']),
                                        default='private')
        group_lfs_enabled = click.prompt(click.style('Group lfs enabled [True/False]', fg='magenta'),
                                         type=bool, default=True)
        group_request_access_enabled = click.prompt(
            click.style('Group request access enabled [True/False]', fg='magenta'), type=bool,
            default=True)
        group_parent_id = click.prompt(click.style('Group parent id (optional)', fg='magenta'), type=str,
                                       default='',
                                       show_default=False)

        # Defaults
        default_workspaces = [
            {
                'name': 'assignments',
                'description': '',
                'path': '',
                'visibility': 'private',
                'lfs_enabled': True,
                'request_access_enabled': False
            },
            {
                'name': 'exams',
                'description': '',
                'path': '',
                'visibility': 'private',
                'lfs_enabled': True,
                'request_access_enabled': False
            }
        ]
        default_resources = {
            'name': 'content',
            'description': '',
            'path': '',
            'visibility': 'private',
            'lfs_enabled': True,
            'request_access_enabled': False
        }
        default_lfs = self.__get_default_lfs()

        return {
            'gitlab': {
                'url': gitlab_url,
                'token': gitlab_token,
                'group': {
                    'name': group_name,
                    'description': group_description,
                    'visibility': group_visibility,
                    'lfs_enabled': group_lfs_enabled,
                    'request_access_enabled': group_request_access_enabled,
                    'parent_id': group_parent_id
                }
            },
            'workspaces': default_workspaces,
            'resources': default_resources,
            'lfs': default_lfs
        }

    def __handle_from_url(self):
        """
        Handle construction of `roseconfig.json` when given a url.

        This will also handle cloning/replicating structure within the Group.

        :return: roseconfig.json
        """
        gitlab_token = click.prompt(click.style('Gitlab Private Token', fg='magenta'), type=str,
                                    default='',
                                    show_default=False)
        if gitlab_token == '':
            self._error('Initializing from URL requires a non-empty Gitlab Token')
            token_url = 'https://docs.gitlab.com/ce/user/profile/personal_access_tokens.html#creating-a-personal-access-token'
            self._warn('Please follow {} and provide a token with api scope'.format(token_url))
            sys.exit(1)

        group_parsed_url = urlparse(self.group_url)
        gitlab_url = urlunsplit((group_parsed_url.scheme, group_parsed_url.hostname, '', '', ''))

        api_url = urljoin(gitlab_url, '/api/v4/')
        gitlab_groups_api = GroupsApi(self.config, api_url)

        def get_parent_group(group_name, headers):
            self._verbose('Fetching Group {} data from Gitlab'.format(group_name))
            groups, status = gitlab_groups_api.search_groups(group_name, headers)
            if status != requests.codes.ok:
                self._error(
                    'Unable to retrieve group information from URL {}. Got {}'.format(self.group_url, groups))
                sys.exit(1)
            parent_group = next((group for group in groups if group.get('name', '') == group_name), None)
            if parent_group is None:
                self._error('Unable to find group with web_url {}'.format(self.group_url))
                sys.exit(1)
            return parent_group

        def get_subgroups(parent_group_id, headers):
            subgroups, status = gitlab_groups_api.get_subgroups(parent_group_id, headers)
            if status != requests.codes.ok:
                self._error('Unable to retrieve workspaces of group {}'.format(group_name))
                sys.exit(1)
            return subgroups

        def make_workspace(subgroup):
            return {
                'name': subgroup.get('name'),
                'description': subgroup.get('description'),
                'path': '',
                'visibility': subgroup.get('visibility'),
                'lfs_enabled': subgroup.get('lfs_enabled'),
                'request_access_enabled': subgroup.get('request_access_enabled')
            }

        def get_resources_repo(parent_group_id, headers):
            repositories, status = gitlab_groups_api.get_group_projects(parent_group_id, headers)
            if status != requests.codes.ok:
                self._error('Unable to retrieve resources of group {}'.format(group_name))
                sys.exit(1)
            if len(repositories) != 1:
                self._error('Expected one resources repository per group but got {}'.format(len(content)))
                sys.exit(1)
            resources_repo, *ignore = repositories
            return resources_repo

        def make_local_directory(path):
            try:
                self._verbose('Making directory {}'.format(path.as_posix()))
                path.mkdir(parents=True, exist_ok=True)
                return True
            except FileExistsError as e:
                self._error(str(e))
                return False

        def clone_repo(repo, base_destination_path):
            clone_url = repo.get('ssh_url_to_repo')
            self._verbose('Cloning repo {}'.format(clone_url))
            project_path = base_destination_path.joinpath(repo.get('name'))
            Repo.clone_from(clone_url, project_path.as_posix(), branch='master')

        def clone_workspaces(subgroups):
            self._verbose('Cloning workspaces repositories')
            for subgroup in subgroups:
                name = subgroup.get('name')
                workspace_path = self.base.joinpath(name)

                status = make_local_directory(workspace_path)
                if not status:
                    self._warn('Skipping subgroup {}'.format(name))
                    continue

                projects, status = gitlab_groups_api.get_group_projects(subgroup.get('id'), headers)
                if status != requests.codes.ok:
                    self._error('Failed to get subgroup {} projects with reason {}'.format(name, projects))
                    self._warn('Skipping subgroup {}'.format(name))
                    continue

                for project in projects:
                    clone_repo(project, workspace_path)

        # Should be of the form: https://ada-stage.csse.rose-hulman.edu/csse373
        group_name = group_parsed_url.path[1:]  # csse373

        headers = {'PRIVATE-TOKEN': gitlab_token}

        parent_group = get_parent_group(group_name, headers)
        group_description = parent_group.get('description')
        group_visibility = parent_group.get('visibility')
        group_lfs_enabled = parent_group.get('lfs_enabled')
        group_request_access_enabled = parent_group.get('request_access_enabled')
        group_parent_id = parent_group.get('parent_id')

        parent_group_id = parent_group.get('id')
        subgroups = get_subgroups(parent_group_id, headers)
        workspaces = list(map(make_workspace, subgroups))

        resources_repo = get_resources_repo(parent_group_id, headers)
        resources = make_workspace(resources_repo)

        clone_workspaces(subgroups)

        self._verbose('Cloning resources repository')
        clone_repo(resources_repo, self.base)

        default_lfs = self.__get_default_lfs()

        return {
            'gitlab': {
                'url': gitlab_url,
                'token': gitlab_token,
                'group': {
                    'name': group_name,
                    'description': group_description,
                    'visibility': group_visibility,
                    'lfs_enabled': group_lfs_enabled,
                    'request_access_enabled': group_request_access_enabled,
                    'parent_id': group_parent_id
                }
            },
            'workspaces': workspaces,
            'resources': resources,
            'lfs': default_lfs
        }

    def __get_default_lfs(self):
        return [
            '**/*.pptx',
            '**/*.xls',
            '**/*.pdf',
            '**/*.docx',
            '**/*.mp4',
            '**/*.mp3',
            '**/*.iso',
            '**/*.png',
            '**/*.webm',
            '**/*.jpeg',
            '**/*.jpg'
        ]
