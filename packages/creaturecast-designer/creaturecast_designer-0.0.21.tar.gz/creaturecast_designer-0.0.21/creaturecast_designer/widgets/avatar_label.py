from qtpy.QtCore import *
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

import creaturecast_designer.media as med
from os.path import expanduser
home_directory = expanduser("~").replace('\\', '/')
creaturecast_directory = '%s/creaturecast' % home_directory


class AvatarLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super(AvatarLabel, self).__init__(*args, **kwargs)
        self.image_size = QSize(32, 32)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    def set_image_size(self, size):
        self.image_size = size
        self.set_image(med.get_icon_path('generic_user'))

    def sizeHint(self, *args, **kwargs):
        return self.image_size

    def set_image(self, path):
        height = self.image_size.height()
        width = self.image_size.width()

        user_image = QImage(path)

        alpha_image = QImage(med.get_icon_path('circle_alpha'))

        alpha_image = alpha_image.scaled(
            height,
            width,
            Qt.IgnoreAspectRatio,
            Qt.SmoothTransformation
        )

        user_image = user_image.scaled(
            height,
            width,
            Qt.IgnoreAspectRatio,
            Qt.SmoothTransformation
        )

        user_image.setAlphaChannel(alpha_image)
        user_pixmap = QPixmap.fromImage(user_image)

        self.setPixmap(user_pixmap)
