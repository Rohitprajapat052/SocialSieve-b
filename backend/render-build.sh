#!/usr/bin/env bash
# Install system dependencies (FFmpeg for Whisper)
apt-get update && apt-get install -y ffmpeg

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
