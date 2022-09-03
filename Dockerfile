FROM python:3.9-slim-buster
WORKDIR /app
COPY requirements.txt ./

RUN pip install -r requirements.txt
RUN pip install pymongo

COPY . .

CMD [ "python", "send_news.py"]