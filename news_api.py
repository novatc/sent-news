import argparse
import logging
import sys

import pandas as pd
import requests

key = ' '


def get_recent_headlines(key: str):
    r = requests.get(url=f'https://newsapi.org/v2/top-headlines?country=us&apiKey={key}')
    return r.json()


def get_headlines_to_certain_category(key: str, category: str):
    r = requests.get(url=f'https://newsapi.org/v2/top-headlines?country=us&category={category}&apiKey={key}')
    return r.json()

def json_to_dataframe(json):
    return pd.DataFrame.from_dict(pd.json_normalize(json), orient='columns')

def get_news():
    parser = argparse.ArgumentParser()
    logging.basicConfig(level=logging.INFO)
    parser.add_argument('--key', type=str, required=True, help='News API key, necessary to access the API')
    parser.add_argument('--category', type=str, required=False, help='Category of news')

    args = parser.parse_args()

    # not null check
    recent_news = get_recent_headlines(key=args.key)
    logging.info('Request status: {}'.format(recent_news['status']))
    logging.info(f'Fetched {recent_news["totalResults"]} new entries')

    # drop rows with null values
    recent_news = json_to_dataframe(recent_news['articles'])
    recent_news = recent_news.dropna()
    recent_news = recent_news.drop(columns=['urlToImage', 'publishedAt', 'source.id'])



    if args.category is not None:
        category_news = get_headlines_to_certain_category(key=args.key, category=args.category)
        category_news = json_to_dataframe(category_news['articles'])
        category_news = category_news.dropna()
        category_news = category_news.drop(columns=['urlToImage', 'publishedAt', 'source.id'])
        return recent_news, category_news

    return recent_news

if __name__ == "__main__":
    sys.exit(get_news())