# Use an official Python runtime as a parent image.
FROM python:3.8-bookworm

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

# Install MySQL server
RUN apt-get update && apt-get install -y mysql-server

# Configure MySQL with the specified password for the 'alejandro' user
RUN service mysql start && mysql -e "CREATE DATABASE card_fraud_detection;"
RUN service mysql start && mysql -e "CREATE USER 'alejandro'@'localhost' IDENTIFIED BY 't!''o\"oGr'%)5GY<l2fX,g:23';"
RUN service mysql start && mysql -e "GRANT ALL PRIVILEGES ON card_fraud_detection.* TO 'alejandro'@'localhost';"
RUN service mysql start && mysql -e "FLUSH PRIVILEGES;"

# Make port 5000 available to the world outside this container.
EXPOSE 5000

# Run wsgi.py when the container launches.
ENTRYPOINT ["python", "run.py"]