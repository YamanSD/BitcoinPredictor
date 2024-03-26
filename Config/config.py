from dataclasses import dataclass
from typing import TypedDict


from Utils import convert_to_dataclass, read_json


@dataclass(frozen=True)
class HfConfig:
    """
    Class used for HuggingFace configuration.


    sentiment_token: Bearer token for the sentiment query requests.

    sentiment_url: URL to the sentiment model API.
    """
    sentiment_token: str
    sentiment_url: str


@dataclass(frozen=True)
class KaggleConfig:
    """
    Class used for Kaggle configuration.


    username: Kaggle username.

    key: Kaggle auth key.
    """
    username: str
    key: str


class ProxiesConfig(TypedDict):
    """
    Class used for proxy configuration.


    http: HTTP proxy.

    https: HTTPS proxy.
    """
    http: str
    https: str


"""
Class used for request headers.

User-Agent: User agent header for requests that require user browsers.
"""
HeaderConfig = TypedDict('HeaderConfig', {'User-Agent': str})


@dataclass(frozen=True)
class Config:
    """
    Class used for app configuration.


    hf: HuggingFace configuration.

    proxies: Proxies for the requests.

    spider: spider authentication keys.
    """
    hf: HfConfig
    proxies: ProxiesConfig
    kaggle: KaggleConfig
    header: HeaderConfig


def load_config(path: str) -> Config:
    """
    Reads the given JSON config file.
    :param path: Path to JSON config.
    :return:
    """
    data: dict = read_json(path)

    # Convert to ConfigType object and return
    return convert_to_dataclass(Config, {
        **data,
        "hf": convert_to_dataclass(HfConfig, data['hf']),
        "kaggle": convert_to_dataclass(KaggleConfig, data['kaggle'])
    })
