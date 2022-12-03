from eventregistry import *

from db.firebase_connection import FirebaseConnection
from text_analysis import Analyser

key = "2f01a585-19e6-4928-9f8f-18240ba81842"


class Articles:
    def __init__(self, apiKey):
        self.er = EventRegistry(apiKey=apiKey, allowUseOfArchive=False)

    def get_articles(self, keywords, dataType, sortBy, sortByAsc, maxItems):
        q = QueryArticlesIter(keywords=keywords, dataType=dataType)
        # we limit here the results to 100. If you want more, remove or increasae maxItems
        return [article for article in q.execQuery(self.er, sortBy=sortBy, sortByAsc=sortByAsc, maxItems=maxItems)]

    def start_article_stream(self, firebase: FirebaseConnection, analyser: Analyser):
        recentQ = GetRecentArticles(self.er,
                                    lang=["eng"],
                                    recentActivityArticlesMaxArticleCount = 10,
                                    recentActivityArticlesUpdatesAfterMinsAgo=10,
                                    keyword=["Climate"],
                                    returnInfo=ReturnInfo(ArticleInfoFlags(concepts=False, categories=True)))
        start_time = time.time()

        while True:
            article_list = recentQ.getUpdates()
            print("%d articles were added since the last call" % len(article_list))

            for article in article_list:
                if len(firebase.get_article_by_uri(article['uri'])) == 0:
                    updated_article = analyser.analyse(article)
                    firebase.push(updated_article)
                    logging.info('Article added to database: ' + updated_article['title'])
                else:
                    print("Article already exists")
                    pass
            time.sleep(3600.0 - ((time.time() - start_time) % 60.0))

    def get_article_details(self, uri):
        q = QueryArticle(uri)
        return self.er.execQuery(q)

