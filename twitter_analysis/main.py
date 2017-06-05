import datetime
import json
import sys

from lib import Options
from lib import TwitterAnalysis


def timestamp():
    now = datetime.datetime.now()
    return "%d-%02d-%02d %02d:%02d:%02d" % (now.year, now.month, now.day, now.hour, now.minute, now.second)


if __name__ == '__main__':
    options = Options()
    opts = options.parse(sys.argv[1:])

    print("Reading %s" % opts.tweets_file)

    tweets = []
    with open(opts.tweets_file) as f:
        # tweets = [json.loads(l.rstrip('\n')) for l in f.readlines()]
        lines = f.readlines()
        batch_size = (len(lines) / 10)
        count = 0
        for l in lines:
            count += 1
            if int(count % batch_size) == 0:
                print("[%s] Read %d lines..." % (timestamp(), count))
            tweets.append(json.loads(l.rstrip('\n')))

    print("[%s] Read %d tweets" % (timestamp(), len(tweets)))

    analyser = TwitterAnalysis(opts)

    analyser.analyse(tweets)

    print("Finished at %s" % timestamp())
