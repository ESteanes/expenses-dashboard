# app/Dockerfile

FROM python:3.13-slim

WORKDIR /app


COPY requirements.txt ./
COPY app/ ./app/

RUN pip3 install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get -y install poppler-utils && apt-get clean

EXPOSE 8501

ENTRYPOINT ["env", "PYTHONPATH=.", "streamlit", "run", "app/Home_Page.py", "--server.port=8501", "--server.address=0.0.0.0"]
