# Use an ARM-compatible base image
FROM arm32v7/python:3.9-slim

# Set the working directory
WORKDIR /usr/src/app

# Copy the Python script to the container
COPY fan_control.py .

# Install RPi.GPIO
RUN pip install RPi.GPIO

# Run the Python script
CMD ["python", "./fan_control.py"]
