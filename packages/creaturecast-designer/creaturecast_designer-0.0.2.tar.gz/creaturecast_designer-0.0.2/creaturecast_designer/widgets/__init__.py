import os
import platform
import traceback
import time


from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *



class LoadingDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(LoadingDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle('Connect Dialog')
        self.layout = QHBoxLayout(self)
        self.label = QLabel('Connecting...', self)
        self.label.setFont(QFont('Arial', 35, True))
        self.layout.addWidget(self.label)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)
        #self.setStyleSheet("background-color:transparent;")

class RaisedFrame(QFrame):
    def __init__(self, *args, **kwargs):
        super(RaisedFrame, self).__init__(*args, **kwargs)
        self.setFrameStyle(QFrame.Panel)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(80, 80, 80))
        self.setPalette(p)
        self.setFrameShadow(QFrame.Raised)


class TableView(QTableView):

    def __init__(self, *args, **kwargs):
        super(TableView, self).__init__(*args, **kwargs)
        self.items = args[0]

    def item_from_index(self, index):
        if index.row() != -1 and index.column() != -1:
            return self.items[index.row()][index.column()]



class ListView(QListView):

    def __init__(self, *args, **kwargs):
        super(ListView, self).__init__(*args, **kwargs)
        self.items = args[0]

class TreeView(QTreeView):

    def __init__(self, *args, **kwargs):
        super(TreeView, self).__init__(*args, **kwargs)


    def map_index_to_source(self, index):
        if isinstance(self.model(), QSortFilterProxyModel):
            index = self.model().mapToSource(index)
        return index

    def map_index_from_source(self, index):
        if isinstance(self.model(), QSortFilterProxyModel):
            index = self.model().mapFromSource(index)
        return index

    def get_model(self):
        model = self.model()
        while isinstance(model, QSortFilterProxyModel):
            model = model.sourceModel()
        return model

    def frame_node(self, index):

        index = self.map_index_from_source(index)
        self.clearSelection()
        self.set_expanded_descendants(QModelIndex(), False)
        self.set_expanded_parenpal
        self.scrollTo(index)

    def frame_nodes(self, indices):
        #self.clearSelection()
        #self.set_expanded_descendants(QModelIndex(), False)

        for index in indices:
            index = self.map_index_from_source(index)
            self.set_expanded_parents(index, True)
            self.select_item(index)
            self.scrollTo(index)


    def set_expanded_parents(self, index, value):
        index = self.map_index_from_source(index)

        model = self.get_model()
        for i in model.get_ancestors(index):
            self.setExpanded(i, value)

    def set_expanded_descendants(self, index, value):
        index = self.map_index_from_source(index)
        model = self.get_model()
        if model:
            for i in model.get_descendants(index):
                self.setExpanded(i, value)

    def select_item(self, index):
            self.selectionModel().select(
                index,
                QItemSelectionModel.Select |
                QItemSelectionModel.Rows
            )

class RatingBox(QComboBox):


    def __init__(self, data, key, *args, **kwargs):
        super(RatingBox, self).__init__(*args, **kwargs)
        self.data = data
        self.key = key
        self.setIconSize(QSize(55, 55))
        self.addItem(QIcon(mda.get_image_path('no_stars')), '')
        self.addItem(QIcon(mda.get_image_path('one_star')), '')
        self.addItem(QIcon(mda.get_image_path('two_stars')), '')
        self.addItem(QIcon(mda.get_image_path('three_stars')), '')
        self.addItem(QIcon(mda.get_image_path('four_stars')), '')
        self.addItem(QIcon(mda.get_image_path('five_stars')), '')
        self.setMaximumSize(QSize(88, 22))
        self.update_widget_value()
        self.currentIndexChanged.connect(self.set_data)

    def update_widget_value(self):
        if self.key in self.data:
            self.setCurrentIndex(self.data[self.key])
            self.setVisible(True)
        else:
            self.setVisible(False)

    def set_data(self, value):
        if self.key in self.data:
            self.setVisible(True)
            self.data[self.key] = value
        else:
            self.setVisible(False)


class Line(QFrame):
    def __init__(self, *args, **kwargs):
        super(Line, self).__init__(*args, **kwargs)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)



