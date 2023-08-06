
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *


import creaturecast_designer.media as med
import creaturecast_designer.widgets.progress_indicator as prg



class LoadingPage(QWidget):

    create_rig_component = Signal(dict)

    def __init__(self, *args, **kwargs):
        super(LoadingPage, self).__init__(*args, **kwargs)


        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.horizontal_layout = QHBoxLayout(self)
        self.vertical_layout = QVBoxLayout()
        self.horizontal_layout.setAlignment(Qt.AlignCenter)
        self.icon_label = QLabel('', self)
        default_image = QImage(med.get_icon_path('clock'))
        default_pixmap = QPixmap.fromImage(default_image.scaled(45, 45, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        self.icon_label.setPixmap(default_pixmap)
        self.icon_label.setAlignment(Qt.AlignCenter);
        self.message_label = QLabel('   loading...', self)
        self.message_label.setAlignment(Qt.AlignCenter);
        self.message_font = QFont("arial", 22, True)
        self.message_font.setWeight(15)
        self.message_font.setBold(False)
        self.message_font.setLetterSpacing(QFont.PercentageSpacing, 100)
        self.message_label.setFont(self.message_font)
        self.horizontal_layout.addLayout(self.vertical_layout)
        self.vertical_layout.addItem(
            QSpacerItem(55, 55)
        )

        self.busy_widget = prg.QProgressIndicator(self)
        self.busy_widget.setAnimationDelay(70)
        self.busy_widget.setVisible(False)

        self.vertical_layout.addWidget(self.icon_label)
        self.vertical_layout.addWidget(self.message_label)
        self.vertical_layout.addStretch()

    def resizeEvent(self, event):
        self.busy_widget.resize(event.size())
        event.accept()
