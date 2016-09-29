import unicodedata


def get_or(m, k, v):
    if k not in m:
        m[k] = v
    return m[k]


def make_safe(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')


class Kudos:
    """
    Structure to capture kudos of an individual
    data.'quotes'.quoted_tweet_id.[(quoting_user, quote_tweet_id)]
        .'retweets'.retweeted_tweet_id.[retweeting_user]
        .'mentions'.mentioning_user.[mentioning_tweet]
        .'replies_to'.original_tweet_id.replying_user_id.[reply_tweet_id]
        .'replies_from'.replying_user_id.[(original_tweet_id, reply_tweet_id)]
        .'favourited'.favourited_tweet_id.count
    """
    def __init__(self):
        self.data = {}

    def get_interactions(self, user_id, interaction_type):
        return self.get_or(self.get_or(self.data, user_id, {}), interaction_type, {})

    def add_quote(self, quoter, quoted_tweet_id, quoting_tweet_id):
        my_tweets_quoted = get_or(self.data, 'my_tweets_quoted', {})
        my_tweets_quoted_by = get_or(my_tweets_quoted, quoted_tweet_id, [])
        my_tweets_quoted_by.append((quoter, quoting_tweet_id))

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

    def add_favourite(self, tweet_id):
        faves = self.get_interactions('favourited')
        fave_count = get_or(faves, tweet_id, 0)
        faves[tweet_id] = fave_count + 1


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
        # for t in tweets:
        #     print('@%s' % t['user']["screen_name"])

        # user -> mentions, retweets, quotes
        kudos = {}

        def get_kudos(user_id):
            return get_or(kudos, user_id, Kudos())

        for t in tweets:
            tweeting_user = t['user']['screen_name']
            tweet_id = t['id_str']
            tweet_text = make_safe(t['text'])
            # favourites.
            if self.is_favourited(t):
                get_kudos(tweeting_user).add_favourite(tweet_id)
                self.debug("FAVE:    @%s tweet favourited (%s)" % (tweeting_user, tweet_id))
            if self.is_a_quote(t):
                quoted_user = t['quoted_status']['user']['screen_name']
                quoted_tweet_id = t['quoted_status']['id_str']
                get_kudos(quoted_user).add_quote(tweeting_user, quoted_tweet_id, tweet_id)
                # kudos.add_quote(quoted_user, tweeting_user, tweet_id)
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

        print(len(kudos))

        print("Done.")
