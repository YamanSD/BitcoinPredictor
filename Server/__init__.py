from flask import Flask, Response
from flask_cors import CORS, cross_origin
from time import sleep, strftime

from Config import config


app: Flask = Flask(__name__)
cors: CORS = CORS(app)


@app.route('/events')
@cross_origin()
def events() -> Response:
    def generate():
        while True:
            yield 'data: {}\n\n'.format(strftime('%H:%M:%S'))
            sleep(1)

    return Response(generate(), mimetype='text/event-stream')


def start() -> None:
    app.run(debug=True, port=config.server.port)
