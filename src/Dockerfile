FROM python:3.12-slim

WORKDIR /app

COPY config/requirements.txt .

RUN pip install -r requirements.txt

COPY . .
