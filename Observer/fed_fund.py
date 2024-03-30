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


    :returns: The latest Federal Interest response.
    """

    # Do not use proxies, AlphaVantage does not accept it
    data: dict = get(
        config.alpha_vantage.url,
        params={
            "apikey": config.alpha_vantage.keys[key_counter // (config.alpha_vantage.limit - 1)],
            "function": "TREASURY_YIELD",
            "maturity": "3month",
            "interval": "daily",
            "datatype": "json"
        }
    ).json()['data'][0]

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
