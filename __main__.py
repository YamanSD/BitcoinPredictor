import asyncio

from Sentiment import query, SentimentRequest
from Crawler import spider


def main() -> None:
    # output = query(SentimentRequest(
    #     inputs=["Bitcoin is a scam LOL. Fell 40% overnight.", "Bitcoin skyrocketed to 50k!"],
    # ))
    #
    # print(type(output), output)

    l = asyncio.run(spider.query_text(
        keywords="What is an apple",
        max_results=1028
    ))
    print(len(l))
    return


if __name__ == '__main__':
    main()
