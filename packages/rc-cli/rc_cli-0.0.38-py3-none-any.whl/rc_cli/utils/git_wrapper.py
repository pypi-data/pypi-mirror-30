import sys

import click
from git import Repo, InvalidGitRepositoryError

from .context_extractor import get_config
from .git_alias_handler import GitAliasHandler
from ..logger import Logger


@click.group(cls=GitAliasHandler)
@click.pass_context
def git(context):
    """
    RoseCloud Git Wrapper.
    """
    # This method here exist so that click can create a Click.Group
    pass


@git.command()
@click.argument('file_pattern', default='.')
@click.pass_context
def add(context, file_pattern):
    """
    RoseCloud Git Add.

    This will stage all files in the current repository and, if any submodules exist,

    :param context: Context object passed in by Click\n
    :param file_pattern: Stage files matching pattern\n
    :return: None
    """
    # Click does not allow you to call commands in another command. Share add logic with commit.
    repo = __get_repo()

    git_logger = Logger(get_config(context))
    __git_add(repo, file_pattern, git_logger)
    repo.close()
    sys.exit(0)


@git.command()
@click.option('--add-tracked', '-a', is_flag=True, help='Add tracked files and commit.')
@click.option('--message', '-m', default='rc client commit', help='Commit message.')
@click.pass_context
def commit(context, add_tracked, message):
    """
    RoseCloud Git Commit.

    Alias ci.

    It will commit all submodules if any and then the base repository.

    :param context: Context object passed in by Click\n
    :param add_tracked: Add all changed tracked files\n
    :param message: Commit message. Defaults to 'rc client commit'\n
    :return: None
    """
    repo = __get_repo()
    git_logger = Logger(get_config(context))

    if add_tracked:
        git_logger._verbose('Adding all tracked files')
        __git_add(repo, '.', git_logger)

    for submodule in repo.submodules:
        subrepo = submodule.module()
        if subrepo.is_dirty():
            git_logger._verbose('Committing to subrepo {}'.format(subrepo.working_dir))
            subrepo.index.commit(message)
        subrepo.close()

    git_logger._verbose('Committing to base repo {}'.format(repo.working_dir))
    repo.index.commit(message)
    repo.close()
    git_logger._success('Commit success')
    sys.exit(0)


def __git_add(repo, file_pattern, git_logger):
    """
    Perform a Git Add.

    :param repo: Repo object.
    :param file_pattern: Add files matching pattern.
    :param git_logger: Logger.
    :return:
    """

    def stage_file(repo):
        git_logger._verbose('Adding {} to subrepo {}'.format(file_pattern, repo.working_dir))
        try:
            if file_pattern == '.':
                repo.git.add(A=True)
            else:
                repo.index.add([file_pattern])
        except FileNotFoundError:
            git_logger._warn('{} is missing'.format(repo.working_dir))

    for submodule in repo.submodules:
        subrepo = submodule.module()
        stage_file(subrepo)
        subrepo.close()

    stage_file(repo)

    git_logger._success('Added {} success'.format(file_pattern))


@git.command()
@click.argument('remote_name')
@click.argument('branch_name')
@click.pass_context
def push(context, remote_name, branch_name):
    """
    RoseCloud Git Push.

    Push all changes in submodules to the provided remote_name
    and branch_name. Once all submodules are pushed

    :param context: Context object passed in by Click\n
    :param remote_name: Name of the remote to push to\n
    :param branch_name: Name of the branch to push to\n
    :return: None
    """
    git_logger = Logger(get_config(context))

    def push_remote(repo):
        remote = __get_remote(repo, remote_name)
        if remote is None:
            git_logger._warn('Remote {} does not exist'.format(remote_name))
            return

        branch = __get_branch(repo, branch_name)
        if branch is None:
            git_logger._warn('Branch {} does not exist'.format(branch_name))
            return

        git_logger._verbose('Pushing to {} {} in repo {}'.format(remote, branch, repo.working_dir))
        push_infos = remote.push(branch)
        for push_info in push_infos:
            log_push(push_info, repo)

    def log_push(push_info, repo):
        if push_info.flags in {push_info.REJECTED, push_info.REMOTE_FAILURE, push_info.REMOTE_REJECTED,
                               push_info.ERROR}:
            git_logger._error('Failed to push {}'.format(repo.working_dir))
        else:
            git_logger._success('Pushed {}'.format(repo.working_dir))

    repo = __get_repo()

    for submodule in repo.submodules:
        subrepo = submodule.module()
        push_remote(subrepo)
        subrepo.close()

    repo.git.add(A=True)
    repo.index.commit('Updating submodule links')
    push_remote(repo)
    repo.close()
    git_logger._success('Pushed repositories')
    sys.exit(0)


