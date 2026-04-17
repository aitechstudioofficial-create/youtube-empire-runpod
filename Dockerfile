FROM python:3.11-slim-bullseye

RUN apt-get update -y && \
    apt-get install -y ffmpeg git && \
    apt-get clean

WORKDIR /app

RUN git clone https://github.com/aitechstudioofficial-create/youtube-empire-runpod /app

RUN pip install runpod==1.7.3

CMD ["python", "-u", "/app/handler.py"]
