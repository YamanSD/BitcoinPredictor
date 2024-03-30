from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from matplotlib import pyplot as plt

try:
    from colorama import just_fix_windows_console
except ImportError:
    # Must be defined
    def just_fix_windows_console():
        return


from pandas import options, DataFrame

from Config import config
from Data import get_data
from Observer import *
import Train


def main() -> None:
    # Enable ANSI support on Windows
    just_fix_windows_console()
    options.display.max_columns = None

    # output = query(SentimentRequest(
    #     inputs=["Bitcoin is a scam LOL. Fell 40% overnight.", "Bitcoin skyrocketed to 50k!"],
    # ))
    #
    # print(type(output), output)

    # l = asyncio.run(spider.query_text(
    #     keywords="What is an apple",
    #     max_results=1028,
    # ))
    # print(len(l))

    # t = loader.load_dxy()
    # print(t, type(t))

    # df = load_clean_dxy()
    # dfb = load_clean_bitcoin()
    # print(df.shape, dfb.shape)
    # df = get_data()
    #
    # print(df.shape)
    # print(df.columns)
    # X, y = get_split_data()
    # scaler: StandardScaler = StandardScaler().set_output(transform="pandas")
    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, shuffle=False)
    #
    # X_train = scaler.fit_transform(X_train)
    # X_test = scaler.transform(X_test)
    #
    # # print(lr_test(4))    print(m)
    # m = elr_load()
    # y_pred = DataFrame(m.predict(X_test), columns=["high", "low", "close"])
    # print(r2_score(y_test, y_pred))
    #
    # plt.plot(X_test.index, y_pred["close"], color='r')
    # plt.plot(X_test.index, y_test["close"], color='g')
    # plt.savefig("g.svg")

    # BTC
    # FNG
    # Federal Fund
    # DXY
    # Sentiment

    # number_of_trades
    # quote_asset_volume
    # taker_buy_base_asset_volume
    # taker_buy_quote_asset_volume
    # m = Train.lgr_train()
    # https://livecoinwatch.github.io/lcw-api-docs/#coinscontract
    # get_data(True)
    # m = Train.lgr_train()
    # print(m[1])

    #, 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume'

    # print(
    #     df[['number_of_trades']]
    # )
    # print((df['volume'] / df['close']))
    r = dxy_fetch()

    print(r)


if __name__ == '__main__':
    main()
