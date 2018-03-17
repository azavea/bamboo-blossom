FROM python:3.6

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -m gunicorn
USER gunicorn

COPY . /usr/src/app

CMD gunicorn --bind 0.0.0.0:${PORT} --capture-output bamboo_blossom.app:api
