import os
import subprocess
import sys
from urllib.parse import urljoin

import click
import requests
from git import Repo

from ..emoji import MEMO, KEYBOARD
from ..gitlab.groups_api import GroupsApi
from ..gitlab.projects_api import ProjectsApi
from ..phase import Phase


class Deployer(Phase):
    def __init__(self, config, directory):
        super(Deployer, self).__init__(config, directory)
        self.gitignore = None  # for caching

    def execute(self):
        """
        Deploy the rc workspace to gitlab creating groups, subgroups, and projects.

        :return: None
        """
        if not self._validate():
            self._error('Please address `roseconfig.json` issues before deploying')
            sys.exit(1)
        config_json = self.config_json()

        gitlab = config_json.get('gitlab')
        group_obj = gitlab.get('group')
        token = gitlab.get('token')

        # NOTE: urljoin will override the last path component if there is no '/' at the end.
        # If it was '/api/v4', the next urljoin with the return value will be '../api/newstuff'.
        # Use `/api/v4/` instead (last '/').
        api_url = urljoin(gitlab['url'], '/api/v4/')
        gitlab_groups_api = GroupsApi(self.config, api_url)
        gitlab_projects_api = ProjectsApi(self.config, api_url)

        self._verbose('Using token {} to hit {} {}'.format(token, api_url, MEMO))

        headers = {'PRIVATE-TOKEN': token}
        parent_group = self.__create_group_if_not_exist(gitlab_groups_api, group_obj, headers)
        if parent_group is None:
            self._error('Failed to create group. Please check if this group name is available on Gitlab')
            sys.exit(1)

        workspaces = config_json.get('workspaces')
        parent_group_id = parent_group.get('id')
        sub_groups = self.__create_workspaces_if_not_exist(gitlab_groups_api, workspaces, parent_group_id, headers)
        if not sub_groups:
            self._error('Failed to create workspaces on Gitlab')
            sys.exit(1)
        self._success('Created workspaces on Gitlab')

        status = self.__push_workspaces(gitlab_projects_api, gitlab_groups_api, sub_groups, headers)
        if not status:
            self._error('Failed to push workspaces')
            sys.exit(1)

        self.__push_resources(gitlab_projects_api, gitlab_groups_api, parent_group, headers)
        self._success('Deploy phase complete')
        sys.exit(0)

    def __create_group_if_not_exist(self, gitlab_groups_api, group_obj, headers):
        """
        Create group if does not exist on Gitlab

        :param gitlab_groups_api: Gitlab Groups API
        :param group_obj: `roseconfig.json` gitlab.group object
        :param headers: dictionary with `PRIVATE-TOKEN` key
        :return: Gitlab Group specified by the group_obj
        """
        group_name = group_obj.get('name')
        groups, status_code = gitlab_groups_api.search_groups(group_name, headers)
        if status_code != requests.codes.ok:
            self._error(groups)
            return

        parent_group = next((group for group in groups if group.get('name', '') == group_name), None)
        if parent_group is None:
            self._verbose('Group {} does not exists'.format(group_name))
            # No groups user is member of. Could still fail if group exist already.
            group_obj['path'] = group_name
            git_group, status_code = gitlab_groups_api.create_group(group_obj, headers)
            if status_code != requests.codes.created:
                self._error(git_group)
                self._error('Unavailable group names {}'.format(groups))
                return None
            parent_group = git_group

        self._verbose('Parent group {}'.format(parent_group))
        return parent_group

    def __create_workspaces_if_not_exist(self, gitlab_groups_api, workspaces, parent_group_id, headers):
        """
        Create workspaces (subgroups) on Gitlab if it does not exists.

        :param gitlab_groups_api: Gitlab Groups API
        :param workspaces: `roseconfig.json` workspaces list
        :param parent_group_id: group_id of the Gitlab group these workspaces are under
        :param headers: dictionary with `PRIVATE-TOKEN` key
        :return: List of Gitlab subgroups
        """

        def create_sub_groups(existing_workspaces):
            existing_workspace_names = set(map(lambda x: x.get('name'), existing_workspaces))
            sub_groups = existing_workspaces
            for index, workspace in enumerate(workspaces):
                if workspace.get('name') in existing_workspace_names:
                    self._verbose('Sub-group {} {} already exists {}'.format(index, workspace.get('name'), MEMO))
                    continue
                self._verbose('Creating sub-group {} {} {}'.format(index, workspace.get('name'), KEYBOARD))
                workspace['path'] = workspace.get('name')
                workspace['parent_id'] = parent_group_id
                sub_group, status_code = gitlab_groups_api.create_group(workspace, headers)
                if status_code != requests.codes.created:
                    self._error(sub_group)
                    continue
                sub_groups.append(sub_group)
            return sub_groups

        existing_subgroups, status_code = gitlab_groups_api.get_subgroups(parent_group_id, headers)
        if status_code != requests.codes.ok:
            self._error(existing_subgroups)
            return None
        return create_sub_groups(existing_subgroups)

    def __push_workspaces(self, gitlab_projects_api, gitlab_groups_api, sub_groups, headers):
        """
        Push `roseconfig.json` workspaces to Gitlab.

        :param gitlab_projects_api: Gitlab Projects API
        :param gitlab_groups_api: Gitlab Groups API
        :param sub_groups: List of Gitlab sub_groups to push data to
        :param headers: dictionary with `PRIVATE-TOKEN` key
        :return: None
        """

        def setup_lfs():
            try:
                self._verbose('Setting up git-lfs')
                git_lfs = subprocess.run(['git', 'lfs', 'install'], stdout=subprocess.PIPE)
                self._verbose('Executed `git lfs install` and got {}'.format(git_lfs.stdout.decode('utf-8')))
                return True
            except:
                help_url = 'https://github.com/git-lfs/git-lfs/wiki/Installation'
                self._error('Failed to setup git-lfs. Please install git-lfs {}'.format(help_url))
                return False

        def upload_gitlab_project(sub_group, workspace_project_paths):
            sub_group_id = sub_group.get('id')
            existing_subgroup_projects, existing_subgroup_project_names = self.__get_existing_projects(
                gitlab_groups_api, sub_group_id, headers)
            if existing_subgroup_projects is None and existing_subgroup_project_names is None:
                self._error('Failed to upload gitlab projects')
                return

            for project_path in workspace_project_paths:
                project_name = project_path.name

                gitlab_project = self.__get_or_create_project(gitlab_projects_api, project_name,
                                                              existing_subgroup_projects,
                                                              existing_subgroup_project_names, sub_group, headers)
                if gitlab_project is None:
                    self._error('Failed to get gitlab project to push to for {}'.format(project_name))
                    continue

                ssh_url = gitlab_project.get('ssh_url_to_repo')
                self.__push_to_repo(project_path, ssh_url)

        lfs_status = setup_lfs()
        if not lfs_status:
            return False
        for sub_group in sub_groups:
            workspace_path = self.base.joinpath(sub_group.get('name'))
            workspace_project_paths = [x for x in workspace_path.iterdir() if x.is_dir()]
            upload_gitlab_project(sub_group, workspace_project_paths)

        self._success('Pushed workspaces')
        return True

    def __push_resources(self, gitlab_projects_api, gitlab_groups_api, parent_group, headers):
        """
        Push `roseconfig.json` resources to Gitlab.

        :param gitlab_projects_api: Gitlab Projects API
        :param gitlab_groups_api: Gitlab Groups API
        :param parent_group_id: Group id of the group the resources is under
        :param headers: dictionary with `PRIVATE-TOKEN` key
        :return: None
        """
        config_json = self.config_json()
        resources = config_json.get('resources')
        resource_name = resources.get('name')

        existing_projects, existing_project_names = self.__get_existing_projects(gitlab_groups_api,
                                                                                 parent_group.get('id'),
                                                                                 headers)
        if existing_projects is None and existing_project_names is None:
            self._error('Failed to push resources to gitlab')
            return

        gitlab_project = self.__get_or_create_project(gitlab_projects_api, resource_name, existing_projects,
                                                      existing_project_names, parent_group, headers)

        resource_path = self.base.joinpath(resource_name)
        if not resource_path.exists():
            self._error('Resources path does not exist : {}'.format(resource_path.as_posix()))
            return
        ssh_url = gitlab_project.get('ssh_url_to_repo')
        self.__push_to_repo(resource_path, ssh_url)
        self._success('Pushed resources')

    def __get_existing_projects(self, gitlab_groups_api, group_id, headers):
        """
        Get a list of existing projects and a set of their names under the group_id

        :param gitlab_groups_api: Gitlab Groups API
        :param group_id: group_id to get projects under
        :param headers: dictionary with `PRIVATE-TOKEN` key
        :return: (list of dict: projects_under_grouping, set: project_names_under_grouping)
        """
        existing_projects, status_code = gitlab_groups_api.get_group_projects(group_id, headers)
        if status_code != requests.codes.ok:
            self._error('Failed to get projects for group {} with reason {}'.format(group_id, existing_projects))
            return (None, None)
        existing_project_names = set(map(lambda x: x.get('name'), existing_projects))
        return existing_projects, existing_project_names

    def __get_or_create_project(self, gitlab_projects_api, project_name, existing_projects, existing_project_names,
                                sub_group, headers):
        """
        Get the project in existing_projects or creates it on gitlab.

        :param gitlab_projects_api: Gitlab Projects API
        :param project_name: Name of project to get or create
        :param existing_projects: List of known projects
        :param existing_project_names: List of known project names (for efficiency reasons)
        :param namespace_id: Namespace to create project under
        :param headers: dictionary with `PRIVATE-TOKEN` key
        :return:
        """
        if project_name in existing_project_names:
            gitlab_project = next((project for project in existing_projects if project.get('name', '') == project_name))
        else:
            form_data = {
                'name': project_name,
                'path': project_name,
                'namespace_id': sub_group.get('id'),
                'lfs_enabled': sub_group.get('lfs_enabled'),
                'request_access_enabled': sub_group.get('request_access_enabled'),
                'visibility': sub_group.get('visibility')
            }
            gitlab_project, status_code = gitlab_projects_api.create_project(form_data, headers)
            if status_code != requests.codes.created:
                self._error(
                    'Failed to create project {} with reason {}'.format(project_name, gitlab_project))
                return None
        return gitlab_project

    def __push_to_repo(self, project_path, url):
        """
        Push contents at project_path to git url.

        :param project_path: Path object to project
        :param url: Git url
        :return: None
        """
        project_posix = project_path.as_posix()

        def write_gitignore_if_not_exists():
            gitignore_path = project_path.joinpath('.gitignore')
            self._verbose('Writing .gitignore {}'.format(gitignore_path.as_posix()))
            if not gitignore_path.exists():
                gitignore = self.__get_gitignore()
                with click.open_file(gitignore_path.as_posix(), 'w') as f:
                    f.write(gitignore)
                self._verbose('gitignore added at {}'.format(gitignore_path.as_posix()))

        def create_remote_for_repository(repo):
            origin = None
            for remote in repo.remotes:
                if remote.name == 'origin':
                    if remote.url != url:
                        self._verbose('Modifying existing .git config url {} to {}'.format(remote.url, url))
                        with remote.config_writer as cw:
                            cw.set('url', url)
                    origin = remote
                    break
            if origin is None:
                origin = repo.create_remote('origin', url)
            return origin

        def push_existing_branches_if_any(origin):
            if repo.branches:
                for branch in repo.branches:
                    branch.checkout()
                    self._verbose('Pushing existing branch {}'.format(branch.name))
                    origin.push(branch.name)
                    push_any_lfs(branch.name)

        def track_lfs_patterns(lfs_patterns, project_posix):
            self._verbose('Adding lfs tracking {}'.format(project_posix))
            os.chdir(project_posix)
            for lfs_pattern in lfs_patterns:
                track_command = subprocess.run(['git', 'lfs', 'track', '"{}"'.format(lfs_pattern)],
                                               stdout=subprocess.PIPE)
                self._verbose(track_command.stdout.decode('utf-8').strip())
            os.chdir(self.base.as_posix())
            self._success('Successfully added lfs tracking')

        def push_any_lfs(branch_name):
            os.chdir(project_posix)
            self._verbose('Pushing all lfs files for branch {}'.format(branch_name))
            push_all_command = subprocess.run(['git', 'lfs', 'push', 'origin', branch_name, '--all'],
                                              stdout=subprocess.PIPE)
            self._verbose(push_all_command.stdout.decode('utf-8').strip())
            os.chdir(self.base.as_posix())

        def log_push(push_info):
            if push_info.flags in {push_info.REJECTED, push_info.REMOTE_FAILURE, push_info.REMOTE_REJECTED,
                                   push_info.ERROR}:
                self._error('Failed to push {}'.format(project_posix))
            else:
                self._success('Pushed {}'.format(project_posix))

        self._verbose('Preparing to push files {} to {}'.format(project_path.name, url))

        write_gitignore_if_not_exists()

        repo = Repo.init(project_posix)
        origin = create_remote_for_repository(repo)

        push_existing_branches_if_any(origin)

        lfs_patterns = self.config_json().get('lfs')
        track_lfs_patterns(lfs_patterns, project_posix)

        repo.git.add(A=True)
        repo.index.commit('Initialized repository')
        push_infos = origin.push('master')
        for push_info in push_infos:
            log_push(push_info)

    def __get_gitignore(self):
        if self.gitignore is None:
            self._verbose('Initializing gitignore')
            url = 'https://www.gitignore.io/api/c%2Cqt%2Cvim%2Cc%2B%2B%2Cjava%2Cnode%2Cxcode%2Clatex' \
                  '%2Cswift%2Clinux%2Cemacs%2Cpydev%2Cmacos%2Cmaven%2Cgradle%2Cscheme%2Cpython%2Cwindows' \
                  '%2Ceclipse%2Cnetbeans%2Cintellij%2Cxilinxise%2Cobjective-c%2Cvisualstudio' \
                  '%2Candroidstudio%2Cvisualstudiocode'
            r = requests.get(url)
            data = r.content.decode('utf-8')
            self._request_log('GET', url, r.status_code, data)

            if r.status_code != requests.codes.ok:
                self._error('Failed to initialize gitignore')
                return None
            self.gitignore = data
        return self.gitignore
