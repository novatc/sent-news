import argparse
import logging
import sys

from pandas import read_csv
from transformers import pipeline, AutoModelForSequenceClassification, DistilBertTokenizer

from news_api import get_recent_headlines, json_to_dataframe, get_headlines_to_certain_category


def prepare_model(model, tokenizer):
    return pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)


# turn row from csv file into list
def row_to_list(file, row):
    data = read_csv(file)
    items = data[row].tolist()
    return dict(zip(items, ['None'] * len(items)))


# def get_sentiment(model, articles):
#     # iterate over dict and get sentiment for each article
#     for key in articles:
#         articles[key] = model(key)[0]['label']
#     return articles


def get_news(key,category):
    # not null check
    recent_news = get_recent_headlines(key=key)
    logging.info('Request status: {}'.format(recent_news['status']))
    logging.info(f'Fetched {recent_news["totalResults"]} new entries')

    # drop rows with null values
    recent_news = json_to_dataframe(recent_news['articles'])
    recent_news = recent_news.dropna()

    if category is not None:
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


    logging.info('Loading the model...')
    if (args.model == 'emotion'):
        logging.info('Preparing the emotion model...')
        model = AutoModelForSequenceClassification.from_pretrained("model/emotion")
        tokenizer = DistilBertTokenizer.from_pretrained("model/vocab.txt")
        model = prepare_model(model, tokenizer)

    elif (args.model == 'binary'):
        logging.info('Preparing the binary model...')
        model = AutoModelForSequenceClassification.from_pretrained("model/binary/500")
        tokenizer = DistilBertTokenizer.from_pretrained("model/vocab.txt")
        model = prepare_model(model, tokenizer)

    elif (args.model == 'both'):
        logging.info('Preparing both model...')
        model = AutoModelForSequenceClassification.from_pretrained("model/binary/500")
        tokenizer = DistilBertTokenizer.from_pretrained("model/vocab.txt")
        bin_model = prepare_model(model, tokenizer)
        model = AutoModelForSequenceClassification.from_pretrained("model/emotion")
        tokenizer = DistilBertTokenizer.from_pretrained("model/vocab.txt")
        emo_model = prepare_model(model, tokenizer)

    if(args.category is not None):
        general, category_news = get_news(key=args.key, category=args.category)

        general = get_sentiment(bin_model, general)
        general = get_emotion(emo_model, general)

        category_news = get_sentiment(bin_model, category_news)
        category_news = get_emotion(emo_model, category_news)

        #drop columns that are not needed
        general = general.drop(columns=['urlToImage'])

        #save data to csv
        logging.info('Saving data to csv...')

        general.to_csv('output/general_news.csv')
        category_news.to_csv('output/category_news.csv')




    # articles = row_to_list(row='description', file='news.csv')
    #
    # logging.info('Getting the sentiment...')
    # get_sentiment(model, articles)
    #
    #
    # logging.info('Saving the sentiment...')
    # # save dict as csv file
    # with open('sentiment_pos_neg.csv', 'w') as f:
    #     w = csv.writer(f)
    #     w.writerow(['description', 'sentiment'])
    #     for key, value in articles.items():
    #         w.writerow([key, value])
    #
    # # count positive and negative news
    # pos_count = 0
    # neg_count = 0
    # for key, value in articles.items():
    #     if value == 'POSITIVE':
    #         pos_count += 1
    #     elif value == 'NEGATIVE':
    #         neg_count += 1
    # logging.info('Positive news: ' + str(pos_count))
    # logging.info('Negative news: ' + str(neg_count))

if __name__ == "__main__":
    sys.exit(send_news())