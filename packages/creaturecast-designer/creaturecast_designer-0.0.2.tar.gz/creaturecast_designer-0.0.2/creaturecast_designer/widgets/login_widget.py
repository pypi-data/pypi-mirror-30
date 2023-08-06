import os
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
from qtpy.QtWebEngineWidgets import *

import string
import random
import creaturecast_designer.services as svc
import creaturecast_designer.services.thread_worker as wrk
import creaturecast_designer.services.get_user_data as gud
import creaturecast_designer.widgets.pixmap_label as pxl
import creaturecast_designer.widgets.progress_indicator as prg

#include <QtGui>
#include <QtWebKit>


def random_string_generator(size=48, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

class LoginWidget(QFrame):

    logged_in = Signal(object)
    facebook_pin = random_string_generator()
    google_pin = random_string_generator()
    start_login = Signal()

    def __init__(self, *args, **kwargs):
        super(LoginWidget, self).__init__(*args, **kwargs)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAutoFillBackground(True)
        self.icon_label = pxl.PixmapLabel('/images/Creaturecast.png', self)
        self.icon_label.setAlignment(Qt.AlignCenter)

        self.google_login_button = ButtonLabel(
            '/images/sign_in_google.png',
            always_download=True,
            parent=self
        )
        self.google_login_button.setAlignment(Qt.AlignCenter)

        self.vertical_layout = QVBoxLayout(self)
        self.horizontal_layout = QHBoxLayout()
        self.button_layout = QVBoxLayout()

        self.horizontal_layout.addLayout(self.vertical_layout)
        self.vertical_layout.addItem(
            QSpacerItem(55, 55)
        )
        self.vertical_layout.addWidget(self.icon_label)
        self.vertical_layout.addLayout(self.horizontal_layout)

        self.horizontal_layout.addStretch()
        self.horizontal_layout.addLayout(self.button_layout)
        self.horizontal_layout.addStretch()

        self.button_layout.addWidget(self.google_login_button)
        self.button_layout.addStretch()
        self.google_login_button.pressed.connect(self.google_login)


    def google_login(self):
        self.start_login.emit()
        #self.web_dialog = WebDialog(self)
        url = '%s/login?temporary_pin=%s' % (svc.library_url, self.google_pin)
        #url = 'https://www.popsci.com/sites/popsci.com/files/styles/655_3x2/public/images/2018/03/n.obscurus_helpers.jpg?itok=J5_GdHsC&fc=50,50'
        #self.web_dialog.web_view.load(QUrl(url))
        #self.web_dialog.show()

        os.startfile(url)
        self.google_worker = wrk.FunctionWorker(gud.get_user_data, self.google_pin, pause=0.0)
        self.google_thread = QThread()
        self.google_thread.start()
        self.google_worker.moveToThread(self.google_thread)
        self.google_worker.data.connect(self.logged_in.emit)
        self.google_worker.start.connect(self.google_worker.run)
        self.google_worker.start.emit()

class ButtonLabel(pxl.PixmapLabel):
    pressed = Signal()

    def __init__(self, *args, **kwargs):
        super(ButtonLabel, self).__init__(*args, **kwargs)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.pressed.emit()


class WebDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(WebDialog, self).__init__(*args, **kwargs)
        self.layout = QHBoxLayout(self)
        self.web_view = QWebEngineView(self)
        self.layout.addWidget(self.web_view)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    widget = LoginWidget()
    widget.show()
    sys.exit(app.exec_())
