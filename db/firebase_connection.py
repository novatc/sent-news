import firebase_admin
from firebase_admin import db
import json


class FirebaseConnection:
    def __init__(self, firebase_url, firebase_secret):
        self.credentials = firebase_admin.credentials.Certificate(firebase_secret)
        self.default_app = default_app = firebase_admin.initialize_app(self.credentials, {
            'databaseURL': firebase_url})
        self.ref = db.reference('/articles')

    def push(self, data):
        self.ref.push(data)

    def get(self):
        return self.ref.get()

    def get_article_by_uri(self, title):
        return self.ref.order_by_child('uri').equal_to(title).get()

    def delete_all(self):
        self.ref.delete()