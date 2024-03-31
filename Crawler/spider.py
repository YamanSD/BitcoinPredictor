from __future__ import annotations

from re import compile as compile_re
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Annotated
from duckduckgo_search import AsyncDDGS

from Config import config
from Utils import convert_to_dataclass

# Type of search regions
Region = Literal[
    'xa-ar', 'xa-en',
    'ar-es', 'au-en',
    'at-de', 'be-fr',
    'be-nl', 'br-pt',
    'bg-bg', 'ca-en',
    'ca-fr', 'ct-ca',
    'cl-es', 'cn-zh',
    'co-es', 'hr-hr',
    'cz-cs', 'dk-da',
    'ee-et', 'fi-fi',
    'fr-fr', 'de-de',
    'gr-el', 'hk-tzh',
    'hu-hu', 'in-en',
    'id-id', 'id-en',
    'ie-en', 'il-he',
    'it-it', 'jp-jp',
    'kr-kr', 'lv-lv',
    'lt-lt', 'xl-es',
    'my-ms', 'my-en',
    'mx-es', 'nl-nl',
    'nz-en', 'no-no',
    'pe-es', 'ph-en',
    'ph-tl', 'pl-pl',
    'pt-pt', 'ro-ro',
    'ru-ru', 'sg-en',
    'sk-sk', 'sl-sl',
    'za-en', 'es-es',
    'se-sv', 'ch-de',
    'ch-fr', 'ch-it',
    'tw-tzh', 'th-th',
    'tr-tr', 'ua-uk',
    'uk-en', 'us-en',
    'ue-es', 've-es',
    'vn-vi', 'wt-wt'
]

# Date string type, does not detect invalid dates based on leap year (ex. 2021-02-29 is matched)
DateBound = Annotated[str, compile_re(
    r"^\d{4}-(((0[13578]|(10|12))-(0[1-9]|[1-2]\d|3[0-1]))|(02-(0[1-9]|[1-2]\d))|((0[469]|11)-(0[1-9]|[1-2]\d|30)))$"
)]

# Handles searching
browser: AsyncDDGS = AsyncDDGS(
    proxies=config.proxies,
)


@dataclass
class SpiderNewsResponse:
    """
    Class for the responses of a Spider news query.
    """
    date: datetime
    title: str
    body: str
    url: str
    source: str
    image: str


@dataclass
class SpiderTextResponse:
    """
    Class for the responses of a Spider text query.
    """
    title: str
    body: str
    href: str


@dataclass
class SpiderImageResponse:
    """
    Class for the responses of a Spider images query.
    """
    title: str
    image: str
    thumbnail: str
    url: str
    height: int
    width: int
    source: str


@dataclass
class SpiderVideoStatisticResponse:
    """
    Class used for Spider video response statistics.
    """
    viewCount: int


@dataclass
class SpiderVideoImagesResponse:
    """
    Class used for Spider video response images.
    """
    small: str
    motion: str
    medium: str
    large: str


@dataclass
class SpiderVideoResponse:
    """
    Class for the responses of a Spider videos query.
    """
    content: str
    description: str
    duration: str
    embed_html: str
    embed_url: str
    image_token: str
    provider: str
    published: datetime
    publisher: str
    statistics: SpiderVideoStatisticResponse
    images: SpiderVideoImagesResponse
    title: str
    uploader: str


@dataclass
class SpiderSuggestionResponse:
    """
    Class for the responses of a Spider suggestion query.
    """
    phrase: str


@dataclass
class SpiderTranslateResponse:
    """
     Class for the responses of a Spider translation query.
    """
    detected_language: str | None
    translated: str
    original: str


async def query_news(
        keywords: str,
        max_results: int = 1,
        timelimit: Literal['d', 'w', 'm'] | None = None,
        safe_search: Literal['on', 'moderate', 'off'] = 'off',
        region: Region = 'wt-wt',
) -> list[SpiderNewsResponse]:
    """

    Queries DuckDuckGo for news results.

    Args:
        keywords: Search term of spider.
        max_results: Number of maximum results.
        timelimit: d for day, w for week, m for month, or use bounds for search from time to time.
        safe_search: on, moderate, or off.
        region: Search region.

    Returns:
        List of responses.

    Raises:
        DuckDuckGoSearchException: Raised when there is a generic exception during the API request.

    """
    return list(
        map(
            lambda doc: convert_to_dataclass(
                SpiderNewsResponse,
                {
                    **doc,
                    'date': datetime.strptime(doc['date'], "%Y-%m-%dT%H:%M:%S%z"),
                }
            ),
            await browser.news(
                keywords=keywords,
                max_results=max_results,
                safesearch=safe_search,
                timelimit=timelimit,
                region=region
            )
        )
    )


async def query_text(
        keywords: str,
        max_results: int = 1,
        timelimit: Literal['d', 'w', 'm'] | tuple[DateBound, DateBound] | None = None,
        safe_search: Literal['on', 'moderate', 'off'] = 'off',
        region: Region = 'wt-wt',
) -> list[SpiderTextResponse]:
    """

    Queries DuckDuckGo for text results.


    Args:
        keywords: Search term of spider.
        max_results: Number of maximum results.
        timelimit: d for day, w for week, m for month, or use bounds for search from time to time.
        safe_search: on, moderate, or off.
        region: Search region.

    Returns:
        List of responses.

    Raises:
        DuckDuckGoSearchException: Raised when there is a generic exception during the API request.

    """
    return list(
        map(
            lambda doc: convert_to_dataclass(SpiderTextResponse, doc),
            await browser.text(
                keywords=keywords,
                max_results=max_results,
                safesearch=safe_search,
                timelimit=(
                    str(timelimit) if type(timelimit) is str
                    else f"{timelimit[0]}..{timelimit[1]}" if type(timelimit) is tuple[DateBound, DateBound]
                    else None
                ),
                region=region
            )
        )
    )


