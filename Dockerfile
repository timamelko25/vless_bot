FROM python:3.12-alpine

WORKDIR /app

ENV PYTHONDONOTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

CMD ["python app/main.py"]