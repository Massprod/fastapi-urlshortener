FROM python:alpine

WORKDIR /shorty

COPY requirements.txt .

RUN pip install -r requirements.txt


COPY . .

EXPOSE 5000/tcp

CMD ["uvicorn", "shorty:shorty", "--host", "0.0.0.0", "--port", "5000"]