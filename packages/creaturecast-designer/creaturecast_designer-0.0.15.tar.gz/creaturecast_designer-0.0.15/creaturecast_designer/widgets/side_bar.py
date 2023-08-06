import json
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import creaturecast_designer.models.sidebar_model as sbm
import creaturecast_designer.services.list_extensions as lex
import creaturecast_designer.services.thread_worker as thd
import creaturecast_designer.widgets.progress_indicator as prg
import creaturecast_designer.environment as env
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

        self.extensions_worker = None
        self.extensions_thread = None

        self.list_view.item_selection.connect(self.item_selection.emit)

        self.list_view.setModel(sbm.SidebarModel([]))

        env.user_handler.user_changed.connect(self.load_extensions)

    def load_extensions(self, user_data):
        print 'SIDEBAR', user_data['settings']['extensions']
        model = sbm.SidebarModel([])
        filter_model = sbm.ToolFilterModel(user_data['settings']['extensions'])
        filter_model.setSourceModel(model)

        self.list_view.setModel(filter_model)

        self.busy_widget.setVisible(True)
        self.busy_widget.startAnimation()

        self.extensions_worker = thd.GeneratorWorker(lex.list_extensions)
        self.extensions_thread = QThread()
        self.extensions_thread.start()
        self.extensions_worker.moveToThread(self.extensions_thread)
        self.extensions_worker.data.connect(self.create_item)
        self.extensions_worker.success.connect(self.end_loading)
        self.extensions_worker.start.connect(self.extensions_worker.run)
        self.extensions_worker.start.emit()

    def end_loading(self):
        self.busy_widget.setVisible(False)

    def create_item(self, json_string):
        self.list_view.get_model().add_item(json.loads(json_string))
        proxy_model = self.list_view.model()
        proxy_model.reset()

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
