from argparse import ArgumentParser


class Options:

    def __init__(self):
        self._init_parser()

    def _init_parser(self):
        usage = 'bin/py_twitter_analysis\n' + \
                '-i|--input-file <tweets_file.json>   : File of tweets, one per line\n' +\
                '[-m|--max-iterations <max loops>]    : D-rank iteration roof value (default: 20)\n' +\
                '[-w|--weight <weight factor value>]  : D-rank weighting factor (default: 0.2)' + \
                '[-c|--count <tweet_count_limit>]     : Only consider up to this many tweets (default: -1, all)\n' + \
                '[-d|--verbose]                       : Verbose debugging flag\n'

        self.parser = ArgumentParser(usage=usage)
        self.parser.add_argument('-i',
                                 '--input-file',
                                 default='data/tweets.json',
                                 dest='tweets_file',
                                 help='A file of tweets, one JSON object per line')
        self.parser.add_argument('-m',
                                 '--max-iterations',
                                 default='20',
                                 dest='max_iterations',
                                 help='Maximum number of iterations for Duan-rank calculation')
        self.parser.add_argument('-w',
                                 '--weight',
                                 default='0.2',
                                 dest='d_rank_weight_factor',
                                 help='Weight factor value for Duan-rank calculation')
        self.parser.add_argument('-c',
                                 '--count',
                                 default='-1',
                                 dest='tweet_count',
                                 help='Limit the tweets to consider to this many')
        self.parser.add_argument('-d',
                                 '--verbose',
                                 action='store_true',
                                 dest='debug',
                                 help='Turns verbose logging on')

    def parse(self, args=None):
        return self.parser.parse_args(args)
