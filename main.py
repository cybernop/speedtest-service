import json
import subprocess
import time
from datetime import datetime

from prometheus_client import Gauge, start_http_server

g_down = Gauge('speedtest_down', 'Download Speed')
g_up = Gauge('speedtest_up', 'Upload Speed')


def measure_speed():
    # cmd = ['speedtest-cli', '--json', '--single']
    cmd = ['speedtest-cli', '--json']

    process_result = subprocess.run(cmd, capture_output=True)
    output = json.loads(process_result.stdout)

    download = output['download'] / (1000**2)
    upload = output['upload'] / (1000**2)

    g_down.set_to_current_time()
    g_down.set(download)

    g_up.set_to_current_time()
    g_up.set(upload)


def repeat(func, delay_secs: int = 0):
    while True:
        try:
            start = datetime.now()
            func()

            end = datetime.now()
            wait_time = delay_secs - (end-start).total_seconds()

            if (wait_time > 0):
                time.sleep(wait_time)
        except KeyboardInterrupt:
            exit()


if __name__ == "__main__":
    start_http_server(8000, addr="0.0.0.0")
    repeat(measure_speed, delay_secs=60)
