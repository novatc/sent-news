import firebase_admin
from firebase_admin import db
import json


class FirebaseConnection:
    def __init__(self, firebase_url, firebase_secret):
        self.credentials = firebase_admin.credentials.Certificate(firebase_secret)
        self.default_app = default_app = firebase_admin.initialize_app(self.credentials, {
            'databaseURL': firebase_url})
        self.ref_articles = db.reference('/articles')
        self.ref_topics = db.reference('/topics')

    def push(self, data):
        self.ref_articles.push(data)

    def push_article_from_topic(self, article):
        self.ref_topics.push(article)

    def get_topic_article_by_uri(self, title):
        return self.ref_topics.order_by_child('uri').equal_to(title).get()

    def get(self):
        return self.ref_articles.get()

    def get_article_by_uri(self, title):
        return self.ref_articles.order_by_child('uri').equal_to(title).get()

    def delete_all(self):
        self.ref_articles.delete()