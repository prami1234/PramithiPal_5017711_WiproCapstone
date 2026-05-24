import configparser
import os


class ConfigReader:
    _config = None

    @staticmethod
    def get_config():
        if ConfigReader._config is None:
            ConfigReader._config = configparser.ConfigParser()
            config_path = os.path.join(os.path.dirname(__file__), "config.ini")
            ConfigReader._config.read(config_path)
        return ConfigReader._config

    @staticmethod
    def get(section, key):
        config = ConfigReader.get_config()
        return config.get(section, key)

    @staticmethod
    def get_browser():
        return ConfigReader.get("browser", "browser")

    @staticmethod
    def get_base_url():
        return ConfigReader.get("url", "base_url")

    @staticmethod
    def get_implicit_wait():
        return int(ConfigReader.get("browser", "implicit_wait"))

    @staticmethod
    def get_explicit_wait():
        return int(ConfigReader.get("browser", "explicit_wait"))

    @staticmethod
    def get_page_load_timeout():
        return int(ConfigReader.get("browser", "page_load_timeout"))

    @staticmethod
    def get_manual_otp_timeout():
        return int(ConfigReader.get("browser", "manual_otp_timeout"))

    @staticmethod
    def get_testdata_path():
        base = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(base, ConfigReader.get("paths", "testdata"))

    @staticmethod
    def get_screenshots_path():
        custom_path = os.environ.get("SCREENSHOTS_PATH")
        if custom_path:
            return custom_path

        base = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(base, ConfigReader.get("paths", "screenshots"))

    @staticmethod
    def get_source():
        return ConfigReader.get("search", "source")

    @staticmethod
    def get_destination():
        return ConfigReader.get("search", "destination")

    @staticmethod
    def get_travel_date():
        return ConfigReader.get("search", "travel_date")

    @staticmethod
    def get_bus_type_filter():
        return ConfigReader.get("filters", "bus_type")

    @staticmethod
    def get_departure_time_filter():
        return ConfigReader.get("filters", "departure_time")

    @staticmethod
    def get_mobile_number():
        return ConfigReader.get("login", "mobile_number")

    @staticmethod
    def get_passenger_defaults():
        return {
            "name": ConfigReader.get("passenger", "name"),
            "age": ConfigReader.get("passenger", "age"),
            "gender": ConfigReader.get("passenger", "gender"),
            "email": ConfigReader.get("passenger", "email"),
            "phone": ConfigReader.get("passenger", "phone"),
        }

    @staticmethod
    def is_headless():
        return ConfigReader.get("browser", "headless").lower() == "true"