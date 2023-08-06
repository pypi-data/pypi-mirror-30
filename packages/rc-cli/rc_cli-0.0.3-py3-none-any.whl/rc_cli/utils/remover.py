import os
import pathlib
import shutil

import click

from ..logger import Logger


class Remover(Logger):
    def __init__(self, config, file_pattern, search_directories, force, interactive):
        super().__init__(config)

        self.file_pattern = file_pattern
        self.search_directory_paths = list(map(lambda x: pathlib.Path(x), search_directories))

        self.force = force
        self.interactive = interactive
        if self.force and self.interactive:
            self._warn('Force and Interactive flags are enabled. Force flag will be ignored.')

    def execute(self):
        """
        Executes the general utility remover.

        :return: None
        """
        self._verbose(
            'Attempting to remove files with pattern {} in {}'.format(self.file_pattern,
                                                                      list(map(lambda x: x.as_posix(),
                                                                               self.search_directory_paths))))
        search_paths = self.search_directory_paths.copy()
        for search_path in search_paths:
            if search_path.match(self.file_pattern):
                status = self.__delete_match(search_path)
                if not status and search_path.is_dir():
                    search_paths += [x for x in search_path.iterdir()]
            elif search_path.is_dir():
                # Not matched but match could be found nested
                search_paths += [x for x in search_path.iterdir()]
        self._success('remove utility completed')

    def __delete_match(self, matched_path):
        """
        Delete the match based on its whether it is a directory or file.
        Takes into account force and interactive flag where interactive flag takes precedence.

        If neither force nor interactive flags are enabled, it will perform a dry-run and
        log the matches without any deletion.

        :param matched_path: Path to remove.
        :return: True if successful, False otherwise.
        """
        posix_path = matched_path.as_posix()

        def get_confirmation():
            if self.interactive:
                confirmation = click.confirm('Do you want to remove {}?'.format(posix_path))
            elif self.force:
                confirmation = self.force
            else:
                confirmation = False
            return confirmation

        def log_and_return_success(match_type):
            self._success('Deleted {} at {}'.format(match_type, posix_path))
            return True

        def log_and_return_failure(match_type, error):
            self._error('Failed to remove {} {} with {}'.format(match_type, posix_path, str(error)))
            return False

        def log_and_return_dry_run(confirmation, match_type):
            if not confirmation:
                self._success('Found match {} in {}'.format(match_type, posix_path))
            # Return False to delve deeper in for further matches.
            return False

        def delete_file(confirmation):
            match_type = 'file'
            if confirmation:
                # If it fails, for user experience, avoid having it blow up.
                try:
                    os.remove(matched_path.as_posix())
                    return log_and_return_success(match_type)
                except Exception as e:
                    return log_and_return_failure(match_type, e)
            return log_and_return_dry_run(confirmation, match_type)

        def delete_directory(confirmation):
            match_type = 'directory'
            if confirmation:
                try:
                    # This will recursively delete repo.
                    shutil.rmtree(matched_path.as_posix())
                    return log_and_return_success(match_type)
                except Exception as e:
                    return log_and_return_failure(match_type, e)
            return log_and_return_dry_run(confirmation, match_type)

        confirmation = get_confirmation()

        if matched_path.is_file():
            return delete_file(confirmation)
        elif matched_path.is_dir():
            return delete_directory(confirmation)
        else:
            match_type = 'unknown'
            return log_and_return_dry_run(confirmation, match_type)
