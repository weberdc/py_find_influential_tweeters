import json
import sys

from lib import Options
from lib import TwitterAnalysis


if __name__ == '__main__':
    options = Options()
    opts = options.parse(sys.argv[1:])

    print("Reading %s" % opts.tweets_file)

    with open(opts.tweets_file) as f:
        # for l in f.readlines():
        #     print(json.loads(l.rstrip('\n')))
        tweets = [json.loads(l.rstrip('\n')) for l in f.readlines()]

    print("Read %d tweets" % len(tweets))

    analyser = TwitterAnalysis(opts)

    analyser.analyse(tweets)
