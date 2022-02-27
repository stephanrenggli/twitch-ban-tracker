FROM python:alpine

RUN mkdir /app

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

# use unbuffered output https://stackoverflow.com/questions/29663459/python-app-does-not-print-anything-when-running-detached-in-docker
CMD ["python","-u","twitch-ban-tracker.py"]