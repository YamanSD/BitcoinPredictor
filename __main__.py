try:
    from colorama import just_fix_windows_console
except ImportError:
    # Must be defined
    def just_fix_windows_console():
        return

from concurrent.futures import ThreadPoolExecutor, wait, Future
from threading import Thread
from typing import Any, Callable
from pandas import options, DataFrame
from sklearn.pipeline import Pipeline

import Train
from Config import config
from Observer import observe, Observation
from Sentiment import general_sentiment, SentimentResponse
from Utils import every


def run(model: Pipeline) -> None:
    with ThreadPoolExecutor(max_workers=2) as executor:
        res: tuple[Future, ...] = tuple(
            executor.submit(f) for f in (
                observe,
                general_sentiment
            )
        )

        # Wait for the threads
        wait(res)

        observation: Observation = res[0].result()
        sentiment: SentimentResponse = res[1].result()

    y_pred = model.predict(
        observation.to_df()
    )

    print(observation)
    print("-----------------------------------")
    print(y_pred)


def main() -> None:
    # Enable ANSI support on Windows
    just_fix_windows_console()
    options.display.max_columns = None

    model: Pipeline = Train.lr_load()

    # t: Thread = every(30, run, model, Train.lr_scale)
    run(model)


if __name__ == '__main__':
    main()