async def query_images(
        keywords: str,
        max_results: int = 1,
        timelimit: Literal['Day', 'Week', 'Month', 'Year'] | None = None,
        size: Literal['Small', 'Medium', 'Large', 'Wallpaper'] | None = None,
        color: Literal[
                   'color', 'Monochrome', 'Red', 'Orange',
                   'Yellow', 'Green', 'Blue', 'Purple',
                   'Pink', 'Brown', 'Black', 'Gray',
                   'Teal', 'White'] | None = None,
        type_image: Literal['photo', 'clipart', 'gif', 'transparent', 'line'] | None = None,
        layout: Literal['Square', 'Tall', 'Wide'] | None = None,
        license_image: Literal[
                           'any', 'Public', 'Share',
                           'ShareCommercially', 'Modify',
                           'ModifyCommercially'] | None = None,
        safe_search: Literal['on', 'moderate', 'off'] = 'off',
        region: Region = 'wt-wt',
) -> list[SpiderImageResponse]:
    """

    Queries DuckDuckGo for image results.

    Args:
        keywords: Search term of spider.
        max_results: Number of maximum results.
        timelimit: d for day, w for week, m for month, or use bounds for search from time to time.
        size: Size of the image.
        color: Color of the image.
        type_image: Type of the image.
        layout: Shape of the image dimensions.
        license_image: License of the image.
        safe_search: on, moderate, or off.
        region: Search region.

    Returns:
        List of responses.

    Raises:
        DuckDuckGoSearchException: Raised when there is a generic exception during the API request.

    """
    return list(
        map(
            lambda doc: convert_to_dataclass(SpiderImageResponse, doc),
            await browser.images(
                keywords=keywords,
                layout=layout,
                license_image=license_image,
                type_image=type_image,
                color=color,
                size=size,
                max_results=max_results,
                safesearch=safe_search,
                timelimit=timelimit,
                region=region
            )
        )
    )


async def query_videos(
        keywords: str,
        max_results: int = 1,
        timelimit: Literal['d', 'w', 'm'] | None = None,
        resolution: Literal['high', 'standard'] | None = None,
        duration: Literal['short', 'medium', 'large'] | None = None,
        license_videos: Literal['creativeCommon', 'youtube'] | None = None,
        safe_search: Literal['on', 'moderate', 'off'] = 'off',
        region: Region = 'wt-wt',
) -> list[SpiderVideoResponse]:
    """

    Queries DuckDuckGo for video results.

    Args:
        keywords: Search term of spider.
        max_results: Number of maximum results.
        timelimit: d for day, w for week, m for month, or use bounds for search from time to time.
        resolution: Resolution of the videos.
        duration: Duration of the videos.
        license_videos: Licence of the videos.
        safe_search: on, moderate, or off.
        region: Search region.

    Returns:
        List of responses.

    Raises:
        DuckDuckGoSearchException: Raised when there is a generic exception during the API request.

    """
    return list(
        map(
            lambda doc: convert_to_dataclass(
                SpiderVideoResponse,
                {
                    **doc,
                    'images': convert_to_dataclass(SpiderVideoImagesResponse, doc['images']),
                    'statistics': convert_to_dataclass(SpiderVideoStatisticResponse, doc['statistics']),
                    'published': datetime.strptime(doc['published'][:-1], "%Y-%m-%dT%H:%M:%S.%f"),
                }
            ),
            await browser.videos(
                keywords=keywords,
                resolution=resolution,
                duration=duration,
                license_videos=license_videos,
                max_results=max_results,
                safesearch=safe_search,
                timelimit=timelimit,
                region=region
            )
        )
    )


async def query_translate(
        keywords: str,
        from_lang: str = None,
        to_lang: str = "en"
) -> list[SpiderTranslateResponse]:
    """

    Queries DuckDuckGo for translation results.

    Args:
        keywords: Search term of spider.
        from_lang: Language to translate from.
        to_lang: Language to translate to.

    Returns:
        The translation.

    Raises:
        DuckDuckGoSearchException: Raised when there is a generic exception during the API request.

    """
    return list(
        map(
            lambda doc: convert_to_dataclass(SpiderTranslateResponse, doc),
            await browser.translate(
                keywords=keywords,
                from_=from_lang,
                to=to_lang
            )
        )
    )


async def query_suggestions(
        keywords: str,
        region: Region = "wt-wt"
) -> list[SpiderSuggestionResponse]:
    """

    Queries DuckDuckGo for suggestion results.

    Args:
        keywords: Search term of spider.
        region: Region of the suggestions.

    Returns:
        DuckDuckGo Suggestion.

    Raises:
        DuckDuckGoSearchException: Raised when there is a generic exception during the API request.

    """
    return list(
        map(
            lambda doc: convert_to_dataclass(SpiderSuggestionResponse, doc),
            await browser.suggestions(
                keywords=keywords,
                region=region
            )
        )
    )
