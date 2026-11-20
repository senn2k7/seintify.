"""Titik masuk Vercel (serverless function) untuk aplikasi Django."""
import os
import sys

# Folder proyek (berisi manage.py, config/, portal/) harus bisa di-import.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from django.core.wsgi import get_wsgi_application  # noqa: E402

# Vercel mencari objek WSGI bernama `app`.
app = get_wsgi_application()
