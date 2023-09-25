import argparse
import RPi.GPIO as GPIO
import time

# Argument parsing
parser = argparse.ArgumentParser(description='Control a PWM fan based on CPU temperature.')
parser.add_argument('--metrics', type=str, default='/usr/src/app/fan_speed.prom', help='Metrics file for node_exporter')
parser.add_argument('--min_temp', type=float, default=60, help='Temperature where the minimum fan speed is applied (default: 60°C)')
parser.add_argument('--max_temp', type=float, default=80, help='Temperature where the maximum fan speed is applied (default: 80°C)')
parser.add_argument('--min_fan', type=int, default=10, help='Minimum fan speed (default: 10%)')
parser.add_argument('--max_fan', type=int, default=100, help='Maximum fan speed (default: 100%)')
parser.add_argument('--gp_io', type=int, default=14, help='GPIO port (default: 14)')

args = parser.parse_args()

# Define the file path where the metric will be stored
METRICS_FILE = args.metrics

# Setup
fan_pin = args.gp_io
GPIO.setmode(GPIO.BCM)
GPIO.setup(fan_pin, GPIO.OUT)
pwm = GPIO.PWM(fan_pin, 25)
pwm.start(0)

def write_fan_speed_to_file(duty_cycle):
    with open(METRICS_FILE, "w") as f:
        f.write("# HELP fan_speed Fan Speed as a duty cycle percentage\n")
        f.write("# TYPE fan_speed gauge\n")
        f.write(f"fan_speed {duty_cycle}\n")

def get_cpu_temperature():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp = f.read().strip()
    cpu_temp = int(temp) / 1000
    return cpu_temp

try:
    while True:
        temp = get_cpu_temperature()
        if temp < args.min_temp:
            duty_cycle = 0
        elif temp > args.max_temp:
            duty_cycle = args.max_fan
        else:
            scale = (temp - args.min_temp) / (args.max_temp - args.min_temp)
            duty_cycle = args.min_fan + (scale * (args.max_fan - args.min_fan))
        
        pwm.ChangeDutyCycle(duty_cycle)
        print(f"CPU Temperature: {temp}°C, Fan Speed: {duty_cycle}%")

        # Write the fan speed to file in Prometheus format
        write_fan_speed_to_file(duty_cycle)

        time.sleep(5)

except KeyboardInterrupt:
    pass

pwm.stop()
GPIO.cleanup()
