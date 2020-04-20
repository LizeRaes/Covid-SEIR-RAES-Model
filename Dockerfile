FROM python:3.7-slim

COPY requirements.txt /

RUN apt-get update

RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install gunicorn gevent

COPY . /app
WORKDIR /app

EXPOSE 8080

ENTRYPOINT ["gunicorn", "-c", "gunicorn.config.py", "app:server"]