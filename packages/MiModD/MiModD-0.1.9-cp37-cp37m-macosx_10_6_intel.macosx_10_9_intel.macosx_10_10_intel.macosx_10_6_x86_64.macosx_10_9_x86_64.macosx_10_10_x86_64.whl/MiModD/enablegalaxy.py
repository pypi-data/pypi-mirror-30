import os.path
import re

# make sure this is run from inside the package
from . import config as mimodd_settings
from . import ArgumentParseError


class GalaxyConfigSetting(object):
    """Represent a parameter/value pair obtained from a Galaxy config file.

    The class gives access to the parsed setting through its key and value
    properties, but when turned back into a string returns the config line
    in the exact original format.
    """

    def __init__(self, config_line, line_pattern, context=None):
        """Return a new setting from a line as read from a config file.

        line_pattern should be a compiled regex that allows parsing of the
        config line and must contain named groups "key" and "value" that
        give access to the matched parameter/value pair on the line.
        """
        m = line_pattern.match(config_line)
        if m:
            self._components = list(m.groups())
            try:
                self._key_index = line_pattern.groupindex['key'] - 1
                self._value_index = line_pattern.groupindex['value'] - 1
            except KeyError:
                raise ValueError(
                    'The regular expression used as the line pattern must '
                    'define a "key" and a "value" group.'
                    )
        else:
            self._components = list(config_line)
            self._key_index = None
            self._value_index = None
        if context is None:
            self.context = []
        else:
            self.context = context

    @property
    def key(self):
        if self._key_index is not None:
            return self._components[self._key_index]

    @key.setter
    def key(self, new_key):
        if self._key_index is not None:
            self._components[self._key_index] = new_key

    @property
    def value(self):
        if self._value_index is not None:
            v = self._components[self._value_index]
            if v[0] in ("'", '"') and v[0] == v[-1]:
                return v[1:-1]
            else:
                return v

    @value.setter
    def value(self, new_value):
        if self._value_index is not None:
            self._components[self._value_index] = new_value

    def __str__(self):
        return ''.join(self._components)


class GalaxyConfigParser(object):
    """Abstract base class for Galaxy config parsers."""

    def __init__(self, config_file):
        """Instantiate a parser from the contents of a config file."""

        with open(config_file, 'r', encoding='utf-8') as config_in:
            self.config_data = config_in.readlines()
        self.config_file = config_file

    def writeout(self, config_file):
        """Write the stored config back to the indicated file."""

        with open(config_file, 'w', encoding='utf-8') as config_out:
            config_out.writelines(self.config_data)

    def update_setting(self, setting, new_value):
        """Change the value of a configuration setting."""

        search_item = setting.context
        search_item.append(setting.key)
        setting, line_no = self.get_setting(search_item)
        setting.value = new_value
        self.config_data[line_no] = str(setting)

    def get_setting(self, token):
        """Return a Galaxy config setting by parameter name.

        Subclasses need to implement this.
        """
        raise NotImplementedError


class GalaxyConfigINIParser(GalaxyConfigParser):
    """Parser for an old-style (before 18.01) ini-style Galaxy config file."""

    def __init__(self, config_file):
        """Get a new parser for the indicated config file."""
        super().__init__(config_file)
        # regex for parsing an uncommented paramter/value line from the
        # config file
        self.line_pattern = re.compile(
            # The parameter name must be the first thing on the line and
            # gets stored in the "key" group. The value gets extracted into
            # a named "value" group and needs to be assigned using "=" with
            # or without surrounding whitespace. Terminal comments and/or
            # whitespace gets matched and stored in an unnamed group to
            # enable reconstituion of the original line on demand.
            r'^(?P<key>\S+?)(\s*=\s*)(?P<value>.+?)((?:\s+#.+?)?\s*)$'
            )

    def get_setting(self, token):
        """Find the indicated config parameter and return its setting.

        Returns a tuple of the setting, preparsed as a GalaxyConfigSetting,
        and the config file line number that the setting was found on, or
        (None, -1) if no matching setting can be found.
        """

        # no sections in ini-style configs -> ignore section info if present
        token = token[-1]
        for line_no, line in enumerate(self.config_data):
            if line.strip().startswith(token):
                setting = GalaxyConfigSetting(line, self.line_pattern)
                if setting.key == token:
                    return setting, line_no
        return None, -1


