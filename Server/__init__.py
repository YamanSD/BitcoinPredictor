from concurrent.futures import ThreadPoolExecutor, wait, Future
from flask import Flask, Response
from flask_cors import CORS, cross_origin
from json import dumps
from multiprocessing import Process, Queue
from numpy import ndarray
from threading import Thread
from time import sleep
from pandas import options
from sklearn.pipeline import Pipeline

import Train
from Config import config
from Observer import observe, Observation, fed_rate_key
from Sentiment import general_sentiment, SentimentResponse
from Utils import every


app: Flask = Flask(__name__)
cors: CORS = CORS(app)

# Load the model from the files
lr_model: Pipeline = Train.lr_load()
lgr_model: Pipeline = Train.lgr_load()
elr_model: Pipeline = Train.elr_load()
g_fed_rate: dict = {}


def format_sse_msg(
        ob0: Observation,
        ob1: Observation,
        pred: ndarray,
        logistic: bool,
) -> str:
    """

    Args:
        ob0: Previous observation.
        ob1: Current observation.
        pred: Predicted state based on current observation.
        logistic: True for logistic model.

    Returns:
        Message suitable for use in SSE.

    """
    # Data to be formatted to JSON
    if logistic:
        data: dict = {
            "prev": {
                "timestamp": str(ob0.timestamp),
                "open": ob0.open,
                "close": ob0.close,
                "high": ob0.high,
                "low": ob0.low,
            },
            "current": {
                "timestamp": str(ob1.timestamp),
                "open": ob1.open,
                "p_direction": float(pred)
            }
        }
    else:
        data: dict = {
            "prev": {
                "timestamp": str(ob0.timestamp),
                "open": ob0.open,
                "close": ob0.close,
                "high": ob0.high,
                "low": ob0.low,
            },
            "current": {
                "timestamp": str(ob1.timestamp),
                "open": ob1.open,
                "p_close": pred[0][0],
                "p_high": pred[0][1],
                "p_low": pred[0][2]
            }
        }

    return f"data: {dumps(data)}\n\n"


def run(
        pipeline: Pipeline,
        fed_rate: dict,
        logistic: bool = False,
        q: Queue = None
) -> str:
    """

    Args:
        pipeline: Model pipeline to use for prediction.
        fed_rate: Federal rate that is already in use.
        logistic: True for logistic learning.
        q: Queue that holds the multiprocessing output.

    """
    if q is None:
        q = Queue()
        p: Process = Process(target=run, args=(pipeline, fed_rate, logistic, q))
        p.start()

        res: str = q.get(block=True, timeout=None)
        p.join()

        return res

    # Sleep for 60 seconds
    sleep(60)

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

    # Apply the sentiment to the observation
    cur_observation.apply_sentiment(sentiment)

    y_pred = pipeline.predict(
        cur_observation.to_df()
    )

    # yield the predicted close, high, low
    q.put(format_sse_msg(prev_observation, cur_observation, y_pred, logistic))


def set_observe(fed_rate: dict) -> None:
    """

    Sets the observation flag.

    """
    del fed_rate[fed_rate_key]


@app.route('/lr')
@cross_origin()
def lr() -> Response:
    global lr_model, g_fed_rate
    return Response(run(lr_model, g_fed_rate, False), mimetype='text/event-stream')


@app.route('/lgr')
@cross_origin()
def lgr() -> Response:
    global lgr_model, g_fed_rate
    return Response(run(lgr_model, g_fed_rate, True), mimetype='text/event-stream')


@app.route('/elr')
@cross_origin()
def elr() -> Response:
    global elr_model, g_fed_rate
    return Response(run(elr_model, g_fed_rate, False), mimetype='text/event-stream')


def start() -> None:
    global lr_model

    options.display.max_columns = None

    fed_t: Thread = every(
        86_400 // (len(config.alpha_vantage.keys) * config.alpha_vantage.limit),
        set_observe,
        g_fed_rate
    )

    # Start the threads
    fed_t.start()

    app.run(debug=True, port=config.server.port)
