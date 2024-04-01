const eventSource = new EventSource('http://127.0.0.1:8081/lr');

// Listen to the events
eventSource.onmessage = function(event) {
    console.log("P")
    const eventsDiv = document.getElementById('test_div');
    eventsDiv.innerHTML += '<p>New event received: ' + event.data + '</p>';
};

let actual = {
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

let predicted = {
  x: [],
  close: [],
  decreasing: {line: {color: '#7F7F7F'}},
  high: [],
  increasing: {line: {color: '#17BECF'}},
  line: {color: 'rgba(31,119,180,1)'},
  low: [],
  open: [],
  type: 'candlestick',
  name: 'Predicted',
  xaxis: 'x',
  yaxis: 'y'
};

let data = [actual, predicted];

// https://plotly.com/javascript/reference/layout/#layout-paper_bgcolor
let layout = {
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
        range: ['2017-01-03 12:00', '2017-02-15 12:00'],
        rangeslider: {
            range: ['2017-01-03 12:00', '2017-02-15 12:00'],
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
        range: [114.609999778, 137.410004222],
        type: 'linear'
    },
    gap: 0
};

// ignore
// Plotly.newPlot('lr_chart', data, layout);
// Plotly.newPlot('lgr_chart', data, {
//     ...layout, title: {
//         ...layout.title,
//         text: "Logistic Regression"
//     }
// });
// Plotly.newPlot('elr_chart', data, {
//     ...layout, title: {
//         ...layout.title,
//         text: "Elastic Net"
//     }
// });

let c = 0

// Function to add new candlestick data
function addCandlestickData(open, high, low, close) {
    d = new Date()
    d.setMilliseconds(0)
    d.setSeconds(0)
    d.setMinutes(d.getMinutes() + c)
    c++;

    let newData = {
        x: [[d]],
        close: [[close]],
        high: [[high]],
        low: [[low]],
        open: [[open]]
    };

    Plotly.extendTraces('lr_chart', newData, [0]); // Update the chart with new data
}

// Update the chart with random candlestick data every second
function updateChart() {
    let open = Math.random() * 100;
    let high = open + Math.random() * 100;
    let low = open - Math.random() * 100;
    let close = low + Math.random() * (high - low);

    addCandlestickData(open, high, low, close);
}

// setInterval(updateChart, 1_000);

