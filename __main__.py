try:
    from colorama import just_fix_windows_console
except ImportError:
    # Must be defined
    def just_fix_windows_console():
        return

from concurrent.futures import ThreadPoolExecutor, wait, Future
from threading import Thread
from typing import Callable
from pandas import options
from sklearn.pipeline import Pipeline

import Train
from Config import config
from Observer import observe, Observation
from Sentiment import general_sentiment, SentimentResponse
from Utils import every


# Observation for the fed-rate flag
observe_fed: bool = True


def run(
        pipeline: Pipeline,
        callback: Callable,
        logistic: bool = False,
        incremental: bool = False
) -> None:
    """

    Args:
        pipeline: Model pipeline to use for prediction.
        callback: Callback function that takes the prev-observation, curr-observation, and prediction.
        logistic: True for logistic learning.
        incremental: True if the model supports partial fitting

    """
    global observe_fed

    with ThreadPoolExecutor(max_workers=2) as executor:
        observation_fu: Future = executor.submit(observe, observe_fed)
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
    observe_fed = False

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


def set_observe() -> None:
    """

    Sets the observation flag.

    """
    global observe_fed
    observe_fed = True


def main() -> None:
    # Enable ANSI support on Windows
    just_fix_windows_console()
    options.display.max_columns = None

    model: Pipeline = Train.lr_load()
    incremental: bool = False

    fed_t: Thread = every(
        86_400 / (len(config.alpha_vantage.keys) * config.alpha_vantage.limit),
        set_observe
    )
    run_t: Thread = every(60, run, model, print, False, incremental)

    if incremental:
        save_t: Thread = every(config.observer.save, save, model)
        save_t.start()

    # Start the threads
    fed_t.start()
    run_t.start()


if __name__ == '__main__':
    main()
