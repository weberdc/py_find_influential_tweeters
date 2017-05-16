from argparse import ArgumentParser


class Options:

    def __init__(self):
        self._init_parser()

    def _init_parser(self):
        usage = 'bin/py_twitter_analysis\n' + \
                '    -i|--input-file <tweets_file.json>  : File of tweets, one per line\n' +\
                '    [-x|--max-iterations <max loops>]   : D-rank iteration roof value (default: 20)\n' +\
                '    [-w|--weight <weight factor value>] : D-rank weighting factor (default: 0.2)\n' + \
                '    [-c|--count <tweet_count_limit>]    : Consider up to this many tweets (default: -1 = all)\n' + \
                '    [--rt_weight <rt_weight>]           : PA weighting for retweets (default: 1.0)\n' + \
                '    [--qu_weight <qu_weight>]           : PA weighting for quote (default: 2.0)\n' + \
                '    [--re_weight <re_weight>]           : PA weighting for replies (default: 3.0)\n' + \
                '    [--fav_weight <fav_weight>]         : PA weighting for favourites (default: 1.0)\n' + \
                '    [-v|--verbose]                      : Verbose debugging flag (default: off)\n'

        self.parser = ArgumentParser(usage=usage)
        self.parser.add_argument('-i',
                                 '--input-file',
                                 default='data/tweets.json',
                                 dest='tweets_file',
                                 help='A file of tweets, one JSON object per line')
        self.parser.add_argument('-x',
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
        self.parser.add_argument('-v',
                                 '--verbose',
                                 action='store_true',
                                 dest='debug',
                                 help='Turns verbose logging on')
        self.parser.add_argument('--rt-weight',
                                 default=1.0,
                                 dest='rt_weight',
                                 help='Post/Activity ratio weighting for retweets')
        self.parser.add_argument('--qu-weight',
                                 default=2.0,
                                 dest='qu_weight',
                                 help='Post/Activity ratio weighting for quotes')
        self.parser.add_argument('--re-weight',
                                 default=3.0,
                                 dest='re_weight',
                                 help='Post/Activity ratio weighting for replies')
        self.parser.add_argument('--fav-weight',
                                 default=1.0,
                                 dest='fav_weight',
                                 help='Post/Activity ratio weighting for favourites')

    def parse(self, args=None):
        return self.parser.parse_args(args)
