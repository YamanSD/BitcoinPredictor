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


@dataclass(frozen=True)
class FearGreedConfig:
    """
    Class used for Fear & Greed Index configuration.


    historical_url: API URL used to obtain historic data.

    live_url: API URL used to obtain live data.
    """
    historical_url: str
    live_url: str


class ProxiesConfig(TypedDict):
    """
    Class used for proxy configuration.


    http: HTTP proxy.

    https: HTTPS proxy.
    """
    http: str
    https: str


@dataclass(frozen=True)
class BinanceConfig:
    """
    Class used for Binance API configuration.


    url: API URL endpoint. Does not need a key.
    """
    url: str


@dataclass(frozen=True)
class AlphaVantageConfig:
    """
    Class used for AlphaVantage API configuration.


    url: API endpoint.

    keys: List of usable API keys.

    limit: Maximum number of requests per key.
    """
    url: str
    keys: list[str]
    limit: int


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
    fng: FearGreedConfig
    binance: BinanceConfig
    alpha_vantage: AlphaVantageConfig


def load_config(path: str) -> Config:
    """

    Reads the given JSON config file.

    Args:
        path: Path to the config file.

    Returns:
        The loaded config object.

    """
    data: dict = read_json(path)

    # Convert to ConfigType object and return
    return convert_to_dataclass(Config, {
        **data,
        "hf": convert_to_dataclass(HfConfig, data['hf']),
        "kaggle": convert_to_dataclass(KaggleConfig, data['kaggle']),
        "fng": convert_to_dataclass(FearGreedConfig, data['fng']),
        "binance": convert_to_dataclass(BinanceConfig, data['binance']),
        "alpha_vantage": convert_to_dataclass(AlphaVantageConfig, data['alpha_vantage']),
    })
