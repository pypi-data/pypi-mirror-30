import os
import requests
import json
import shutil
from os.path import expanduser
import creaturecast_designer.services as svc

home_directory = expanduser("~").replace('\\', '/')
creaturecast_directory = '%screaturecast' % home_directory


def get_image(local_path, always_download=False):

    url = '%s/get_image' % svc.library_url

    data = dict(local_path=local_path)
    path = '%s%s' % (creaturecast_directory, local_path)
    if os.path.exists(path) and not always_download:
        return path
    else:
        response = requests.post(
            url,
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'},
            stream=True
        )
        if response.status_code == 200:
            dirname = os.path.dirname(path)
            try:
                os.makedirs(dirname)
            except:
                pass
            with open(path, 'wb') as f:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, f)
                return path


if __name__ == '__main__':
    get_image('/python.png')