import config
from loader import TweetLoader
from enricher import TweetEnricher


if __name__ == '__main__':

    queries = config.TWITTER_SEARCH

    files = TweetLoader().load(queries)
    TweetEnricher().enrich(files)
