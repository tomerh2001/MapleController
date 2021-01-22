import json


class SettingsController:
    DEFAULT_VAL = "~SETTINGS_CONTROLLER_DEFAULT_VALUE~"

    def __init__(self, settings_path):
        self.settings = SettingsController.load_settings(settings_path)

    @staticmethod
    def load_settings(path):
        with open(path) as fd:
            return json.load(fd)

    def get(self, key, default_value=DEFAULT_VAL):
        if key not in self.settings:
            if default_value == SettingsController.DEFAULT_VAL:
                raise ValueError("The .json file does not contain the key '" + key + "'")
            else:
                return default_value
        else:
            return self.settings[key]
