from __future__ import annotations

import asyncio
from os import name as os_name

# Enable ANSI support on Windows & apply asyncio patches
if os_name == 'nt':
    from colorama import just_fix_windows_console

    just_fix_windows_console()
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from concurrent.futures import ThreadPoolExecutor, wait
from threading import Thread
from time import sleep
from typing import Callable
from pandas import options
from sklearn.pipeline import Pipeline

import Train
from Config import config
from Observer import observe, Observation, fed_rate_key
from Sentiment import general_sentiment, SentimentResponse
from Server import start
from Utils import every


def run(
        pipeline: Pipeline,
        callback: Callable,
        fed_rate: dict,
        logistic: bool = False,
        incremental: bool = False
) -> None:
    """

    Args:
        pipeline: Model pipeline to use for prediction.
        callback: Callback function that takes the prev-observation, curr-observation, and prediction.
        fed_rate: Federal rate that is already in use.
        logistic: True for logistic learning.
        incremental: True if the model supports partial fitting

    """
    with ThreadPoolExecutor(max_workers=2) as executor:
        observation_fu: Future = executor.submit(observe, fed_rate)
        sentiment_fu: Future = executor.submit(general_sentiment)

        # Wait for the threads
        wait((observation_fu, sentiment_fu))

        # Type declarations
        prev_observation: Observation
        cur_observation: Observation
        sentiment: SentimentResponse

        prev_observation, cur_observation = observation_fu.result()
        sentiment: SentimentResponse = sentiment_fu.result()

        # Set back to false
        fed_rate[fed_rate_key] = cur_observation.fed_rate

        # Incremental learning based on previous candle
        if incremental:
            pipeline.named_steps['model'].partial_fit(
                *prev_observation.to_train_df(logistic)
            )

        # Apply the sentiment to the observation
        cur_observation.apply_sentiment(sentiment)

        y_pred = pipeline.predict(
            cur_observation.to_df()
        )

        # Callback with the predicted close, high, low
        callback(prev_observation, cur_observation, y_pred)


def save(model: Pipeline) -> None:
    """

    Args:
        model: To be saved.

    """
    Train.lr_save(model)


def set_observe(fed_rate: dict) -> None:
    """

    Sets the observation flag.

    """
    del fed_rate[fed_rate_key]


def main() -> None:
    options.display.max_columns = None

    model: Pipeline = Train.lr_load()
    incremental: bool = False
    fed_rate: dict = {}

    fed_t: Thread = every(
        86_400 // (len(config.alpha_vantage.keys) * config.alpha_vantage.limit),
        set_observe,
        fed_rate
    )
    run_t: Thread = every(
        60, run, model, lambda a, b, c: print(a, b, c, sep='\n------------------------\n'), fed_rate, False, incremental
    )

    if incremental:
        save_t: Thread = every(config.observer.save, save, model)
        save_t.start()

    # Start the threads
    fed_t.start()
    run_t.start()

    # Keeps the interpreter running
    while True:
        # Less expensive than a pass statement on CPU
        sleep(100_000)  # Might need to change to 60


if __name__ == '__main__':
    # Keeps the interpreter running
    main()
