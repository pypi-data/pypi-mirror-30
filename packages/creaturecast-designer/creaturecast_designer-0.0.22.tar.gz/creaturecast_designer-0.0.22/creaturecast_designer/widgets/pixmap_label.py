import os
import requests
import json
import shutil
from qtpy.QtCore import *
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from os.path import expanduser
import creaturecast_designer.media as media
from creaturecast_designer.widgets.progress_widget import ProgressWidget

home_directory = expanduser("~").replace('\\', '/')
creaturecast_directory = '%s/creaturecast' % home_directory
empty_tool_path = media.get_image_path('empty_tool')
import creaturecast_designer.services as svc
import creaturecast_designer.services.get_image as gmg
import creaturecast_designer.services.thread_worker as twk

pixmaps = dict()


class PixmapLabel(QLabel):

    def __init__(self, local_path, always_download=True, *args, **kwargs):
        super(PixmapLabel, self).__init__(*args, **kwargs)

        self.busy_widget = ProgressWidget(self)
        self.busy_widget.setAnimationDelay(70)
        self.busy_widget.setVisible(False)
        image_path = '%s%s' % (creaturecast_directory, local_path)

        if os.path.exists(image_path):
            self.setPixmap(QPixmap(image_path))
        else:
            self.setPixmap(QPixmap(empty_tool_path))
            self.busy_widget.setVisible(True)
            self.busy_widget.startAnimation()

            self.worker = twk.FunctionWorker(gmg.get_image, local_path)
            self.thread = QThread()
            self.thread.start()
            self.worker.moveToThread(self.thread)
            self.worker.start.connect(self.worker.run)
            self.worker.data.connect(self.load_pixmap)
            self.worker.start.emit()

    def load_pixmap(self, path):
        self.setPixmap(QPixmap(path))
        self.busy_widget.setVisible(False)

    def resizeEvent(self, event):
        self.busy_widget.resize(event.size())
        event.accept()
