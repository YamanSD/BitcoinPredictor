from datetime import datetime
from dataclasses import dataclass
from requests import get

from Config import config
from Utils import convert_to_dataclass


@dataclass(frozen=True)
class KlineResponse:
    """
    Class used to encapsulate kline API responses.
    """
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    quote_asset_volume: float
    number_of_trades: int
    taker_buy_base_asset_volume: float
    taker_buy_quote_asset_volume: float


def fetch() -> list[KlineResponse]:
    """
    https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-data
    Fetch the latest current-minute-interval information.


    :returns: The latest 5 minute KlineResponse.
    """

    data: list[list] = get(
        f"{config.binance.endpoint}/klines",
        proxies=config.proxies,
        params={
            'symbol': "BTCUSDT",
            'interval': '1m',
            'limit': 5
        }
    ).json()

    return list(
        map(
            lambda doc: convert_to_dataclass(
                KlineResponse, {
                    "timestamp": datetime.utcfromtimestamp(int(doc[0]) // 1_000),
                    "open": float(doc[1]),
                    "high": float(doc[2]),
                    "low": float(doc[3]),
                    "close": float(doc[4]),
                    "volume": float(doc[5]),
                    "quote_asset_volume": float(doc[7]),
                    "number_of_trades": int(doc[8]),
                    "taker_buy_base_asset_volume": float(doc[9]),
                    "taker_buy_quote_asset_volume": float(doc[10]),
                }
            ),
            data
        )
    )
