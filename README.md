# AO3 RSS

This Flask app can be used to serve RSS feeds for works from Archive of Our Own (AO3).

## Quick Start

### Docker

The Docker image uses a [Gunicorn](https://gunicorn.org/) server.

```shell
docker run -d ghcr.io/kthchew/ao3-rss:latest
```

Or, use a `docker-compose.yml` file:

```yaml
version: '3'

services:
  ao3-rss:
    image: ghcr.io/kthchew/ao3-rss:latest
    restart: unless-stopped
```

Then go to `http://127.0.0.1:8000/works/<work_id>`

#### Environment Variables

You can set environment variables in the Docker container to change its behavior.

| Variable            | Default     | Value         | Description                                                         |
| ------------------- | ----------- | ------------- | ------------------------------------------------------------------- |
| `ADDRESS`           | `127.0.0.1` | IP Address    | An IP address to bind to (e.g. `0.0.0.0` to bind to all interfaces) |
| `PORT`              | `8000`      | Port          | A port to bind to                                                   |
| `GUNICORN_CMD_ARGS` | *unset*     | Any arguments | Additional arguments you wish to pass to Gunicorn                   |