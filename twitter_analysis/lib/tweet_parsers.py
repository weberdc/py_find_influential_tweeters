class StandardParser:
    """
    Given a dictionary populated from parsing the JSON of tweets provided by the
    Twitter API, this parser will interrogate the dictionary using the appropriate
    field/key names.
    """

    def is_a_retweet(self, t):
        return 'retweeted_status' in t

    def is_favourited(self, t):
        return t['favorited'] == 'true' or int(t['favorite_count']) > 0

    def is_a_quote(self, t):
        return 'quoted_status' in t

    def has_mentions(self, t):
        return 'entities' in t and 'user_mentions' in t['entities']

    def get_retweeted_status(self, t):
        return t['retweeted_status']

    def get_quoted_status(self, t):
        return t['quoted_status']

    def get_mentions(self, t):
        return t['entities']['user_mentions']

    def get_id(self, t):
        return t['id_str']

    def get_screen_name(self, screen_name_owner):
        return screen_name_owner['screen_name']

    def get_followers_count(self, t):
        return t['user']['followers_count']

    def get_friends_count(self, t):
        return t['user']['friends_count']

    def get_statuses_count(self, t):
        return t['user']['statuses_count']

    def get_favourite_count(self, t):
        return t['favorite_count']

    def get_in_reply_to_user_id(self, t):
        return t['in_reply_to_user_id_str']

    def get_in_reply_to_status_id(self, t):
        return t['in_reply_to_status_id_str']


class Twitter4JParser(StandardParser):
    """
    Given a dictionary populated from parsing the JSON of tweets serialised by using
    the Twitter4J Java library (when, say, the Jackson JSON library is used to serialise
    the Tweet JavaBeans that Twitter4J uses), this parser will interrogate the
    dictionary using the expected field/key names (which differ from the standard
    Twitter API ones).
    """

    def is_a_retweet(self, t):
        return 'retweetedStatus' in t and t['retweetedStatus']

    def is_favourited(self, t):
        return t['favorited'] == 'true' or int(t['favoriteCount']) > 0

    def is_a_quote(self, t):
        return 'quotedStatus' in t and t['quotedStatus']

    def has_mentions(self, t):
        return 'userMentionEntities' in t and t['userMentionEntities']

    def get_retweeted_status(self, t):
        return t['retweetedStatus']

    def get_quoted_status(self, t):
        return t['quotedStatus']

    def get_mentions(self, t):
        return t['userMentionEntities']

    def get_id(self, t):
        return t['id']

    def get_screen_name(self, screen_name_owner):
        return screen_name_owner['screenName']

    def get_followers_count(self, t):
        return t['user']['followersCount']

    def get_friends_count(self, t):
        return t['user']['friendsCount']

    def get_statuses_count(self, t):
        return t['user']['statusesCount']

    def get_favourite_count(self, t):
        return t['favoriteCount']

    def get_in_reply_to_user_id(self, t):
        return t['inReplyToUserId']

    def get_in_reply_to_status_id(self, t):
        return t['inReplyToStatusId']