@git.command()
@click.argument('remote_name')
@click.argument('branch_name')
@click.pass_context
def pull(context, remote_name, branch_name):
    """
    RoseCloud Git Pull.

    Pull all submodules if any. Then, pulls base repo.

    :param context: Context object passed in by Click\n
    :param remote_name: Name of the remote to push to\n
    :param branch_name: Name of the branch to push to\n
    :return: None
    """
    git_logger = Logger(get_config(context))

    def pull_remote(repo):
        remote = __get_remote(repo, remote_name)
        if remote is None:
            git_logger._warn('Remote {} does not exist'.format(remote_name))
            return

        branch = __get_branch(repo, branch_name)
        if branch is None:
            git_logger._warn('Branch {} does not exist'.format(branch_name))
            return

        git_logger._verbose('Pulling from {} {} in repo {}'.format(remote, branch, repo.working_dir))
        pull_infos = remote.pull(branch)
        for pull_info in pull_infos:
            log_pull(pull_info, repo)

    def log_pull(pull_info, repo):
        if pull_info.flags in {pull_info.REJECTED, pull_info.ERROR}:
            git_logger._error('Failed to pull {}'.format(repo.working_dir))
        else:
            git_logger._success('Pulled {}'.format(repo.working_dir))

    repo = __get_repo()

    for submodule in repo.submodules:
        subrepo = submodule.module()
        pull_remote(subrepo)
        subrepo.close()
    pull_remote(repo)
    repo.close()
    git_logger._success('Pulled repositories')
    sys.exit(0)


def __get_remote(repo, remote_name):
    """
    Get a Remote from a repo if it exists.

    :param repo: Repo object.
    :param remote_name: Remote name to get.
    :return: Remote if it exists. None otherwise.
    """
    remote = None
    for r in repo.remotes:
        if r.name == remote_name:
            remote = r
            break
    return remote


def __get_branch(repo, branch_name):
    """
    Get a Branch from a repo if it exists.

    :param repo: Repo object.
    :param branch_name: Branch name to get.
    :return: Branch if it exists. None otherwise.
    """
    branch = None
    for b in repo.branches:
        if b.name == branch_name:
            branch = b
            break
    return branch


@git.command()
def status():
    """
    RoseCloud Git Status.

    Alias s.

    Display the status of all submodules (if any) and base repository without
    the Git clutter. It will attempt to bold and color code if possible.

    Symbol Guide:\n
        A: Added\n
        R: Renamed\n
        U: Untracked\n
        M: Modified\n
        D: Deleted\n

    :return: None
    """

    def display_submodules_diff(repo):
        for submodule in repo.submodules:
            subrepo = submodule.module()
            display_repo_diff(subrepo)
            subrepo.close()

    def display_repo_diff(repo):
        display_current_repo(repo)
        diff_index_vs_head = repo.index.diff(None)
        diff_head_vs_index = repo.head.commit.diff()
        display_diff(diff_index_vs_head)
        display_diff(diff_head_vs_index)
        display_untracked_files(repo)

    def display_current_repo(repo):
        click.secho('Git Repo: {}'.format(repo.working_dir), underline=True, fg='cyan', bold=True)

    def display_diff(diff_index):
        for change_type in diff_index.change_type:
            printer = change_type_printer(change_type)
            for diff in diff_index.iter_change_type(change_type):
                printer(diff.a_path)

    def display_untracked_files(repo):
        printer = change_type_printer('U')  # U for untracked.
        for untracked_file in repo.untracked_files:
            printer(untracked_file)

    def change_type_printer(change_type):
        if change_type == 'A':
            return lambda msg: click.secho('  {} {}'.format(change_type, msg), fg='green', bold=True)
        elif change_type == 'R' or change_type == 'U':
            return lambda msg: click.secho('  {} {}'.format(change_type, msg), fg='magenta')
        elif change_type == 'M':
            return lambda msg: click.secho('  {} {}'.format(change_type, msg), fg='red', bold=True)
        elif change_type == 'D':
            return lambda msg: click.secho('  {} {}'.format(change_type, msg), fg='red', dim=True)
        else:
            return lambda msg: click.secho('  {} {}'.format(change_type, msg))

    repo = __get_repo()
    display_submodules_diff(repo)  # Show all submodules status.
    display_repo_diff(repo)  # Show base repo status.
    repo.close()
    sys.exit(0)


