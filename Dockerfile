FROM python:3.12-alpine

WORKDIR /app

ENV PYTHONDONOTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /app/

RUN apk add --no-cache bash && \
    pip install --no-cache-dir -r requirements.txt

COPY . /app/

CMD ["bash", "-c", "python app/main.py"]