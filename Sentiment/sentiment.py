from __future__ import annotations

import asyncio
from dataclasses import dataclass, asdict
from requests import post
from typing import Literal, Optional

from Config import config
from Crawler import spider


@dataclass(frozen=True)
class SentimentResponse:
    """
    Class used for sentiment queries.


    score: Probability of the sentiment label [0, 1].

    label: Either negative, neutral, or positive.
    """
    score: int
    label: Literal['negative', 'neutral', 'positive']


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
    inputs: str | list[str]
    options: Optional[SentimentRequestOptions] = SentimentRequestOptions(True, True)


def query(payload: SentimentRequest) -> list[list[SentimentResponse]]:
    """
    Queries an NLP sentiment model using its serverless API.
    :param payload: request to the sentiment model.
    :return:
    """
    # For documentation of requests consult: https://docs.python-requests.org/en/latest/user/advanced/
    # For documentation of API check config.json for API link
    return post(
        config.hf.sentiment_url,
        headers={
            "Authorization": config.hf.sentiment_token
        },
        json=asdict(payload),
        proxies=config.proxies
    ).json()


async def general_sentiment(keywords: str = "bitcoin sentiment") -> SentimentResponse:
    """
    Queries the web for the current general sentiment
    :param keywords: keywords of the query.
    :returns: the current general sentiment of the market.
    """
    news: list[spider.SpiderNewsResponse] = await spider.query_news(keywords)


