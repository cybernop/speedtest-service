import json
import subprocess
from datetime import datetime, time


def measure_speed():
    cmd = ['speedtest-cli', '--json']
    process_result = subprocess.run(cmd, capture_output=True)
    output = json.loads(process_result.stdout)
    timestamp = datetime.strptime(output['timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ')
    return {
        'download': output['download'],
        'upload': output['upload'],
        'ping': output['ping'],
        'date': timestamp.date(),
        'time': timestamp.time(),
    }


if __name__ == "__main__":
    measure_speed()
