import json
import time
import shutil
import requests
import os, zipfile, StringIO
from os.path import expanduser
import creaturecast_designer.services as svc
home_directory = expanduser("~").replace('\\', '/')
local_user = os.getenv('USER')
creaturecast_directory = '%screaturecast' % home_directory

def get_extension(name):
    get_extension_url = '%s/get_extension' % svc.library_url

    response = requests.post(
        get_extension_url,
        data=json.dumps(dict(name=name)),
        headers={'Content-Type': 'application/json'}
    )

    if response.status_code == 200:

        path = '%s/extensions/%s.zip' % (creaturecast_directory, name)
        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        with open(path, "wb") as f:
            f.write(response.content)
        print path
        print '%s/extensions' % creaturecast_directory
        zip_ref = zipfile.ZipFile(path, 'r')
        zip_ref.extractall('%s/extensions' % creaturecast_directory)
        zip_ref.close()
        return name

    else:
        print 'Failed with status code %s' % response.status_code



if __name__ == '__main__':
    print get_extension('creaturecast_scenegraph')