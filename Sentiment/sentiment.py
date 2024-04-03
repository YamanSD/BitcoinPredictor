from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from numpy import average, ndarray, sign
from math import exp
from requests import post
from typing import Optional, Iterable, Callable

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

    def net_sentiment(self) -> float:
        return self.positive - self.negative


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


def relative_sentiment(
        news: list[spider.SpiderNewsResponse | spider.SpiderTextResponse],
        weight_func: Callable[[spider.SpiderNewsResponse], float]
) -> SentimentResponse:
    """

    Args:
        news: List of news fetched from the web.
        weight_func: Weight function applied on each news article.

    Returns:
        The weighted average sentiment response based on the given weight function.

    """

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
        weights=tuple(map(weight_func, news))
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
        timelimit='d',
        max_results=255
    )

    # Current datetime
    current: datetime = datetime.now()

    # Query the NLP model and average the weights
    return relative_sentiment(news, lambda n: 24 - abs(current.hour - n.date.hour))


def apply_sentiment(y_pred: ndarray, sentiment: SentimentResponse, logistic: bool = False) -> ndarray:
    """

    Args:
        y_pred: Predicted y.
        sentiment: Predicted sentiment.
        logistic: True for logistic model

    Returns:
        Altered y_pred based on sentiment

    """
    # Mapping function
    f: Callable = lambda x: 0 if x == 0 else (1 / (1 + exp(1 / x)) + min(0, sign(x))) / 4
    sentiment_score: float = f(sentiment.net_sentiment())

    if logistic:
        return y_pred if sign(sentiment_score) == sign(y_pred) or sign(sentiment_score) == 0 \
            else -y_pred if abs(sentiment_score) >= 0.4 \
            else y_pred

    return y_pred * (1 + sentiment_score)
