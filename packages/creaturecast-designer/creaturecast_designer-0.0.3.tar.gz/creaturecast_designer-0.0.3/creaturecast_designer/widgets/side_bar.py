import json

import sys
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import creaturecast_designer.models.sidebar_model as sbm
import creaturecast_designer.services.list_tools as list_tools
import creaturecast_designer.services.thread_worker as thd
import creaturecast_designer.widgets.progress_indicator as prg
dock_options = QMainWindow.AnimatedDocks | QMainWindow.AllowNestedDocks | QMainWindow.AllowTabbedDocks | QMainWindow.VerticalTabs
#| QMainWindow.AllowNestedDocks | QMainWindow.AllowTabbedDock


class SidebarWidget(QWidget):
    item_indent_spaces = 4
    item_selection = Signal(list)
    log_out = Signal()

    def __init__(self, *args, **kwargs):
        super(SidebarWidget, self).__init__(*args, **kwargs)

        self.vertical_layout = QVBoxLayout(self)
        self.list_view = SideBarView(self)
        self.list_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.list_view.setIconSize(QSize(32, 32))
        self.list_view.setSpacing(2)
        self.dock_widgets = {}

        self.vertical_layout.addWidget(self.list_view)
        self.setContentsMargins(0, 0, 0, 0)
        self.list_view.setContentsMargins(0, 0, 0, 0)
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.setMaximumWidth(215)
        self.setMinimumWidth(215)

        self.busy_widget = prg.QProgressIndicator(self)
        self.busy_widget.setAnimationDelay(70)
        self.busy_widget.setVisible(False)

        self.tools_worker = None
        self.tools_thread = None

        self.list_view.item_selection.connect(self.item_selection.emit)
        self.list_view.setModel(sbm.SidebarModel([]))

    def load_tools(self, user_data):
        model = sbm.SidebarModel([])
        filter_model = sbm.ToolFilterModel(user_data['settings']['tools'])
        filter_model.setSourceModel(model)

        self.list_view.setModel(filter_model)

        self.busy_widget.setVisible(True)
        self.busy_widget.startAnimation()

        self.tools_worker = thd.GeneratorWorker(list_tools.list_tools)

        self.tools_thread = QThread()
        self.tools_thread.start()

        self.tools_worker.moveToThread(self.tools_thread)

        self.tools_worker.data.connect(self.create_item)
        self.tools_worker.success.connect(self.end_loading)

        self.tools_worker.start.connect(self.tools_worker.run)
        self.tools_worker.start.emit()

    def end_loading(self):
        self.busy_widget.setVisible(False)

    def create_item(self, json_string):
        self.list_view.get_model().add_item(json.loads(json_string))

    def resizeEvent(self, event):
        self.busy_widget.resize(event.size())
        event.accept()

class SideBarView(QListView):

    item_selection = Signal(list)

    def __init__(self, *args, **kwargs):
        super(SideBarView, self).__init__(*args, **kwargs)
        self.setFocusPolicy(Qt.NoFocus)

    def setModel(self, model):
        super(SideBarView, self).setModel(model)
        if model:
            selectionModel = self.selectionModel()
            selectionModel.selectionChanged.connect(self.emit_selected_items)

    def emit_selected_items(self, *args):
        model = self.model()
        new_selection, old_selection = args

        old_indices = [i for i in self.selectedIndexes() if i.column() == 0]
        new_indices = [i for i in new_selection.indexes() if i.column() == 0]
        self.item_selection.emit([model.get_item(x) for x in old_indices])

    def get_model(self):
        model = self.model()
        while isinstance(model, QSortFilterProxyModel):
            model = model.sourceModel()
        return model

class SideBarItem(object):
    def __init__(self, **kwargs):
        super(SideBarItem, self).__init__()
        self.data = dict(kwargs)
        self.dock_widget = None

    def __str__(self):
        return self.data['name']

    def __repr__(self):
        return self.__str__()
