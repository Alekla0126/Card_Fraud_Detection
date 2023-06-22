# Use an official Python runtime as a parent image.
FROM python:3.8-slim-buster

# Set the working directory in the container to /app.
WORKDIR /app

# Install protobuf dependencies.
RUN apt-get update && apt-get install -y \
    protobuf-compiler \
    libprotobuf-dev \
    && rm -rf /var/lib/apt/lists/*

# Install TensorFlow and other dependencies.
RUN pip install --no-cache-dir tensorflow

# Add the current directory contents into the container at /app.
ADD . /app

# Install any other needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container.
EXPOSE 5000

# Run wsgi.py when the container launches.
ENTRYPOINT ["python", "wsgi.py"]