#!/bin/bash

# Startup script for Django + Nginx
set -e

echo "🚀 Starting Django application with Nginx..."

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate --noinput

# Start Django application on port 8001 (internal)
echo "🐍 Starting Django application on port 8001..."
gunicorn --bind 127.0.0.1:8001 --workers 3 --timeout 120 --access-logfile - --error-logfile - core.wsgi:application &
DJANGO_PID=$!

# Wait a moment for Django to start
sleep 3

# Start Nginx on port 80 (external)
echo "🌐 Starting Nginx on port 80..."
nginx -g "daemon off;" &
NGINX_PID=$!

echo "✅ Both Django and Nginx are running!"
echo "🌐 Application is available at: http://localhost:8000"
echo "🔍 Django running internally on: http://127.0.0.1:8001"
echo "🌐 Nginx serving on: http://0.0.0.0:80"

# Wait for both processes
wait $DJANGO_PID $NGINX_PID
