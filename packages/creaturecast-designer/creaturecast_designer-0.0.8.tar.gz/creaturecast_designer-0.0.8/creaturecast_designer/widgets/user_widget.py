
from os.path import expanduser
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

import creaturecast_designer.widgets.progress_indicator as prg
import creaturecast_designer.widgets.avatar_label as avl
import creaturecast_designer.services.download_image as dim
import creaturecast_designer.services.thread_worker as wkr

home_directory = expanduser("~").replace('\\', '/')
creaturecast_directory = '%s/creaturecast' % home_directory

class UserWidget(QFrame):

    log_out = Signal()
    def __init__(self, *args, **kwargs):
        super(UserWidget, self).__init__(*args, **kwargs)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.vertical_layout = QVBoxLayout(self)
        self.horizontal_layout = QHBoxLayout()
        self.label_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()

        self.avatar_label = avl.AvatarLabel(self)
        self.avatar_label.set_image_size(QSize(128, 128))

        self.user_label = QLabel(self)
        self.log_out_button = QPushButton('Log Out', self)
        self.avatar_label.setAlignment(Qt.AlignCenter)
        self.user_label.setAlignment(Qt.AlignCenter)

        self.font = QFont('', 18, True)
        self.button_font = QFont('', 12, False)

        self.user_label.setFont(self.font)
        self.log_out_button.setFont(self.button_font)

        self.busy_widget = prg.QProgressIndicator(self)
        self.busy_widget.setAnimationDelay(70)
        self.busy_widget.setVisible(True)
        self.busy_widget.startAnimation()
        self.horizontal_layout.addLayout(self.vertical_layout)

        self.vertical_layout.addLayout(self.label_layout)
        self.vertical_layout.addStretch()

        self.label_layout.addStretch()
        self.label_layout.addWidget(self.avatar_label)
        self.label_layout.addWidget(self.user_label)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.log_out_button)
        self.button_layout.addStretch()
        self.label_layout.addSpacerItem(QSpacerItem(20, 20))
        self.label_layout.addLayout(self.button_layout)

        self.label_layout.addStretch()

        self.log_out_button.pressed.connect(self.log_out)

    def set_user(self, data):
        if data['given_name'] and data['family_name']:
            self.user_label.setText('%s %s' % (data['given_name'], data['family_name']))
        else:
            self.user_label.setText(data['email'])

        avatar_path = data['avatar']
        exrension = avatar_path.split('.')[-1]
        self.worker = wkr.FunctionWorker(
            dim.download_image,
            data['avatar'],
            '%s.%s' % (data['token'], exrension),
            always_download=True
        )
        self.thread = QThread()
        self.thread.start()
        self.worker.moveToThread(self.thread)
        self.worker.start.connect(self.worker.run)
        self.worker.data.connect(self.avatar_label.set_image)
        self.worker.start.emit()
