from eventregistry import *

from db.firebase_connection import FirebaseConnection
from text_analysis import Analyser

key = "2f01a585-19e6-4928-9f8f-18240ba81842"


class Topics:

    def __init__(self, apiKey):
        self.er = EventRegistry(apiKey=apiKey, allowUseOfArchive=False)

    def get_topics(self, firebase: FirebaseConnection, analyser: Analyser):
        t = TopicPage(self.er)
        t.loadTopicPageFromER("b21e6fdb-8553-4f58-8b0c-468dec02465a")

        start_time = time.time()

        while True:
            query = t.getArticles(count=10, sortBy="date", sortByAsc=False)
            articleList = query.get("articles", {}).get("results", [])
            print("%d articles from Topic were added since the last call" % len(articleList))

            for article in articleList:
                if len(firebase.get_topic_article_by_uri(article['uri'])) == 0:
                    updated_article = analyser.analyse(article)
                    firebase.push_article_from_topic(updated_article)
                    logging.info('Article added to database: ' + updated_article['title'])
                else:
                    print("Article already exists")
                    pass
            time.sleep(3600.0 - ((time.time() - start_time) % 60.0))


