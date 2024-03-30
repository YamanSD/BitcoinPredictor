from datetime import datetime
from dataclasses import dataclass
from requests import get

from Config import config
from Utils import convert_to_dataclass

import yfinance as yf

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
