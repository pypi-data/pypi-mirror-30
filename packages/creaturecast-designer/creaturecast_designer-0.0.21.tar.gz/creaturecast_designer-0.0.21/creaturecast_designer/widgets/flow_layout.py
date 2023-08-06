from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()

        flowLayout = FlowLayout()
        flowLayout.addWidget(MyWidget(self))
        flowLayout.addWidget(MyWidget(self))
        flowLayout.addWidget(MyWidget(self))
        flowLayout.addWidget(MyWidget(self))
        flowLayout.addWidget(MyWidget(self))
        self.setLayout(flowLayout)
        self.setWindowTitle("Flow Layout")


class FlowLayout(QLayout):

    geometry_changed = Signal()

    def __init__(self, parent=None, margin=0, spacing=-1):
        super(FlowLayout, self).__init__(parent)

        #if parent is not None:
        #    self.setMargin(margin)

        self.setSpacing(spacing)

        self.item_list = []

    def clear(self):
        for x in range(len(self.item_list)):
            self.takeAt(0)

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.item_list.append(item)

    def count(self):
        return len(self.item_list)

    def itemAt(self, index):
        if index >= 0 and index < len(self.item_list):
            return self.item_list[index]

        return None

    def takeAt(self, index):
        if index >= 0 and index < len(self.item_list):
            return self.item_list.pop(index)

        return None

    #def expandingDirections(self):
    #    return Qt.Orientations(Qt.Orientation(0))

    #def hasHeightForWidth(self):
    #    return True

    #def heightForWidth(self, width):
    #    height = self.doLayout(QRect(0, 0, width, 0), True)
    #    return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)
        self.geometry_changed.emit()

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.item_list:
            size = size.expandedTo(item.minimumSize())
        size += QSize(2 * self.margin(), 2 * self.margin())
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for item in self.item_list:
            wid = item.widget()
            spaceX = self.spacing() + wid.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal)
            spaceY = self.spacing() + wid.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical)
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()


class MyWidget(QWidget):
    clicked = Signal()
    keyPressed = Signal(unicode)

    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)

    def sizeHint(self):
        return QSize(128, 128)

    def heightForWidth(self, width):
        return width * 1.5




if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)

    mainWin = Window()
    mainWin.show()
    sys.exit(app.exec_())