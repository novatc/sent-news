import logging
import os
from datetime import datetime

from transformers import AutoTokenizer, AutoModelForSequenceClassification, BartForConditionalGeneration, \
     BartTokenizer

from db.firebase_connection import FirebaseConnection
from db.topics import Topics
from text_analysis import Analyser
from apscheduler.schedulers.blocking import BlockingScheduler


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


def check_for_local_model(model_path):
    if not os.path.exists(model_path):
        return False
    else:
        return True


sentiment_model_path = 'local_models/finiteautomata/bertweet-base-sentiment-analysis'
emotion_model_path = 'local_models/cardiffnlp/twitter-roberta-base-emotion'
emotion_tokenizer_path = 'local_models/cadiffnlp/tokenizer'
summary_model_path = 'local_models/facebook/bart-large-cnn'
summary_tokenizer_path = 'local_models/facebook/token/bart-large-cnn'
tokenize_path = 'local_models/finiteautomata/tokenizer'

key = "2f01a585-19e6-4928-9f8f-18240ba81842"


def sent_news(fire_connection: FirebaseConnection):
    logging.basicConfig(level=logging.INFO)
    logging.info('Starting the program...')
    welcome()

    if check_for_local_model(sentiment_model_path):
        logging.info('Loading sentiment model from local files...')
        tokenizer = AutoTokenizer.from_pretrained(tokenize_path)
        sentiment_model = AutoModelForSequenceClassification.from_pretrained(sentiment_model_path)
    else:
        logging.info('Downloading sentiment model...')
        tokenizer = AutoTokenizer.from_pretrained("finiteautomata/bertweet-base-sentiment-analysis")
        sentiment_model = AutoModelForSequenceClassification.from_pretrained(
            "finiteautomata/bertweet-base-sentiment-analysis")

        tokenizer.save_pretrained(tokenize_path)
        sentiment_model.save_pretrained(sentiment_model_path)

    if check_for_local_model(summary_model_path):
        logging.info('Loading summary model from local files...')
        summarizer = BartForConditionalGeneration.from_pretrained(summary_model_path)
        summary_tokenizer = BartTokenizer.from_pretrained(summary_tokenizer_path)
    else:
        logging.info('Downloading summary model...')
        summarizer = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")
        summary_tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")

        summarizer.save_pretrained(summary_model_path)
        summary_tokenizer.save_pretrained(summary_tokenizer_path)

    if check_for_local_model(emotion_model_path):
        logging.info('Loading emotion model from local files...')
        emotion_model = AutoModelForSequenceClassification.from_pretrained(emotion_model_path)
        emotion_tokenizer = AutoTokenizer.from_pretrained(emotion_tokenizer_path)
    else:
        logging.info('Downloading emotion model...')
        emotion_model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-emotion")
        emotion_tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-emotion")

        emotion_model.save_pretrained(emotion_model_path)
        emotion_tokenizer.save_pretrained(emotion_tokenizer_path)

    analyser = Analyser(tokenizer_sentiment=tokenizer, sentiment_model=sentiment_model, summary_model=summarizer,
                        emotion_model=emotion_model, emotion_tokenizer=emotion_tokenizer,
                        tokenizer_summary=summary_tokenizer)

    fire = fire_connection
    topic_gateway = Topics(key)

    logging.info('Starting the analysis...')
    topic_gateway.get_topics(analyser=analyser, firebase=fire)
# welcome()
if __name__ == '__main__':
    logging.info('Initializing the database...')

    fire = FirebaseConnection('https://sent-news-357414-default-rtdb.europe-west1.firebasedatabase.app/',
                              'db/keys/sent-news-357414-firebase-adminsdk-okg5o-dfc08d365d.json')
    sent_news(fire)
    print('Starting scheduler...')
    scheduler = BlockingScheduler()
    scheduler.add_job(sent_news, 'interval', minutes=10, args=[fire])
    scheduler.start()

