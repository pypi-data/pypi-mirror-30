# -*- coding: utf-8 -*-
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import json
import logging
import os

from six import iteritems

from ..exceptions import ColinConfigException
from ..constant import CONFIG_DIRECTORY, JSON
from ..loader import load_check_implementation
from ..target import is_compatible

logger = logging.getLogger(__name__)


class Config(object):

    def __init__(self, config_name=None, config_file=None):
        """
        Load config for colin.

        :param config_name: str (name of the config file (without .json), default is "default"
        :param config_file: fileobj
        """
        if config_file:
            try:
                logger.debug("Loading configuration from file '{}'.".format(config_file.name))
                self.config_dict = json.load(config_file)
            except Exception as ex:
                msg = "Config file '{}' cannot be loaded.".format(config_file.name)
                logger.error(msg)
                raise ColinConfigException(msg)
        else:
            try:
                logger.debug("Loading configuration with the name '{}'.".format(config_name))
                config_path = config_file or get_config_file(config=config_name)
                with open(config_path, mode='r') as config_file_obj:
                    self.config_dict = json.load(config_file_obj)
            except ColinConfigException as ex:
                raise ex
            except Exception as ex:
                file_name = config_path if config_path else config_name
                msg = "Configuration '{}' cannot be loaded.".format(file_name)

                logger.error(msg)
                raise ColinConfigException(msg)

    def get_checks(self, target_type, group=None, severity=None, tags=None):
        """
        Get all checks for given type/group/severity/tags.

        :param target_type: TargetType enum
        :param group: str (if not group, get checks from all groups/directories)
        :param severity: str (optional x required)
        :param tags: list of str
        :return: list of check instances
        """
        check_files = self._get_check_files(group=group,
                                            severity=severity)
        groups = {}
        for (group, check_files) in iteritems(check_files):
            checks = []
            for severity, check_file in check_files:

                check_classes = load_check_implementation(path=check_file, severity=severity)
                for check_class in check_classes:
                    if is_compatible(target_type, check_class, severity, tags):
                        checks.append(check_class)

            groups[group] = checks
        return groups

    @staticmethod
    def get_check_file(group, name):
        """
        Get the check file from given group with given name.

        :param group: str
        :param name: str
        :return: str (path)
        """
        return os.path.join(get_checks_path(), group, name + ".py")

    @staticmethod
    def get_check_files(group, names, severity):
        """
        Get the check files from given group with given names.

        :param severity: str
        :param group: str
        :param names: list of str
        :return: list of str (paths)
        """
        check_files = []
        for f in names:
            check_file = Config.get_check_file(group=group,
                                               name=f)
            check_files.append((severity, check_file))
        return check_files

    def _get_check_groups(self, group=None):
        """
        Get check group to validate

        :param group: str (if None, all from the config will be used)
        :return: list of str (group names)
        """
        groups = [g for g in self.config_dict]
        if group:
            if group in groups:
                check_groups = [group]
            else:
                check_groups = []
        else:
            check_groups = groups
        logger.debug("Found groups: {}.".format(check_groups))
        return check_groups

    def _get_check_files(self, group=None, severity=None):
        """
        Get file names with checks filtered by group and severity.

        :param group: str (if None, all groups will be used)
        :param severity: str (if None, all severities will be used)
        :return: list of str (absolute paths)
        """
        groups = {}
        for g in self._get_check_groups(group):
            logger.debug("Getting checks for group '{}'.".format(g))
            check_files = []
            for sev, files in iteritems(self.config_dict[g]):
                if (not severity) or severity == sev:
                    check_files += Config.get_check_files(group=g,
                                                          names=files,
                                                          severity=sev)
            groups[g] = check_files
        return groups


def get_checks_path():
    """
    Get path to checks.

    :return: str (absolute path of directory with checks)
    """
    rel_path = os.path.join(os.pardir, os.pardir, os.pardir, "checks")
    return os.path.abspath(os.path.join(__file__, rel_path))


def get_config_file(config=None):
    """
    Get the config file from name

    :param config: str
    :return: str
    """
    config = config or "default"

    config_directory = get_config_directory()
    config_file = os.path.join(config_directory, config + JSON)

    if os.path.exists(config_file) and os.path.isfile(config_file):
        logger.debug("Configuration file '{}' found.".format(config_file))
        return config_file

    logger.warning("Configuration with the name '{}' cannot be found at '{}'."
                   .format(config, config_file))
    raise ColinConfigException("Configuration with the name '{}' cannot be found.".format(config))


def get_config_directory():
    """
    Get the directory with config files
    First directory to check:  $HOME/.local/share/colin/config
    Second directory to check: /usr/local/share/colin/config
    :return: str
    """

    local_share = os.path.join(os.path.expanduser("~"),
                               ".local",
                               CONFIG_DIRECTORY)
    if os.path.isdir(local_share) and os.path.exists(local_share):
        logger.debug("Local configuration directory found ('{}').".format(local_share))
        return local_share

    usr_local_share = os.path.join("/usr/local", CONFIG_DIRECTORY)
    if os.path.isdir(usr_local_share) and os.path.exists(usr_local_share):
        logger.debug("Global configuration directory found ('{}').".format(usr_local_share))
        return usr_local_share

    msg = "Config directory cannot be found."
    logger.warning(msg)
    raise ColinConfigException(msg)
