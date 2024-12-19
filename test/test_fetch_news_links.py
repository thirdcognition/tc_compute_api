from source.helpers.panel import fetch_news_links, GoogleNewsConfig


def test_fetch_news_links():
    config = GoogleNewsConfig(
        lang="en", country="US", topic="technology", since="1d", articles=5
    )
    news_links = fetch_news_links(config)
    print(news_links)


if __name__ == "__main__":
    test_fetch_news_links()
