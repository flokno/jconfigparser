""" Settings class for holding settings, based on configparser.ConfigParser """
import configparser
import json
import time
from typing import Sequence

from .dict import BASE_DICT, DotDict

DEFAULT_SETTINGS_FILE = "settings.jconf"

# Key separators
key_separator = "."
aux_key_separators = ["_", ":"]
DotDict.key_separator = key_separator


class DictList(list):
    """list used to store multiple keys for a dictionary"""


class MultiOrderedDict(BASE_DICT):
    """A dict that can store multiple values for a key"""

    key_separator = key_separator

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


class ConfigDict(DotDict):
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

        config = ConfigParser(dict_type=dict_type)
        config.read(filenames)

        # create dictionary
        for sec in config.sections():
            dot_sec = sec
            for sep in aux_key_separators:
                dot_sec = dot_sec.replace(sep, key_separator)

            self[dot_sec] = DotDict()
            for key in config[sec]:
                self[dot_sec][key] = config.getval(sec, key)

    def __str__(self):
        """ for printing the object """
        return self.get_string()

    def print(self, only_settings=False):
        """ literally print(self) """
        print(self.get_string(only_settings=only_settings), flush=True)

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
                elif issubclass(elem.__class__, DotDict):
                    string += f"\n[{sec}{key_separator}{key}]\n"
                    for k, v in elem.items():
                        string += "{:{}s} {}\n".format(f"{k}:", width, v)

                else:
                    string += "{:{}s} {}\n".format(f"{key}:", width, elem)
        return string
