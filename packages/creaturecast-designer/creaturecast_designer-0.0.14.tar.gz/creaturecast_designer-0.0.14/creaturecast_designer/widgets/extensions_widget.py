import functools
import os
import shutil
import copy
import json
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import PySignal

from creaturecast_designer.widgets.progress_widget import ProgressWidget
import creaturecast_designer.widgets.flow_layout as flt
import creaturecast_designer.environment as env
import creaturecast_designer.widgets.icon as ico
import creaturecast_designer.services.list_extensions as lex
from creaturecast_designer.services.thread_worker import GeneratorWorker, FunctionWorker
import creaturecast_designer.media as med
import creaturecast_designer.services.pip_functions as pfn
import creaturecast_designer.services.update_user_data as uud

item_size = 1.0
library_url = 'https://creaturecast-library.herokuapp.com'


class ExtensionsWidget(QFrame):

    go_to_tool = Signal(dict)
    delete_tool = Signal(dict)

    def __init__(self, *args, **kwargs):
        super(ExtensionsWidget, self).__init__(*args, **kwargs)
        self.main_layout = QVBoxLayout(self)
        self.search_layout = QHBoxLayout()
        self.search_button = QPushButton('Search', self)

        self.search_field = SearchLineEdit(self)
        self.scroll_area = QScrollArea(self)
        self.search_field.setFont(QFont('', 12, False))
        self.search_button.setFont(QFont('', 12, False))
        self.main_layout.addLayout(self.search_layout)
        self.search_layout.addWidget(self.search_field)
        self.search_layout.addWidget(self.search_button)

        self.main_layout.addWidget(self.scroll_area)
        self.flow_layout = flt.FlowLayout(self.scroll_area)
        self.setAcceptDrops(True)
        self.main_layout.setSpacing(5)
        self.main_layout.setContentsMargins(10, 5, 5, 5)
        self.flow_layout.setSpacing(8)
        self.flow_layout.setContentsMargins(0, 0, 0, 0)
        self.search_layout.setSpacing(5)
        self.search_layout.setContentsMargins(0, 0, 0, 0)


        self.busy_widget = ProgressWidget(self)
        self.busy_widget.setAnimationDelay(70)
        self.busy_widget.setVisible(False)
        self.search_button.pressed.connect(self.get_tools)


    def get_tools(self):

        search_text = self.search_field.text()
        self.busy_widget.setVisible(True)
        self.busy_widget.startAnimation()
        self.tools_worker = GeneratorWorker(lex.list_extensions)
        self.tools_thread = QThread()
        self.tools_thread.start()
        self.tools_worker.moveToThread(self.tools_thread)
        self.tools_worker.data.connect(self.create_item)
        self.tools_worker.success.connect(self.finish_loading)
        self.tools_worker.start.connect(self.tools_worker.run)
        self.tools_worker.start.emit()

    def finish_loading(self):
        self.busy_widget.setVisible(False)

    def create_item(self, json_string):
        data = json.loads(json_string)
        tool_widget = ExtensionWidget(data, self)
        self.flow_layout.addWidget(tool_widget)
        QApplication.processEvents()

    def search_items(self, text):
        for item in self.flow_layout.itemList:
            widget = item.widget()
            widget.setVisible(True)
            if not text.lower() in widget.table_object.name.lower():
                widget.setVisible(False)


    def resizeEvent(self, event):
        self.busy_widget.resize(event.size())
        event.accept()


class SearchLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super(SearchLineEdit, self).__init__(*args, **kwargs)

        self.setPlaceholderText(self.tr('Search'))
        font = QFont('', 12, False)
        self.setFont(font)
        self.setCursor(Qt.ArrowCursor)

        self.button_toggle = QPushButton(self)
        self.button_toggle.setIcon(ico.get_icon('x'))
        self.button_toggle.setFlat(True)
        self.button_toggle.setIconSize(QSize(22, 22))
        self.button_toggle.setStyleSheet('QPushButton { border: none; padding: 0px;}')

        frame_width = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        #self.setStyleSheet('QLineEdit {{ padding-right: {}px; }} '.format(self.button_toggle.sizeHint().width() + frame_width + 1))
        msz = self.minimumSizeHint()
        self.setMinimumSize(max(msz.width(), self.button_toggle.sizeHint().height() + frame_width * 2 + 2),
                            max(msz.height(), self.button_toggle.sizeHint().height() + frame_width * 2 + 2))

        self.button_toggle.pressed.connect(functools.partial(self.setText, ''))
        self.textChanged.connect(self.set_clear_button_visibility)
        self.button_toggle.setVisible(False)

    def set_clear_button_visibility(self, text):
        self.button_toggle.setVisible(False)
        if text:
            self.button_toggle.setVisible(True)

    def resizeEvent(self, event):
        sz = self.button_toggle.sizeHint()
        frame_width = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        self.button_toggle.move(self.rect().right() - frame_width - sz.width(),
                           (self.rect().bottom() + 1 - sz.height())/2)



