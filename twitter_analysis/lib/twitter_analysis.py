import unicodedata
import operator

from pprint import pprint


def get_or(m, k, v):
    """
    Checks map m for an entry under key k, adding it with value v if it's missing,
    and then returning the value associated with k.
    :return The value in map m associated with key k, or v if it wasn't present.
    """
    if k not in m:
        m[k] = v
    return m[k]


def update_count(m, k, v):
    m[k] = max(v, get_or(m, k, v))


def min_max(l):
    """Convenience method to return the min and max of a list in one call"""
    return min(l), max(l)


def normalise(v, min_v, max_v):
    """Normalises v between min_v and max_v to belong in (0,1)"""
    # norm = v / float(max_v)  # assumes min_v = 0
    norm = (v - min_v) / float(max_v - min_v)
    if norm > 1.0:
        print("[WARN] normalise(%f, %f, %f)" % (v, min_v, max_v))
    return norm


def make_safe(text):
    """Replaces whacky characters with safe ones"""
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
        self.data = {
            'profile': {},
            'my_retweets': {},
            'my_quoted_tweets': {},
            'mentions_of_me': {},
            'replies_to': {},
            'replies_from': {},
            'favourited': {}
        }
        self.cached_h_index = -1
        self.cached_int_ratio = -1
        self.cached_rm_ratio = -1

    def h_index(self):
        """
        The H Index of this user based on tweets that are retweeted or quoted, similar to the academic H Index
        :return The H Index of this user
        """
        if self.cached_h_index != -1:
            return self.cached_h_index

        # turn the retweets & quoted tweets into a list of tuples (tweet_id, list of tweeters)
        interactions = self.data['my_retweets'].items() + self.data['my_quoted_tweets'].items()

        sorted_interactions_list = sorted(interactions, key=operator.itemgetter(1))

        h_index = 0
        i = len(sorted_interactions_list) - 1
        while i >= 0:
            num_interactors_for_this_tweet = len(sorted_interactions_list[i][1])
            if num_interactors_for_this_tweet < h_index + 1:
                break
            h_index += 1
            i -= 1

        self.cached_h_index = h_index
        return self.cached_h_index

    def int_ratio(self):
        """
        Interactor ratio = (|unique retweeters| + |unique mentioners| + |unique_quoters|) / |followers|
        :return The ratio of users interacting with this user to the number of this user's followers
        """
        if self.cached_int_ratio != -1:
            return self.cached_int_ratio

        unique_retweeters = set()
        if 'my_retweets' in self.data:
            for retweeters in self.data['my_retweets']:
                unique_retweeters = unique_retweeters.union(self.data['my_retweets'][retweeters])

        # print("Retweeters of @%s: %s" % (self.data['profile']['screen_name'], unique_retweeters))
        # pprint("Mentions of @%s: %s" % (self.data['profile']['screen_name'], self.data['mentions_of_me']))
        # pprint("Replies to of @%s: %s" % (self.data['profile']['screen_name'], self.data['replies_to']))
        # pprint("Replies from of @%s: %s" % (self.data['profile']['screen_name'], self.data['replies_from']))
        unique_mentioners = set().union(self.data['mentions_of_me'].keys()).union(self.data['replies_from'].keys())
        # print("Mentions of @%s: %s" % (self.data['profile']['screen_name'], unique_mentioners))

        unique_quoters = set()
        if 'my_quoted_tweets' in self.data:
            for quoted_tweets in self.data['my_quoted_tweets']:
                unique_quoters.add(quoted_tweets[0])

        if 'profile' not in self.data:
            pprint(self.data)

        followers_count = get_or(self.data['profile'], 'followers_count', 0)

        self.cached_int_ratio = \
            (len(set().union(unique_retweeters).union(unique_mentioners).union(unique_quoters))) / \
            float(followers_count) if followers_count else 0
        return self.cached_int_ratio

    def rm_ratio(self):
        """
        The Retweet/Mention ratio: (|tweets retweeted| + |tweets mentioning this user| + |tweeets quoted|) /
        |tweets posted in the corpus|
        :return The ratio of interactions (retweets, quotes, mentions) of this user to the number of tweets they
        have posted in the current corpus
        """
        if self.cached_rm_ratio != -1:
            return self.cached_rm_ratio

        retweet_count = len(self.data['my_retweets']) if 'my_retweets' in self.data else 0

        # pprint("Replies to of @%s: %s" % (self.data['profile']['screen_name'], self.data['replies_to']))
        # pprint("Replies from of @%s: %s" % (self.data['profile']['screen_name'], self.data['replies_from']))
        mention_count = 0
        for mentioner in self.data['mentions_of_me']:
            mention_count += len(self.data['mentions_of_me'][mentioner])
        for replies in self.data['replies_to']:
            mention_count += len(self.data['replies_to'][replies])

        quote_count = 0
        for quoted_tweet in self.data['my_quoted_tweets']:
            quote_count += len(self.data['my_quoted_tweets'][quoted_tweet])

        tweet_count = self.get_corpus_tweet_count()
        # print("Tweet count for @%s is %d" % (self.data['profile']['screen_name'], tweet_count))
        # print("Retweet count is %d" % retweet_count)
        # print("Mention count is %d" % mention_count)
        # print("Quote   count is %d" % quote_count)
        self.cached_rm_ratio = \
            (retweet_count + mention_count + quote_count) / float(tweet_count) if tweet_count else 0
        return self.cached_rm_ratio

    def update_screen_name(self, screen_name):
        profile = get_or(self.data, 'profile', {})
        get_or(profile, 'screen_name', screen_name)

    def update_profile(self, tweet):
        profile = get_or(self.data, 'profile', {})
        get_or(profile, 'screen_name', tweet['user']['screen_name'])
        update_count(profile, 'followers_count', tweet['user']['followers_count'])
        update_count(profile, 'friends_count', tweet['user']['friends_count'])
        update_count(profile, 'total_tweet_count', tweet['user']['statuses_count'])
        get_or(profile, 'corpus_tweet_count', set()).add(tweet['id_str'])  # unique tweets in corpus

    def get_corpus_tweet_count(self):
        return len(get_or(self.data['profile'], 'corpus_tweet_count', set()))

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
        print("Loaded %d tweets..." % len(tweets))

        # user -> Kudos instance(mentions, retweets, quotes)
        kudos = {}
        how_few = 20  # top X to report on

        all_tweets = {}  # fleshed out collection of unique tweets, including embedded tweets
        for t in tweets:
            t_id = t['id_str']
            all_tweets[t_id] = t
            if self.is_a_quote(t):
                quoted_status = t['quoted_status']
                all_tweets[quoted_status['id_str']] = quoted_status
            elif self.is_a_retweet(t):
                retweeted_status = t['retweeted_status']
                all_tweets[retweeted_status['id_str']] = retweeted_status

        print("Analysing %d tweets..." % len(all_tweets))

        def get_kudos(user_id):
            return get_or(kudos, user_id, Kudos())

        # parse all tweets and build kudos for each user
        for t in all_tweets.values():
            tweeting_user = t['user']['screen_name']
            tweet_id = t['id_str']
            tweet_text = make_safe(t['text'])
            get_kudos(tweeting_user).update_profile(t)
            if self.is_favourited(t):
                get_kudos(tweeting_user).add_favourite(tweet_id)
                self.debug("FAVE:    @%s tweet favourited (%s)" % (tweeting_user, tweet_id))
            if self.is_a_quote(t):
                quoted_user = t['quoted_status']['user']['screen_name']
                quoted_tweet_id = t['quoted_status']['id_str']
                get_kudos(quoted_user).add_quote(tweeting_user, quoted_tweet_id, tweet_id)
                get_kudos(quoted_user).update_profile(t['quoted_status'])
                self.debug("QUOTE:   @%s quoted tweet by @%s: %s" % (tweeting_user, quoted_user, tweet_text))
            if self.is_a_retweet(t):
                retweeted_user = t['retweeted_status']['user']['screen_name']
                original_tweet_id = t['retweeted_status']['id_str']
                get_kudos(retweeted_user).add_retweet(tweeting_user, original_tweet_id)
                get_kudos(retweeted_user).update_profile(t['retweeted_status'])
                self.debug("RETWEET: @%s retweeted by @%s: %s" % (retweeted_user, tweeting_user, tweet_text))
            if self.has_mentions(t):
                for mentioned_user in t['entities']['user_mentions']:
                    mentioned_sn = mentioned_user['screen_name']
                    if mentioned_user['id_str'] == t['in_reply_to_user_id_str']:
                        get_kudos(mentioned_sn) \
                            .add_reply(tweeting_user, t['in_reply_to_status_id_str'], tweet_id)
                        get_kudos(mentioned_sn).update_screen_name(mentioned_sn)
                        self.debug("REPLY:   @%s replied to by @%s: %s" % (mentioned_sn, tweeting_user, tweet_text))
                    elif not self.is_a_retweet(t):
                        get_kudos(mentioned_sn).add_mention(tweeting_user, tweet_id)
                        get_kudos(mentioned_sn).update_screen_name(mentioned_sn)
                        self.debug("MENTION: @%s mentioned by @%s: %s" % (mentioned_sn, tweeting_user, tweet_text))

        print("Detected %d different Twitter users" % len(kudos))
        kudos_list = kudos.items()

        print("H-Index")
        h_index_top_few = sorted(kudos_list, key=lambda row: row[1].h_index(), reverse=True)[:how_few]
        for r in h_index_top_few:
            print("%5d : @%s" % (r[1].h_index(), r[0]))

        print("Interactor Ratio")
        ir_top_few = sorted(kudos_list, key=lambda row: row[1].int_ratio(), reverse=True)[:how_few]
        for r in ir_top_few:
            print("  %.2f : @%s" % (r[1].int_ratio(), r[0]))

        print("Retweet and Mention Ratio")
        h_index_top_few = sorted(kudos_list, key=lambda row: row[1].rm_ratio(), reverse=True)[:how_few]
        for r in h_index_top_few:
            print("  %.2f : @%s" % (r[1].rm_ratio(), r[0]))

        (min_h_index, max_h_index) = min_max(map(lambda row: row[1].h_index(), kudos_list))
        (min_ir, max_ir) = min_max(map(lambda row: row[1].int_ratio(), kudos_list))
        (min_rmr, max_rmr) = min_max(map(lambda row: row[1].rm_ratio(), kudos_list))

        print("Mixture Model Ratio ((h' + ir' + rmr') / 3)")
        blended_top_few = sorted(kudos_list,
                                 key=lambda row:
                                     (normalise(row[1].h_index(), min_h_index, max_h_index) +
                                      normalise(row[1].int_ratio(), min_ir, max_ir) +
                                      normalise(row[1].rm_ratio(), min_rmr, max_rmr)) / 3.0,
                                 reverse=True)[:how_few]
        for r in blended_top_few:
            print("  %.2f : @%s" % (
                (normalise(r[1].h_index(), min_h_index, max_h_index) +
                 normalise(r[1].int_ratio(), min_ir, max_ir) +
                 normalise(r[1].rm_ratio(), min_rmr, max_rmr)) / 3.0,
                r[0]
            ))

        print("D-Rank")
        d_rank_scores = self.d_rank(all_tweets.values(),
                                    int(self.options.max_iterations),
                                    int(self.options.tweet_count),
                                    float(self.options.d_rank_weight_factor),
                                    self.options.debug)
        d_rank_top_few = sorted(d_rank_scores.items(), key=lambda kv: kv[1], reverse=True)[:how_few]
        for r in d_rank_top_few:
            print("  %.2f : @%s" % (r[1], r[0]))

        print("Done.")

    @staticmethod
    def gather_interactions(tweets, users, incoming, outgoing):
        # tweets: list of parsed tweets
        # users: set of users to populate with usernames seen in tweets
        # incoming: { mentioned_user: { mentioning_user : set(mentioning_tweet_ID) } }
        # outgoing: { mentioning_user: set(mentioned_user) }
        for t in tweets:
            if TwitterAnalysis.is_a_quote(t):
                quoting_user = t['user']['screen_name']
                quoted_user = t['quoted_status']['user']['screen_name']

                incoming_for_the_quoted_user = get_or(incoming, quoted_user, {})
                get_or(incoming_for_the_quoted_user, quoting_user, set()).add(t['id_str'])
                get_or(outgoing, quoting_user, set()).add(quoted_user)
                users.add(quoting_user)
                users.add(quoted_user)

            if TwitterAnalysis.has_mentions(t):
                # covers RTs, replies and mentions
                for mention in t['entities']['user_mentions']:
                    mentioned_user = mention['screen_name']
                    mentioning_user = t['user']['screen_name']

                    incoming_for_the_mentioned_user = get_or(incoming, mentioned_user, {})
                    get_or(incoming_for_the_mentioned_user, mentioning_user, set()).add(t['id_str'])
                    get_or(outgoing, mentioning_user, set()).add(mentioned_user)
                    users.add(mentioning_user)
                    users.add(mentioned_user)

    @staticmethod
    def d_rank(tweets, max_iterations, tweet_count, weight_factor=0.2, debug=False):

        damping_factor = 1 - weight_factor
        interesting_delta = 0.001  # redo scores if new value differs by this
        influence_scores = {}
        users = set()
        users_who_mentioned_x = {}  # to collect users who mentioned X (the key)
        users_mentioned_by_x = {}  # to collect users mentioned by X (the key)

        tweets_to_consider = tweets if tweet_count == -1 else tweets[0:tweet_count]
        if debug:
            print("[INFO] Tweets to consider: %d" % len(tweets_to_consider))
        TwitterAnalysis.gather_interactions(tweets_to_consider, users, users_who_mentioned_x, users_mentioned_by_x)

        # Step 1. Set all weights
        for this_user in users:
            influence_scores[this_user] = weight_factor

        # Step 2.
        iterations = 0
        scores_have_changed = True
        while iterations < max_iterations and scores_have_changed:
            scores_have_changed = False
            iterations += 1
            for this_user in users:
                # grab the previous new_score and call it prev_score
                prev_score = influence_scores[this_user]

                # how many people received a mention or RT from this user?
                all_outgoing_interactions_of_this_user = len(get_or(users_mentioned_by_x, this_user, []))
                # if it was zero, make it non-zero but less than 1 (it'll be a denominator)
                if all_outgoing_interactions_of_this_user == 0:
                    all_outgoing_interactions_of_this_user = 0.5

                # calculate surrounding influence, accounting for own interactions (mentions of others)
                surrounding_influence = 0.0
                inspired_users = get_or(users_who_mentioned_x, this_user, {}).keys()
                for inspired_user in inspired_users:
                    influence_of_inspired_user = influence_scores[inspired_user]
                    num_interactions_from_inspired_user = len(users_who_mentioned_x[this_user][inspired_user])
                    surrounding_influence += (influence_of_inspired_user * num_interactions_from_inspired_user)
                surrounding_influence /= all_outgoing_interactions_of_this_user

                # the next score is...
                new_score = damping_factor + weight_factor * surrounding_influence

                # Step 3. check if it's changed
                if abs(prev_score - new_score) > interesting_delta:
                    scores_have_changed = True

                influence_scores[this_user] = new_score

        if debug and iterations == max_iterations:
            print("[INFO] D-rank hit iteration max. Could have continued.")

        return influence_scores
