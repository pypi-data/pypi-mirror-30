from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *


class AbstractPropertiesModel(QAbstractTableModel):

    def __init__(self, **properties):
        super(AbstractPropertiesModel, self).__init__()
        self.key_font = QFont('None', 14, True)
        self.value_font = QFont('None', 12, False)
        self.key_color = QColor(111, 111, 111)
        self.value_background_color = QColor(210, 210, 210)
        self.value_color = QColor(22, 22, 22)

        self.properties = properties
        self.keys = properties.keys()

    def __setitem__(self, key, value):
        if key in self.keys:
            self.properties[key] = value
            index_row = self.keys.index(key)
            index = self.index(index_row, 0, QModelIndex())
            self.dataChanged.emit(index, index, 0)

    def value_from_index(self, index):
        row = index.row()
        if row != -1:
            return self.properties[self.keys[row]]

    def rowCount(self, index):
        return len(self.keys)

    def columnCount(self, index):
        return 2

    def data(self, index, role):
        column = index.column()
        key = self.keys[index.row()]
        value = self.value_from_index(index)

        if column == 0:
            if role == Qt.FontRole:
                return self.key_font
            if role == Qt.BackgroundColorRole:
                return self.key_color
            if role == Qt.TextAlignmentRole:
                return Qt.AlignLeft
            if role == Qt.DisplayRole or role == Qt.EditRole:
                return key

        if column == 1:
            if role == Qt.FontRole:
                return self.value_font
            if role == Qt.BackgroundColorRole:
                return self.value_background_color
            if role == Qt.TextColorRole:
                return self.value_color
            if role == Qt.TextAlignmentRole:
                return Qt.AlignLeft
            if role == Qt.DisplayRole:
                if isinstance(value, (list, tuple, dict)):
                    value = str(type(value))
                return value

            if role == Qt.EditRole:
                return str(value)


    def flags(self, index):
        column = index.column()
        if column == 0:
            return Qt.ItemIsEnabled
        if column == 1:
            return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def setData(self, index, value, role=Qt.EditRole):
        row = index.row()
        column = index.column()
        key = self.keys[index.row()]
        if role == Qt.EditRole:
            current_value = self.value_from_index(index)
            if isinstance(current_value, (list, tuple, dict)):
                value = eval(value)
            self.properties[key] = value
            self.dataChanged.emit(index, index, 0)
            return True
        return False


class PropertiesModel(AbstractPropertiesModel):

    def __init__(self, **properties):
        super(PropertiesModel, self).__init__(**properties)
