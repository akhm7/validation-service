FROM python:3.11

RUN mkdir /app
WORKDIR /app
RUN mkdir logs

ENV PATH="${PATH}:/root/.local/bin"
ENV PYTHONPATH=.

COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade -r /requirements.txt

COPY ./main.py ./main.py
COPY ./binlist.csv ./binlist.csv