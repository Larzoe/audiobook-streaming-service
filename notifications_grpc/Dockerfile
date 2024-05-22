# Use a base image with the desired version of Python
FROM python:3.8

# Set the working directory inside the container
WORKDIR /app

# Copy the necessary files to the working directory
COPY . /app
RUN apt-get update && apt-get install -y protobuf-compiler
# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Generate the Python code from the Protobuf files
RUN protoc -I=./ --python_out=./proto ./notification.proto

# Set the environment variable for the Protobuf Python module
ENV PYTHONPATH "${PYTHONPATH}:/app/proto"

# Start the notification service
CMD ["python", "app.py"]
