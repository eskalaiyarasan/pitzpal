#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# NEW: Generate a temporary, passwordless SSH key inside the container for Pinggy
if [ ! -f ~/.ssh/id_ed25519 ]; then
    echo "Generating temporary SSH key for Pinggy tunnel..."
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
    ssh-keygen -t ed25519 -N "" -f ~/.ssh/id_ed25519
fi

echo "Checking for missing migrations..."
python manage.py makemigrations crm  --noinput
python manage.py makemigrations home --noinput
python manage.py makemigrations vsComputer --noinput
python manage.py makemigrations pitzpalgame --noinput
python manage.py makemigrations --noinput

echo "Applying database migrations..."
python manage.py migrate --noinput

# Infinite loop to handle restarting every hour
while true; do
    echo "------------------------------------------------"
    echo "Starting background services (Django & Pinggy)..."
    echo "------------------------------------------------"

    # Start Django Server in the background (no exec, so the script can continue)
    python manage.py runserver 0.0.0.0:8000 &
    DJANGO_PID=$! # Capture the process ID of Django

    # Wait a couple of seconds for Django to initialize
    sleep 5

    echo "Starting Pinggy Tunnel with custom domain token..."
    # Authenticated Pinggy format using your domain token as the SSH username
    ssh -o StrictHostKeyChecking=accept-new \
        -p 443 \
        -R 0:localhost:8000 \
        -o ServerAliveInterval=180 f85XiZw3ZAL@pro.pinggy.io
    PINGGY_PID=$! # Capture the process ID of Pinggy

    echo "Services are running. Waiting for 1 hour (3600 seconds) before restarting..."
    sleep 7200

    echo "Time limit reached! Gracefully stopping services..."
    
    # Kill both processes
    #kill $DJANGO_PID $PINGGY_PID || true
    read n
    # Wait briefly to ensure ports are completely released before the next loop starts
    sleep 5
done
