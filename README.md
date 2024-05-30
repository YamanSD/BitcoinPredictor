# BitcoinPredictor 📈

![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![Kaggle](https://img.shields.io/badge/Kaggle-035a7d?style=for-the-badge&logo=kaggle&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)

![main](./screenshots/main.png)

## Project Overview & Technologies

- This project aims to predict the topic of a given news article using Latent Semantic Analysis (LSA) and Latent Dirichlet Allocation (LDA). 
- It also compares the performance of both algorithms using t-Distributed Stochastic Neighbor Embedding (TSNE) to plot the clusters. 
- The project leverages the [Newspaper3K library](https://github.com/codelucas/newspaper) to fetch news articles, Flask for the web interface, and [FinBERT](https://huggingface.co/ProsusAI/finbert) for financial sentiment analysis. 
- To ensure efficiency, multiprocessing is used to run each model as a separate process.

## Features

- **Topic Prediction**: Predicts the topic of a given news article using LSA and LDA by spitting out predicted keywords.
- **Web Interface**: Intuitive web interface to interact with the Flask server.
- **Multiprocessing**: Runs each model as a separate process to enhance efficiency.
- **Sentiment Analysis**: Uses FinBERT API to predict the sentiment of the news article.
- **Automatic Data Fetching**: Uses Kaggle's CroissantML format to automatically download and store the data in parquet format.

## Installation

1. Create a `config.json` file in the root directory of the project. The structure of the file must match that of `example_config.json`.
2. [Optional] Create a virtual python environment and initialize it.
3. Install the project requirements by running the following command `pip install -r requirements.txt`.
    - Note that this project requires Python 3.11.8 and on some systems you must run `pip3 install -r requirements.txt`.

## t-SNE Results

[Bokeh](https://bokeh.org/) was used to generate the following plots:

- [LSA](lsa.html): 

![lsa](./screenshots/lsa.png)

- [LDA](lda.html): 

![lda](./screenshots/lda.png)

Unsurprisingly, LDA does a better job at separating the articles into clusters.

## Usage

1. Change into the project directory and start the server by `python .` or `python3 .`
2. Access the web interface at `http://127.0.0.1:{PORT FROM config.json}`.

## Examples

- This example uses the following [link](https://www.fxstreet.com/cryptocurrencies/news/top-3-price-prediction-bitcoin-ethereum-ripple-facing-correction-after-etfs-led-rally-202405300755): 

![ex0](./screenshots/ex0.png)

- This example uses the following [link](https://cointelegraph.com/news/bitcoin-etfs-traditional-finance-investments), which blocks the download:
  
![ex0](./screenshots/ex1.png)

- This example uses the following [link](https://www.coindesk.com/markets/2024/05/23/bitcoin-drops-below-68k-ether-slumps-in-sudden-crypto-sell-off-as-eth-etf-decision-looms/):

![ex0](./screenshots/ex2.png)

## License

MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
