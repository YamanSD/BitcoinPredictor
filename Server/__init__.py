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
from Sentiment.sentiment import apply_sentiment
from Utils import every


app: Flask = Flask(__name__)
cors: CORS = CORS(app)

# General federal rate
g_fed_rate: dict = {
    fed_rate_key: 5.44
}
lr_q: Queue = Queue()
lgr_q: Queue = Queue()
elr_q: Queue = Queue()
lr_establish = elr_establish = lgr_establish = False
lr_model: Pipeline = Train.lr_load()
lgr_model: Pipeline = Train.lgr_load()
elr_model: Pipeline = Train.elr_load()


def run(
        pipeline: Pipeline,
        fed_rate: dict,
        q: Queue,
        logistic: bool = False,
) -> None:
    """

    Args:
        pipeline: Model pipeline to use for prediction.
        fed_rate: Federal rate that is already in use.
        q: Queue that holds the multiprocessing output.
        logistic: True for logistic learning.

    """

    def format_sse_msg(
            ob0: Observation,
            ob1: Observation,
            pred: ndarray,
    ) -> str:
        """

        Args:
            ob0: Previous observation.
            ob1: Current observation.
            pred: Predicted state based on current observation.

        Returns:
            Message suitable for use in SSE.

        """
        nonlocal logistic

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

    # Loop indefinitely & push to queue
    while True:
        # Initial time
        t0: time = time()

        with ThreadPoolExecutor(max_workers=2) as executor:
            observation_fu: Future = executor.submit(observe, fed_rate)
            sentiment_fu: Future = executor.submit(general_sentiment)

            # Type declarations
            prev_observation: Observation
            cur_observation: Observation
            sentiment: SentimentResponse

            prev_observation, cur_observation = observation_fu.result()
            sentiment: SentimentResponse = sentiment_fu.result()

        # Set back to false
        fed_rate[fed_rate_key] = cur_observation.fed_rate

        y_pred = pipeline.predict(
            cur_observation.to_df()
        )

        # Apply the sentiment to the prediction
        apply_sentiment(y_pred, sentiment, logistic)

        holder: str = format_sse_msg(prev_observation, cur_observation, y_pred)

        # yield the predicted close, high, low to the queue
        q.put_nowait(holder)

        # Time after execution
        t1: time = time()

        # If the difference is less than 59s (additional second for processing time)
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
    global lr_q, lr_establish

    if not lr_establish:
        lr_establish = True
        return Response("", mimetype='text/plain')

    # Continuously take output from lr queue
    return Response(lr_q.get(), mimetype='text/event-stream')


@app.route('/lgr')
@cross_origin()
def lgr() -> Response:
    global lgr_q, lgr_establish

    if not lgr_establish:
        lgr_establish = True
        return Response("", mimetype='text/plain')

    # Continuously take output from lr queue
    return Response(lgr_q.get(), mimetype='text/event-stream')


@app.route('/elr')
@cross_origin()
def elr() -> Response:
    global elr_q, elr_establish

    if not elr_establish:
        elr_establish = True
        return Response("", mimetype='text/plain')

    # Continuously take output from lr queue
    return Response(elr_q.get(), mimetype='text/event-stream')


def start_model(
    pipeline: Pipeline,
    fed_rate: dict,
    q: Queue,
    logistic: bool = False,
) -> None:
    """

    Starts the model process.

    Args:
        pipeline: Model pipeline to use for prediction.
        fed_rate: Federal rate that is already in use.
        q: Queue that holds the multiprocessing output.
        logistic: True for logistic learning.

    """
    # Start the run cycle
    run(pipeline, fed_rate, q, logistic)


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

    # Start the LR model process
    Process(target=start_model, args=(lr_model, g_fed_rate, lr_q, False)).start()

    # Start the LGR model process
    Process(target=start_model, args=(lgr_model, g_fed_rate, lgr_q, True)).start()

    # Start the ELR model process
    Process(target=start_model, args=(elr_model, g_fed_rate, elr_q, False)).start()

    # Do not use reloaded as it starts 2 separate processes (lots of headache)
    app.run(debug=True, port=config.server.port, use_reloader=False)
