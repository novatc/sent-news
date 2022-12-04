import csv
import logging
import urllib.request

import numpy as np
import torch
from scipy.special import softmax


class Analyser:
    def __init__(self, sentiment_model, emotion_model, emotion_tokenizer, summary_model, tokenizer_sentiment, tokenizer_summary):
        logging.info('Initializing the analyser...')

        self.tokenizer_sentiment = tokenizer_sentiment
        self.tokenizer_summary = tokenizer_summary
        self.sentiment_model = sentiment_model
        self.summary_model = summary_model
        self.emotion_model = emotion_model
        self.emotion_tokenizer = emotion_tokenizer

    def get_sentiment(self, text):
        logging.info('Getting the sentiment...')
        with torch.no_grad():
            input = self.tokenizer_sentiment(text, return_tensors="pt")
            logits = self.sentiment_model(**input).logits

        predicted_class_id = logits.argmax().item()
        return self.sentiment_model.config.id2label[predicted_class_id]

    def get_summary(self, text):
        logging.info('Summarizing the text...')
        inputs = self.tokenizer_summary([text], max_length=1024, return_tensors="pt")
        summary_ids = self.summary_model.generate(inputs["input_ids"], num_beams=2, min_length=0, max_length=80)
        sum = self.tokenizer_summary.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
        return sum


    def get_emotion(self, text):
        labels = ['anger', 'joy', 'optimism', 'sadness']
        logging.info('Getting the emotion...')
        encoded_input = self.emotion_tokenizer(text, return_tensors='pt')
        output = self.emotion_model(**encoded_input)
        scores = output[0][0].detach().numpy()
        scores = softmax(scores)
        ranking = np.argsort(scores)
        ranking = ranking[::-1]
        emotions = {}
        for i in range(scores.shape[0]):
            emotions[labels[ranking[i]]] = str(scores[ranking[i]])
        return emotions

    def analyse(self, json_text):
        logging.info('Analysing the text...')
        sum = self.get_summary(json_text['body'])
        # add emotion to json_text
        json_text['emotion'] = self.get_emotion(sum)
        # add sentiment to json_text
        json_text['sentiment'] = self.get_sentiment(sum)
        # add summary to json_text
        json_text['summary'] = sum

        return json_text

