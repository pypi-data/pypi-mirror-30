import requests
import os
from tqdm import tqdm

URL = "https://docs.google.com/uc?export=download"
CHUNK_SIZE = 32768


def download(path, file, file_id, total=0):

    if not os.path.exists(path):
        os.makedirs(path)

    destination = os.path.join(path, file)
    if os.path.exists(destination):
        return

    session = requests.Session()

    response = session.get(URL, params={'id': file_id}, stream=True)
    token = _get_confirm_token(response)

    if token:
        params = {'id': file_id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    _save_response_content(response, destination, total)


def _get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None


def _save_response_content(response, destination, total):
    total_size = int(response.headers.get('content-length', total))
    with tqdm(total=total_size / 1000**2, unit='MB', unit_scale=True, unit_divisor=1024) as bar:
        with open(destination, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                bar.update(CHUNK_SIZE / 1000**2)
                # filter out keep-alive new chunks
                if chunk:
                    f.write(chunk)