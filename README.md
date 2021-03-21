# Portfolio

## About

A Python 3 web application, built using Flask to serve my portfolio.

### Features

- Home and about sections
- Simple blog 
- Contact (emails sent via SendGrid)

### Stack

- Python 3
- [Flask](https://flask.palletsprojects.com/en/1.1.x/)
- [Halfmoon UI](https://www.gethalfmoon.com/)
- [Feather Icons](https://feathericons.com/)


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