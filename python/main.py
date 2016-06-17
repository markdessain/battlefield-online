

from loader import TweetLoader
from enricher import TweetEnricher


if __name__ == '__main__':

    queries = [
        '#bf1',
        '#battlefield1',
        '#battlefieldone',
        '@battlefield'
    ]
    files = TweetLoader().load(queries)

    TweetEnricher().enrich(files)
