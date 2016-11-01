import unicodedata
import operator

from pprint import pprint


def get_or(m, k, v):
    if k not in m:
        m[k] = v
    return m[k]


def update_count(m, k, v):
    m[k] = max(v, get_or(m, k, v))


def make_safe(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')


class Kudos:
    """
    Structure to capture kudos of an individual
    data.'profile'.{screen_name,followers_count,friends_count,total_tweet_count,corpus_tweet_count}
        .'my_quoted_tweets'.quoted_tweet_id.[(quoting_user, quote_tweet_id)]
        .'my_retweets'.retweeted_tweet_id.[retweeting_user]
        .'mentions_of_me'.mentioning_user.[mentioning_tweet]
        .'replies_to'.original_tweet_id.replying_user_id.[reply_tweet_id]
        .'replies_from'.replying_user_id.[(original_tweet_id, reply_tweet_id)]
        .'favourited'.favourited_tweet_id.count
    """
    def __init__(self):
        self.data = {}
        self.tweets_db = {}

    def set_tweets(self, tweets_db): self.tweets_db = tweets_db

    def h_index(self):
        if 'my_retweets' not in self.data:
            return 0

        # turn the retweets into a list of tuples (tweet_id, list of tweeters)
        sorted_retweets_list = sorted(self.data['my_retweets'].items(), key=operator.itemgetter(1))

        h_index = 0
        i = len(sorted_retweets_list) - 1
        while i >= 0:
            num_retweeters_for_this_tweet = len(sorted_retweets_list[i][1])
            # print("num retweeters: %s" % str(sorted_retweets_list[i][1]))
            if num_retweeters_for_this_tweet < h_index + 1:
                break
            h_index += 1
            i -= 1

        return h_index

    def ir_ratio(self):
        if 'profile' not in self.data or \
                ('my_retweets' not in self.data and
                 'mentions_of_me' not in self.data):
            return 0

        unique_retweeters = set()
        if 'my_retweets' in self.data:
            for retweeters in self.data['my_retweets']:
                unique_retweeters = unique_retweeters.union(self.data['my_retweets'][retweeters])

        unique_mentioners = len(self.data['mentions_of_me']) if 'mentions_of_me' in self.data else 0

        if 'profile' not in self.data:
            pprint(self.data)

        followers_count = self.data['profile']['followers_count']

        return (len(unique_retweeters) + unique_mentioners) / float(followers_count) if followers_count else 0

    def rm_ratio(self):
        if 'profile' not in self.data or \
                ('my_retweets' not in self.data and
                 'mentions_of_me' not in self.data):
            return 0

        retweet_count = len(self.data['my_retweets']) if 'my_retweets' in self.data else 0

        mention_count = 0
        if 'mentions_of_me' in self.data:
            for mentioner in self.data['mentions_of_me']:
                mention_count += len(self.data['mentions_of_me'][mentioner])

        if 'profile' not in self.data:
            return 0
        else:
            tweet_count = self.data['profile']['corpus_tweet_count']
            return (retweet_count + mention_count) / float(tweet_count)

    def update_profile(self, tweet):
        profile = get_or(self.data, 'profile', {})
        get_or(profile, 'screen_name', tweet['user']['screen_name'])
        update_count(profile, 'followers_count', tweet['user']['followers_count'])
        update_count(profile, 'friends_count', tweet['user']['friends_count'])
        update_count(profile, 'total_tweet_count', tweet['user']['statuses_count'])
        profile['corpus_tweet_count'] = get_or(profile, 'corpus_tweet_count', 0) + 1

    def add_favourite(self, tweet_id):
        faves = get_or(self.data, 'favourited', {})
        fave_count = get_or(faves, tweet_id, 0)
        faves[tweet_id] = fave_count + 1

    def add_quote(self, quoter, quoted_tweet_id, quoting_tweet_id):
        my_tweets_quoted = get_or(self.data, 'my_quoted_tweets', {})
        my_tweet_quoted_by = get_or(my_tweets_quoted, quoted_tweet_id, [])
        my_tweet_quoted_by.append((quoter, quoting_tweet_id))

    def add_retweet(self, retweeter, tweet_id):
        my_retweets = get_or(self.data, 'my_retweets', {})
        my_tweets_retweeted_by = get_or(my_retweets, tweet_id, [])
        my_tweets_retweeted_by.append(retweeter)

    def add_mention(self, mentioner, tweet_id):
        mentions_of_me = get_or(self.data, 'mentions_of_me', {})
        mentions_by = get_or(mentions_of_me, mentioner, [])
        mentions_by.append(tweet_id)

    def add_reply(self, replying_user, original_tweet_id, reply_tweet_id):
        replies_to_me = get_or(self.data, 'replies_to', {})
        repliers_to_my_tweet = get_or(replies_to_me, original_tweet_id, {})
        replier_to_my_tweet = get_or(repliers_to_my_tweet, replying_user, [])
        replier_to_my_tweet.append(reply_tweet_id)

        replies_to_me_from = get_or(self.data, 'replies_from', {})
        replier_to_my_tweets = get_or(replies_to_me_from, replying_user, [])
        replier_to_my_tweets.append((original_tweet_id, reply_tweet_id))


class TwitterAnalysis:

    def __init__(self, options):
        self.options = options

    @staticmethod
    def is_favourited(tweet):
        return tweet['favorited'] == 'true'

    @staticmethod
    def is_a_quote(tweet):
        return 'quoted_status' in tweet

    @staticmethod
    def is_a_retweet(tweet):
        return 'retweeted_status' in tweet

    @staticmethod
    def has_mentions(tweet):
        return 'user_mentions' in tweet['entities']

    def debug(self, msg):
        if self.options.debug:
            print(msg)

    def analyse(self, tweets):
        print("Analysing %d tweets..." % len(tweets))

        # user -> Kudos instance(mentions, retweets, quotes)
        kudos = {}

        tweet_db = {}
        for t in tweets:
            t_id = t['id_str']
            tweet_db[t_id] = t
            if self.is_a_quote(t):
                quoted_tweet = t['quoted_status']
                tweet_db[quoted_tweet['id_str']] = quoted_tweet
            elif self.is_a_retweet(t):
                retweeted_tweet = t['retweeted_status']
                tweet_db[retweeted_tweet['id_str']] = retweeted_tweet

        def get_kudos(user_id):
            return get_or(kudos, user_id, Kudos())

        for t in tweets:
            tweeting_user = t['user']['screen_name']
            tweet_id = t['id_str']
            tweet_text = make_safe(t['text'])
            get_kudos(tweeting_user).set_tweets(tweet_db)  # HACK!
            get_kudos(tweeting_user).update_profile(t)
            if self.is_favourited(t):
                get_kudos(tweeting_user).add_favourite(tweet_id)
                self.debug("FAVE:    @%s tweet favourited (%s)" % (tweeting_user, tweet_id))
            if self.is_a_quote(t):
                quoted_user = t['quoted_status']['user']['screen_name']
                quoted_tweet_id = t['quoted_status']['id_str']
                get_kudos(quoted_user).add_quote(tweeting_user, quoted_tweet_id, tweet_id)
                self.debug("QUOTE:   @%s quoted tweet by @%s: %s" % (tweeting_user, quoted_user, tweet_text))
            if self.is_a_retweet(t):
                retweeted_user = t['retweeted_status']['user']['screen_name']
                original_tweet_id = t['retweeted_status']['id_str']
                get_kudos(retweeted_user).add_retweet(tweeting_user, original_tweet_id)
                self.debug("RETWEET: @%s retweeted by @%s: %s" % (retweeted_user, tweeting_user, tweet_text))
            if self.has_mentions(t):
                for mentioned_user in t['entities']['user_mentions']:
                    mentioned_sn = mentioned_user['screen_name']
                    if mentioned_user['id_str'] == t['in_reply_to_user_id_str']:
                        get_kudos(mentioned_sn) \
                            .add_reply(tweeting_user, t['in_reply_to_status_id_str'], tweet_id)
                        self.debug("REPLY:   @%s replied to by @%s: %s" % (mentioned_sn, tweeting_user, tweet_text))
                    elif not self.is_a_retweet(t):
                        get_kudos(mentioned_sn).add_mention(tweeting_user, tweet_id)
                        self.debug("MENTION: @%s mentioned by @%s: %s" % (mentioned_sn, tweeting_user, tweet_text))

        print("Detected %d different Twitter users" % len(kudos))
        kudos_list = kudos.items()
        how_few = 20

        # print("Ranked")
        # top_few = sorted(kudos_list, key=lambda row: row[1].rank(), reverse=True)[:how_few]
        # for r in top_few:
        #     print("%.4f : @%s" % (r[1].rank(), r[0]))

        print("H-Index")
        h_index_top_few = sorted(kudos_list, key=lambda row: row[1].h_index(), reverse=True)[:how_few]
        for r in h_index_top_few:
            print("%5d : @%s" % (r[1].h_index(), r[0]))

        print("Interactor Ratio")
        ir_top_few = sorted(kudos_list, key=lambda row: row[1].ir_ratio(), reverse=True)[:how_few]
        for r in ir_top_few:
            print("  %.3f : @%s" % (r[1].ir_ratio(), r[0]))

        print("Retweet and Mention Ratio")
        h_index_top_few = sorted(kudos_list, key=lambda row: row[1].rm_ratio(), reverse=True)[:how_few]
        for r in h_index_top_few:
            print("  %.3f : @%s" % (r[1].rm_ratio(), r[0]))
        #
        # print("Mixture Model Ratio ((h + ir + rmr) / 3)")
        # h_index_top_few = sorted(kudos_list, key=lambda row: row[1].h_index(), reverse=True)[:how_few]
        # for r in h_index_top_few:
        #     print("%d : @%s" % (r[1].h_index(), r[0]))

        print("Done.")
