FROM python:3.12-slim

WORKDIR /bot

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY main.py ./main.py

EXPOSE 8080

CMD [ "python", "main.py" ]