twitter-mood
============
[![Build Status](https://travis-ci.org/jmhossler/twitter-mood.svg?branch=master)](https://travis-ci.org/jmhossler/twitter-mood)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

twitter-mood is a python tool meant to simplify sentiment analysis of twitter queries.


Description
-----------

Using textblob and python-twitter, twitter-mood aggregates sentiment analysis of
tweets from twitter matching a specific query.

Usage
-----

`from twitter_mood import TwitterMoodGatherer
import twitter

consumer_key='consumer_key'
consumer_secret='consumer_secret'
access_token_key='access_token'
access_token_secret='access_token_secret'


twitter_api = twitter.Api(consumer_secret=consumer_secret,
                          api_token_key=api_token_key,
                          api_token_secret=api_token_secret,
                          consumer_key=consumer_key)

twitter_mood_tool = TwitterMoodGatherer(twitter_api, query)

twitter_mood_tool.gather_tweets()

twitter_mood_tool.analyze_mood()  # return Sentiment Aggregate
`


Note
----

This project has been set up using PyScaffold 3.0.1. For details and usage
information on PyScaffold see http://pyscaffold.org/.
