FROM python:3.8
COPY requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt
COPY . /app
WORKDIR /app
EXPOSE 5000

ENTRYPOINT gunicorn main:app --reload --bind 0.0.0.0:5000 --workers 1 --threads 2 --timeout 0 