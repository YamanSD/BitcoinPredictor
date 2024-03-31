from datetime import datetime
from dataclasses import dataclass
from requests import get

from Config import config
from Utils import convert_to_dataclass


# Counts the number of sent requests
key_counter: int = 0


@dataclass(frozen=True)
class FedFundResponse:
    """
    Class used to encapsulate Federal Fund AlphaVantage API responses.
    """
    timestamp: datetime
    fed_rate: float


def fetch() -> FedFundResponse:
    """

    https://www.alphavantage.co/documentation/
    Fetch the latest Federal Funds information.

    Returns:
        The latest Federal Interest response.

    """
    global key_counter

    # Do not use proxies, AlphaVantage does not accept it (probably due to WAF)
    res: dict = get(
        config.alpha_vantage.url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        },
        params={
            "apikey": config.alpha_vantage.keys[key_counter // (config.alpha_vantage.limit - 1)],
            "function": "TREASURY_YIELD",
            "maturity": "3month",
            "interval": "daily",
            "datatype": "json"
        }
    ).json()

    if "Information" in res and "25 requests per day" in res['Information']:
        if key_counter >= config.alpha_vantage.limit * len(config.alpha_vantage.keys):
            raise "AlphaVantage not responding"

        key_counter += config.alpha_vantage.limit
        return fetch()

    data: dict = res['data'][0]

    # Current UTC time
    current: datetime = datetime.utcnow()

    return convert_to_dataclass(FedFundResponse, {
        "timestamp": datetime.strptime(
            data['date'],
            "%Y-%m-%d"
        ).replace(
            hour=current.hour,
            minute=current.minute
        ),
        "fed_rate": float(data['value'])
    })
