import subprocess
import time
import csv
import argparse
import datetime


def get_cpu_temperatures() -> dict:
    """Extract the CPU temperatures from the output of "sensors" (lm_sensors)."""
    # Run the 'sensors' command and capture its output
    sensors_output = subprocess.check_output(["sensors"]).decode()
    core_temps = {}
    for line in sensors_output.split("\n"):
        if "Core" in line:
            # Extract core name and temperature
            parts = line.split()
            core_name = parts[0].lower() + " " + parts[1]
            temperature = parts[2]
            # Remove the '+' and '°C' characters
            temperature = temperature.replace("+", "").replace("°C", "")
            core_temps[core_name] = float(temperature)
    return core_temps


def record_temperatures_to_csv(filename: str, interval: int, duration: int) -> None:
    """Record the CPU temperatures to csv."""
    end_time = time.time() + duration
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['timestamp']
        core_names = list(get_cpu_temperatures().keys())
        fieldnames.extend(core_names)
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        while time.time() < end_time:
            timestamp = datetime.datetime.now().isoformat()
            core_temps = get_cpu_temperatures()
            row = {'timestamp': timestamp}
            row.update(core_temps)
            writer.writerow(row)
            time.sleep(interval)


def define_cli_args() -> dict:
    """Define the set of CLI args to use in the script."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interval", type=int, default=1, help="Interval in seconds")
    parser.add_argument("-d", "--duration", type=int, default=60, help="Duration in seconds")
    parser.add_argument("-o", "--output", type=str, help="Output file for the collected temps.")
    return vars(parser.parse_args())


if __name__ == "__main__":
    args = define_cli_args()
    record_temperatures_to_csv(
        interval=args['interval'],
        duration=args['duration'],
        filename=args['output'],
    )
