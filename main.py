import threading
import os
from pathlib import Path
import requests
import json
import base64
import logging
from logger import init_logger, print_and_log
import pytz


def send_data():
    if Path(PATH_FOLDER).is_dir():
        files = list(Path(PATH_FOLDER).iterdir())
        for file in files:
            try:
                if file.suffix not in ('.png', '.jpg'):
                    continue
                id_ = file.name.split('_')[0][2:]
                with open(file, 'rb') as f:
                    encoded_string = (base64.b64encode(f.read())).decode()
                json_pattern = {
                    'recognition_id': int(id_),
                    'picture': encoded_string,
                }
                headers = {'Content-Type': 'application/json; charset=utf-8', 'Authorization': API_TOKEN}
                json_string = json.dumps(json_pattern, ensure_ascii=False)
                response = requests.post(URL, data=json_string.encode('utf8'), timeout=int(os.environ['SERVER_REQUEST_TIMEOUT']), headers=headers)
                if response.status_code == 200:
                    print_and_log(logging.INFO, f'Send file with id {id_}')
                    file.unlink()
                else:
                    print_and_log(logging.ERROR, f'Error with file id {id_}')
                    print_and_log(logging.ERROR, response.text)
            except requests.exceptions.ReadTimeout:
                print_and_log(logging.ERROR, 'Timeout sending picture to api!')
            except Exception as e:
                print_and_log(logging.ERROR, 'Error while sending picture to api!')
                print_and_log(logging.ERROR, repr(e))
    threading.Timer(INTERVAL_MINUTE, send_data).start()


TZ = pytz.timezone(os.environ["TIMEZONE"])
init_logger('logs', 'sending_full_picture', TZ, True)
INTERVAL_MINUTE = float(os.environ['SEND_INTERVAL_MINUTE'])
PATH_FOLDER = os.environ['PATH_FOLDER']
URL = os.environ['API_URL']
API_TOKEN = os.environ['API_TOKEN']
send_data()
