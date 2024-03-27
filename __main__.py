try:
    from colorama import just_fix_windows_console
except ImportError:
    # Must be defined
    def just_fix_windows_console():
        return
    pass

from Config import config
from Data import load_clean_dxy, load_clean_bitcoin, load_clean_fedFunds


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
    df = load_clean_fedFunds()
    print(df.shape)
    return


if __name__ == '__main__':
    main()
