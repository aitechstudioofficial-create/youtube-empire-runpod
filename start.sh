#!/bin/bash
apt-get update -y
apt-get install -y ffmpeg git
pip install runpod==1.7.3
python -u /app/handler.py
