try:
    from colorama import just_fix_windows_console
except ImportError:
    # Must be defined
    def just_fix_windows_console():
        return
    pass

from Config import config
from Data import clean_dxy, clean_fedFunds, clean_bitcoin


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
    df = clean_dxy()
    df1 = clean_fedFunds()
    df2 = clean_bitcoin()[0]
    print(df.head())
    print(df1.head())
    print(df2.head())
    return


if __name__ == '__main__':
    main()
