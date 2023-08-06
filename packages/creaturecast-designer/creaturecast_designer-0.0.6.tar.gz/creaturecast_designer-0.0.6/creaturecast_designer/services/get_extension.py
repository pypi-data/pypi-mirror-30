import json
import time
import shutil
import requests
import os
from os.path import expanduser

home_directory = expanduser("~").replace('\\', '/')
local_user = os.getenv('USER')
creaturecast_directory = '%s/creaturecast' % home_directory

url = 'https://creaturecast-library.herokuapp.com'
#url = 'http://127.0.0.1:5000'



def get_extension(name):
    get_extension_url = '%s/get_extension' % url
    start = time.time()
    response = requests.post(
        get_extension_url,
        data=json.dumps(dict(name=name)),
        headers={'Content-Type': 'application/json'},
        allow_redirects=False
    )

    if response.status_code == 200:
        path = '%s%s.zip' % (creaturecast_directory, name)
        print path
        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(path, 'wb') as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)
    else:
        print response.text
        print 'Failed with status code %s' % response.status_code

    end = time.time()
    print(end - start)


if __name__ == '__main__':
    print get_extension('creaturecast_scenegraph')