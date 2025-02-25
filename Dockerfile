FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

ENV PYTHONPATH="/app"

ENTRYPOINT ["python3", "bot.py"]