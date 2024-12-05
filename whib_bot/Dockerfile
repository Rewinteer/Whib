FROM python:3.11-slim

WORKDIR /whib_bot

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/whib_bot

COPY . /whib_bot

CMD ["python", "-u", "main.py"]