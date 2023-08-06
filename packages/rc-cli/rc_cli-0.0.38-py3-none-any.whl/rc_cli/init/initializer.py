import json
import sys

import click

from ..emoji import PENCIL, KEYBOARD, MEMO
from ..phase import Phase


class Initializer(Phase):
    def __init__(self, config, directory):
        super().__init__(config, directory)

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

            # In the order that the config_json is built.
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
            config_json = {
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
                'workspaces': [
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
                ],
                'resources': {
                    'name': 'content',
                    'description': '',
                    'path': '',
                    'visibility': 'private',
                    'lfs_enabled': True,
                    'request_access_enabled': False
                },
                'lfs': [
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
                    '**/*.jpg']
            }

            with click.open_file(config_path.as_posix(), 'w') as f:
                f.write(json.dumps(config_json, indent=2))

            return True
        else:
            self._validate()
            return False
