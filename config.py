import json
from typing import TypedDict


class HfConfigType(TypedDict):
    """
    Class used for type hints of HuggingFace configuration.


    sentiment_token: Bearer token for the sentiment query requests.

    sentiment_url: URL to the sentiment model API.
    """
    sentiment_token: str
    sentiment_url: str


class ProxiesConfigType(TypedDict):
    """
    Class used for type hints of proxy configuration.


    http: HTTP proxy.
    https: HTTPS proxy.
    """
    http: str
    https: str


class ConfigType(TypedDict):
    """
    Class used for type hints of app configuration.


    hf: HuggingFace configuration.

    proxies: Proxies for the requests.
    """
    hf: HfConfigType
    proxies: ProxiesConfigType


def load_config(path: str) -> ConfigType:
    """
    Reads the given JSON config file.
    :param path: Path to JSON config.
    :return:
    """
    with open(path, 'r') as file:
        return json.load(file)
