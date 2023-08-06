import argparse
import collections
import configparser
import json
import os
import sys
import traceback
import yaml

from confmerge import __version__
from io import StringIO


class ConfigFile(object):
    """ Base class for configuration files.

    Args:
        path (str): Path of the configuration file.

    """

    def __init__(self, path):
        self.path = path

    def read(self):
        """ Reads the file content.

        Returns:
            dict: The file content as a dict.

        """
        if not os.path.exists(self.path):
            raise IOError("File does not exist: " + self.path)
        if not os.path.isfile(self.path):
            raise IOError("Not a file: " + self.path)

    def write(self, content, mode='644', force=False, dry_run=False):
        """ Writes the content (dict) into the configuration file.

        Args:
            content (dict): The content to write.
            mode (dict): File mode for the resulting file.
            force (dict): Force overwriting of an existing file.
            dry_run (dict): Print result instead of writing it into the file.

        """
        raise NotImplementedError()

    def _finalize_write(self, mode=None, dry_run=False):
        """ Finalizes the write to the output stream.

        Args:
            mode (dict): File mode for the resulting file.
            dry_run (dict): Print result instead of writing it into the file.

        """
        if not dry_run:
            self._close_stream()
            if mode:
                if os.stat(self.path).st_uid == 0 or \
                        os.stat(self.path).st_uid == os.getuid():
                    os.chmod(self.path, int(mode, 8))
                else:
                    print("Cannot set file mode!")
        else:
            print(self.stream.getvalue())
            self._close_stream()

    def _open_stream(self, force, dry_run):
        """ Opens a stream for writing the configuration file.

        Args:
            force (dict): Force overwriting of an existing file.
            dry_run (dict): Print result instead of writing it into the file.

        """
        if dry_run:
            self.stream = StringIO()
        else:
            if os.path.exists(self.path):
                if not os.path.isfile(self.path):
                    raise IOError("Destination is not a file: " + self.path)
                if not force:
                    raise IOError("Destination file exists: " + self.path)

            self.stream = open(self.path, 'w')

    def _close_stream(self):
        self.stream.close()


class IniFile(ConfigFile):
    """ Represents an INI file.

    Args:
        path (str): Path of the configuration file.

    """

    def __init__(self, path):
        super().__init__(path)

    def read(self):
        super().read()
        f = configparser.ConfigParser()
        try:
            f.read(self.path)
        except Exception as e:
            raise yaml.parser.ParserError(
                "Failed to parse INI file: {0}\n\n{1}".format(self.path, e.message))
        return f._sections

    def write(self, content, mode=None, force=False, dry_run=False):
        config = configparser.ConfigParser()
        for section in content:
            config.add_section(section)
            section_data = content[section]
            section_data_keys = section_data.keys()
            for key in section_data_keys:
                config.set(section, key, section_data[key])

        self._open_stream(force, dry_run)
        config.write(self.stream)
        self._finalize_write(mode, dry_run)


class JsonFile(ConfigFile):
    """ Represents an JSON file.

    Args:
        path (str): Path of the configuration file.

    """

    def __init__(self, path):
        super().__init__(path)

    def read(self):
        super().read()
        with open(self.path, 'r') as f:
            file_content = f.read()
        try:
            return json.loads(file_content) or dict()
        except Exception as e:
            raise yaml.parser.ParserError(
                "Failed to parse JSON file: {0}\n\n{1}".format(self.path, str(e)))

    def write(self, content, mode=None, force=False, dry_run=False):
        self._open_stream(force, dry_run)
        self.stream.write(json.dumps(content, indent=2))
        self._finalize_write(mode, dry_run)


class YamlFile(ConfigFile):
    """ Represents an YAML file.

    Args:
        path (str): Path of the configuration file.

    """

    def __init__(self, path):
        super().__init__(path)

    def read(self):
        super().read()
        with open(self.path, 'r') as f:
            file_content = f.read()
        try:
            return yaml.load(file_content) or dict()
        except Exception as e:
            raise yaml.parser.ParserError(
                "Failed to parse YAML file: {0}\n\n{1}".format(self.path, str(e)))

    def write(self, content, mode=None, force=False, dry_run=False):
        self._open_stream(force, dry_run)
        self.stream.write(yaml.dump(content, default_flow_style=False))
        self._finalize_write(mode, dry_run)


