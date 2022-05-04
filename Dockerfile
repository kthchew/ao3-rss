FROM python:3.10.4-alpine

ENV ADDRESS=0.0.0.0
ENV PORT=8000
ENV GUNICORN_CMD_ARGS=""

COPY ./requirements.txt /app/

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt \
    && adduser -D -u 307 app

COPY ./ao3_rss /app/ao3_rss

USER 307:307

CMD ["/bin/sh", "-c", "/usr/bin/gunicorn --bind $ADDRESS:$PORT ao3_rss.server:app"]
