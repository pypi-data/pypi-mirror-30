
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import creaturecast_designer.widgets.icon as ico

class SidebarModel(QAbstractTableModel):

    def __init__(self, items):
        super(SidebarModel, self).__init__()
        self.items = items
        self.title_font = QFont('', 15, True)
        self.item_font = QFont('', 12, False)


    def rowCount(self, index):
        return len(self.items)

    def columnCount(self, index):
        return 2

    def data(self, index, role):
        item = self.get_item(index)
        icon = item['icon']

        if role == Qt.DisplayRole or role == Qt.EditRole:
            return item['name']
        if role == Qt.FontRole:
            if not icon:
                return self.title_font
            else:
                return self.item_font
        if role == Qt.DecorationRole:
            if icon:
                return ico.get_icon(icon)

    def flags(self, index):
        if index.isValid():
            item = self.get_item(index)
            if item['icon']:
                return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsSelectable
            return Qt.ItemIsEnabled


    def get_item(self, index):
        if index.isValid():
            return self.items[index.row()]

    def add_item(self, data):
        row = len(self.items)
        self.beginInsertRows(QModelIndex(), row, row+1)
        self.items.append(data)
        self.endInsertRows()


class ToolFilterModel(QSortFilterProxyModel):
    def __init__(self, user_tools, *args, **kwargs):
        super(ToolFilterModel, self).__init__(*args, **kwargs)
        self.setDynamicSortFilter(True)
        self.user_tools = user_tools

    def set_user_tools(self, user_tools):
        self.user_tools = user_tools
        self.invalidateFilter()

    def filterAcceptsRow(self, sourceRow, sourceParent):
        index = self.sourceModel().index(sourceRow, 0, sourceParent)

        if index.isValid():
            tool = self.sourceModel().get_item(index)
            if tool['name'] in self.user_tools:
                return True
        return False

    def get_item(self, index):
        source_index = self.mapToSource(index)
        return self.sourceModel().get_item(source_index)
