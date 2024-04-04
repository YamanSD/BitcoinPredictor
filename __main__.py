from __future__ import annotations

import asyncio
from os import name as os_name

# Enable ANSI support on Windows & apply asyncio patches
if os_name == 'nt':
    try:
        from colorama import just_fix_windows_console
    except ImportError:
        def just_fix_windows_console() -> None:
            return

    just_fix_windows_console()
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# from Server import start
from Sentiment import relative_sentiment, SentimentRequest, SentimentResponse
from Crawler import spider
from datetime import date, timedelta
from pandas import DataFrame
from itertools import repeat
from concurrent.futures import ThreadPoolExecutor, Future, wait
from time import sleep, time
from collections import deque


def main() -> None:
    # start()
    finalDate: date = date(2023, 12, 31)
    t0: date = date(2017, 1, 1)
    delta: timedelta = timedelta(days=7)
    delta_prev: timedelta = timedelta(days=-7)
    r = {
        'timestamp': [],
        'sentiment': []
    }
    timestamps = []

    while t0 <= finalDate:
        timestamps.append(t0)
        t0 += delta

    def func(t) -> None:
        sentiment = relative_sentiment(
            spider.query_text(
                "bitcoin news",
                max_results=500,
                timelimit=(str(t + delta_prev), str(t))
            ),
            lambda _: 1
        )
        r['timestamp'].append(t)
        r['sentiment'].append(sentiment.net_sentiment())
        print(t)

    tr0: float = time()
    with (ThreadPoolExecutor(max_workers=len(timestamps)) as executor):
        res: tuple[Future, ...] = tuple(
            map(
                lambda t: executor.submit(func, t),
                timestamps
            )
        )

        wait(res)

    print(time() - tr0)

    df = DataFrame(r)
    df.set_index('timestamp', inplace=True)
    df.to_csv("./sentiment.csv")

    print("DONE")


if __name__ == '__main__':
    main()
