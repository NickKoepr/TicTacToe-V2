FROM python:3.10-alpine

WORKDIR /tictactoe

COPY . .

RUN pip install -r requirements.txt

ENV PYTHONPATH="/tictactoe"

ENTRYPOINT ["python3", "bot.py"]