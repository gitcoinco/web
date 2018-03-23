# -*- coding: utf-8 -*-
"""Define the project gunicorn configuration."""
import multiprocessing
import os

backlog = int(os.environ.get('GUNICORN_BACKLOG', 2048))
bind = os.environ.get('WEB_BIND_INTERFACE', '0.0.0.0:8000')
worker_class = os.environ.get('GUNICORN_WORKER_CLASS', 'sync')
workers = os.environ.get('GUNICORN_WORKERS', None) or (multiprocessing.cpu_count() * 2) + 1
worker_connections = int(os.environ.get('GUNICORN_WORKER_CONNECTIONS', 1000))
timeout = int(os.environ.get('GUNICORN_TIMEOUT', 30))
keepalive = int(os.environ.get('GUNICORN_KEEPALIVE', 2))
spew = bool(os.environ.get('GUNICORN_SPEW', False))
accesslog = os.environ.get('GUNICORN_ACCESSLOG', '-')
errorlog = os.environ.get('GUNICORN_ERRORLOG', '-')
loglevel = os.environ.get('GUNICORN_LOGLEVEL', 'info')