class ConfMerge(object):
    """ Merge multiple configuration files into one.

    Args:
        sources (list): The source files.
        dest (str): The destination file.
        file_type (list): File mode for newly merged file.
        mode (str): File mode for the resulting file.
        force (boolean): Force overwriting of an existing file.
        dry_run (boolean): Print the resulting merged content but don't write it into the destination file.

    """

    def __init__(self, sources, dest, file_type=None, mode=None, force=False, dry_run=False):
        self.sources = sources
        self.dest = dest
        self.file_type = file_type
        self.mode = mode
        self.force = force
        self.dry_run = dry_run

        if not sources:
            raise ValueError("No sources specified")
        if not dest:
            raise ValueError("No destination specified")

        # merge configurations
        merged_content = None
        for src in sources:
            f = self._get_file(src, file_type)
            merged_content = self._simple_dict(
                self._merge_dicts(
                    merged_content,
                    f.read()))

        # write new configuration file
        f = self._get_file(dest, file_type)
        f.write(merged_content, mode, force, dry_run)

    def _get_file(self, path, file_type=None):
        """ Get configuration file object from path.

        Args:
            path (str): The path of the config file.
            file_type (str): Type of the config file.

        Returns:
            ConfigFile: The config file object.

        """
        ext = path.split('.')[-1]
        if not file_type:
            if ext == 'json':
                file_type = 'json'
            elif ext == 'ini':
                file_type = 'ini'
            elif ext in ['yaml', 'yml']:
                file_type = 'yaml'

        if file_type == 'ini':
            return IniFile(path)
        elif file_type == 'json':
            return JsonFile(path)
        elif file_type == 'yaml':
            return YamlFile(path)
        else:
            raise ValueError("Unknown file type: " + str(file_type or ext))

    def _merge_dicts(self, x, y):
        """ Recursively merges two dicts.

        When keys exist in both the value of 'y' is used.

        Args:
            x (dict): First dict
            y (dict): Second dict

        Returns:
            dict: Merged dict containing values of x and y

        """
        if x is None and y is None:
            return dict()
        if x is None:
            return y
        if y is None:
            return x

        merged = dict(x, **y)
        xkeys = x.keys()

        for key in xkeys:
            if (type(x[key]) is dict or type(x[key]) is collections.OrderedDict) and key in y:
                merged[key] = self._merge_dicts(x[key], y[key])
        return merged

    def _simple_dict(self, d):
        """ Converts an OrderedDict into a plain dict.

        Args:
            d (dict): The OrderedDict.

        Returns:
            dict: Plain dict

        """
        for key in d:
            if type(d[key]) is collections.OrderedDict:
                d[key] = dict(d[key])
            if type(d[key]) is dict:
                d[key] = self._simple_dict(d[key])
        return d


def cli():
    """ CLI entry point """
    # parsing arguments
    parser = argparse.ArgumentParser(
        description="Merge multiple configuration files into one file", add_help=False)
    parser.add_argument('-d', '--dry-run', dest='dry_run', action='store_true', default=False,
                        help="Print the merged content on stdout instead of writing it to the destination file")
    parser.add_argument('-f', '--force', dest='force',  action='store_true',
                        default=False, help="Force overwriting of any existing destination file")
    parser.add_argument("-h", "--help", action="help",
                        help="Show this help message and exit")
    parser.add_argument('-m', '--mode', dest='mode',
                        help="File mode for newly created files")
    parser.add_argument('-t', '--type', dest='file_type',
                        help="Type of file can be one of 'ini', 'json' or 'yaml'. If not specified the type will be guessed from the file extension")
    parser.add_argument('--debug', dest='debug', action='store_true',
                        default=False, help="Print debug trace on error")
    parser.add_argument('--version', action='version', version='ConfMerge {0}'.format(
        __version__), help="Print the program version and exit")
    parser.add_argument('src', nargs='+', help="The source files")
    parser.add_argument('dest', nargs=1, help="The destination file")
    args = parser.parse_args(sys.argv[1:])

    sources = [os.path.abspath(p) for p in args.src]
    dest = os.path.abspath(args.dest[0])

    # execute main logic
    try:
        ConfMerge(
            sources=sources,
            dest=dest,
            file_type=args.file_type,
            mode=args.mode,
            force=args.force,
            dry_run=args.dry_run)
        exit(0)
    except Exception as e:
        if args.debug:
            print(traceback.format_exc())
        else:
            print(str(e))
        exit(1)
