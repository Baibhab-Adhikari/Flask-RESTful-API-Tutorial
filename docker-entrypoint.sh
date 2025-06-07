#!/bin/sh
# This line is the shebang, specifying that the script should be executed with sh (Bourne shell).

# Apply database migrations.
# This command ensures that the database schema is up to date with the latest
# migration scripts before starting the application.
flask db upgrade

# Start the Gunicorn web server to serve the Flask application.
# 'exec' replaces the current shell process with the Gunicorn process,
# which is good practice for a container's main process.
# '--bind 0.0.0.0:80' tells Gunicorn to listen on all network interfaces
# within the container on port 80.
# '"app:create_app()"' specifies the WSGI application callable:
# 'app' refers to app.py (or the app module).
# 'create_app()' is the application factory function within that module.
exec gunicorn --bind 0.0.0.0:80 "app:create_app()"