from unittest.mock import MagicMock, patch
from twitter_mood.mood_gatherer import TwitterMoodGatherer


class TestGetMoodSuite:
    def test_get_mood_empty_tweets(self):
        twitter_mock = MagicMock()
        mood_gatherer = TwitterMoodGatherer(twitter_mock, 'foo')
        mood = mood_gatherer.get_mood()
        assert mood.polarity == 0
        assert mood.subjectivity == 0

    @patch('twitter_mood.mood_gatherer.TextBlob')
    def test_get_mood_single_tweet(self, text_mock):
        twitter_mock = MagicMock()
        twitter_mock.GetSearch.return_value = [MagicMock(text='bar')]
        mood_gatherer = TwitterMoodGatherer(twitter_mock, 'foo')
        text_mock.return_value = MagicMock(
                sentiment=MagicMock(
                    polarity=-0.1,
                    subjectivity=0.8))

        mood_gatherer.gather_tweets()
        mood = mood_gatherer.get_mood()
        assert mood.polarity == -0.1
        assert mood.subjectivity == 0.8

    @patch('twitter_mood.mood_gatherer.TextBlob')
    def test_get_mood_multiple_tweets(self, text_mock):
        twitter_mock = MagicMock()
        twitter_mock.GetSearch.return_value = [
                MagicMock(text='bar'),
                MagicMock(text='baz')]
        text_mock.side_effect = [
                MagicMock(
                    sentiment=MagicMock(polarity=-0.3, subjectivity=1)),
                MagicMock(
                    sentiment=MagicMock(polarity=-0.1, subjectivity=0.8))]

        mood_gatherer = TwitterMoodGatherer(twitter_mock, 'foo')

        mood_gatherer.gather_tweets()
        mood = mood_gatherer.get_mood()
        assert mood.polarity == -0.2
        assert mood.subjectivity == 0.9
