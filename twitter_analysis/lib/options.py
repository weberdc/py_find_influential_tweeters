from argparse import ArgumentParser


class Options:

    def __init__(self):
        self._init_parser()

    def _init_parser(self):
        usage = 'bin/py_twitter_analysis -i <tweets_file.json> [--verbose] [--count <tweet_count_limit>]'
        self.parser = ArgumentParser(usage=usage)
        self.parser.add_argument('-i',
                                 '--input-file',
                                 default='data/tweets.json',
                                 dest='tweets_file',
                                 help='A file of tweets, one JSON object per line')
        self.parser.add_argument('-d',
                                 '--verbose',
                                 action='store_true',
                                 dest='debug',
                                 help='Turns verbose logging on')
        self.parser.add_argument('-c',
                                 '--count',
                                 default='-1',
                                 dest='tweet_count',
                                 help='Limit the tweets to consider to this many')

    def parse(self, args=None):
        return self.parser.parse_args(args)
