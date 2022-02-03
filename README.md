# AO3 RSS

This Flask app can be used to serve RSS feeds for works from Archive of Our Own (AO3).

## Quick Start

### Docker

The Docker image uses a [Gunicorn](https://gunicorn.org/) server.

```shell
git clone https://github.com/kthchew/ao3-rss.git
cd ao3-rss
docker build -t ao3-rss .
docker run --publish 127.0.0.1:8000:8000 ao3-rss
```

Then go to `http://127.0.0.1:8000/works/<work_id>`