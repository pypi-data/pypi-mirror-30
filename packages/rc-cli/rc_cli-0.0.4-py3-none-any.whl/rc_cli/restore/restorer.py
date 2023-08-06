import json
import pathlib
import re
import shutil
import sys
import tempfile
from time import gmtime, strftime

import click
import requests
from git import Repo

from ..gitlab.groups_api import GroupsApi
from ..gitlab.projects_api import ProjectsApi
from ..gitlab.users_api import UsersApi
from ..logger import Logger


class Restorer(Logger):
    def __init__(self, config, restore_directory, group_name, prefixes, token, user, stage_mode):
        super().__init__(config)

        self.restore_directory = pathlib.Path.cwd().joinpath(restore_directory)  # directory where files are restored
        self.group_name = group_name  # gitlab group name
        self.prefixes = prefixes  # tuple of prefixes
        self.token = token  # gitlab token. admin may run this anywhere --> roseconfig.json may not exist
        self.user = user
        self.api_url = 'https://ada-stage.csse.rose-hulman.edu/api/v4/' if stage_mode else 'https://ada.csse.rose-hulman.edu/api/v4/'
        self.gitlab_groups_api = GroupsApi(config, self.api_url)
        self.gitlab_projects_api = ProjectsApi(config, self.api_url)
        self.gitlab_users_api = UsersApi(config, self.api_url)

    def execute(self):
        """
        Execute the restore phase.

        :return: None
        """
        self._verbose('Attempting restore phase')
        if not self.restore_directory.is_dir():
            self._error('The restore_directory is not a directory')
            sys.exit(1)

        restorable_projects = self.__get_restorable_projects()

        headers = {'PRIVATE-TOKEN': self.token}
        parent_group = self.__get_parent_group(headers)
        if parent_group is None:
            sys.exit(1)
        parent_group_id = parent_group.get('id')
        projects_to_restore = self.__get_projects_to_restore(restorable_projects, parent_group_id, headers)
        if len(projects_to_restore) == 0:
            self._warn(
                'No projects are restorable. Please address any warnings or adjust prefixs or user specifications')
            sys.exit(1)

        project_data = self.__restore_from_backup(parent_group_id, projects_to_restore, headers)
        masters, status_code = self.gitlab_groups_api.get_group_members(parent_group_id, headers)
        if status_code != requests.codes.ok:
            self._error('Failed to get group members. Projects will not be configured. Reason: {}'.format(masters))
            sys.exit(1)
        self.__configure_projects(masters, project_data, headers)
        self.__write_restore_json(project_data)
        self._success('restore phase complete')
        sys.exit(0)

    def __get_restorable_projects(self):
        """
        Returns a list of Path objects in the restore_directory that match any prefixes given and user specifications.

        :return: List of Path objects
        """

        def project_contains_prefix(project_path):
            name = project_path.name
            for prefix in self.prefixes:
                if name.startswith(prefix):
                    return True
            return False

        def project_contains_user(project_path):
            ignore, user = self.__get_project_components(project_path)
            return user == self.user

        restorable_projects = [x for x in self.restore_directory.iterdir() if x.is_dir()]
        if self.prefixes:
            restorable_projects = list(filter(project_contains_prefix, restorable_projects))

        perform_for_all = self.user is None
        if not perform_for_all:
            restorable_projects = list(filter(project_contains_user, restorable_projects))
        self._verbose('Found projects: {}'.format(list(map(lambda x: x.as_posix(), restorable_projects))))
        return restorable_projects

    def __get_parent_group(self, headers):
        """
        Returns the Group specified by group_name.

        :param headers: dictionary with `PRIVATE-TOKEN` key
        :return: Group of the group_name or None on failure
        """
        groups, status_code = self.gitlab_groups_api.search_groups(self.group_name, headers)
        if status_code != requests.codes.ok:
            self._error('Could not found group {}'.format(self.group_name))
            return None
        parent_group = next((group for group in groups if group.get('name', '') == self.group_name), None)
        if parent_group is None:
            self._error('Group {} does not exists'.format(self.group_name))
            return None
        self._verbose('Found parent group: {}'.format(parent_group))
        return parent_group

    def __get_projects_to_restore(self, restorable_projects, parent_group_id, headers):
        """
        Filter out projects that exist on Gitlab. Restorable projects must be projects
        in which do not exist on Gitlab.

        :param restorable_projects: List of Path objects
        :param parent_group_id: Id of the parent group projects will be nested under
        :param headers: dictionary with `PRIVATE-TOKEN` key
        :return: List of projects that can be restored without conflicts
        """

        def non_matching_restorable_projects(group_project_names):
            non_matching = []
            for restorable_project in restorable_projects:
                repository_name = self.__get_repository_name_from_path(restorable_project)
                if repository_name not in group_project_names:
                    non_matching.append(restorable_project)
                else:
                    self._warn(
                        'Restorable project {} exist in Gitlab. To restore, delete the project first and re-run rc command'.format(
                            repository_name))
            self._verbose('Found restorable projects without repositories: {}'.format(non_matching))
            return non_matching

        group_projects, status_code = self.gitlab_groups_api.get_group_projects(parent_group_id, headers)
        if status_code != requests.codes.ok:
            self._error('Failed to find projects for parent_group')
            return
        group_project_names = set(map(lambda project: project.get('name', project), group_projects))
        self._success('Group projects found {}'.format(group_project_names))
        return non_matching_restorable_projects(group_project_names)

    def __restore_from_backup(self, parent_group_id, projects_to_restore, headers):
        """
        Restore the backups. Creates a temporary directory and copies each projects_to_restore Path
        to the temp directory. It attempts to create the corresponding repository on Gitlab. If it
        succeeds, it will then push the repository changes to Gitlab.

        The user should address errors accordingly.
        In addition, these projects may not be properly configured with master permissions,
        student set as members, and feedback branch protected. Default branch may not necessarily
        be master. Thus, the user should use the project_ids to reconfigure the projects as needed.

        :param parent_group_id: group_id of the parent grouping
        :param projects_to_restore:  list of Path objects to projects that can be restored
        :param headers: dictionary with `PRIVATE-TOKEN` key
        :return: List of {id, user}
        """

        def copy_backups_to_temp(repository_name, temp_dir_path, project_path):
            self._verbose('copying {} to temp directory {}'.format(repository_name, temp_dir_path))
            local_repository_path = pathlib.Path(temp_dir_path).joinpath(repository_name)
            shutil.copytree(project_path.as_posix(),
                            local_repository_path.joinpath('.git').as_posix())
            return local_repository_path

        def create_gitlab_repo(repository_name):
            self._verbose('creating gitlab repo for {}'.format(repository_name))
            form_data = {
                'name': repository_name,
                'path': repository_name,
                'namespace_id': parent_group_id
            }
            repository_project, status_code = self.gitlab_projects_api.create_project(form_data, headers)
            return repository_project, status_code  # done for clarity

        def log_push(push_info, repo_posix):
            if push_info.flags in {push_info.REJECTED, push_info.REMOTE_FAILURE, push_info.REMOTE_REJECTED,
                                   push_info.ERROR}:
                self._error('Failed to push {}'.format(repo_posix))
            else:
                self._success('Pushed {}'.format(repo_posix))

        def push_backup_to_gitlab(repo_path, repo_url):
            self._verbose('pushing backups to {}'.format(repo_url))
            repo_posix = repo_path.as_posix()
            repo = Repo.init(repo_path.as_posix())
            origin = repo.create_remote('origin', repo_url)
            for repo_branch in repo.branches:
                self._verbose('pushing branch {}'.format(repo_branch.name))
                repo_branch.checkout()
                # Note: This assumes the person running this is a member of the group.
                # Behaves similar to `git push origin <branch>`
                # If this does unanticipated things, avoid the with block for tempfile
                # below, run this, navigate to temp directory (it should be logged in verbose mode),
                # and attempt to run `git push origin <branch>`. Git should tell you more information.
                origin.push(repo_branch.name)
                push_infos = origin.push(repo_branch.name)
                for push_info in push_infos:
                    log_push(push_info, repo_posix)

        project_data = []
        with tempfile.TemporaryDirectory() as temp_dir_path:
            self._verbose('Attempting to push backups to gitlab {}'.format(temp_dir_path))
            for project_path in projects_to_restore:
                repository_name = self.__get_repository_name_from_path(project_path)
                temp_repo_path = copy_backups_to_temp(repository_name, temp_dir_path, project_path)
                repository_project, status_code = create_gitlab_repo(repository_name)

                ignore, user = self.__get_project_components(project_path)
                project_data.append({'id': repository_project.get('id'), 'name': repository_name, 'user': user})
                if status_code != requests.codes.created:
                    self._error('Failed to create repository for {} : {}'.format(repository_name, repository_project))
                    continue

                # Note: To do this, you must be a master of the group.
                push_backup_to_gitlab(temp_repo_path, repository_project.get('ssh_url_to_repo'))
                self._success('Pushed backups to Gitlab for {}'.format(repository_name))

        self._success('Finished pushing backups')
        return project_data

    def __configure_projects(self, masters, project_data, headers):
        """
        Configures projects to meet RoseCloud specifications:
        1. Master branch is protected for Developer + Master for push and merge.
        2. Feedback branch is protected for Master for push and merge.
        3. All group members are added as master
        4. Robot admin is added as master
        5. student (individual assignment) is added to project if possible.

        :param masters: Group members
        :param project_data: List of {id, user}
        :param headers: dictionary with `PRIVATE-TOKEN` key
        :return:
        """

        def add_robot_admin(access_level):
            robot_user_obj = get_user_object('robotadmin')
            form_data = {
                'access_level': access_level,
                'user_id': robot_user_obj.get('id')
            }
            for project_datum in project_data:
                data, status_code = self.gitlab_projects_api.add_member(project_datum.get('id'), form_data, headers)
                if status_code == requests.codes.created:
                    self._success(data)
                else:
                    self._error(data)

        def add_master_members(access_level):
            form_data = {
                'access_level': access_level
            }
            for project_datum in project_data:
                for master in masters:
                    form_data['user_id'] = master.get('id')
                    data, status_code = self.gitlab_projects_api.add_member(project_datum.get('id'), form_data, headers)
                    if status_code == requests.codes.created:
                        self._success(data)
                    else:
                        self._error(data)

        def unprotect_branch():
            for project_datum in project_data:
                project_id = project_datum.get('id')
                protected_branches, status_code = self.gitlab_projects_api.get_protected_branches(project_id, headers)
                if status_code != requests.codes.ok:
                    self._warn(protected_branches)
                    self._warn('Unable to get protected_branch of {}'.format(project_datum))
                    continue

                for protected_branch in protected_branches:
                    branch_name = protected_branch.get('name')
                    if branch_name == 'master' or branch_name == 'feedback':
                        data, status_code = self.gitlab_projects_api.unprotect_branch(project_id, branch_name, headers)
                        if status_code == requests.codes.no_content:
                            self._success('Unprotect {} was successful'.format(branch_name))
                        else:
                            self._warn(data)
                            self._warn(
                                'If the repository is created but empty, this may indicate that you do not have proper'
                                ' permissions to push backup data. Otherwise, you may ignore this warning.')

        def protect_branch(master_access_level, feedback_access_level):
            master_form_data = {
                'push_access_level': master_access_level,
                'merge_access_level': master_access_level
            }
            feedback_form_data = {
                'push_access_level': feedback_access_level,
                'merge_access_level': feedback_access_level
            }

            for project_datum in project_data:
                project_id = project_datum.get('id')
                branches, status_code = self.gitlab_projects_api.get_branches(project_id, headers)
                if status_code != requests.codes.ok:
                    self._warn(branches)
                    self._warn('Unable to get branches of {}'.format(project_datum))
                    continue
                for branch in branches:
                    branch_name = branch.get('name')
                    status_code = None

                    if branch_name == 'master':
                        master_form_data['name'] = branch_name
                        data, status_code = self.gitlab_projects_api.protect_branch(project_id, master_form_data,
                                                                                    headers)
                    elif branch_name == 'feedback':
                        feedback_form_data['name'] = branch_name
                        data, status_code = self.gitlab_projects_api.protect_branch(project_id, feedback_form_data,
                                                                                    headers)

                    if status_code == requests.codes.created:
                        self._success(data)
                    else:
                        self._error(data)

        def set_default_branch(branch_name):
            for project_datum in project_data:
                data, status_code = self.gitlab_projects_api.default_branch(project_datum.get('id'), branch_name,
                                                                            headers)
                if status_code == requests.codes.ok:
                    self._success(data)
                else:
                    self._error(data)

        def add_user(access_level):
            form_data = {
                'access_level': access_level
            }
            for project_datum in project_data:
                username = project_datum.get('user')
                user_obj = get_user_object(username)
                form_data['user_id'] = user_obj.get('id')
                data, status_code = self.gitlab_projects_api.add_member(project_datum.get('id'), form_data, headers)
                if status_code == requests.codes.created:
                    self._success(data)
                else:
                    self._error(data)

        def get_user_object(username):
            data, status_code = self.gitlab_users_api.search_user_by_username(username, headers)
            if status_code != requests.codes.ok:
                self._error('Failed to search for user {}'.format(username))
                return None
            user_obj = next((datum for datum in data if datum.get('username', '') == username), None)
            if user_obj is None:
                self._warn('Unable to find user {}'.format(username))
                return None
            return user_obj

        self._verbose(project_data)

        MASTER_PERMISSION_LEVEL = 40
        DEVELOPER_PERMISSION_LEVEL = 30

        add_robot_admin(MASTER_PERMISSION_LEVEL)
        add_master_members(MASTER_PERMISSION_LEVEL)
        unprotect_branch()
        protect_branch(DEVELOPER_PERMISSION_LEVEL, MASTER_PERMISSION_LEVEL)
        set_default_branch('master')
        add_user(DEVELOPER_PERMISSION_LEVEL)
        self._success('Finished configuring all restored projects')

    def __write_restore_json(self, project_data):
        """
        Writes a timestamp_restore.json file documenting the projects that were restored.

        :param project_data: {id, name, user} dictionary
        :return: None
        """
        timestamp = strftime('%Y-%m-%d_%H:%M:%S', gmtime())
        file_name = '{}_restore.json'.format(timestamp)
        self._verbose('Writing {}'.format(file_name))

        projects = list(map(lambda datum: {'name': datum.get('name'), 'gitlabId': datum.get('id')}, project_data))
        restore = {
            'group': self.group_name,
            'projects': projects
        }

        with click.open_file(file_name, 'w') as f:
            f.write(json.dumps(restore, indent=2))
        self._success('Finished writing {}'.format(file_name))

    def __get_project_components(self, project_path):
        """
        Get the name and user component of a rosebuild project.

        All projects are assumed to have the form:
        name-user.git

        This method returns the (name, user) tuple

        Example:
        assignment1-lamd.git
        --> (assignment1, lamd)

        :param project_path: Path object from pathlib.
        :return: (name, user) tuple
        """
        # Use regex to capture both test usernames (i.e testcsse-1, testinst-1) and regular usernames.
        pattern = r'(.*)-([a-z]+-\d|[a-z]+[0-9]*)'
        match = re.fullmatch(pattern, self.__get_repository_name_from_path(project_path))
        return match.group(1), match.group(2)

    def __get_repository_name_from_path(self, project_path):
        """
        Get the project repository name from a Path object.

        All projects are assumed to have the form:
        name-user.git

        This method returns the name-user part of the path.

        Example:
        assignment1-lamd.git
        --> assignment1-lamd

        :param project_path: Path object from pathlib
        :return: name-user String
        """
        HIDDEN_FILE_SEPARATOR = '.'
        return project_path.name.split(HIDDEN_FILE_SEPARATOR)[0]
