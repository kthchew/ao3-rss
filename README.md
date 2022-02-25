# AO3 RSS

This Flask app can be used to serve RSS and Atom feeds for works and series from Archive of Our Own (AO3).

## Quick Start

### Docker

The Docker image uses a [Gunicorn](https://gunicorn.org/) server.

```shell
docker run --detach --publish 127.0.0.1:8000:8000 ghcr.io/kthchew/ao3-rss:latest
```

Or, use a `docker-compose.yml` file:

```yaml
version: '3'

services:
  ao3-rss:
    image: ghcr.io/kthchew/ao3-rss:latest
    ports:
      - "127.0.0.1:8000:8000"
    restart: unless-stopped
```

Then go to `http://127.0.0.1:8000/works/<work_id>` or `http://127.0.0.1:8000/series/<series_id>`. These will output Atom feeds. If you need RSS, you can add just `/rss` to the end: `http://127.0.0.1:8000/works/<work_id>/rss`.

#### Environment Variables

You can set environment variables in the Docker container to change its behavior.

| Variable            | Default   | Value         | Description                                                         |
| ------------------- | --------- | ------------- | ------------------------------------------------------------------- |
| `ADDRESS`           | `0.0.0.0` | IP Address    | An IP address to bind to (e.g. `0.0.0.0` to bind to all interfaces) |
| `PORT`              | `8000`    | Port          | A port to bind to                                                   |
| `GUNICORN_CMD_ARGS` | *unset*   | Any arguments | Additional arguments you wish to pass to Gunicorn                   |

### Development

For development purposes, you can also just use `flask run`:

```shell
git clone https://github.com/kthchew/ao3-rss.git
cd ao3-rss
pip install -r requirements.txt
FLASK_APP=ao3_rss.server flask run
```
