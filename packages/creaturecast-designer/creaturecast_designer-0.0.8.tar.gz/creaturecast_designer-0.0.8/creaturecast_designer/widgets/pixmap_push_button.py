import os
import requests
import json
import shutil
from qtpy.QtCore import *
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from os.path import expanduser
import extensions_widget.media as media
from extensions_widget.widgets.QProgressIndicator import QProgressIndicator

home_directory = expanduser("~").replace('\\', '/')
creaturecast_directory = '%s/creaturecast' % home_directory
empty_tool_path = media.get_image_path('empty_tool')
library_url = 'https://creaturecast-library.herokuapp.com'

pixmaps = dict()


class PixmapPushButton(QLabel):

    def __init__(self, local_path, *args, **kwargs):
        super(PixmapPushButton, self).__init__(*args, **kwargs)

        self.busy_widget = QProgressIndicator(self)
        self.busy_widget.setAnimationDelay(70)
        self.busy_widget.setVisible(False)
        image_path = '%s%s' % (creaturecast_directory, local_path)

        if os.path.exists(image_path):
            self.setIcon(QIcon(image_path))
        else:
            self.setIcon(QIcon(empty_tool_path))
            self.busy_widget.setVisible(True)
            self.busy_widget.startAnimation()
            self.worker = ImageDownloadWorker(local_path)
            self.thread = QThread()
            self.thread.start()
            self.worker.moveToThread(self.thread)
            self.worker.start.connect(self.worker.run)
            self.worker.finished.connect(self.load_pixmap)
            self.worker.start.emit()

    def load_pixmap(self, path):
        self.setIcon(QIcon(path))
        self.busy_widget.setVisible(False)

    def resizeEvent(self, event):
        self.busy_widget.resize(event.size())
        event.accept()



class ImageDownloadWorker(QObject):

    start = Signal()
    finished = Signal(str)
    failed = Signal()
    success = Signal()


    def __init__(self, local_path):
        super(ImageDownloadWorker, self).__init__()
        self.local_path = local_path
        self.url = '%s/get_image' % library_url
        self.chunk_size = 580

    @Slot()
    def run(self):

        data = dict(local_path=self.local_path)

        response = requests.post(
            self.url,
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'},
            allow_redirects=False,
            stream=True
        )

        path = '%s%s' % (creaturecast_directory, self.local_path)

        if response.status_code == 200:
            dirname = os.path.dirname(path)
            try:
                os.makedirs(dirname)
            except:
                pass
            with open(path, 'wb') as f:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, f)

            self.finished.emit(path)
            self.success.emit()
        else:
            self.failed.emit()