class GalaxyConfigYAMLParser(GalaxyConfigParser):
    """Parser for a new-style (>= 18.01) Yaml-based Galaxy config file."""

    def __init__(self, config_file):
        """Get a new parser for the indicated config file."""

        super().__init__(config_file)
        self.section_pattern = re.compile(
            r'^(?P<indent>\s*)(?P<section>\S+?)(:)((?:\s+#.+?)?\s*)$'
            )
        # regex for parsing an uncommented paramter/value line from the
        # config file
        self.line_pattern = re.compile(
            # Matches lines with parameter: value pairs. The line is allowed
            # to be indented and the indentation itself, just like terminal
            # comments and/or whitespace will be matched and made accessible
            # for reconstituion of the original line.
            # The colon separator has to be followed, but is not allowed to
            # be preceeded by a space.
            r'^(\s*)(?P<key>\S+?)(: )(?P<value>.+?)((?:\s+#.+?)?\s*)$'
            )

    def get_setting(self, token):
        """Find the indicated config parameter and return its setting.

        The parameter name must be passed as an iterable of (possibly nested)
        section names and the actual parameter as the last element, and the
        parameter will only be matched if it occurs inside the specified
        section/subsection.

        Returns a tuple of the setting, preparsed as a GalaxyConfigSetting,
        and the config file line number that the setting was found on, or
        (None, -1) if no matching setting can be found.
        """
        containing_sections = list(token[:-1])
        search_key = token[-1]
        current_level = level = 0
        config_tokens = []
        indents = []
        for line_no, line in enumerate(self.config_data):
            m = self.section_pattern.match(line)
            if m:
                for level, indent in enumerate(indents):
                    if m.group('indent') <= indent:
                        current_level = level
                        config_tokens[current_level:] = [m.group('section')]
                        break
                else:
                    current_level = level + 1
                    indents.append(m.group('indent'))
                    config_tokens.append(m.group('section'))
            elif (config_tokens == containing_sections) and (
              line.strip().startswith(search_key)):
                setting = GalaxyConfigSetting(
                    line,
                    self.line_pattern,
                    containing_sections)
                if setting.key == search_key:
                    return setting, line_no
        return None, -1

    def update_setting(self, setting, new_value):
        super().update_setting(setting, repr(new_value))


class GalaxyAccessError(Exception):
    pass


class GalaxyINIParseError(GalaxyAccessError):
    pass


class GalaxyYAMLParseError(GalaxyAccessError):
    pass


