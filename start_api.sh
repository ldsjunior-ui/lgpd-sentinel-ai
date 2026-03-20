#!/bin/bash
# Runs uvicorn without entering venv context (bypasses pyvenv.cfg sandbox restriction)
export PYTHONPATH="/Users/leonardobergonzidesouzajunior/Documents/lgpd-sentinel-ai/.venv/lib/python3.11/site-packages:$PYTHONPATH"
exec /opt/homebrew/opt/python@3.11/bin/python3.11 -m uvicorn src.main:app --reload --port 8000
