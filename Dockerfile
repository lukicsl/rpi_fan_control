# Stage 1: Building unavailable dependencies
FROM debian:buster AS builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libraspberrypi-bin && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* 

# Stage 2: Creating a runtime image
FROM python:3.7-slim-buster

WORKDIR /usr/src/app

COPY --from=builder /path-to-some-binary-or-lib /path-to-destination

# Update and install required packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    pip install RPi.GPIO && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY fan_control.py .

ENV MIN_TEMP=60
ENV MAX_TEMP=80
ENV MIN_FAN=10
ENV MAX_FAN=100
ENV GP_IO=14

CMD ["python", "./fan_control.py", \
     "--min_temp", "$MIN_TEMP", "--max_temp", "$MAX_TEMP", \
     "--min_fan", "$MIN_FAN", "--max_fan", "$MAX_FAN", "--gp_io", "$GP_IO"]
