FROM python:3.8.5-buster

WORKDIR /app
COPY requirements.txt ./

RUN python -m pip install --upgrade pip
RUN pip install numpy
RUN pip install -r requirements.txt
RUN pip install pymongo

COPY . .

CMD [ "python", "send_news.py"]