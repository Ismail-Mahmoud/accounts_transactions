FROM python:3.10

WORKDIR /app

RUN apt-get update 
RUN apt-get install python3-dev gcc -y

RUN pip install --upgrade pip

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