@git.command()
@click.argument('branch_name')
@click.option('--create-branch', '-b', is_flag=True, help='Checkout and Create a new branch')
@click.option('--before', default=None, help='Get latest commit before date in the form YYYY-mm-dd HH:MM')
@click.pass_context
def checkout(context, branch_name, create_branch, before):
    """
    RoseCloud Git Checkout.

    Alias co.

    This will attempt to checkout the branch if it exist. Otherwise, it will not attempt to.
    If the create_branch flag is True, it will attempt to create a branch and checkout to that
    branch_name if and only if it does not already exists.

    If there are submodules, all submodules will attempt to checkout to the same branch_name if possible.

    If the before is specified, it must be in the form YYYY-mm-dd HH:MM where HH:MM is in 24hr format.
    This will reset the branch_name to a commit found in master. It will prompt the user before attempting to do
    so as such resets will lose data if it has not been merged to master.

    :param context: Context object passed in by Click\n
    :param branch_name: Branch name to checkout\n
    :param create_branch: Flag indicating to create a branch\n
    :param before: Grader utility. Checkout a commit before this date in YYYY-mm-dd HH:MM\n
    :return: None
    """
    git_logger = Logger(get_config(context))
    repo = __get_repo()

    def should_checkout(repo):
        if repo.head.is_detached:
            git_logger._warn('Repo {} is in a DETACHED HEAD {}'.format(repo.working_dir, repo.head.commit.hexsha))
            return True
        if repo.active_branch.name == branch_name and before is None:
            git_logger._success('Already on branch {}'.format(branch_name))
            return False
        return True

    def handle_checkout(repo):
        branch_exists = __check_branch_existence(repo, branch_name, git_logger)
        if not branch_exists:
            if create_branch:
                git_logger._verbose('Creating new branch {}'.format(branch_name))
                branch = repo.create_head(branch_name)
                branch.checkout()
                return True
            else:
                git_logger._error(
                    'Branch {} does not exist. Try `rc git checkout -b {}`'.format(branch_name, branch_name))
                return False
        if create_branch:
            git_logger._error(
                'Branch {} already exist. Unable create a new branch. Try `rc git checkout {}`'.format(branch_name,
                                                                                                       branch_name))
            return False
        repo.git.checkout(branch_name)
        return True

    def reset_onto_commit(repo):
        if before is not None:
            # Localize imports.
            from datetime import datetime
            from pytz import timezone

            __git_merge(repo, 'origin/master', git_logger)
            # Fix timezone to be eastern. This library handles daylight saving.
            eastern_timezone = timezone('US/Eastern')
            try:
                cutoff_date = eastern_timezone.localize(datetime.strptime(before, '%Y-%m-%d %H:%M'))
            except ValueError:
                git_logger._error('Unable to convert before {}. '
                                  'Please verify it is in the form YYYY-mm-dd HH:MM '
                                  'where HH:MM are in 24hr format'.format(before))
                return False
            commit_to_reset_to = None
            for commit in repo.iter_commits(rev=repo.active_branch):
                commit_datetime = commit.committed_datetime.replace(tzinfo=None)
                commit_datetime = eastern_timezone.localize(commit_datetime)
                if cutoff_date >= commit_datetime:
                    commit_to_reset_to = commit
                    break

            if commit_to_reset_to is None:
                git_logger._error('There does not exist a commit before {}'.format(before))
                return False
            confirmation = click.confirm(
                click.style(
                    'This will reset branch {} to this commit sha {}.\n'
                    'You will lose any changes in this branch not merged with master.\n'
                    'Are you sure you want to do this?'.format(
                        branch_name,
                        commit_to_reset_to.hexsha),
                    fg='red',
                    bold=True))
            if confirmation:
                repo.head.reset(commit=commit_to_reset_to.hexsha, working_tree=True)
            return True

    def checkout_repo(repo):
        if should_checkout(repo):
            status = handle_checkout(repo)
            if status:
                reset_onto_commit(repo)

    for submodule in repo.submodules:
        subrepo = submodule.module()
        git_logger._verbose('Checking out {}'.format(subrepo.working_dir))
        checkout_repo(subrepo)
        subrepo.close()

    git_logger._verbose('Checking out {}'.format(repo.working_dir))
    checkout_repo(repo)
    repo.close()
    git_logger._success('Checkout {} completed'.format(branch_name))
    sys.exit(0)


@git.command()
@click.argument('branch_name')
@click.pass_context
def merge(context, branch_name):
    """
    RoseCloud Git Merge.

    Merge with a branch. Unlike other RoseCloud commands, this will not recurse into submodules.

    :param context: Context object passed in by Click\n
    :param branch_name: Branch name to checkout\n
    :return: None
    """
    git_logger = Logger(get_config(context))
    repo = __get_repo()
    __git_merge(repo, branch_name, git_logger)
    repo.close()
    git_logger._success('Merge completed')


