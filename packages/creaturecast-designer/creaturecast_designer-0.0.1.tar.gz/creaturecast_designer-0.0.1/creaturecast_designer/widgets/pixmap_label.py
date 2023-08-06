import os
import requests
import json
import shutil
from qtpy.QtCore import *
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import creaturecast_designer.widgets.progress_indicator as prg
import creaturecast_designer.services.get_image as gim
import creaturecast_designer.services.thread_worker as twr
pixmaps = dict()


class PixmapLabel(QLabel):

    def __init__(self, local_path, always_download=False, *args, **kwargs):

        super(PixmapLabel, self).__init__(*args, **kwargs)

        self.busy_widget = prg.QProgressIndicator(self)
        self.busy_widget.setAnimationDelay(70)
        self.busy_widget.setVisible(False)
        self.busy_widget.setVisible(True)
        self.busy_widget.startAnimation()
        self.worker = twr.FunctionWorker(
            gim.get_image,
            local_path,
            always_download=always_download
        )
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
