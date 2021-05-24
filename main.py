import json
import logging
import pathlib
import subprocess
import time
from datetime import datetime

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)

logger = logging.getLogger('speedtest')


def measure_speed(single: bool = False):
    cmd = ['speedtest-cli', '--json']

    if single:
        cmd.append('--single')

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
    multi_result = measure_speed()
    single_result = measure_speed(single=True)

    if (file.exists()):
        file_contents = json.loads(file.read_text())
    else:
        file_contents = {'multi': [], 'single': []}

    file_contents['multi'].append(multi_result)
    file_contents['single'].append(single_result)

    file.write_text(json.dumps(file_contents, default=str))

    logger.info('Multi\tDownload: %.2f Mbps,\tUpload: %.2f Mbps,\tPing: %.1f',
                multi_result['download'], multi_result['upload'], multi_result['ping'])

    logger.info('Single\tDownload: %.2f Mbps,\tUpload: %.2f Mbps,\tPing: %.1f',
                single_result['download'], single_result['upload'], single_result['ping'])


def reoccurend_measure(file: pathlib.Path, delay_secs: int = 0, repeat: int = -1):
    while True:
        try:
            start = datetime.now()
            protocol_measure(file)

            repeat -= 1
            if repeat == 0:
                break

            end = datetime.now()
            wait_time = delay_secs - (end-start).total_seconds()

            if (wait_time > 0):
                time.sleep(wait_time)
        except KeyboardInterrupt:
            logger.info('stopped')
            exit()


if __name__ == "__main__":
    import os

    logger.setLevel(logging.INFO)

    base_path = os.environ.get('SPEEDTEST_OUTPUT_PATH')
    delay = os.environ.get('SPEEDTEST_DELAY')
    repeat = os.environ.get('SPEEDTEST_REPEAT')

    if not base_path:
        base_path = '.'

    if delay:
        delay = int(delay)
    else:
        delay = 60

    if repeat:
        repeat = int(repeat)
    else:
        repeat = -1

    file = pathlib.Path('result.json')
    reoccurend_measure(file, delay_secs=delay, repeat=repeat)