def __git_merge(repo, branch_name, git_logger):
    """
    Helper method to merge. `merge` is a command and cannot be called from other commands without Click magic.
    To avoid this, we externalize the work in this method.

    :param repo: Repo Object
    :param branch_name: Branch name to merge
    :param git_logger: Logger
    :return:
    """
    git_logger._verbose('Merging branch {} with branch {}'.format(repo.active_branch, branch_name))
    if __check_branch_existence(repo, branch_name, git_logger):
        git_logger._verbose('Merge result: {}'.format(repo.git.merge(branch_name)))
    else:
        git_logger._error('Branch {} does not exists'.format(branch_name))


def __check_branch_existence(repo, branch_name, git_logger):
    """
    Check if the branch exist.

    :param repo: Repo object
    :param branch_name: Branch name to check the for the existence of
    :param git_logger: Logger
    :return: True if branch exists; False otherwise
    """
    branches = list(map(lambda x: x.strip('* '), repo.git.branch('-a').split('\n')))
    git_logger._verbose('Found branches: {}'.format(branches))

    remote_reference = 'remotes/' if branch_name.startswith('origin') else 'remotes/origin/'
    remote_reference_prefix_length = len(remote_reference)
    branch_exists = False
    for branch in branches:
        if branch.startswith(remote_reference):
            first_space = branch.find(' ')
            if first_space == -1:
                name = branch[remote_reference_prefix_length:]
            else:  # handle "HEAD -> ..." we only want "HEAD"
                name = branch[remote_reference_prefix_length: first_space]
            if name == branch_name:
                branch_exists = True
                break
        elif branch == branch_name:
            branch_exists = True
            break
    return branch_exists


@git.command()
@click.option('--due-date', default=None, help='Date in form YYYY-mm-dd HH:MM')
@click.option('--output', '-o', type=click.File('w'), default=None, help='Output history to a file')
@click.pass_context
def history(context, due_date, output):
    """
    RoseCloud Git Submodule Commit Comparator.

    This is a utility command to help Graders check the time of the last commit for each submodule.
    It can be outputted to a file using the `--output` flag. Otherwise, it will print to the console.

    It prints 2 columns, the first is the submodule name of within the repo and the second is the
    date of the last commit made.

    Nothing will be done if this repository has no submodules.

    If `--due-date` is specified in YYYY-mm-dd HH:MM where Y is year, m is month, d is day, H is hour,
    M is minute, and H and M are specified in 24 hour format, it will print an additional column of
    time deltas since the last commit to the provided due-date. If it is negative, it is late.

    :param context: Context object passed in by Click\n
    :param due_date: Date in YYYY-mm-dd HH:MM format\n
    :param output: File to write data to\n
    :return: None
    """
    git_logger = Logger(get_config(context))
    repo = __get_repo()

    def get_history(cutoff_date, local_timezone):
        for submodule in repo.submodules:
            subrepo = submodule.module()

            username = subrepo.working_dir.split('/')[-1]
            message = '{} {}'.format(username, subrepo.head.commit.committed_datetime)
            if cutoff_date is not None and local_timezone is not None:
                latest_commit = subrepo.head.commit.committed_datetime.replace(tzinfo=None)
                latest_commit = local_timezone.localize(latest_commit)
                diff = str(cutoff_date - latest_commit)

                message = '{} {}'.format(message, diff)
            click.echo(message, file=output)
            subrepo.close()

    cutoff_date = None
    local_timezone = None
    if due_date is not None:
        from datetime import datetime
        from pytz import timezone

        local_timezone = timezone('US/Eastern')
        try:
            cutoff_date = local_timezone.localize(datetime.strptime(due_date, '%Y-%m-%d %H:%M'))
        except ValueError:
            git_logger._error('Unable to convert due_date {}. '
                              'Please verify it is in the form YYYY-mm-dd HH:MM '
                              'where HH:MM are in 24hr format'.format(due_date))
            sys.exit(1)

    git_logger._verbose('Getting history')
    get_history(cutoff_date, local_timezone)
    repo.close()
    git_logger._success('History obtained')
    sys.exit(0)


def __get_repo():
    """
    Helper method to validate whether the current working directory is a git repo or not.

    :return: Repo object.
    """
    try:
        return Repo('.')
    except InvalidGitRepositoryError:
        click.secho('You are running a git wrapped command in a non-git repository', fg='red', bold=True)
        sys.exit(1)