class ExtensionWidget(QFrame):

    open_tool = Signal(object)
    delete_tool = Signal(object)

    def __init__(self, data, *args, **kwargs):
        self.data = data
        self.extension_name = self.data['class_location'].split('.')[0]
        super(ExtensionWidget, self).__init__(*args, **kwargs)
        self.image_label = QLabel(self)
        self.text_label = QLabel(data['name'], self)
        self.body_label = QLabel('A tree veiw that lets you explore and create heirarchical scene graphs with nodes.', self)
        self.get_button = QPushButton('pip install...', self)
        self.busy_widget = ProgressWidget(self)

        self.main_vertical_layout = QVBoxLayout(self)
        self.top_horizontal_layout = QHBoxLayout()
        self.top_vertical_layout = QVBoxLayout()
        self.main_vertical_layout.addLayout(self.top_horizontal_layout)
        self.top_horizontal_layout.addStretch()
        self.top_horizontal_layout.addLayout(self.top_vertical_layout)
        self.top_horizontal_layout.addStretch()
        self.top_vertical_layout.addStretch()
        self.bottom_vertical_layout = QVBoxLayout()

        self.top_vertical_layout.addWidget(self.image_label)
        self.top_vertical_layout.addWidget(self.text_label)
        self.top_vertical_layout.addStretch()
        self.main_vertical_layout.addWidget(LineWidget(self))
        self.main_vertical_layout.addLayout(self.bottom_vertical_layout)
        self.bottom_vertical_layout.addStretch()
        self.bottom_vertical_layout.addWidget(self.body_label)
        self.bottom_vertical_layout.addStretch()
        self.bottom_vertical_layout.addWidget(self.get_button)
        self.text_label.setFont(QFont('', 12, False))
        self.text_label.setAlignment(Qt.AlignHCenter)
        self.image_label.setAlignment(Qt.AlignHCenter)
        self.body_label.setAlignment(Qt.AlignHCenter)


        image = QImage(med.get_icon_path(data['icon']))
        self.busy_widget.setAnimationDelay(70)
        self.busy_widget.setVisible(False)
        self.image_label.setPixmap(QPixmap.fromImage(image.scaled(45, 45)))
        self.body_label.setWordWrap(True)
        self.body_label.setFont(QFont('', 10, False))
        self.get_button.setFont(QFont('', 14, False))
        self.setProperty('WA_Hover', True)
        #self.get_button.setStyleSheet("background-color: grey;")
        self.main_vertical_layout.setSpacing(0)
        self.main_vertical_layout.setContentsMargins(5, 5, 5, 5)
        #self.bottom_vertical_layout.setSpacing(0)
        self.bottom_vertical_layout.setContentsMargins(5, 5, 5, 5)

        self.get_button.pressed.connect(self.download)

    def sizeHint(self, *args, **kwargs):
        return QSize(256, 256)

    def download(self):
        self.get_button.setText('installing')
        self.busy_widget.setVisible(True)
        self.busy_widget.startAnimation()
        self.tools_worker = FunctionWorker(pfn.pip_install, self.extension_name)
        self.tools_thread = QThread()
        self.tools_thread.start()
        self.tools_worker.moveToThread(self.tools_thread)
        self.tools_worker.start.connect(self.tools_worker.run)
        self.tools_worker.data.connect(self.new_extension)
        self.tools_worker.end.connect(self.finish_download)
        self.tools_worker.start.emit()

    def new_extension(self, package_name):
        print '---------->>', package_name
        current_user = env.user_handler.current_user
        current_user['settings']['extensions'].append(package_name)
        print 'EXTENSION WIDGET', current_user['settings']['extensions']
        env.user_handler.user_changed.emit(current_user)

    def finish_download(self):
        self.busy_widget.setVisible(False)
        self.busy_widget.stopAnimation()


        '''
        self.user_worker = FunctionWorker(
            uud.update_user_data,
            current_user['token'],
            extensions=users_extensions
        )
        self.user_thread = QThread()
        self.user_thread.start()
        self.user_worker.moveToThread(self.user_thread)

        #self.user_worker.end.connect(env.user_handler.set_user)
        self.user_worker.start.connect(self.user_worker.run)
        self.user_worker.start.emit()
        '''
        self.get_button.setText('pip uninstall...')



    def resizeEvent(self, event):
        self.busy_widget.resize(event.size())
        event.accept()



def clear_dir(path):
    shutil.rmtree(path, ignore_errors=False, onerror=onerror)


def onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise Exception('Could not delete path %s' % path)




class LineWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super(LineWidget, self).__init__(*args, **kwargs)
        self.setFixedHeight(1)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet("background-color: grey;")

if __name__ == '__main__':

    import sys
    import creaturecast_designer.stylesheets as stl
    app = QApplication(sys.argv)
    app.setStyleSheet(stl.get_stylesheet('slate'))
    mainWin = ExtensionsWidget()
    mainWin.resize(300, 500)
    mainWin.show()
    sys.exit(app.exec_())