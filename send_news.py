import argparse
import logging
import sys

from pandas import read_csv
from transformers import pipeline, DistilBertTokenizer, \
    DistilBertForSequenceClassification

from news_api import get_recent_headlines, json_to_dataframe, get_headlines_to_certain_category


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
        articles_dataframe.at[index, 'sentiment'] = model(row['description'])[0]['label']

    return articles_dataframe


def get_emotion(model, articles_dataframe):
    articles_dataframe['emotion'] = 'None'

    for index, row in articles_dataframe.iterrows():
        articles_dataframe.at[index, 'emotion'] = model(row['description'])[0]['label']

    return articles_dataframe


def write_to_csv(dataframe_general, dataframe_category):
    # drop columns that are not needed
    dataframe_general = dataframe_general.drop(
        columns=['urlToImage', 'publishedAt', 'source.id', 'author', 'content', 'url'])

    # save data to csv
    logging.info('Saving data to csv...')

    dataframe_general.to_csv('output/general_news.csv')
    if dataframe_category is not None:
        dataframe_category.drop(
            columns=['urlToImage', 'publishedAt', 'source.id', 'author', 'content', 'url'])
        dataframe_category.to_csv('output/category_news.csv')


def send_news():
    parser = argparse.ArgumentParser()
    logging.basicConfig(level=logging.INFO)
    parser.add_argument('--key', type=str, required=False,
                        help='News API key, necessary to access the API and to expand'
                             'the news database',
                        default='1356bdb2fd6c4b889edba37049b6ab2d')
    parser.add_argument('--model', type=str, required=True, help='Path to the model to use for prediction. Two '
                                                                 'models are available: binary and emotional classification.'
                                                                 'use "both" if both models should be used.')
    parser.add_argument('--category', type=str, required=False, help='Category of news')

    args = parser.parse_args()

    bin_model_path = 'distilbert-base-uncased-finetuned-sst-2-english'
    emotion_model_path = 'bhadresh-savani/distilbert-base-uncased-emotion'

    logging.info('Loading the model...')

    if (args.category is not None) and (args.model == 'both'):
        logging.info('Preparing both model...')
        tokenizer = DistilBertTokenizer.from_pretrained(bin_model_path)
        bin_model = DistilBertForSequenceClassification.from_pretrained(bin_model_path)
        bin_model = prepare_model(bin_model, tokenizer)

        emo_model = pipeline("text-classification", model=emotion_model_path,
                             return_all_scores=False)

        general, category_news = get_news(key=args.key, category=args.category)
        general = get_sentiment(bin_model, general)
        category_news = get_sentiment(bin_model, category_news)

        general = get_emotion(emo_model, general)
        category_news = get_emotion(emo_model, category_news)

        write_to_csv(general, category_news)

    if (args.category is None) and (args.model == 'both'):
        logging.info('Preparing both model...')
        tokenizer = DistilBertTokenizer.from_pretrained(bin_model_path)
        bin_model = DistilBertForSequenceClassification.from_pretrained(bin_model_path)
        bin_model = prepare_model(bin_model, tokenizer)

        emo_model = pipeline("text-classification", model=emotion_model_path,
                             return_all_scores=False)

        general = get_news(key=args.key, category=None)
        general = get_sentiment(bin_model, general)
        general = get_emotion(emo_model, general)

        write_to_csv(general, None)

    if (args.category is not None) and (args.model == 'binary'):
        logging.info('Preparing binary model...')
        tokenizer = DistilBertTokenizer.from_pretrained(bin_model_path)
        bin_model = DistilBertForSequenceClassification.from_pretrained(bin_model_path)
        bin_model = prepare_model(bin_model, tokenizer)

        general, category_news = get_news(key=args.key, category=args.category)
        general = get_sentiment(bin_model, general)
        category_news = get_sentiment(bin_model, category_news)
        write_to_csv(general, category_news)

    if (args.category is None) and (args.model == 'binary'):
        logging.info('Preparing binary model...')
        tokenizer = DistilBertTokenizer.from_pretrained(bin_model_path)
        bin_model = DistilBertForSequenceClassification.from_pretrained(bin_model_path)
        bin_model = prepare_model(bin_model, tokenizer)

        general = get_news(key=args.key, category=None)
        general = get_sentiment(bin_model, general)
        write_to_csv(general, None)

    if (args.category is not None) and (args.model == 'emotional'):
        logging.info('Preparing emotional model...')
        emo_model = pipeline("text-classification", model=emotion_model_path,
                             return_all_scores=False)

        general, category_news = get_news(key=args.key, category=args.category)
        general = get_emotion(emo_model, general)
        category_news = get_emotion(emo_model, category_news)
        write_to_csv(general, category_news)

    if (args.category is None) and (args.model == 'emotional'):
        logging.info('Preparing emotional model...')
        emo_model = pipeline("text-classification", model=emotion_model_path,
                             return_all_scores=False)

        general = get_news(key=args.key, category=None)
        general = get_emotion(emo_model, general)
        write_to_csv(general, None)


if __name__ == "__main__":
    sys.exit(send_news())
