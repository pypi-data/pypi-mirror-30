import copy

from qtpy.QtCore import *
import creaturecast_designer.widgets.icon as ico
import py_maya_core.node as nod


class AbstractTreeModel(QAbstractItemModel):
    def __init__(self, *args):
        super(AbstractTreeModel, self).__init__()
        self.root = args[0]

    def rowCount(self, index):
        item = self.get_item(index)
        return len(item.children)

    def columnCount(self, index):
        return 1

    def index(self, row, column, parent_index):
        if not self.hasIndex(row, column, parent_index):
            return QModelIndex()

        parent = self.get_item(parent_index)
        if parent:
            return self.createIndex(row, column, parent.children[row])
        return QModelIndex()

    def data(self, index, role):
        item = self.get_item(index)

        if index.column() == 0:

            if role == Qt.DisplayRole or role == Qt.EditRole:
                return item.data['name']

            if role == Qt.DecorationRole:
                if isinstance(item, nod.Node):
                    return ico.get_icon('animal_fly')

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsSelectable

    def get_item(self, index):
        return index.internalPointer() if index.isValid() else self.root


class TreeModel(AbstractTreeModel):

    def __init__(self, *args):
        super(TreeModel, self).__init__(*args)
        self.index_dictionary = dict()

    def get_child_indices(self, index):
        item = self.get_item(index)
        indexes = []
        for itr in range(len(item.children)):
            indexes.append(self.index(itr, 0, index))
        return indexes

    def get_descendants(self, index):
        descendants = []
        for childIndex in self.get_child_indices(index):
            descendants.append(childIndex)
            descendants.extend(self.get_descendants(childIndex))
        return descendants

    def get_ancestors(self, index):
        indices = []
        while self.get_item(index) is not self.root:
            indices.append(index.parent())
            index = index.parent()
        return indices

    def items_from_indices(self, indices):
        return [self.get_item(x) for x in indices]

    def parent(self, index):
        item = self.get_item(index)
        parent = item.parent
        if parent == self.root:
            return QModelIndex()
        if parent is None:
            return QModelIndex()
        return self.createIndex(parent.get_index(), 0, parent)

    def reset_data(self, index):
        item = self.get_item(index)
        item.data.update(copy.copy(item.default_data))

    def delete_item(self, index):
        node = self.get_item(index)
        parent_index = index.parent()
        row = self.items.index(node)
        self.beginRemoveRows(parent_index, row, row)
        self.items.remove(node)
        self.endRemoveRows()

    def index_from_item(self, item):
        index = QModelIndex()
        for x in item.get_position():
            index = self.index(x, 0, index)
        if item == self.get_item(index):
            return index

class ListModel(QAbstractListModel):

    def __init__(self, items):
        super(ListModel, self).__init__()
        self.items = items

    def rowCount(self, index):
        return len(self.items)

    def columnCount(self, index):
        return 1

    def data(self, index, role):
        item = self.get_item(index)

        if role == Qt.DisplayRole or role == Qt.EditRole:
            return item.data['name']

        if role == Qt.DecorationRole:
            return ico.get_icon(item.data['icon'])

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsSelectable

    def delete_item(self, index):
        node = self.get_item(index)
        parent_index = index.parent()
        row = self.items.index(node)
        self.beginRemoveRows(parent_index, row, row)
        self.items.remove(node)
        self.endRemoveRows()

    def get_item(self, index):
        if index.isValid():
            return self.items[index.row()]





class TableModel(QAbstractTableModel):
    def __init__(self, data=[[]], headers=[], parent=None):
        super(TableModel, self).__init__(parent)
        self._data = data
        self.__headers = headers

    def itemFromIndex(self, index):
        return self._data[index.row()][index.column()]

    def rowCount(self, parent):
        return len(self._data)

    def columnCount(self, parent):
        if len(self._data):
            return len(self._data[0])
        return -1

    def flags(self, index):
        #if not index.isValid():
        #    return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsSelectable


    def supportedDropActions(self):
        return Qt.CopyAction | Qt.MoveAction

    def supportedDragActions(self):
        return Qt.MoveAction | Qt.CopyAction

    def data(self, index, role):

        row = index.row()
        column = index.column()
        if row < len(self._data) and column < len(self._data[row]):
            if role == Qt.EditRole:
                row = index.row()
                column = index.column()
                data = self._data[row][column]
                return data

            if role == Qt.ToolTipRole:
                row = index.row()
                column = index.column()
                return  self._data[row][column]

            if role == Qt.DisplayRole:

                row = index.row()
                column = index.column()
                value = self._data[row][column]
                return value

    def setData(self, index, value, role = Qt.EditRole):
        if role == Qt.EditRole:
            row = index.row()
            column = index.column()
            self._data[row][column] = str(value.toString())
            # Why does this throw a warning!!!!!??!

            self.dataChanged.emit(index, index)
            return True
        return False

    def headerData(self, section, orientation, role):

        return None
        if role == Qt.DisplayRole:
            return None
            if orientation == Qt.Horizontal:

                if section < len(self.__headers):
                    return self.__headers[section]
                else:
                    return "not implemented"
            else:
                return None



    #=====================================================#
    #INSERTING & REMOVING
    #=====================================================#
    def insertRows( self, row, count, parentIndex = QModelIndex() ):
        self.beginInsertRows( parentIndex, row, row+count-1 )
        parentItem = self.itemFromIndex(parentIndex)
        print 'Inserting row [%s] under [%s]' % (row, parentItem)
        self.endInsertRows()
        return True

    def insertColumns(self, position, columns, parent = QModelIndex()):
        self.beginInsertColumns(parent, position, position + columns - 1)

        self.endInsertColumns()

        return True

    def moveRows( self, position, count,  parent = QModelIndex()):
        print 'MovingRows...'
        return True
        self.beginRemoveRows(parent, position, position+count-1 )
        for x in range( count ):
            print 'Removing row [%s] under [%s]' % (row, parent)
            self._data.pop(position)
        self.endRemoveRows()
        return True



    def removeRows( self, row, count, parentIndex = QModelIndex()):
        print 'RemovingRows...'
        self.beginRemoveRows( parentIndex, row, row+count-1 )
        for x in range( count ):
            self._data.pop(row)
        self.endRemoveRows()
        return True

    def removeColumns( self, position, count,  parentIndex = QModelIndex()):
        return False


    def removeRow( self, position,  parentIndex = QModelIndex()):
        print 'RemovingRow...'
        return False

    def removeColumn( self, position,  parentIndex = QModelIndex()):
        print 'RemovingColumn..'
        return False
