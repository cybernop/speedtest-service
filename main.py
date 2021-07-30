import json
import logging
import subprocess
import time

from prometheus_client import Gauge, start_http_server
from speedtest import Speedtest

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)

logger = logging.getLogger('speedtest')

g_down = Gauge('speedtest_down', 'Download Speed')
g_up = Gauge('speedtest_up', 'Upload Speed')


def measure_speed():
    servers = []
    threads = None

    s = Speedtest()

    s.get_servers(servers)
    s.get_best_server()

    s.download(threads=threads)
    s.upload(threads=threads)

    results = s.results.dict()

    download = results.get('download', 0) / (1000**2)
    upload = results.get('upload', 0) / (1000**2)

    if download != 0:
        logger.info(f'measured download speed: {download:.1f} Mbps')
        g_down.set_to_current_time()
        g_down.set(download)
    else:
        logger.warning('measured download speed is zero!')

    if upload != 0:
        logger.info(f'measured upload speed: {upload:.1f} Mbps')
        g_up.set_to_current_time()
        g_up.set(upload)
    else:
        logger.warning('measured upload speed is zero!')


def repeat(func, delay_secs: int = 0):
    while True:
        try:
            func()
            time.sleep(delay_secs)
        except KeyboardInterrupt:
            exit()


if __name__ == "__main__":
    start_http_server(8000, addr="0.0.0.0")
    repeat(measure_speed, delay_secs=300)
