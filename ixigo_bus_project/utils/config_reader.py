import configparser
import os


class ConfigReader:
    _config = None

    @staticmethod
    def _load():
        if ConfigReader._config is None:
            config = configparser.ConfigParser()

            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, "config", "config.properties")

            if not os.path.exists(config_path):
                raise FileNotFoundError(f"Config file not found at: {config_path}")

            config.read(config_path, encoding="utf-8")
            ConfigReader._config = config

        return ConfigReader._config

    @staticmethod
    def get(key):
        config = ConfigReader._load()
        try:
            return config["DEFAULT"][key].strip()
        except KeyError:
            raise KeyError(f"Key '{key}' not found in config.properties")