from concurrent.futures import ThreadPoolExecutor, Future
from datetime import datetime, timedelta
from flask import Flask, Response
from flask_cors import CORS, cross_origin
from json import dumps
from multiprocessing import Process, Queue
from numpy import ndarray
from threading import Thread
from time import sleep, time
from pandas import options
from sklearn.pipeline import Pipeline

import Train
from Config import config
from Observer import observe, Observation, fed_rate_key
from Sentiment import general_sentiment, SentimentResponse
from Utils import every, join_jsons, format_sse


app: Flask = Flask(__name__)
cors: CORS = CORS(app)

# General federal rate (For testing only, due to API limits)
g_fed_rate: dict = {
    fed_rate_key: 5.44
}
lr_q: Queue = Queue()
lgr_q: Queue = Queue()
elr_q: Queue = Queue()
observation_q: Queue = Queue()
lr_model: Pipeline = Train.lr_load()
lgr_model: Pipeline = Train.lgr_load()
elr_model: Pipeline = Train.elr_load()


def format_sse_msg(
        ob0: Observation,
        ob1: Observation,
        pred: ndarray,
        name: str,
        logistic: bool
) -> str:
    """

    Args:
        ob0: Previous observation.
        ob1: Current observation.
        pred: Predicted state based on current observation.
        name: Name of the model.
        logistic: True for logistic learning.

    Returns:
        Message suitable for use in SSE.

    """
    global observation_q

    # Data object
    data: dict = {
        name: {
            "prev": {
                "timestamp": str(ob0.timestamp),
                "open": ob0.open,
                "close": ob0.close,
                "high": ob0.high,
                "low": ob0.low,
            },
        }
    }

    # Data to be formatted to JSON
    if logistic:
        pred_val: float = float(pred)
        direction: float = ob1.open + (1 if pred_val else -1)

        data[name]["current"] = {
            "timestamp": str(ob1.timestamp),
            "open": ob1.open,
            "p_close": direction,
            "p_high": direction,
            "p_low": direction
        }
    else:
        data[name]["current"] = {
            "timestamp": str(ob1.timestamp),
            "open": ob1.open,
            "p_close": pred[0][0],
            "p_high": pred[0][1],
            "p_low": pred[0][2]
        }

    return dumps(data)


def run(
        name: str,
        pipeline: Pipeline,
        fed_rate: dict,
        q: Queue,
        logistic: bool = False,
) -> None:
    """

    Args:
        name: Name of the model.
        pipeline: Model pipeline to use for prediction.
        fed_rate: Federal rate that is already in use.
        q: Queue that holds the multiprocessing output.
        logistic: True for logistic learning.

    """

    # Loop indefinitely & push to queue
    while True:
        # Initial time
        t0: time = time()

        # Type declarations
        prev_observation: Observation
        cur_observation: Observation
        sentiment: SentimentResponse

        # Read the observations from the observation queue
        prev_observation, cur_observation, sentiment = observation_q.get()

        # Set back to false
        fed_rate[fed_rate_key] = cur_observation.fed_rate

        cur_observation.apply_sentiment(sentiment)

        y_pred = pipeline.predict(
            cur_observation.to_df()
        )

        # yield the predicted close, high, low to the queue
        q.put_nowait(
            format_sse_msg(prev_observation, cur_observation, y_pred, name, logistic)
        )

        # Time after execution
        t1: time = time()

        # If the difference is less than 60s
        if t1 - t0 < 60:
            # Sleep for the remainder of the time
            sleep(abs(60 - t1 + t0))


def total_observation(fed_rate: dict) -> None:
    """

    Args:
        fed_rate: Federal rate that is already in use.

    """
    global observation_q

    # Loop indefinitely & push to queue
    while True:
        # Initial time
        t0: time = time()

        with ThreadPoolExecutor(max_workers=2) as executor:
            observation_fu: Future = executor.submit(observe, fed_rate)
            sentiment_fu: Future = executor.submit(general_sentiment)

            prev_observation, cur_observation = observation_fu.result()
            sentiment: SentimentResponse = sentiment_fu.result()

        # Insert one observation for each model
        for i in range(3):
            observation_q.put_nowait((prev_observation, cur_observation, sentiment))

        # Time after execution
        t1: time = time()

        # If the difference is less than 60s
        if t1 - t0 < 60:
            # Sleep for the remainder of the time
            sleep(abs(60 - t1 + t0))


def set_observe(fed_rate: dict) -> None:
    """

    Sets the observation flag.

    """
    del fed_rate[fed_rate_key]


@app.route('/info')
@cross_origin()
def info() -> Response:
    def generate() -> str:
        global lr_q, elr_q, lgr_q
        return format_sse(
            join_jsons(
                q.get() for q in (lr_q, elr_q, lgr_q)
            )
        )

    # Continuously take output from lr queue
    return Response(generate(), mimetype='text/event-stream')


def start_model(
    name: str,
    pipeline: Pipeline,
    fed_rate: dict,
    q: Queue,
    logistic: bool = False,
) -> None:
    """

    Starts the model process.

    Args:
        name: String that holds the prediction values in the SSE response.
        pipeline: Model pipeline to use for prediction.
        fed_rate: Federal rate that is already in use.
        q: Queue that holds the multiprocessing output.
        logistic: True for logistic learning.

    """
    # Start the run cycle
    run(name, pipeline, fed_rate, q, logistic)


def start() -> None:
    global g_fed_rate, lr_q, lr_model, lgr_q, lgr_model, elr_q, elr_model

    options.display.max_columns = None

    # Synchronize the clock
    t0: datetime = datetime.utcnow()
    t1: datetime = t0.replace(second=0, microsecond=0) + timedelta(minutes=1)
    sleep((t1 - t0).total_seconds())

    fed_t: Thread = every(
        86_400 // (len(config.alpha_vantage.keys) * config.alpha_vantage.limit),
        set_observe,
        g_fed_rate
    )

    # Start the threads
    fed_t.start()

    # Start the observation listener
    Process(target=total_observation, args=(g_fed_rate,)).start()

    # Start the LR model process
    Process(target=start_model, args=("lr", lr_model, g_fed_rate, lr_q, False)).start()

    # Start the LGR model process
    Process(target=start_model, args=("lgr", lgr_model, g_fed_rate, lgr_q, True)).start()

    # Start the ELR model process
    Process(target=start_model, args=("elr", elr_model, g_fed_rate, elr_q, False)).start()

    # Do not use reloaded as it starts 2 separate processes (lots of headache)
    app.run(debug=True, port=config.server.port, use_reloader=False)
