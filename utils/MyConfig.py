import configparser
import os
import threading
import traceback


class ConfigFile(object):
    _instance = None
    lock = threading.Lock()
    PATH = os.path.join(os.getcwd(), "config.ini")

    def __new__(cls, *args, **kwargs):
        if cls._instance:
            return cls._instance
        else:
            with cls.lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    return cls._instance
                return cls._instance

    def __init__(self, path=PATH, encoding="utf-8"):
        self.path = path
        if not os.path.exists(self.path):
            with open(self.path, 'w') as file:
                pass
        try:
            self.ConfigFile = configparser.RawConfigParser(allow_no_value=True)
            self.ConfigFile.optionxform = lambda option: option
            self.ConfigFile.read(self.path, encoding=encoding)
        except:
            traceback.print_exc()

    def get(self, section, option, default=None):
        if self.ConfigFile.has_section(section):
            if self.ConfigFile.has_option(section, option):
                return self.ConfigFile.get(section, option)
            return default
        return default

    def get_int(self, section, option, default=0):
        if self.ConfigFile.has_section(section):
            if self.ConfigFile.has_option(section, option):
                try:
                    return self.ConfigFile.getint(section, option)
                except:
                    traceback.print_exc()
                    return default
            else:
                return default
        else:
            return default

    def get_items(self, section, default=None):
        if default is None:
            default = ()
        if self.ConfigFile.has_section(section):
            return self.ConfigFile.items(section)
        else:
            return default

    def get_sections(self):
        return self.ConfigFile.sections()

    def get_options(self, section, default=None):
        if default is None:
            default = []
        if self.ConfigFile.has_section(section):
            return self.ConfigFile.options(section)
        else:
            return default

    def set(self, section, option, value):
        if not self.ConfigFile.has_section(section):
            self.ConfigFile.add_section(section)
        return self.ConfigFile.set(section, option, value)

    def save(self):
        with open(self.path, "w") as flag:
            self.ConfigFile.write(flag)
        return True

    def remove_option(self, section, option):
        if self.ConfigFile.has_section(section) and self.ConfigFile.has_option(section, option):
            return self.ConfigFile.remove_option(section, option)
        return True

    def remove_section(self, section):
        if self.ConfigFile.has_section(section):
            return self.ConfigFile.remove_section(section)
        return True
