import pandas as pd
from transformers import pipeline, DistilBertTokenizer, DistilBertForSequenceClassification

news_df = pd.read_csv('output/general_news.csv')

summarizer = pipeline("summarization", model="facebook/bart-large-cnn", max_length=130, min_length=30)

news_df['summary'] = 'None'
for index, row in news_df.iterrows():
    news_df.at[index, 'summary'] = summarizer(row['content'])[0]['summary_text']
