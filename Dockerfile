# Use an official Python runtime as a parent image.
# python:3.13-alpine uses a specific version of Python on a lightweight Alpine Linux base.
FROM python:3.13-alpine

# Inform Docker that the container listens on port 5000 at runtime.
# Note: This does not actually publish the port. Publishing is done with `docker run -p`.
EXPOSE 5000

# Set the working directory for subsequent instructions in the container.
# If the directory doesn't exist, it will be created.
WORKDIR /app

# Copy the requirements.txt file from the host to the /app directory in the container.
COPY ./requirements.txt requirements.txt

# Install Python dependencies specified in requirements.txt.
# --no-cache-dir: Disables the pip cache to reduce image layer size.
# --upgrade: Ensures packages and their dependencies are upgraded to the latest allowed versions.
# -r requirements.txt: Specifies the file containing the list of packages to install.
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the application's source code from the host's current directory
# into the /app directory in the container.
COPY . .

# Specify the command to run when the container starts.
# This executes the docker-entrypoint.sh script using /bin/bash.
# The entrypoint script typically handles tasks like database migrations
# before starting the main application process.
CMD ["/bin/bash", "docker-entrypoint.sh"]