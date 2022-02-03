FROM alpine:3.15

COPY ./requirements.txt /app/

WORKDIR /app

RUN apk add --no-cache py-pip py3-lxml \
    && pip install -r requirements.txt \
    && pip install gunicorn

COPY ./ao3_rss /app/ao3_rss

CMD gunicorn ao3_rss.server:app
