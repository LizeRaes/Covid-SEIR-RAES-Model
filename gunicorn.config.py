"""Gunicorn configuration."""
import os
bind = ':{}'.format(int(os.environ.get('PORT', 8080)))

workers = 4
#worker_class = 'gevent'

accesslog = '-'