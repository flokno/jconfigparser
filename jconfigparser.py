""" Settings class for holding settings, based on configparser.ConfigParser """
import collections
import configparser
import json
import sys
import time
from typing import Sequence

DEFAULT_SETTINGS_FILE = "settings.jconf"

if sys.version_info >= (3, 7):
    BASE_DICT = dict
else:
    BASE_DICT = collections.OrderedDict


class DictList(list):
    """list used to store multiple keys for a dictionary"""


class MultiOrderedDict(BASE_DICT):
    """A dict that can store multiple values for a key"""

    def __setitem__(self, key, value):
        if isinstance(value, list) and key in self:
            pre_value = self.get(key)
            self.update({key: DictList(pre_value + value)})
        else:
            super().__setitem__(key, value)


class ConfigParser(configparser.ConfigParser):
    """ConfigParser that uses JSON to parse the values instead returning stings"""

    def __init__(self, *args, dict_type=BASE_DICT, **kwargs):
        super().__init__(
            *args,
            dict_type=dict_type,
            interpolation=configparser.ExtendedInterpolation(),
            strict=False,
            **kwargs,
        )

    def getval(self, *args, **kwargs):
        """ Redifine getval() to allow for json formated values (not only string) """
        option = self.get(*args, **kwargs)

        try:
            result = json.loads(option)
        except json.JSONDecodeError:
            try:
                result = self.getboolean(*args, **kwargs)
            except ValueError:
                result = option

        if isinstance(result, str) and "\n" in result:
            result = DictList(result.split("\n"))

        return result


class ConfigDict(BASE_DICT):
    """Dictionary that holds the configuration settings"""

    def __init__(
        self,
        filenames: Sequence[str] = None,
        dct: dict = None,
        allow_multiple_options: bool = False,
        **kwargs,
    ):
        """Initialize ConfigDict

        Args:
            filenames: A list of configure files to read in
            dct: a dictionary
            allow_multiple_options: convert multiple options into list
        """
        super().__init__(**kwargs)

        # make sure `filenames` is a list
        if isinstance(filenames, str):
            filenames = [filenames]

        if allow_multiple_options:
            dict_type = MultiOrderedDict
        else:
            dict_type = BASE_DICT

        self.config = ConfigParser(dict_type=dict_type)
        self.config.read(filenames)

        config = self.config

        # create dictionary
        for sec in config.sections():
            sub_d = {}

            self[sec] = dict_type()
            for key in config[sec]:
                self[sec][key] = config.getval(sec, key)

            # check for nested section
            dot_sec = sec.replace("_", ".")
            if "." in dot_sec:
                sub_sec, sub_opt = dot_sec.split(".")
                sub_d = {sub_opt: {k: config.getval(sec, k) for k in config[sec]}}
                del self[sec]
                self[sub_sec].update(sub_d)

    def __str__(self):
        """ for printing the object """
        return self.get_string()

    def print(self, only_settings=False):
        """ literally print(self) """
        print(self.get_string(only_settings=only_settings), flush=True)

    def write_raw(self, filename: str = DEFAULT_SETTINGS_FILE):
        """write input file as parsed"""
        self.config.write(open(filename, "w"))

    def write(self, filename: str = DEFAULT_SETTINGS_FILE):
        """write a settings object human readable

        Args:
            filename: path use to write the file
        """
        with open(filename, "w") as f:
            timestr = time.strftime("%Y/%m/%d %H:%M:%S")
            f.write(f"# configfile written at {timestr}\n")
            f.write(self.get_string())

    def get_string(self, width: int = 30, ignore_sections: Sequence[str] = None) -> str:
        """ return string representation for writing etc.

        Args:
            width: The width of the string column to print
            ignore_section: ignore these sections

        Returns:
            string: The string representation of the ConfigDict
        """
        if ignore_sections is None:
            ignore_sections = []

        string = ""
        for sec in self:
            # Filter out the private attributes
            if sec.startswith("_") or sec in ignore_sections:
                continue

            string += f"\n[{sec}]\n"
            for key in self[sec]:
                elem = self[sec][key]
                if "numpy.ndarray" in str(type(elem)):

                    elem = elem.tolist()
                #
                if elem is None:
                    elem = "null"
                #
                if key == "verbose":
                    continue
                # write out `MultiDict` keys one by one for readability
                if isinstance(elem, DictList):
                    for elem in self[sec][key]:
                        string += "{:{}s} {}\n".format(f"{key}:", width, elem)
                # parse out dotted values
                elif issubclass(elem.__class__, BASE_DICT):
                    string += f"\n[{sec}.{key}]\n"
                    for k, v in elem.items():
                        string += "{:{}s} {}\n".format(f"{k}:", width, v)

                else:
                    string += "{:{}s} {}\n".format(f"{key}:", width, elem)
        return string
