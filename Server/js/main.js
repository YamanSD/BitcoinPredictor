// Actual trace plot
const actual = {
    x: [],
    close: [],
    decreasing: {
        line: {
            color: '#FF0000'
        }
    },
    high: [],
    increasing: {
        line: {
            color: '#008000'
        }
    },
    line: {
        color: 'white'
    },
    low: [],
    open: [],
    type: 'candlestick',
    name: 'Actual',
    xaxis: 'x',
    yaxis: 'y',
};

// Predicted trace plot
const predicted = {
  x: [],
  close: [],
  high: [],
  decreasing: {line: {color: '#FF9900'}},
  increasing: {line: {color: '#17BECF'}},
  line: {color: 'rgba(31,119,180,1)'},
  low: [],
  open: [],
  type: 'candlestick',
  name: 'Predicted',
  xaxis: 'x',
  yaxis: 'y'
};

// Traces of the candle sticks for all graphs
const traces = [actual, predicted];

// https://plotly.com/javascript/reference/layout/#layout-paper_bgcolor
const layout = {
    title: {
        text: "Linear Regression",
        font: {
            color: "green"
        }
    },
    dragmode: 'zoom',
    margin: {
        r: 10,
        t: 25,
        b: 40,
        l: 60
    },
    showlegend: true,
    xaxis: {
        gridcolor: 'rgb(100, 100, 100)',
        tickfont: {
            color: 'rgb(255, 255, 255)'
        },
        autorange: true,
        domain: [0, 1],
        rangeslider: {
            bgcolor: 'rgba(0, 0, 0)'
        },
        title: 'Date',
        type: 'date'
    },
    modebar: {
        color: 'rgb(100, 100, 100)',
    },
    font: {
        family: 'Courier New, monospace',
        color: '#7f7f7f'
    },
    paper_bgcolor: "rgba(0, 0, 0)",
    plot_bgcolor: "rgba(0, 0, 0)",
    yaxis: {
        gridcolor: 'rgb(100, 100, 100)',
        tickfont: {
            color: 'rgb(255, 255, 255)'
        },
        autorange: true,
        domain: [0, 1],
        type: 'linear'
    },
    gap: 0
};

// Create the plots
Plotly.newPlot('lr_chart', traces, layout);
Plotly.newPlot('lgr_chart', traces, {
    ...layout, title: {
        ...layout.title,
        text: "Logistic Regression"
    }
});
Plotly.newPlot('elr_chart', traces, {
    ...layout, title: {
        ...layout.title,
        text: "Elastic Net"
    }
});


/**
 * Appends the given information into the specified candle stick chart.
 *
 * @param chart {"lr", "lgr", "elr"} Chart to update.
 * @param timestamp {string} String of the candle stick.
 * @param open {number} Open of the candle stick.
 * @param high {number} High of the candle stick.
 * @param low {number} Low of the candle stick.
 * @param close {number} of the candle stick.
 * @param type {0, 1} Type of the candle stick to plot. 0 for actual, 1 for predicted.
 */
function addData(chart, timestamp, open, high, low, close, type) {
    // Update the chart with new data
    Plotly.extendTraces(
        `${chart}_chart`,
        {
            x: [[new Date(timestamp.replace(' ', 'T'))]],
            close: [[close]],
            high: [[high]],
            low: [[low]],
            open: [[open]],
        },
        [type]
    );
}


const lrSource = new EventSource('http://127.0.0.1:8081/lr');
const lgrSource = new EventSource('http://127.0.0.1:8081/lgr');
const elrSource = new EventSource('http://127.0.0.1:8081/elr');

// Listen to the events
lrSource.onmessage = function(event) {
    /**
     * @type {{
     *     prev: {
     *         open: number,
     *         close: number,
     *         high: number,
     *         low: number,
     *         timestamp: string,
     *     },
     *     current: {
     *         open: number,
     *         p_close: number,
     *         p_high: number,
     *         p_low: number,
     *         timestamp: string,
     *     }
     * }}
     */
    const data = JSON.parse(event.data);
    const {prev, current} = data

    addData('lr', prev.timestamp, prev.open, prev.high, prev.low, prev.close, 0);
    addData('lr', current.timestamp, current.open, current.p_high, current.p_low, current.p_close, 1);
};

// Listen to the events
lgrSource.onmessage = function(event) {
    /**
     * @type {{
     *     prev: {
     *         open: number,
     *         close: number,
     *         high: number,
     *         low: number,
     *         timestamp: string,
     *     },
     *     current: {
     *         open: number,
     *         p_close: number,
     *         p_high: number,
     *         p_low: number,
     *         timestamp: string,
     *     }
     * }}
     */
    const data = JSON.parse(event.data);
    const {prev, current} = data

    // TODO make the prev-observation scatter a candle stick chart and the predicted a bar graph showing increase, decrease or neutral
    console.log(data)

    // addData('lgr', prev.timestamp, prev.open, prev.high, prev.low, prev.close, 0);
    // addData('lgr', current.timestamp, current.open, current.p_high, current.p_low, current.p_close, 1);
};

// Listen to the events
elrSource.onmessage = function(event) {
    /**
     * @type {{
     *     prev: {
     *         open: number,
     *         close: number,
     *         high: number,
     *         low: number,
     *         timestamp: string,
     *     },
     *     current: {
     *         open: number,
     *         p_close: number,
     *         p_high: number,
     *         p_low: number,
     *         timestamp: string,
     *     }
     * }}
     */
    const data = JSON.parse(event.data);
    const {prev, current} = data

    addData('elr', prev.timestamp, prev.open, prev.high, prev.low, prev.close, 0);
    addData('elr', current.timestamp, current.open, current.p_high, current.p_low, current.p_close, 1);
};
