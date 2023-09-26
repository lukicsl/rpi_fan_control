import argparse
import RPi.GPIO as GPIO
import time
# Import required libraries
import collections

# Argument parsing
parser = argparse.ArgumentParser(description='Control a PWM fan based on CPU temperature.')
parser.add_argument('--metrics', type=str, default='/usr/src/app/fan_speed.prom', help='Metrics file for node_exporter')
parser.add_argument('--min_temp', type=float, default=60, help='Temperature where the minimum fan speed is applied (default: 60°C)')
parser.add_argument('--max_temp', type=float, default=80, help='Temperature where the maximum fan speed is applied (default: 80°C)')
parser.add_argument('--min_fan', type=int, default=10, help='Minimum fan speed (default: 10%)')
parser.add_argument('--max_fan', type=int, default=100, help='Maximum fan speed (default: 100%)')
parser.add_argument('--gp_io', type=int, default=14, help='GPIO port (default: 14)')
parser.add_argument('--window_size', type=int, default=5, help='Window size for smoothing temperature readings (default: 5)')
parser.add_argument('--step', type=float, default=1, help='Step size for adjusting the fan speed (default: 1%)')

args = parser.parse_args()

# Define the file path where the metric will be stored
METRICS_FILE = args.metrics

# Initialize variables
window = collections.deque(maxlen=args.window_size)  # For smoothing temperature readings
current_duty_cycle = 0  # Start with fan off

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
        window.append(temp)  # Add current reading to the window
        
        # Compute the average temperature over the window
        avg_temp = sum(window) / len(window)
        
        # Compute the error (Proportional part)
        if avg_temp < args.min_temp:
            error = 0
        elif avg_temp > args.max_temp:
            error = args.max_fan
        else:
            scale = (avg_temp - args.min_temp) / (args.max_temp - args.min_temp)
            error = args.min_fan + (scale * (args.max_fan - args.min_fan))
        
        # Gradually adjust fan speed in smaller steps
        if current_duty_cycle < error:
            current_duty_cycle = min(current_duty_cycle + args.step, error)
        elif current_duty_cycle > error:
            current_duty_cycle = max(current_duty_cycle - args.step, error)
        
        pwm.ChangeDutyCycle(current_duty_cycle)
        print(f"Average CPU Temperature: {avg_temp}°C, Fan Speed: {current_duty_cycle}%")
        
        # Write the fan speed to file in Prometheus format
        write_fan_speed_to_file(current_duty_cycle)

        time.sleep(1)  # Sleep for shorter periods, so we can adjust in smaller steps

except KeyboardInterrupt:
    pass

pwm.stop()
GPIO.cleanup()
