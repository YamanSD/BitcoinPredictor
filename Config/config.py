from dataclasses import dataclass
from typing import TypedDict

import json

from Utils import convert_to_dataclass


@dataclass(frozen=True)
class HfConfig:
    """
    Class used for HuggingFace configuration.


    sentiment_token: Bearer token for the sentiment query requests.

    sentiment_url: URL to the sentiment model API.
    """
    sentiment_token: str
    sentiment_url: str


class ProxiesConfig(TypedDict):
    """
    Class used for proxy configuration.


    http: HTTP proxy.

    https: HTTPS proxy.
    """
    http: str
    https: str


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


def load_config(path: str) -> Config:
    """
    Reads the given JSON config file.
    :param path: Path to JSON config.
    :return:
    """
    with open(path, 'r') as file:
        data: dict = json.load(file)

    # Convert to ConfigType object
    hf_config: HfConfig = convert_to_dataclass(HfConfig, data['hf'])

    return convert_to_dataclass(Config, {
        **data,
        "hf": hf_config,
    })
