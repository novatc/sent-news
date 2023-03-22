import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials


class FirestoreConnection:
    def __init__(self):
        cred = credentials.Certificate("db/keys/sent-news-357414-firebase-adminsdk-okg5o-511d2deffd.json")
        firebase_admin.initialize_app(cred)

        self.db = firestore.client()

    def add_article(self, article):
        if article['source']['title'] == 'RT':
            return

        self.db.collection('articles').add(article)

    def get_topic_article_by_uri(self, param):
        return self.db.collection('articles').where('uri', '==', param).get()
