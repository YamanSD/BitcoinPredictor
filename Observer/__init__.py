from concurrent.futures import ThreadPoolExecutor, wait, Future
from dataclasses import dataclass, asdict
from datetime import datetime

from .bitcoin import fetch as btc_fetch, KlineResponse
from .dxy import fetch as dxy_fetch, DxyResponse
from .fng import fetch as fng_fetch, FngResponse
from .fed_fund import fetch as fed_rate_fetch, FedFundResponse

from Utils import convert_to_dataclass


@dataclass
class Observation:
    """
    Class encapsulating the current state of the parameters,
    fetched from their data sources
    """
    timestamp: datetime
    open: float
    close: float
    low: float
    close: float
    volume: float
    quote_asset_volume: float
    number_of_trades: int
    taker_buy_base_asset_volume: float
    taker_buy_quote_asset_volume: float
    open_dxy: float
    fng: int
    fed_fund: float


def observe() -> Observation:
    """
    Observes the current state of the parameters.
    :returns: the current observation.
    """

    # For documentation https://docs.python.org/3/library/concurrent.futures.html
    # Note that another viable option is the use grequests
    with ThreadPoolExecutor(max_workers=4) as executor:
        res: tuple[Future, ...] = tuple(
            executor.submit(f) for f in (
                btc_fetch,
                dxy_fetch,
                fng_fetch,
                fed_rate_fetch,
            )
        )

        # Wait for all the threads to finish
        wait(res)

        btc_res: KlineResponse = res[0].result()[-1]
        dxy_res: DxyResponse = res[1].result()
        fng_res: FngResponse = res[2].result()
        fed_rate_res: FedFundResponse = res[3].result()

        return convert_to_dataclass(Observation, {
            **asdict(dxy_res),
            **asdict(fng_res),
            **asdict(fed_rate_res),
            **asdict(btc_res)
        })
