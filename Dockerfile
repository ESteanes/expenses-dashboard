# app/Dockerfile

FROM --platform=$BUILDPLATFORM python:3.11-slim

ARG TARGETOS
ARG TARGETARCH

RUN echo "I am running on $TARGETOS, building for $TARGETARCH" > /log
WORKDIR /app


COPY requirements.txt ./
COPY app/ ./app/

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app/Home_Page.py", "--server.port=8501", "--server.address=0.0.0.0"]
