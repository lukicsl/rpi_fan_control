# Use an ARM-compatible base image
FROM arm32v7/python:3.9-slim

# Set the working directory
WORKDIR /usr/src/app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libffi-dev libssl-dev make libc-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the Python script to the container
COPY fan_control.py .

# Install RPi.GPIO
RUN pip install RPi.GPIO

ENV METRICS=/usr/src/app/collector/fan_speed.prom
ENV MIN_TEMP=60
ENV MAX_TEMP=80
ENV MIN_FAN=10
ENV MAX_FAN=100
ENV GP_IO=14

CMD ["sh", "-c", "python -u ./fan_control.py --metrics $METRICS --min_temp $MIN_TEMP --max_temp $MAX_TEMP --min_fan $MIN_FAN --max_fan $MAX_FAN --gp_io $GP_IO"]
