from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, wait, Future
from dataclasses import dataclass, asdict
from datetime import datetime

from numpy import ravel, ndarray
from pandas import DataFrame

from .bitcoin import fetch as btc_fetch, KlineResponse
from .dxy import fetch as dxy_fetch, DxyResponse
from .fng import fetch as fng_fetch, FngResponse
from .fed_fund import fetch as fed_rate_fetch, FedFundResponse

from Data import target_labels
from Utils import convert_to_dataclass


# Key used by the fed rate observation refresh
fed_rate_key: str = 'fed_rate'


@dataclass
class Observation:
    """
    Class encapsulating the current state of the parameters,
    fetched from their data sources
    """
    timestamp: datetime
    open: float
    close: float
    high: float
    low: float
    close: float
    volume: float
    quote_asset_volume: float
    number_of_trades: int
    taker_buy_base_asset_volume: float
    taker_buy_quote_asset_volume: float
    open_dxy: float
    fng: int
    fed_rate: float

    def _to_def(self) -> DataFrame:
        """

        Returns:
            Observer object as an un-tampered DataFrame.

        """
        df: DataFrame = DataFrame(
            {k: [v] for k, v in asdict(self).items()},
        )
        df.set_index("timestamp", inplace=True)

        return df

    def to_df(self) -> DataFrame:
        """

        Returns:
            A DataFrame representation of the observation, without the targets.

        """

        df: DataFrame = self._to_def()
        df.drop(target_labels, axis=1, inplace=True)

        return df

    def to_train_df(self, logistic: bool = False) -> tuple[DataFrame, DataFrame | ndarray]:
        """

        Args:
            logistic: If True treats the data for use in logistic regression.

        Returns:
            The separated X and Y components as DataFrames

        """
        df: DataFrame = self._to_def()

        if logistic:
            return df.drop(target_labels, axis=1), ravel(
                (df['open'] - df['close']).map(lambda v: -1 if v < 0 else int(0 < v))
            )

        return df.drop(target_labels, axis=1), df[target_labels]


def observe(fed_rate: dict) -> tuple[Observation, Observation]:
    """

    Args:
        fed_rate: Current fed-rate, used when given.

    Returns:
        The current observed state of the parameters

    """
    refresh_fed: bool = fed_rate_key not in fed_rate

    # For documentation https://docs.python.org/3/library/concurrent.futures.html
    # Note that another viable option is the use grequests
    with ThreadPoolExecutor(max_workers=4) as executor:
        res: tuple[Future, ...] = tuple(
            executor.submit(f) for f in (
                btc_fetch,
                dxy_fetch,
                fng_fetch,
            ) + (
                (fed_rate_fetch,) if refresh_fed else ()
            )
        )

        # Wait for all the threads to finish
        wait(res)

        prev_btc_res, cur_btc_res = res[0].result()
        dxy_res: DxyResponse = res[1].result()
        fng_res: FngResponse = res[2].result()
        fed_rate_res: FedFundResponse = res[3].result() if refresh_fed else fed_rate

        temp: dict = {
            **asdict(dxy_res),
            **asdict(fng_res),
            **(asdict(fed_rate_res) if refresh_fed else fed_rate),
        }

        # Type declarations
        prev: Observation
        cur: Observation

        prev, cur = convert_to_dataclass(Observation, {
            **temp,
            **asdict(prev_btc_res)
        }), convert_to_dataclass(Observation, {
            **temp,
            **asdict(cur_btc_res)
        })

        if refresh_fed:
            fed_rate[fed_rate_key] = cur.fed_rate

        return prev, cur
