FROM python:3.8
COPY requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt
COPY . /app
WORKDIR /app
EXPOSE 80
ENTRYPOINT ["./start.sh"]