import pathlib
import shutil

from ..emoji import PENCIL, KEYBOARD
from ..phase import Phase


class Builder(Phase):
    def __init__(self, config, directory):
        super(Builder, self).__init__(config, directory)

    def execute(self):
        """
        Builds the rc workspace.

        :return:
        """
        self._verbose('Stubing workspaces {}'.format(KEYBOARD))
        self._validate()  # Ignore results. Use to notify user of needed actions.
        self.__stub_workspaces()
        self.__stub_resources()
        self._success('Build phase complete')

    def __stub_workspaces(self):
        """
        Stubs Workspaces.

        :return: None
        """
        config_json = self.config_json()
        workspaces = config_json['workspaces']
        self.__stub(workspaces, stub_type='workspace')

    def __stub_resources(self):
        """
        Stubs Resources.

        :return: None
        """
        config_json = self.config_json()
        resources = [config_json['resources']]
        self.__stub(resources, stub_type='resource')

    def __stub(self, stub_objects, stub_type='workspace'):
        """
        Creates stubs for each stub object.

        Stub objects are of the format
        {
           'name': 'name',
           'path': 'path'
        }

        :param type: How to refer to stub objects. Used mainly for formatting.
        :param stub_object: See above.
        :return: None
        """

        for index, stub_object in enumerate(stub_objects):
            if 'name' in stub_object:
                name = stub_object['name']
            else:
                self._warn('Name missing in {} {} : {}'.format(stub_type, index, stub_object))
                continue
            if 'path' in stub_object:
                path = stub_object['path']
            else:
                self._warn('Path missing in {} {} : {}'.format(stub_type, index, stub_object))
                continue

            stub_path = self.base.joinpath(name)
            if stub_path.exists():
                try:
                    stub_path.rmdir()  # Attempt to remove. If empty, no exception thrown.
                except OSError:
                    self._warn('{} already exists and is non-empty {} : {}'.format(stub_type, index, stub_object))
                    continue
            copied = False
            if path != '':
                source_path = pathlib.Path(path)
                if not source_path.exists():
                    self._warn('Path for {} {} must exist : {}'.format(stub_type, index, stub_object))
                elif source_path.is_file():
                    self._warn('Path for {} {} must point to directories : {}'.format(stub_type, index, stub_object))
                elif source_path.is_dir():
                    self._verbose(
                        'Copying {} to {}'.format(source_path.as_posix(), stub_path.as_posix()))
                    shutil.copytree(source_path.as_posix(), stub_path.as_posix())
                    self._verbose(
                        'Copied {} to {}'.format(source_path.as_posix(), stub_path.as_posix()))
                    copied = True
                else:
                    self._warn('Unable to detect path {} in {} {} : {}'.format(source_path.as_posix(), stub_type, index,
                                                                               stub_object))

            if not copied:
                self._verbose('Stubbing {} {} : {} {}'.format(stub_type, index, stub_object, PENCIL))
                stub_path.mkdir(parents=False, exist_ok=True)

            self._success('Stubbed {} {} : {}'.format(stub_type, index, stub_object))
