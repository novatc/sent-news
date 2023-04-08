import logging

from apscheduler.schedulers.blocking import BlockingScheduler

from chatGPT_api import analyze_sentiment, analyze_emotions
from db.firestore import FirestoreConnection
from db.topics import Topics

key = "2f01a585-19e6-4928-9f8f-18240ba81842"


def welcome():
    print(''' ________       _______       ________       _________        ________       _______       ___       __       ________      
|\   ____\     |\  ___ \     |\   ___  \    |\___   ___\     |\   ___  \    |\  ___ \     |\  \     |\  \    |\   ____\     
\ \  \___|_    \ \   __/|    \ \  \\ \  \   \|___ \  \_|     \ \  \\ \  \   \ \   __/|    \ \  \    \ \  \   \ \  \___|_    
 \ \_____  \    \ \  \_|/__   \ \  \\ \  \       \ \  \       \ \  \\ \  \   \ \  \_|/__   \ \  \  __\ \  \   \ \_____  \   
  \|____|\  \    \ \  \_|\ \   \ \  \\ \  \       \ \  \       \ \  \\ \  \   \ \  \_|\ \   \ \  \|\__\_\  \   \|____|\  \  
    ____\_\  \    \ \_______\   \ \__\\ \__\       \ \__\       \ \__\\ \__\   \ \_______\   \ \____________\    ____\_\  \ 
   |\_________\    \|_______|    \|__| \|__|        \|__|        \|__| \|__|    \|_______|    \|____________|   |\_________\
   \|_________|                                                                                                 \|_________|

  
                                                                                                                        ''')


def sent_news_with_open_ai(fire):
    topic_gateway = Topics(key)
    logging.info('Starting the analysis...')
    topic_gateway.get_topics_with_open_ai(fire)
    logging.info('Analysis finished...')


if __name__ == '__main__':
    welcome()
    logging.basicConfig(level=logging.INFO)
    logging.info('Initializing the database...')

    fire = FirestoreConnection()
    topic_gateway = Topics(key)
    topic_gateway.get_topics_with_open_ai(fire)

    logging.info('Starting scheduler...')
    scheduler = BlockingScheduler()
    scheduler.add_job(sent_news_with_open_ai, 'interval', hours=1, args=[fire])
    scheduler.start()
