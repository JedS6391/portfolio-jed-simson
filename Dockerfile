FROM python:3.10.0

WORKDIR /

COPY . .

RUN pip install -r requirements.txt

CMD gunicorn --bind 0.0.0.0:$PORT wsgi:app