""" Class for work with JSON config files. """

from collections import OrderedDict
import os
import shutil
import pkg_resources
import json

class Config:
    """ Work with config files: create desired file if it not exists, read and save settings. """
    def __init__(self, desired_location, resource_file, package):
        """
        Initiailzation.

        Parameters
        ----------
        desired_location : str
            Name of default file. Full path, may incude '~'. For example: '~/config.json'
        resource_file : str
            Package resource file name.
        package : str
            Name of the package.

        """
        self.set_desired_location(desired_location)
        self.resource_file = resource_file
        self.fname = None
        self.package = package
        self.settings = OrderedDict([])
        self._version = None

    def set_desired_location(self, fname):
        """ Set the desired config file location. """
        abspath = os.path.expanduser(fname)
        self.desired_location = abspath

    def use_another_file(self, fname):
        self.save_settings()
        self.open(fname)
        try:
            self.read_settings()
            return True
        except Exception:
            return False

    def open(self, fname):
        self.fname = fname

    def open_or_create(self):
        """ Open or create default config file. """
        if not os.path.exists(self.desired_location):
            self._copy_resource_file()
        self.open(self.desired_location)
        return True

    def read_settings(self):
        """ Read settings from file. Settings then can be achieved from 'settings' (OrderedDict) field. """
        with open(self.fname) as f:
            json_str = f.read() 
        settings = json.loads(json_str, object_pairs_hook=OrderedDict)
           
        if not self.is_version_valid(settings):
            self.upgrade()
            with open(self.fname) as f:
                json_str = f.read()
            settings = json.loads(json_str, object_pairs_hook=OrderedDict)

        self.settings = settings
        
        return True

    def save_settings(self):
        """ Save settings to config file. For example, can be used on
        exit program event. """
        json_str = json.dumps(self.settings, indent=4)
        with open(self.fname, "w") as f:
            f.write(json_str)
        return True

    def is_version_valid(self, settings):
        """ Check if version of configuration is more or equal to
        minimal. """
        if self.version is None:
            return True
        if 'version' not in settings.keys() and self.version is None:
            return True
        if 'version' not in settings.keys() and self.version is not None:
            return False
        if 'version' in settings.keys() and self.version is not None:
            if settings['version'] != self.version:
                return False
            else:
                return True
        return True

    def upgrade(self):
        """ Replace config file which have unsupported version newer
        file. """
        self._backup()
        self._copy_resource_file()
        self.open(self.desired_location)
        
    def _copy_resource_file(self):
        filename = pkg_resources.resource_filename(self.package, self.resource_file)
        shutil.copy(filename, self.desired_location)

    def _backup(self):
        shutil.copy(self.fname, self.desired_location + ".bak")

    def get_version(self):
        """ Return version. """
        return self._version
    def set_version(self, version):
        """ Set version. """
        self._version = version
    version = property(get_version, set_version, doc="The supported version.")
