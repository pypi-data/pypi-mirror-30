# coding=utf-8
from requests_oauthlib import OAuth1
import requests

BASE_URL = 'https://api.twitter.com/1.1/'
VERIFY_URL = 'account/verify_credentials.json'
TWEETS_URL = 'search/tweets.json'
LANG_URL = 'help/languages.json'
USER_URL = 'statuses/user_timeline.json'

class TweetSearch:

    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        """Constructor."""
        self.set_default_parameters()

        self.oauth = OAuth1(
            consumer_key, client_secret=consumer_secret, resource_owner_key=access_token, resource_owner_secret=access_token_secret
        )

        self.r = requests.get(
            BASE_URL + VERIFY_URL, auth=self.oauth,
            proxies={ "https": self.proxy }
        )

    def set_keyword_list(self, words, or_condition=False):
        """Add search arguments to argument list."""
        words = [ (i if " " not in i else '"{}"'.format(i)) for i in words ]
        self.keywords = words

        if or_condition:
            self.keyword_args = " OR ".join(words)
        else:
            self.keyword_args = " ".join(words)

    def get_keyword_list(self):
        """Return all keywords specified by set_keyword_list function."""
        return self.keywords

    def add_ignored_word(self, word):
        """Add keywords with NOT operator."""
        self.ignored_words.append(word)

    def create_search_url(self):
        """Create a complete query with keywords and another parameters."""
        args = "?q={}&lang={}&result_type={}&tweet_mode=extended&count={}".format(
            self.keyword_args, self.language, self.result_type, self.count
        )
        self.search_url = BASE_URL + TWEETS_URL + args

    def get_last_search_url(self):
        """Return last url used for search on Twitter API."""
        return self.last_search_url

    def set_result_type(self, result_type):
        """Change tweet search type.

        Options:
            mixed : Include both popular and real time results in the response.
            recent : return only the most recent results in the response.
            popular : return only the most popular results in the response.

        Default:
            mixed
        """
        self.result_type = result_type

    def set_language(self, language):
        """Change tweet search language.

        The languages are given by an ISO 639-1. See more in
        https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes.

        Default:
            en
        """
        self.language = language

    def set_max_tweet_response(self, count):
        """Change tweet count per page for a result.

        Default:
            100
        Max:
            100
        """
        self.count = count

    def set_max_tweet_id(self, id):
        """Define the base tweet for pagination."""
        self.max_tweet_id = id

    def remove_max_tweet_id(self):
        """Remove max_tweet_id argument."""
        self.max_tweet_id = None

    def set_since_tweet_id(self, id):
        """Define the base tweet for pagination."""
        self.since_tweet_id = id

    def remove_since_tweet_id(self):
        """Remove since_tweet_id argument."""
        self.since_tweet_id = None

    def search_tweets(self):
        """Call for Twitter REST API and return itself to iterate."""
        self.create_search_url()

        return self.search(
            self.search_url, self.max_tweet_id, self.since_tweet_id
        )

    def search_older_tweets(self):
        """Triggers the search for more results using the Twitter API."""
        older_tweet = self.get_older_tweet()

        if older_tweet and len(self.tweets) >= self.count:
            return self.search(
                self.search_url, older_tweet_id=older_tweet['id_str']
            )

        return []

    def search_newer_tweets(self):
        """Triggers the search for more results using the Twitter API."""
        newer_tweet = self.get_newer_tweet()

        if newer_tweet:
            return self.search(
                self.last_search_url, newer_tweet_id=newer_tweet['id_str']
            )

        return []

    def search_by_url(self, url):
        """Search on Twitter API with a given url."""
        return self.search(url)

    def search(self, url, older_tweet_id=None, newer_tweet_id=None):
        """Call for Twitter REST API and return itself to iterate."""
        endpoint = None

        if older_tweet_id:
            endpoint = "{}&max_id={}".format(url, older_tweet_id)
        elif newer_tweet_id:
            endpoint = "{}&since_id={}".format(url, newer_tweet_id)
        else:
            endpoint = url

        response = requests.get(
            endpoint, auth=self.oauth,
            proxies={ "https": self.proxy }
        )

        self.response_headers = response.headers
        self.last_search_url = endpoint

        self.tweets = response.json().get('statuses', [])

        return self

    def get_older_tweet(self):
        """Return the last tweet from the last search.

        The last tweet is the older one.
        """
        if self.tweets:
            return self.tweets[-1]

        return None

    def get_newer_tweet(self):
        """Return the first tweet from the last search.

        The first tweet is the newer one.
        """
        if self.tweets:
            return self.tweets[0]

        return None

    def get_tweets(self):
        """Return last searched tweets."""
        return self.tweets

    def get_tweet_count(self):
        """Return the last searched tweets count."""
        return len(self.tweets)

    def set_default_parameters(self):
        """Reset all arguments to class default."""
        self.keywords = []
        self.keyword_args = ""
        self.ignored_keywords = []
        self.result_type = "mixed"
        self.language = "en"
        self.count = 100
        self.last_search_url = ""
        self.max_tweet_id = None
        self.since_tweet_id = None
        self.search_url = ""
        self.proxy = None
        self.response_headers = []

    def check_parameters(self):
        """Verify if all url parameters are ok."""
        pass

    def get_response_headers(self):
        """Return response metadata."""
        return self.response_headers

    def get_rate_limit_remaining(self):
        """Return Twitter rate limite remaing from last response headers."""
        if self.response_headers:
            return self.response_headers.get('x-rate-limit-remaining', None)

        return None

    def get_rate_limit(self):
        """Return Twitter rate limite total from last response headers."""
        if self.response_headers:
            return self.response_headers.get('x-rate-limit-limit', None)

        return None

    def get_rate_limit_reset(self):
        """Return Twitter rate limite reset from last response headers."""
        if self.response_headers:
            return self.response_headers('x-rate-limit-reset', None)

        return None

    def __len__(self):
        """Return the length of the last tweet search result."""
        return len(self.tweets)

    def __getitem__(self, position):
        """Return a tweet for a given position."""
        return self.tweets[position]

# https://api.twitter.com/1.1/search/tweets.json?q=from:Cmdr_Hadfield #nasa&result_type=popular
