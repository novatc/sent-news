import argparse
import logging
import sys

from pandas import read_csv
from transformers import pipeline, DistilBertTokenizer, DistilBertForSequenceClassification

from db_client import save_articles
from news_api import get_recent_headlines, json_to_dataframe, get_headlines_to_certain_category
from apscheduler.schedulers.blocking import BlockingScheduler


def prepare_model(model, tokenizer):
    return pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)


# turn row from csv file into list
def row_to_list(file, row):
    data = read_csv(file)
    items = data[row].tolist()
    return dict(zip(items, ['None'] * len(items)))


def get_news(key, category):
    recent_news = get_recent_headlines(key=key)
    logging.info('Request status: {}'.format(recent_news['status']))
    logging.info(f'Fetched {recent_news["totalResults"]} new entries')

    # drop rows with null values
    recent_news = json_to_dataframe(recent_news['articles'])
    recent_news = recent_news.dropna()

    if category is not None:
        logging.info('Fetching headlines for category: {}'.format(category))
        category_news = get_headlines_to_certain_category(key=key, category=category)
        category_news = json_to_dataframe(category_news['articles'])
        category_news = category_news.dropna()
        return recent_news, category_news

    return recent_news


def get_sentiment(model, articles_dataframe):
    articles_dataframe['sentiment'] = 'None'

    for index, row in articles_dataframe.iterrows():
        articles_dataframe.at[index, 'sentiment'] = model(row['summary'])[0]['label']

    return articles_dataframe


def get_emotion(model, articles_dataframe):
    articles_dataframe['emotion'] = 'None'

    for index, row in articles_dataframe.iterrows():
        articles_dataframe.at[index, 'emotion'] = model(row['summary'])[0]['label']

    return articles_dataframe


def get_summary(model, dataframe):
    dataframe['summary'] = 'None'

    for index, row in dataframe.iterrows():
        dataframe.at[index, 'summary'] = model(row['content'])[0]['summary_text']

    return dataframe


def write_to_csv(dataframe_general, dataframe_category):
    # drop columns that are not needed
    dataframe_general = dataframe_general.drop(
        columns=['urlToImage', 'publishedAt', 'source.id', 'author', 'url'])

    # save data to csv
    logging.info('Saving data to csv...')

    dataframe_general.to_csv('output/general_news.csv')
    if dataframe_category is not None:
        dataframe_category.drop(
            columns=['urlToImage', 'publishedAt', 'source.id', 'author', 'content', 'url'])
        dataframe_category.to_csv('output/category_news.csv')


def turn_dataframe_in_object(dataframe):
    return dataframe.to_dict('records')


def dataframe_to_json(dataframe):
    return dataframe.to_json(orient='records')


def write_to_database(dataframe):
    logging.info('Saving data to database...')
    save_articles(dataframe)


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


def send_news():
    parser = argparse.ArgumentParser()
    logging.basicConfig(level=logging.INFO)
    parser.add_argument('--key', type=str, required=False,
                        help='News API key, necessary to access the API and to expand'
                             'the news database',
                        default='1356bdb2fd6c4b889edba37049b6ab2d')
    parser.add_argument('--model', type=str, required=True, help='Path to the model to use for prediction. Two '
                                                                 'models are available: binary and emotional classification.'
                                                                 'use "both" if both models should be used.', default='both')
    parser.add_argument('--category', type=str, required=False, help='Category of news')

    args = parser.parse_args()

    bin_model_path = 'distilbert-base-uncased-finetuned-sst-2-english'
    emotion_model_path = 'bhadresh-savani/distilbert-base-uncased-emotion'
    summarization_model_path = 'facebook/bart-large-cnn'
    welcome()
    logging.info('Loading the model...')

    summarizer = pipeline("summarization", model=summarization_model_path)

    if (args.category is not None) and (args.model == 'both'):
        logging.info('Preparing both model...')
        tokenizer = DistilBertTokenizer.from_pretrained(bin_model_path)
        bin_model = DistilBertForSequenceClassification.from_pretrained(bin_model_path)
        bin_model = prepare_model(bin_model, tokenizer)

        emo_model = pipeline("text-classification", model=emotion_model_path,
                             return_all_scores=False)

        general, category_news = get_news(key=args.key, category=args.category)
        general = get_summary(summarizer, general)
        category_news = get_summary(summarizer, category_news)
        general = get_sentiment(bin_model, general)
        category_news = get_sentiment(bin_model, category_news)

        general = get_emotion(emo_model, general)
        category_news = get_emotion(emo_model, category_news)

        #write_to_csv(general, category_news)
        write_to_database(general)
        write_to_database(category_news)

    if (args.category is None) and (args.model == 'both'):
        logging.info('Preparing both model...')
        tokenizer = DistilBertTokenizer.from_pretrained(bin_model_path)
        bin_model = DistilBertForSequenceClassification.from_pretrained(bin_model_path)
        bin_model = prepare_model(bin_model, tokenizer)

        emo_model = pipeline("text-classification", model=emotion_model_path,
                             return_all_scores=False)

        general = get_news(key=args.key, category=None)
        general = get_summary(summarizer, general)
        general = get_sentiment(bin_model, general)
        general = get_emotion(emo_model, general)

        #write_to_csv(general, None)
        write_to_database(general)

    if (args.category is not None) and (args.model == 'binary'):
        logging.info('Preparing binary model...')
        tokenizer = DistilBertTokenizer.from_pretrained(bin_model_path)
        bin_model = DistilBertForSequenceClassification.from_pretrained(bin_model_path)
        bin_model = prepare_model(bin_model, tokenizer)

        general, category_news = get_news(key=args.key, category=args.category)
        general = get_summary(summarizer, general)
        category_news = get_summary(summarizer, category_news)

        general = get_sentiment(bin_model, general)
        category_news = get_sentiment(bin_model, category_news)

        #write_to_csv(general, category_news)

        write_to_database(general)
        write_to_database(category_news)

    if (args.category is None) and (args.model == 'binary'):
        logging.info('Preparing binary model...')
        tokenizer = DistilBertTokenizer.from_pretrained(bin_model_path)
        bin_model = DistilBertForSequenceClassification.from_pretrained(bin_model_path)
        bin_model = prepare_model(bin_model, tokenizer)

        general = get_news(key=args.key, category=None)
        general = get_summary(summarizer, general)
        general = get_sentiment(bin_model, general)

        #write_to_csv(general, None)

        write_to_database(general)

    if (args.category is not None) and (args.model == 'emotional'):
        logging.info('Preparing emotional model...')
        emo_model = pipeline("text-classification", model=emotion_model_path,
                             return_all_scores=False)

        general, category_news = get_news(key=args.key, category=args.category)
        general = get_summary(summarizer, general)
        category_news = get_summary(summarizer, category_news)

        general = get_emotion(emo_model, general)
        category_news = get_emotion(emo_model, category_news)

        #write_to_csv(general, category_news)
        write_to_database(general)
        write_to_database(category_news)

    if (args.category is None) and (args.model == 'emotional'):
        logging.info('Preparing emotional model...')
        emo_model = pipeline("text-classification", model=emotion_model_path,
                             return_all_scores=False)

        general = get_news(key=args.key, category=None)
        general = get_summary(summarizer, general)
        general = get_emotion(emo_model, general)
        #write_to_csv(general, None)
        write_to_database(general)


if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(send_news, 'interval', hours=1)
    scheduler.start()
