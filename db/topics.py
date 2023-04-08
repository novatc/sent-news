import functools

from eventregistry import *

from chatGPT_api import analyze_sentiment, analyze_emotions, summarize_text
from db.firestore import FirestoreConnection
from text_analysis import Analyser

key = "2f01a585-19e6-4928-9f8f-18240ba81842"
open_ai_key = "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"


class Topics:

    def __init__(self, apiKey):
        self.er = EventRegistry(apiKey=apiKey, allowUseOfArchive=False)

    def get_topics_with_open_ai(self, firebase):
        topic_page = TopicPage(self.er)
        topic_page.loadTopicPageFromER("66e29a64-219f-41a5-a0a2-a8373feb86dd")

        query = topic_page.getArticles(count=10, sortBy="date", sortByAsc=False)
        article_list = query.get("articles", {}).get("results", [])

        for article in article_list:
            if len(firebase.get_topic_article_by_uri(article['uri'])) == 0:
                sentiment = analyze_sentiment(article['body'])
                emotions = analyze_emotions(article['body'])
                summary = summarize_text(article['body'])
                article['sentiment'] = sentiment
                article['summary'] = summary
                article['emotions'] = emotions
                firebase.add_article_open_ai(article)
                logging.info('Article added to database: ' + article['title'])
            else:
                logging.info("Article already exists")
                pass






    def get_topics(self, firebase: FirestoreConnection, analyser: Analyser):
        t = TopicPage(self.er)
        t.loadTopicPageFromER("66e29a64-219f-41a5-a0a2-a8373feb86dd")

        query = t.getArticles(count=10, sortBy="date", sortByAsc=False)
        articleList = query.get("articles", {}).get("results", [])

        for article in articleList:
            if len(firebase.get_topic_article_by_uri(article['uri'])) == 0:
                updated_article = analyser.analyse(article)
                sentiment_gpt = analyze_sentiment(updated_article['body'])
                emotions_gpt = analyze_emotions(updated_article['body'])
                summary_gpt = summarize_text(updated_article['body'])
                updated_article['sentiment_gpt'] = sentiment_gpt
                updated_article['summary_gpt'] = summary_gpt
                updated_article['emotions_gpt'] = emotions_gpt
                firebase.add_article(updated_article)
                logging.info('Article added to database: ' + updated_article['title'])
            else:
                logging.info("Article already exists")
                pass