class TightLayoutV(QVBoxLayout):
    def __init__(self, *args, **kwargs):
        super(TightLayoutV, self).__init__(*args, **kwargs)
        self.setSpacing(0)
        #self.setMargin(0)
        self.setContentsMargins(0, 0, 0, 0)

class TightLayoutH(QHBoxLayout):
    def __init__(self, *args, **kwargs):
        super(TightLayoutH, self).__init__(*args, **kwargs)
        self.setSpacing(0)
        #self.setMargin(0)
        self.setContentsMargins(0, 0, 0, 0)

class TightLayoutGrid(QGridLayout):
    def __init__(self, *args, **kwargs):
        super(TightLayoutGrid, self).__init__(*args, **kwargs)
        self.setSpacing(0)
        #self.setMargin(0)
        self.setContentsMargins(0, 0, 0, 0)

class IconButton(QPushButton):
    icon_changed = Signal(str)
    def __init__(self, icon_name, *args, **kwargs):
        super(IconButton, self).__init__(*args, **kwargs)
        self.icon_name = icon_name
        self.set_icon(icon_name)
        self.setFlat(True)
        self.setIconSize(QSize(64, 64))
        self.editable = False


    def mousePressEvent(self, event):
        if self.editable:
            if event.button() == Qt.LeftButton:
                path = mda.icon_directory
                if os.path.exists(path):
                    if platform.system() == 'Darwin':
                        #pySide and Mavericks needs special handling to start in correct dir
                        self.dialog = IconDialog(self, 'Pick an icon', r'%s/icons/icons_orig' % os.path.dirname(__file__))
                        self.dialog.selectFile(r'%s/icons/icons_orig/python.png' % os.path.dirname(__file__))
                        self.dialog.accepted.connect(self.set_icon_mac)
                        self.dialog.exec_()

                    else:
                        path, ok = IconDialog.getOpenFileName(self, 'Pick Icon', path, 'Png (*.png)')
                        if ok:
                            self.set_icon(os.path.basename(str(path)).split('.')[0])
                else:
                    raise IOError('Icon dir does not exist %s ' % path)

    def set_icon(self, icon_name):

        self.icon_name = icon_name

        super(IconButton, self).setIcon(QIcon(ico.get_icon(icon_name)))
        self.icon_changed.emit(self.icon_name)

    def set_icon_mac(self):
        sel = self.dialog.selectedFiles()
        if sel:
            self.set_icon(os.path.basename(sel[0]).split('.')[0])


class IconDialog(QFileDialog):
    def __init__(self, *args, **kwargs):
        super(IconDialog, self).__init__(*args, **kwargs)
        self.iconsDir = mda.icon_directory
        self.setDirectory(self.iconsDir)
        self.setFileMode(QFileDialog.ExistingFile)
        self.setViewMode(QFileDialog.List)
        self.directoryEntered.connect(self.blockDir)

    def blockDir(self, dir):
        if not dir == self.iconsDir:
            self.setDirectory(self.iconsDir)

def progress_generator(iterator, *args, **kwargs):
    prog=QProgressDialog(*args, **kwargs)
    prog.setModal(True)
    prog.show()
    prog.raise_()
    prog.setWindowTitle('Calculating...')
    prog.setWindowIcon(ico.get_icon('progress'))
    prog.setValue(0)
    itr = 0
    #try:
    for rig in iterator():
        #time.sleep(0.01)

        if prog.wasCanceled():
            break
        prog.setValue(itr)
        itr += 1
        yield rig

    #except:
    #print traceback.format_exc()
    #QMessageBox.warning(prog, 'Build Failed', '%s \n See Script Editor for details' % parse_error_message(traceback.format_exc()))
    prog.close()


    def error_dialog(self, e):
        if isinstance(e, prd.AuthenticationFailed):
            reply = QMessageBox.question(self, 'Authentication Failed', '%s\nWould you like to launch the license manager?' % e.message, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                ui = lmg.LicenseManager(self)
                ui.show()
                #self.close()
        if isinstance(e, Exception):
            print traceback.format_exc()




def parse_error_message(errorString):
    items=errorString.split('\n')
    for itr, item in enumerate(items):
        if not item:
            return items[itr-1]
