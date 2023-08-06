import urllib
import os
from os.path import expanduser

home_directory = expanduser("~").replace('\\', '/')
creaturecast_directory = '%s/creaturecast' % home_directory


def download_image(url, file_name, always_download=True):

    path = '%s/images/%s' % (creaturecast_directory, file_name)
    if os.path.exists(path) and not always_download:
        return path
    image_opener = urllib.URLopener()
    image_opener.retrieve(url, path)

    return path