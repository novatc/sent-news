import logging
import os

import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification, BartForConditionalGeneration, \
    AutoModelForSeq2SeqLM

from db.articles_api import Articles
from db.firebase_connection import FirebaseConnection
from text_analysis import Analyser


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
emotion_model_path = 'local_models/j-hartmann/emotion-english-distilroberta-base'
summary_model_path = 'local_models/sshleifer/distilbart-cnn-12-6'
tokenize_path = 'local_models/finiteautomata/tokenizer'
tokenizer_summary_path = 'local_models/sshleifer/tokenizer'

key = "2f01a585-19e6-4928-9f8f-18240ba81842"

# welcome()
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info('Starting the program...')
    # welcome()

    if check_for_local_model(sentiment_model_path):
        logging.info('Loading sentiment model from local files...')
        tokenizer = AutoTokenizer.from_pretrained(tokenize_path)
        sentiment_model = AutoModelForSequenceClassification.from_pretrained(sentiment_model_path)
    else:
        logging.info('Downloading sentiment model...')
        tokenizer = AutoTokenizer.from_pretrained("finiteautomata/bertweet-base-sentiment-analysis")
        sentiment_model = AutoModelForSequenceClassification.from_pretrained("local_models/finiteautomata/tokenizer")

        tokenizer.save_pretrained(tokenize_path)
        sentiment_model.save_pretrained(sentiment_model_path)

    if check_for_local_model(summary_model_path):
        logging.info('Loading summary model from local files...')
        tokenizer_summary = AutoTokenizer.from_pretrained("local_models/sshleifer/distilbart-cnn-12-6")
        summarizer = AutoModelForSeq2SeqLM.from_pretrained("local_models/sshleifer/distilbart-cnn-12-6")
    else:
        logging.info('Downloading summary model...')
        tokenizer_summary = AutoTokenizer.from_pretrained("sshleifer/distilbart-cnn-12-6")
        summarizer = AutoModelForSeq2SeqLM.from_pretrained("sshleifer/distilbart-cnn-12-6")

        summarizer.save_pretrained(summary_model_path)
        tokenizer_summary.save_pretrained(tokenizer_summary_path)

    if check_for_local_model(emotion_model_path):
        logging.info('Loading emotion model from local files...')
        emotion_model = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k = 1)
    else:
        logging.info('Downloading emotion model...')
        emotion_model = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base",
                                 tokenizer=tokenizer)

        emotion_model.save_pretrained(emotion_model_path)

    analyser = Analyser(tokenizer_sentiment=tokenizer, sentiment_model=sentiment_model, summary_model=summarizer,
                        emotion_model=emotion_model, tokenizer_summary=tokenizer_summary)

    logging.info('Initializing the database...')
    fire = FirebaseConnection('https://sent-news-357414-default-rtdb.europe-west1.firebasedatabase.app/',
                              'db/keys/sent-news-357414-firebase-adminsdk-okg5o-dfc08d365d.json')
    articles_gateway = Articles(key)

    logging.info('Starting the analysis...')
    articles_gateway.start_article_stream(analyser=analyser, firebase=fire)



