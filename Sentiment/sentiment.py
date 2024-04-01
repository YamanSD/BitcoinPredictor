from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from numpy import average
from requests import post
from typing import Optional, Iterable

from Config import config
from Crawler import spider


@dataclass
class SentimentResponse:
    """
    Class used for sentiment queries.


    positive: SentimentResponse of the positive sentiment.

    negative: SentimentResponse of the negative sentiment.

    neutral: SentimentResponse of the neutral sentiment.
    """
    positive: float
    negative: float
    neutral: float

    @classmethod
    def fromlist(cls, sentiments: list[dict]) -> SentimentResponse:
        temp: dict = {
            s['label']: s['score'] for s in sentiments
        }

        return cls(
            temp['positive'],
            temp['negative'],
            temp['neutral']
        )

    def __add__(self, other: SentimentResponse) -> SentimentResponse:
        return SentimentResponse(
            self.positive + other.positive,
            self.negative + other.negative,
            self.neutral + other.neutral
        )

    def __truediv__(self, other: float) -> SentimentResponse:
        return SentimentResponse(
            self.positive / other,
            self.negative / other,
            self.neutral / other
        )

    def __mul__(self, other: float) -> SentimentResponse:
        return SentimentResponse(
            self.positive * other,
            self.negative * other,
            self.neutral * other
        )

    def __iadd__(self, other: SentimentResponse) -> None:
        self.positive += other.positive
        self.negative += other.negative
        self.neutral += other.neutral

    def __imul__(self, other: float) -> None:
        self.positive *= other
        self.negative *= other
        self.neutral *= other

    def __itruediv__(self, other: float) -> None:
        self.positive /= other
        self.negative /= other
        self.neutral /= other


@dataclass(frozen=True)
class SentimentRequestOptions:
    """
    Class used for sentiment query options.


    use_cache: True to use caching.

    wait_for_model: True to wait for the model if not booted (due to serverless cold starts).
    """
    use_cache: Optional[bool]
    wait_for_model: Optional[bool]


@dataclass(frozen=True)
class SentimentRequest:
    """
    Class used for sentiment queries.


    inputs: list of queries to the model or a single string query.

    options: HF request options.
    """
    inputs: str | Iterable[str]
    options: Optional[SentimentRequestOptions] = SentimentRequestOptions(True, True)


def query(payload: SentimentRequest) -> list[SentimentResponse]:
    """

    Args:
        payload: Necessary data to perform the sentiment request.

    Returns:
        The sentiment of the given inputs according to an NLP model.

    """

    # For documentation of requests consult: https://docs.python-requests.org/en/latest/user/advanced/
    # For documentation of API check config.json for API link
    return list(
        map(
            lambda ms: SentimentResponse.fromlist(ms),
            post(
                config.hf.sentiment_url,
                headers={
                    "Authorization": config.hf.sentiment_token
                },
                json=asdict(payload),
                proxies=config.proxies
            ).json()
        )
    )


def general_sentiment(keywords: str = "bitcoin sentiment news") -> SentimentResponse:
    """

    Args:
        keywords: Keywords for the sentiment search.

    Returns:
        The current general sentiment of the market, based on the base NLP query.

    """

    # Query the web for news
    news: list[spider.SpiderNewsResponse] = spider.query_news(
        keywords,
        max_results=1_000
    )

    # Current datetime
    current: datetime = datetime.now()

    # Query the NLP model and average the weights
    return average(
        query(
            SentimentRequest(
                tuple(
                    map(
                        lambda n: f"{n.title}\n{n.body}",
                        news
                    )
                )
            )
        ),
        weights=tuple(
            24 - abs(current.hour - n.date.hour) for n in news
        )
    )
