import json
import logging
import pathlib
import subprocess
from datetime import datetime, time

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)

logger = logging.getLogger('speedtest')


def measure_speed():
    cmd = ['speedtest-cli', '--json']
    process_result = subprocess.run(cmd, capture_output=True)
    output = json.loads(process_result.stdout)
    timestamp = datetime.strptime(output['timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ')
    return {
        'download': output['download'] / (1000**2),
        'upload': output['upload'] / (1000**2),
        'ping': output['ping'],
        'date': timestamp.date(),
        'time': timestamp.time(),
    }


def protocol_measure(file: pathlib.Path):
    result = measure_speed()

    if (file.exists()):
        file_contents = json.loads(file.read_text())
    else:
        file_contents = []

    file_contents.append(result)
    file.write_text(json.dumps(file_contents, default=str))

    logger.info('Download: %.2f Mbps, Upload: %.2f Mbps, Ping: %.1f',
                result['download'], result['upload'], result['ping'])


if __name__ == "__main__":
    logger.setLevel(logging.INFO)

    file = pathlib.Path('result.json')
    protocol_measure(file)
