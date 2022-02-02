# AO3 RSS

This web server can be used to serve RSS feeds for works from Archive of Our Own (AO3).

## Usage

```shell
cd src
FLASK_APP=server flask run
```

Then go to `http://127.0.0.1:5000/works/<work_id>`