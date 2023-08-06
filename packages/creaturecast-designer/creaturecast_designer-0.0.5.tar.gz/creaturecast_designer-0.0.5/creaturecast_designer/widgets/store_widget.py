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
import creaturecast_designer.services.list_tools as ltl
from creaturecast_designer.services.thread_worker import GeneratorWorker, FunctionWorker
import creaturecast_designer.media as med
import creaturecast_designer.services.get_extension as gex

item_size = 1.0
library_url = 'https://creaturecast-library.herokuapp.com'


class StoreWidget(QFrame):

    go_to_tool = Signal(dict)
    new_tool = Signal(dict)
    delete_tool = Signal(dict)

    def __init__(self, *args, **kwargs):
        super(StoreWidget, self).__init__(*args, **kwargs)
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
        self.tools_worker = GeneratorWorker(ltl.list_tools)
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
    new_tool = Signal(object)
    delete_tool = Signal(object)

    def __init__(self, data, *args, **kwargs):
        self.data = data
        super(ExtensionWidget, self).__init__(*args, **kwargs)
        self.image_label = QLabel(self)
        self.text_label = QLabel(data['name'], self)
        self.body_label = QLabel('A tree veiw that lets you explore and create heirarchical scene graphs with nodes.', self)
        self.get_button = QPushButton('Get It', self)
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
        self.get_button.setText('Downloading...')
        self.busy_widget.setVisible(True)
        self.busy_widget.startAnimation()
        self.tools_worker = FunctionWorker(gex.get_extension, self.data['name'])
        self.tools_thread = QThread()
        self.tools_thread.start()
        self.tools_worker.moveToThread(self.tools_thread)
        #self.tools_worker.data.connect(self.create_item)
        self.tools_worker.success.connect(self.finish_download)
        self.tools_worker.start.connect(self.tools_worker.run)
        self.tools_worker.start.emit()

    def finish_download(self):
        self.busy_widget.setVisible(False)
        self.busy_widget.stopAnimation()

    def resizeEvent(self, event):
        self.busy_widget.resize(event.size())
        event.accept()

class ToolWidget(QFrame):

    open_tool = Signal(object)
    new_tool = Signal(object)
    delete_tool = Signal(object)


    def __init__(self, data, *args, **kwargs):
        self.data = data
        super(ToolWidget, self).__init__(*args, **kwargs)

        #Create Widgets
        self.icon_label = QLabel('', self)
        image = QImage(med.get_icon_path(data['icon']))
        self.icon_label.setPixmap(QPixmap.fromImage(image.scaled(32, 32)))

        self.install_button = QPushButton(data['name'], parent=self)
        self.uninstall_button = GetItButton(' Uninstall... ', parent=self)

        self.open_button = GetItButton(' Open... ', parent=self)
        self.installing_label = QLabel(' Downloading... ', parent=self)
        self.uninstalling_label = QLabel(' Uninstalling... ', parent=self)
        self.uninstalling_label.setVisible(False)

        self.installing_label.setVisible(False)
        self.uninstall_button.setVisible(False)

        font = QFont('', 12, True)
        self.install_button.setFont(font)
        self.uninstall_button.setFont(font)

        self.open_button.setFont(font)

        #default_image = QImage(self.table_object.image)
        #default_pixmap = QPixmap.fromImage(default_image.scaled(320, 200, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setProperty("value", 24)
        self.progress_bar.setVisible(False)
        self.open_button.setVisible(False)
        #self.icon_label.setEnabled(False)

        #Layouts
        self.v_layout = QVBoxLayout(self)
        self.h_layout = QHBoxLayout()

        self.v_layout.setSpacing(0)
        self.v_layout.setContentsMargins(0, 0, 0, 0)

        self.h_layout.setSpacing(5)
        self.h_layout.setContentsMargins(0,0,0,0)

        self.h_layout.addWidget(self.installing_label)
        self.h_layout.addWidget(self.uninstalling_label)

        self.v_layout.addWidget(self.icon_label)
        self.v_layout.addLayout(self.h_layout)

        self.h_layout.addWidget(self.progress_bar)

        self.h_layout.addWidget(self.install_button)
        self.h_layout.addWidget(self.uninstall_button)

        self.h_layout.addWidget(self.open_button)

        self.busy_widget = QProgressIndicator(self)
        self.busy_widget.setAnimationDelay(70)
        self.busy_widget.setVisible(False)

        self.install_button.pressed.connect(self.install)
        self.uninstall_button.pressed.connect(self.uninstall)

        self.open_button.pressed.connect(self.emit_open_widget)
        self.open_button.pressed.connect(self.emit_new_widget)

        QMetaObject.connectSlotsByName(self)
        self.progress_bar.minimum = 1
        self.progress_bar.maximum = 100


        package_name = self.data['class_location'].split('.')[0]

        #if tol.session.query(tob.Tool).filter(tob.Tool.git_url == self.data['git_url'].all():
        #    self.finish_install()

    def sizeHint(self, event):
        return QSize(100, 100)



    def resizeEvent(self, event):
        self.busy_widget.resize(event.size())
        event.accept()

    def set_progress(self, progress):
        self.progress_bar.setValue(progress)

    def emit_open_widget(self):
        self.open_tool.emit(self.data)

    def emit_new_widget(self):
        self.new_tool.emit(self.data)

    def uninstall(self):
        self.busy_widget.startAnimation()
        self.busy_widget.setVisible(True)
        self.progress_bar.setVisible(False)
        self.install_button.setVisible(False)
        self.uninstall_button.setVisible(False)
        self.git_line_edit.setVisible(False)
        self.installing_label.setVisible(False)
        self.uninstalling_label.setVisible(True)
        self.open_button.setVisible(False)
        self.git_line_edit.setText(self.data['git_url'].split('/')[-1])
        package_name = self.data['class_location'].split('.')[0]
        self.worker = UninstallWorker('%s/%s' % (env.modules_directory, package_name))
        self.worker.success.connect(self.finish_uninstall)
        self.worker.failed.connect(self.finish_install)
        self.worker.start()

    def install(self):
        self.busy_widget.startAnimation()
        self.busy_widget.setVisible(True)
        self.progress_bar.setValue(0)
        self.install_button.setVisible(False)
        self.git_line_edit.setVisible(False)
        self.progress_bar.setVisible(True)
        self.installing_label.setVisible(True)
        self.worker = GitFetchWorker(self.data['git_url'])
        self.worker.update_progress.connect(self.set_progress)
        self.worker.finished.connect(self.finish_install)
        self.worker.failed.connect(self.reset)
        self.worker.start()


    def finish_install(self):

        tol.add_tools(dict(
            git_url=self.data['git_url'],
            name=self.data['name'],
            icon=self.data['icon'],
            image=self.data['image'],
            class_location=self.data['clas_location']
        ))

        self.busy_widget.setVisible(False)
        self.install_button.setVisible(False)
        self.uninstall_button.setVisible(True)
        self.git_line_edit.setVisible(False)
        self.progress_bar.setVisible(False)
        self.open_button.setVisible(True)
        self.installing_label.setVisible(False)
        #self.icon_label.setEnabled(True)
        self.new_tool.emit(self.data)


    def finish_uninstall(self):

        existing_tools = tol.session.query(tob.Tool).filter(tob.Tool.git_url == self.data['git_url']).all()
        for tool in existing_tools:
            tol.session.delete(tool)
        tol.session.commit()

        self.uninstall_button.setVisible(False)
        self.busy_widget.setVisible(False)
        self.install_button.setVisible(True)
        self.git_line_edit.setVisible(True)
        self.progress_bar.setVisible(False)
        self.open_button.setVisible(False)
        self.installing_label.setVisible(False)
        self.uninstalling_label.setVisible(False)
        #self.icon_label.setEnabled(False)
        self.delete_tool.emit(self.data)

    def reset(self):
        self.install_button.setVisible(False)
        self.busy_widget.setVisible(False)
        self.install_button.setVisible(True)
        self.git_line_edit.setVisible(True)
        self.progress_bar.setVisible(False)
        self.open_button.setVisible(False)
        self.installing_label.setVisible(False)
        #self.icon_label.setEnabled(True)


