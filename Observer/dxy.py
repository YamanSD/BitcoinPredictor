from datetime import datetime
from dataclasses import dataclass
from yfinance import Ticker

from Config import config
from Utils import convert_to_dataclass


@dataclass(frozen=True)
class DxyResponse:
    """
    Class used to encapsulate Yahoo Finance DXY API responses.
    """
    timestamp: datetime
    open_dxy: float


def fetch() -> DxyResponse:
    """

    https://pypi.org/project/yfinance/
    Fetch the latest current-minute-interval information.

    Returns:
        The latest DXY response.

    """

    dxy: Ticker = Ticker("DX-Y.NYB", proxy=config.proxies['https_y'])
    data: dict = dxy.info

    return convert_to_dataclass(
        DxyResponse, {
            "timestamp": datetime.utcnow().replace(second=0, microsecond=0),
            "open_dxy": float(data['open']),
        }
    )
