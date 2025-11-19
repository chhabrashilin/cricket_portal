#!/usr/bin/env python
"""
Celery worker entry point
Run with: celery -A worker.worker worker --loglevel=info
"""
import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from backend.celery_app import celery_app

if __name__ == '__main__':
    celery_app.start()

