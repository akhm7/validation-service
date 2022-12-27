FROM python:3.11

RUN mkdir /app
RUN chmod 777 /app
WORKDIR /app

ENV PATH="${PATH}:/root/.local/bin"
ENV PYTHONPATH=.

COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade -r /requirements.txt

COPY ./main.py ./main.py
COPY ./binlist.csv ./binlist.csv