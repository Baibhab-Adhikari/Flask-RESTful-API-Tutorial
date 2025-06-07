# Use an official Python runtime as a parent image
FROM python:3.13-alpine

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY ./requirements.txt requirements.txt

# Install any needed packages specified in requirements.txt
# --no-cache-dir: Disables the cache to reduce image size
# --upgrade: Upgrades packages to the newest versions
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Run the application using Gunicorn
# --bind 0.0.0.0:80: Binds Gunicorn to all network interfaces on port 80 inside the container
# app:create_app(): Specifies the WSGI application object (the create_app factory in app.py)
CMD ["gunicorn","--bind","0.0.0.0:80", "app:create_app()"]