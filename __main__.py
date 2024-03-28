try:
    from colorama import just_fix_windows_console
except ImportError:
    # Must be defined
    def just_fix_windows_console():
        return


    pass

from Config import config
from Data import get_data


def main() -> None:
    # Enable ANSI support on Windows
    just_fix_windows_console()

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
    df = get_data()

    print(df.shape)
    print(df.columns)

    # df1 = load_clean_fed_funds()
    #
    # print(df.head(), df.tail(), df.columns, df.shape)
    # print(df1.head(), df1.tail(), df1.columns, df1.shape)
    # print(df.index.is_unique)
    # print(df1.index.is_unique)
    # return


if __name__ == '__main__':
    main()
