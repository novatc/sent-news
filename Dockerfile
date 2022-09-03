FROM python:3.9-buster

WORKDIR /app
COPY requirements.txt ./

RUN python -m pip install --upgrade pip
RUN pip install --extra-index-url https://alpine-wheels.github.io/index numpy
RUN pip install -r requirements.txt
RUN pip install pymongo

COPY . .

CMD [ "python", "send_news.py"]