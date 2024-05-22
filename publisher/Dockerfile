FROM python:3.8

WORKDIR /app
COPY . /app

RUN apt-get update && apt-get install -y protobuf-compiler
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
