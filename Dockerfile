FROM alpine:3.15

ARG VERSION=1.0.0

ENV ADDRESS=0.0.0.0
ENV PORT=8000
ENV GUNICORN_CMD_ARGS=""

COPY ./requirements.txt /app/

WORKDIR /app

RUN apk add --no-cache py-pip py3-lxml \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn \
    && adduser -D -u 307 app

COPY ./ao3_rss /app/ao3_rss

USER 307:307

CMD ["/bin/sh", "-c", "/usr/bin/gunicorn --bind $ADDRESS:$PORT ao3_rss.server:app"]