class GalaxyAccess(object):
    """Provide access to various configuration-related elements in Galaxy."""

    CONFIG_FILE_GUESSES = [
        ('config/galaxy.yml', GalaxyConfigYAMLParser),
        ('config/galaxy.ini', GalaxyConfigINIParser),
        ('universe_wsgi.ini', GalaxyConfigINIParser)
        ]
    TOOL_CONFIG_FILE_REF = ('galaxy', 'tool_config_file')
    TOOL_DEP_DIR_REF = ('galaxy', 'tool_dependency_dir')
    TOOL_DEP_DIR_GUESS = 'database/dependencies'
    pkg_galaxy_data_path = os.path.join(
        os.path.dirname(mimodd_settings.__file__),
        'galaxy_data')
    tool_conf_file = os.path.join(
        pkg_galaxy_data_path, 'mimodd_tool_conf.xml'
        )

    @classmethod
    def set_toolbox_path(cls):
        """Update the mimodd_tool_conf.xml file installed as part of the
        package with an absolute tool_path to the package xml wrappers."""

        with open(cls.tool_conf_file, 'r', encoding='utf-8') as sample:
            template = sample.readlines()[1:]
        with open(cls.tool_conf_file, 'w', encoding='utf-8') as out:
            out.write('<toolbox tool_path="{0}">\n'
                      .format(cls.pkg_galaxy_data_path)
                      )
            out.writelines(template)

    @classmethod
    def get_config(cls, galaxy_dir):
        for location_guess, ConfigParser in cls.CONFIG_FILE_GUESSES:
            config_file = os.path.join(galaxy_dir, location_guess)
            if os.path.isfile(config_file):
                return ConfigParser(config_file)
        return None

    @staticmethod
    def _get_config_from_user_file(config_file, config_style=None):
        if config_style is None:
            if config_file.endswith('.ini'):
                ConfigParser = GalaxyConfigINIParser
            elif config_file.endswith('.yml') or config_file.endswith('.yaml'):
                ConfigParser = GalaxyConfigYAMLParser
            else:
                raise GalaxyAccessError(
                    'Failed to autodetermine the format of the specified '
                    'Galaxy configuration file {0}.\n'
                    'If this is really the configuration file you would '
                    'like to use, you will need to specify its file '
                    'format - yaml or ini - explicitly.'
                    .format(config_file)
                    )
        elif config_style == 'ini':
            ConfigParser = GalaxyConfigINIParser
        elif config_style == 'yaml':
            ConfigParser = GalaxyConfigYAMLParser
        else:
            raise ArgumentParseError(
                'Unknown configuration file format "{0}". '
                'Valid formats are "ini" and "yaml".'
                .format(config_style)
                )
        return ConfigParser(config_file)

    def __init__(self, galaxydir=None,
                  config_file=None, dependency_dir=None, config_style=None):
        if galaxydir is None:
            if config_file is None:
                raise ArgumentParseError(
                    'The location of either the Galaxy root directory '
                    'or of the Galaxy config file must be specified.'
                    )
            if not os.path.isabs(config_file):
                raise ArgumentParseError(
                    'Need a Galaxy root directory to base relative path to '
                    'config file on.'
                    )
            if dependency_dir and not os.path.isabs(dependency_dir):
                raise ArgumentParseError(
                    'Need a Galaxy root directory to base relative path to '
                    'tool dependency folder on.'
                    )
        elif not os.path.isdir(galaxydir):
            raise GalaxyAccessError(
                'Galaxy root path {0} does not specify a valid directory.'
                .format(galaxydir)
                )
        # TO DO: see if we can reliably determine the Galaxy root directory
        # from the specified config_file in at least some situations.
        # Currently, we just store the passed in value even if it is None.
        self.galaxy_dir = galaxydir

        # Get the path to the Galaxy configuration file and read its content.
        if config_file is None:
            self.config = self.get_config(self.galaxy_dir)
            if not self.config:
                raise GalaxyAccessError(
                    'Could not find any Galaxy configuration file in its '
                    'default location with Galaxy root path {0}.\n'
                    'Please correct the Galaxy root path or specify the '
                    'configuration file directly.'
                    .format(self.galaxy_dir)
                    )
        else:
            config_file = os.path.normpath(
                os.path.join(self.galaxy_dir or '', config_file)
                )
            if not os.path.isfile(config_file):
                raise GalaxyAccessError(
                    'Could not find the specified Galaxy configuration file '
                    '{0}.'
                    .format(config_file)
                    )
            self.config = self._get_config_from_user_file(
                config_file, config_style
                )

        # Get the path to the Galaxy tool dependency folder.
        if dependency_dir is None:
            self.tool_dependency_dir = self.get_tool_dependency_dir()
            if not self.tool_dependency_dir:
                raise GalaxyAccessError(
                    "Could not detect the location of Galaxy's tool "
                    'dependency directory with Galaxy root path {0}.\n'
                    'Please correct the Galaxy root path or specify the '
                    'tool dependency folder directly.'
                    .format(self.galaxy_dir)
                    )
        else:
            self.tool_dependency_dir = os.path.normpath(
                os.path.join(self.galaxy_dir or '', dependency_dir)
                )
            if not os.path.isdir(self.tool_dependency_dir):
                raise GalaxyAccessError(
                    'Could not find a Galaxy tool dependency directory at {0}.'
                    .format(self.tool_dependency_dir)
                    )

    def get_tool_dependency_dir(self):
        # If the Galaxy config file declares an existing folder as the
        # tool dependency directory, return the absolute path to that folder.
        # If the config file does not set a tool dependency directory
        # explicitly (as is the case if the setting is commented out), return
        # a guess of the default setting if that directory exists.
        # In any other case, return None.
        tool_dep_dir_setting, line_no = self.config.get_setting(
            self.TOOL_DEP_DIR_REF
            )
        if tool_dep_dir_setting is None:
            value = self.TOOL_DEP_DIR_GUESS
        else:
            value = tool_dep_dir_setting.value

        tool_dep_dir = os.path.normpath(os.path.join(self.galaxy_dir, value))
        if os.path.isdir(tool_dep_dir):
            return tool_dep_dir

    def get_tool_config_setting(self, tool_config_token=None):
        if tool_config_token is None:
            tool_config_token = self.TOOL_CONFIG_FILE_REF
        tool_config_setting, line_no = self.config.get_setting(
            tool_config_token
            )
        if line_no == -1:
            if type(self.config) is GalaxyConfigINIParser:
                raise GalaxyINIParseError(
                    'Galaxy configuration file {0} has no {1} setting. '
                    'Maybe the line "{1} = ..." has been commented out?'
                    .format(self.config.config_file, tool_config_token[-1])
                    )
            elif type(self.config) is GalaxyConfigYAMLParser:
                raise GalaxyYAMLParseError(
                    'Galaxy configuration file {0} has no {1} setting. '
                    'Maybe the line "{1}: ..." in the "{2}" section has been '
                    'commented out?'
                    .format(
                        self.config.config_file,
                        tool_config_token[-1],
                        '->'.join(tool_config_token[:-1])
                        )
                    )
            else:
                raise ValueError(
                    'Unknown parser type: {0}'.format(type(self.config))
                    )
        return tool_config_setting, line_no

    def add_to_galaxy(self, line_token=None, expose_samtools=True):
        """Register MiModD and its tool wrappers for Galaxy.

        Updates the Galaxy configuration file to include the MiModD
        tool_conf.xml as a tool_config_file and adds MiModD as a
        Galaxy-resolvable dependency package using an env.sh file.
        Also exposes MiModD's bundled samtools/bcftools as a Galaxy package if
        no such package is configured yet.
        """

        # Try to parse the tool_config_file setting from the pre-read
        # configuration file.
        tool_config_setting, line_no = self.get_tool_config_setting(line_token)
        conf_files = [
            file.strip() for file in tool_config_setting.value.split(',')
            ]

        # expose MiModD as a Galaxy package
        mimodd_dependency_folder = os.path.join(
            self.tool_dependency_dir, 'MiModD', 'externally_managed'
            )
        os.makedirs(mimodd_dependency_folder, exist_ok=True)
        with open(os.path.join(mimodd_dependency_folder, 'env.sh'), 'w') as env:
            env.write('# configure PATH to MiModD binaries\n')
            env.write('PATH="{0}:$PATH"\n'.format(mimodd_settings.bin_path))
            env.write('export PATH\n')

        if expose_samtools:
            # if this instance of Galaxy does not have a samtools Galaxy
            # package configured yet, expose MiModD's bundled version now.
            samtools_dependency_folder = os.path.join(
                self.tool_dependency_dir, 'samtools'
                )
            try:
                os.mkdir(samtools_dependency_folder)
            except FileExistsError:
                pass
            else:
                try:
                    os.symlink(
                        os.path.join('..', 'MiModD', 'externally_managed'),
                        os.path.join(samtools_dependency_folder, 'default'),
                        target_is_directory=True
                        )
                except FileExistsError:
                    # unlikely race condition that we want to ignore
                    pass

        if not self.tool_conf_file in conf_files:
            # Add the path to MiModD's tool_conf file to the corresponding
            # setting in the configuration file.
            self.config.update_setting(
                tool_config_setting,
                ','.join([tool_config_setting.value, self.tool_conf_file])
                )

            # ask for user backup before making changes to Galaxy config file
            print('We recommend to back up the Galaxy configuration file {0} '
                  'before proceeding!'
                  .format(self.config.config_file)
                  )
            confirm = input('Proceed (y/n)? ')
            if confirm != 'y' and confirm != 'Y':
                print('No changes made to Galaxy configuration file. Aborting.')
                return

            # write changes to config file
            try:
                self.config.writeout(self.config.config_file)
            except:
                raise GalaxyAccessError(
                    'We are very sorry, but an error has occurred while '
                    'making changes to the Galaxy configuration file {0}. '
                    'If you have made a backup of the file, you may want '
                    'to use it now.'
                    .format(self.config.config_file)
                    )

            print('Successfully updated the Galaxy configuration file {0} '
                  'to include the MiModD tools.'
                  .format(self.config.config_file)
                  )
            print()
        print('Your Galaxy instance is now set up for use of MiModD.')
        print('If Galaxy is currently running, you will have to restart it '
              'for changes to take effect.'
              )


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        usage=argparse.SUPPRESS,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='\nintegrate this installation of MiModD into '
                    'a local Galaxy.\n'
        )
    parser.add_argument(
        'galaxydir',
        metavar='GALAXY_PATH',
        help="the path to your local Galaxy's root directory (default: the "
             'current working directory);\n'
             'the specified path will serve as the basis for locating the '
             'Galaxy configuration file and the tool dependency folder, '
             'or as the base for relative paths provided through the '
             '--config-file or --dependency-dir options.'
        )
    parser.add_argument(
        '-c', '--config-file',
        metavar='CONFIG_FILE',
        default=argparse.SUPPRESS,
        help='skip autodetection of the Galaxy configuration file and use the '
             'indicated file instead; if CONFIG_FILE is a relative path, it '
             'will be interpreted relative to GALAXY_PATH.'
        )
    parser.add_argument(
        '-s', '--config-style',
        metavar='yaml|ini',
        default=argparse.SUPPRESS,
        help='assume the Galaxy configuration file specified through the '
             '--config-file option has the indicated format instead of trying '
             'to autodetermine it; this option will be ignored if not used in '
             'conjunction with --config-file.'
        )
    parser.add_argument(
        '-d', '--dependency-dir',
        metavar='TOOL_DEPENDENCY_DIR',
        default=argparse.SUPPRESS,
        help='do not try to locate the Galaxy tool dependency folder '
             'automatically, but use the indicated folder directly; '
             'if TOOL_DEPENDENCY_DIR is a relative path, it will be '
             'interpreted relative to GALAXY_PATH.'
        )
    parser.add_argument(
        '-t', '--tool-config-token',
        dest='line_token',
        default=argparse.SUPPRESS,
        help='add the path to the MiModD Galaxy tool wrappers to this variable '
             'in the configuration file (default: tool_config_file)'
        )
    parser.add_argument(
        '--without-samtools',
        dest='expose_samtools',
        action='store_false',
        help='do not try to expose the samtools/bcftools versions bundled with '
             'MiModD as a Galaxy package.'
        )

    args = vars(parser.parse_args())
    # Split up args for the GalaxyAccess instance and its add_to_galaxy method
    # and delegate all further work to them.
    if 'line_token' in args:
        args['line_token'] = args['line_token'].split(': ')
    GalaxyAccess(
        **{k: v for k, v in args.items()
           if k in [
               'galaxydir', 'config_file', 'config_style', 'dependency_dir'
               ]}
        ).add_to_galaxy(
            **{k: v for k, v in args.items()
               if k in ['line_token', 'expose_samtools']}
            )
