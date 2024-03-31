from datetime import datetime
from dataclasses import dataclass
from requests import get

from Config import config
from Utils import convert_to_dataclass


@dataclass(frozen=True)
class FngResponse:
    """
    Class used to encapsulate FNG API responses.
    """
    timestamp: datetime
    fng: int


def fetch() -> FngResponse:
    """
    Fetch the latest FNG information.


    Returns:
        The latest FNG information.

    """

    data: dict = get(
        config.fng.live_url,
        proxies=config.proxies,
    ).json()['data'][0]

    # Current UTC time
    current: datetime = datetime.utcnow()

    return convert_to_dataclass(FngResponse, {
        "timestamp": datetime.strptime(
            data['timestamp'],
            "%d-%m-%Y"
        ).replace(
            hour=current.hour,
            minute=current.minute
        ),
        "fng": int(data['value'])
    })