class GitFetchWorker(QThread):

    update_progress = Signal(int)
    failed = Signal()
    success = Signal()
    def __init__(self, *args, **kwargs):
        self.git_url = str(args[0])
        QThread.__init__(self)

    def run(self):

        import git
        from git import RemoteProgress

        module_name = self.git_url.split('/')[-1].split('.')[0]
        package_directory = '%s/%s' % (env.modules_directory, module_name)
        outdir_checker = package_directory + '/.git'

        class ProgressHandler(RemoteProgress):
            update_progress = PySignal.ClassSignal()

            def __init__(self, signal, *args, **kwargs):
                self.signal = signal
                super(ProgressHandler, self).__init__(*args, **kwargs)

            def update(self, op_code, cur_count, max_count=None, message=''):
                self.signal.emit(int(float(cur_count) / (max_count or 100.0) * 100))

        progress_handler = ProgressHandler(self.update_progress)


        if os.path.exists(outdir_checker):
            #repo_worker = git.Repo.init(package_directory)
            #repo_worker.git.reset('--hard')
            #repo_worker.git.clean('-fdx')
            #remotes = repo_worker.remotes
            #for r in remotes:
            #    o = r.origin
            #    o.pull(progress=progress_handler)
            self.success.emit()

        if not os.path.exists(outdir_checker):
            shutil.rmtree(package_directory, ignore_errors=True)
            os.makedirs(package_directory)
            try:
                git.Repo.clone_from(self.git_url, package_directory, progress=progress_handler)
            except:
                self.failed.emit()
                print 'Failed to clone repo. There seems to be a problem with the network connection'
            print('git dir created')


class UninstallWorker(QThread):

    failed = Signal()
    success = Signal()

    def __init__(self, *args, **kwargs):
        self.package_directory = copy.copy(str(args[0]))
        QThread.__init__(self)

    def run(self):
        if not os.path.exists(self.package_directory):
            self.success.emit()
        #clear_dir(self.package_directory)
        self.success.emit()


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
    mainWin = StoreWidget()
    mainWin.resize(300, 500)
    mainWin.show()
    sys.exit(app.exec_())