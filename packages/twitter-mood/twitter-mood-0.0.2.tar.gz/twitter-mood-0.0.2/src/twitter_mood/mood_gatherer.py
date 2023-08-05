import collections

from textblob import TextBlob


class TwitterMoodGatherer:

    def __init__(self, twitter_api, query):
        self.__twitter_api = twitter_api
        self.__query = query
        self.__sentiment_tool = TextBlob
        self.__tweets = []
        self.__sentiment_tuple = collections.namedtuple(
                'Sentiment',
                ['polarity', 'subjectivity'])

    def get_mood(self):
        if len(self.__tweets) == 0:
            return self.__sentiment_tool('')
        sentiments = [self.__sentiment_tool(tweet.text).sentiment
                      for tweet in self.__tweets]
        polarity_avg = sum(sentiment.polarity
                           for sentiment in sentiments) / len(self.__tweets)
        subjectivity_avg = sum(sentiment.subjectivity
                               for sentiment in sentiments) / len(self.__tweets)
        return self.__sentiment_tuple(polarity_avg, subjectivity_avg)

    def gather_tweets(self):
        self.__tweets = self.__twitter_api.GetSearch(
                term=self.__query,
                count=100)
