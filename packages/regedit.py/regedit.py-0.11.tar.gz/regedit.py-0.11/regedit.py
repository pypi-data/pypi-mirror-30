"""
regedit.py
Copyright (C) 2018  James Patrick Dill
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import winreg
import re


def expand(dong):
    """Expands environment variable placeholders, such as `%appdata%`"""

    return winreg.ExpandEnvironmentStrings(dong)


def guess_type(value):
    """Guesses registry type based on a value"""

    if isinstance(value, bytes):
        return winreg.REG_BINARY

    elif isinstance(value, str):
        if re.search("%.+%", value):  # REG_EXPAND_SZ contains expandable environment variable palceholders
            return winreg.REG_EXPAND_SZ
        else:
            return winreg.REG_SZ

    elif isinstance(value, int):
        if value.bit_length() > 32:
            return winreg.REG_QWORD  # QWORD = 64 bits
        else:
            return winreg.REG_DWORD  # DWORD = 32 bits


def name_from_path(path):
    """
    Gets the name of a key from its path
    """
    path = path.replace("/", "\\")

    if path[-1] == "\\":
        path = path[:-1]

    return path.split("\\")[-1]


# dummy class
class Key(object):
    """
    Use this to specify that you are creating a subkey. For example:

        registry["h"] = Key()

    """
    pass


class Registry:
    """
    Used to connect to the registry.

    :param key: Initial key to open. Must be one of winreg's `HKEY_*` constants.
    :param str computer: (Optional) Name of the computer to connect to, in the format r"\\computer_name"
    :param permissions: (Optional) Permissions to connect to registry with. Must be one of winreg's `KEY_*` constants.
    """

    def __new__(cls, key=winreg.HKEY_LOCAL_MACHINE, *, computer=None, access=winreg.KEY_READ | winreg.KEY_WRITE):
        handle = winreg.ConnectRegistry(computer, key)

        return RegistryKey(handle=handle, access=access)


class RegistryKey(object):
    """
    Represents a key in the registry. This class should not be created explicitly, but through :class:`Registry`
    """

    def __init__(self, *, handle, access, name=None):
        self.handle = handle
        self.access = access

        self.name = name  # name isn't always available

    def __repr__(self):
        return "<RegistryKey name={!r}>".format(self.name)

    @property
    def value(self):
        return winreg.QueryValue(self.handle, None)  # return unnamed value

    @value.setter
    def value(self, value):
        inferred_type = guess_type(value)

        winreg.SetValue(self.handle, None, inferred_type, value)

    def __getitem__(self, item):
        """
        Returns a subkey or value to the key.
        This function will first assume that a subkey is being looked for, then query for a value if a key is not found.
        """

        try:
            handle = winreg.OpenKey(self.handle, item, access=self.access)

            return RegistryKey(handle=handle, access=self.access, name=name_from_path(item))

        except (FileNotFoundError, TypeError):  # if no key is found, assume that a value is being requested

            try:
                return winreg.QueryValueEx(self.handle, item)[0]  # return only value. type can be inferred

            except (FileNotFoundError, TypeError):
                raise FileNotFoundError("no key or value found with name {!r}".format(item))

    def __setitem__(self, item, value):
        """
        If the value passed is a :class:`Key`, this will create a new subkey. Otherwise, this will set a value of the
        currently opened key.
        """

        if isinstance(value, Key) or value is Key:  # Key() was passed, create new key
            winreg.CreateKey(self.handle, item)

        else:
            inferred_type = guess_type(value)

            winreg.SetValueEx(self.handle, item, 0, inferred_type, value)

    def subkeys(self):
        """
        Generator yielding the key's subkeys. To retrieve every subkey in a list, use list(RegistryKey) instead.
        """
        i = 0
        try:
            while True:
                yield self[winreg.EnumKey(self.handle, i)]  # open the key while iterating

                i += 1
        except WindowsError:  # all keys have been enumerated
            return

    def __iter__(self):
        """
        Returns an iterator containing every subkey of the opened key.
        """
        return iter([key for key in self.subkeys()])  # flattens generator

    def values(self, prefix=""):
        """
        Returns dict with the key's values.

        :param str prefix: (Optional)
        """
        d = {}

        i = 0
        try:
            while True:
                value = winreg.EnumValue(self.handle, i)[:2]  # only retrieve name and value. type can be inferred

                if value[0].startswith(prefix):
                    d[value[0]] = value[1]

                i += 1
        except WindowsError:  # all values have been enumerated
            return d
