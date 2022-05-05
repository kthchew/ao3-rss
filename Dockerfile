FROM python:3.10.4-slim

ENV ADDRESS=0.0.0.0
ENV PORT=8000
ENV GUNICORN_CMD_ARGS=""

COPY ./requirements.txt /app/

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn \
    && groupadd -g 307 app \
    && useradd -u 307 -g 307 app

COPY ./ao3_rss /app/ao3_rss

USER 307:307

CMD ["/bin/sh", "-c", "/usr/local/bin/gunicorn --bind $ADDRESS:$PORT ao3_rss.server:app"]
