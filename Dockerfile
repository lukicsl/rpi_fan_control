FROM balenalib/raspberry-pi-python:3.7-buster-run

WORKDIR /usr/src/app

COPY fan_control.py .

RUN apt-get update && \
    apt-get install -y gcc libraspberrypi-bin && \
    pip install RPi.GPIO && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# These are the default values
ENV MIN_TEMP=60
ENV MAX_TEMP=80
ENV MIN_FAN=10
ENV MAX_FAN=100
ENV GP_IO=14

# Run the script when the container launches
CMD ["python", "./fan_control.py"]
