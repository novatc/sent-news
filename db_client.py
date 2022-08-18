import csv
import json
import logging

from pymongo import MongoClient


def get_database():
    client = MongoClient('localhost', 27017)
    return client


def make_json(csvFilePath, jsonFilePath):
    # create a dictionary
    data = {}

    # Open a csv reader called DictReader
    with open(csvFilePath, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)

        # Convert each row into a dictionary
        # and add it to data
        for rows in csvReader:
            # Assuming a column named 'No' to
            # be the primary key
            key = rows['title']
            data[key] = rows

    # Open a json writer, and use the json.dumps()
    # function to dump data
    with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(data, indent=4))

    return data


def save_articles(dataframe):
    client = get_database()
    collection = client['sent-news']['articles']
    for index, row in dataframe.iterrows():
        if not check_for_duplicates(row.to_dict()):
            try:
                collection.insert_one(row.to_dict())
            except:
                pass


def check_for_duplicates(article):
    client = get_database()
    db = client['sent-news']
    collection = db['articles']
    query = collection.find_one(article)
    if query: return True
    else: return False