from Sentiment import query


def main() -> None:
    output = query({
        "inputs": ["Bitcoin is a scam LOL. Fell 40% overnight.", "Bitcoin skyrocketed to 50k!"],
    })

    print(type(output), output)
    return


if __name__ == '__main__':
    main()
