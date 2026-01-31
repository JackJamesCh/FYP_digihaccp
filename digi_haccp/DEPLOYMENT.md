# Deployment (Gunicorn)

This project is configured to run with Gunicorn using the Django WSGI module:

```bash
gunicorn digi_haccp.wsgi:application --config gunicorn.conf.py
```

## Render / Procfile

Render will read the `Procfile` at the project root:

```
web: gunicorn digi_haccp.wsgi:application --config gunicorn.conf.py
```

## Required Environment Variables

- `SECRET_KEY`
- `DEBUG` (set to `False` in production)
- `ALLOWED_HOSTS` (update `settings.py` accordingly for production)
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`

## Optional Gunicorn Tuning

- `PORT` (defaults to `8000`)
- `GUNICORN_WORKERS` (defaults to `CPU*2+1`)
- `GUNICORN_THREADS` (defaults to `2`)
- `GUNICORN_TIMEOUT` (defaults to `120`)
- `GUNICORN_LOG_LEVEL` (defaults to `info`)