# Portfolio

## About

A Python 3 web application, built using Flask to serve my portfolio.

### Features

- Home and about sections
- Simple blog 
- Contact (emails sent via SendGrid)

## Installing

Install the necessary packages via `pip`:

```
pip install -r requirements.txt
```

## Running

The app can be run via `gunicorn` with the following command:

```
gunicorn wsgi:app
```