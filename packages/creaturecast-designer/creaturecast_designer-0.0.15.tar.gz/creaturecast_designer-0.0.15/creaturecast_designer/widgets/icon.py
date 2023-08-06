import os
import requests
import json
import shutil
import time
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from os.path import expanduser
import creaturecast_designer.media as media

package_name = __file__.replace('\\', '/').split('/')[-2]
home_directory = expanduser("~").replace('\\', '/')
local_user = os.getenv('USER')
creaturecast_directory = '%s/creaturecast' % home_directory

icon_cache = dict()
empty_icon_path = media.get_icon_path('empty')


pixmaps = dict()











def get_icon(key):
    if key in icon_cache:
        return icon_cache[key]
    else:
        icon_path = media.get_icon_path(key)
        if not os.path.exists(icon_path):
            icon_path = media.get_icon_path('empty')
        new_icon = QIcon(icon_path)
        icon_cache['key'] = new_icon
        return new_icon


