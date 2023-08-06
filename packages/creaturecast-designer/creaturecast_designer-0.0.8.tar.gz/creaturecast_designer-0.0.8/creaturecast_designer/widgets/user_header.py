import os
import platform
from os.path import expanduser
from qtpy.QtCore import *
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import creaturecast_designer.services.download_image as dim
import creaturecast_designer.services.thread_worker as wkr
import creaturecast_designer.widgets.progress_indicator as prg
import creaturecast_designer.widgets.avatar_label as alb

home_directory = expanduser("~").replace('\\', '/')
creaturecast_directory = '%s/creaturecast' % home_directory

class UserHeader(QWidget):

    clicked = Signal()


    def __init__(self, *args, **kwargs):
        super(UserHeader, self).__init__(*args, **kwargs)
        self.layout = QHBoxLayout(self)
        self.avatar_label = alb.AvatarLabel(self)
        self.avatar_label.set_image_size(QSize(32, 32))
        self.user_label = QLabel('Log Out', parent=self)

        self.font = QFont('', 9, False)
        self.user_label.setFont(self.font)
        #self.user_label.setStyleSheet("QLabel{background:transparent}")

        self.layout.addWidget(self.avatar_label)
        self.layout.addWidget(self.user_label)
        self.layout.addStretch()

        self.busy_widget = prg.QProgressIndicator(self)
        self.busy_widget.setAnimationDelay(70)
        self.busy_widget.setVisible(True)
        self.busy_widget.startAnimation()
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.busy_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.user_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.avatar_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    def set_user(self, data):
        if data['given_name'] and data['family_name']:
            self.user_label.setText('%s %s' % (data['given_name'], data['family_name']))
        else:
            self.user_label.setText(data['email'])
        self.thread = QThread()
        self.thread.start()
        avatar_path = data['avatar']
        exrension = avatar_path.split('.')[-1]
        self.worker = wkr.FunctionWorker(
            dim.download_image,
            data['avatar'],
            '%s.%s' % (data['temporary_pin'], exrension),
            always_download=True
        )
        self.worker.moveToThread(self.thread)
        self.worker.start.connect(self.worker.run)
        self.worker.data.connect(self.avatar_label.set_image)
        self.worker.start.emit()

    def mousePressEvent(self, *args, **kwargs):
        self.clicked.emit()

def get_temp_path():
    if platform.system() in ['Darwin','Linux']:
        return os.getenv('TMPDIR').replace('\\', '/')
    else:
        return os.getenv('TEMP').replace('\\', '/')
