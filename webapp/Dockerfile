FROM python:3.11-slim

WORKDIR /webapp

COPY requirements.txt .

RUN apt-get update && apt-get -y install libpq-dev gcc && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--workers=2", "--threads=2", "--bind=0.0.0.0:5000", "app:app"]