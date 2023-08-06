import copy
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *


class Port(QGraphicsWidget):

    size = 12

    def __init__(self, *args, **kwargs):
        super(Port, self).__init__(*args, **kwargs)

        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.setPreferredSize(QSize(self.size, self.size))
        self.setWindowFrameMargins(1, 1, 1, 1)
        self.transform().translate(0, 0)
        self.default_pen = QPen(QColor(200, 100, 100), 1.0)
        self.hover_pen = QPen(QColor(200, 100, 100), 1.5)
        self.brush = QBrush(QColor(200, 100, 100))
        polygon = QPolygonF([QPoint(*x) for x in [0, 0], [0, self.size], [self.size*0.5, self.size*0.5], [0, 0]])
        self.elipse_item = QGraphicsPolygonItem(polygon, parent=self)
        self.elipse_item.setPen(self.default_pen)
        self.elipse_item.setBrush(self.brush)
        #self.elipse_item.setPos(size.width()/2, size.height()/2)
        #self.elipse_item.setRect(
        #    -self.radius,
        #    -self.radius,
        #    self.diameter,
        #    self.diameter,
        #    )


        #self.setColor(QColor(255, 0, 0))
        self.setAcceptHoverEvents(True)


    #def paint(self, painter, option, widget):
    #    window_rect = self.windowFrameRect()

    #    painter.setBrush(QColor(100, 100, 100))
    #
    #    painter.drawRect(window_rect)


class Attribute(QGraphicsWidget):
    font = QFont("", 20, True)
    font.setWeight(0)


    def __init__(self, text, parent):
        super(Attribute, self).__init__(parent)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.setPreferredSize(QSize(100, 20))
        layout = QGraphicsLinearLayout(self)
        layout.setOrientation(Qt.Horizontal)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(3)

        #self.text_widget = QGraphicsWidget(self)
        #self.text_item = QGraphicsTextItem(text, self.text_widget)
        #self.text_item.setDefaultTextColor(parent.outline_color)
        #self.text_item.setFont(self.font)
        #option = self.text_item.document().defaultTextOption()
        #option.setWrapMode(QTextOption.NoWrap)
        #self.text_item.document().setDefaultTextOption(option)
        #self.text_item.adjustSize()


        self.in_port = Port()
        self.out_port = Port()

        layout.addItem(self.in_port)
        layout.setAlignment(self.in_port, Qt.AlignLeft| Qt.AlignTop)

        layout.addStretch()
        #layout.addItem(self.text_widget)
        #layout.setAlignment(self.text_widget, Qt.AlignCenter| Qt.AlignTop)

        layout.addStretch()
        layout.addItem(self.out_port)
        layout.setAlignment(self.out_port, Qt.AlignRight| Qt.AlignTop)

        self.setLayout(layout)

    def get_text_size(self):
        return QSizeF(
            self.text_item.textWidth(),
            self.font.pointSizeF()
            )




class NodeTitle(QGraphicsWidget):

    font = QFont("arial", 32, True)
    font.setWeight(0)
    font.setLetterSpacing(QFont.PercentageSpacing, 100)

    def __init__(self, text, parent):
        super(NodeTitle, self).__init__(parent)

        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        layout = QGraphicsLinearLayout(self)
        layout.setOrientation(Qt.Horizontal)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.text_item = QGraphicsTextItem(text, self)

        self.text_item.setDefaultTextColor(parent.color)
        self.text_item.setFont(self.font)
        option = self.text_item.document().defaultTextOption()
        option.setWrapMode(QTextOption.NoWrap)
        self.text_item.document().setDefaultTextOption(option)
        #self.text_item.adjustSize()
        self.setPreferredSize(QSize(100, 10))
        layout.addItem(self.text_item)
        self.setLayout(layout)

    def set_text(self, text):
        self.text_item.setPlainText(text)
        self.text_item.adjustSize()
        self.setPreferredSize(self.textSize())

    def get_text_size(self):
        return QSizeF(
            self.text_item.textWidth(),
            self.font.pointSizeF()
            )


    def paint(self, painter, option, widget):
        window_rect = self.windowFrameRect()
        # window_rect.setLeft(20)


        painter.drawRoundedRect(window_rect, 5, 5)


class NodeHeader(QGraphicsWidget):

    icon_size = QSize(42, 42)
    def __init__(self, text, *args, **kwargs):
        super(NodeHeader, self).__init__(*args, **kwargs)
        self.icon='handle_blackWhite'
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        layout = QGraphicsLinearLayout(self)
        layout.setOrientation(Qt.Horizontal)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        pixmap = QPixmap(
            "/Users/paxtongerrish/Scripts/creaturecast_pyside/media/icons/%s.png"
            % self.icon).scaled(self.icon_size, transformationMode=Qt.SmoothTransformation )
        self.icon_widget = QGraphicsWidget(self)
        QGraphicsPixmapItem(pixmap, self.icon_widget)
        self.icon_widget.setMaximumSize(self.icon_size)

        self.color = QColor(120, 120, 120)
        #self.title_widget = NodeTitle(text, self)
        layout.addItem(self.icon_widget)
        #layout.addItem(self.title_widget)
        self.setLayout(layout)

    def setText(self, text):
        self.title_widget.setText(text)





class Node(QGraphicsWidget):


    def __init__(self, graph, name='', icon='chain'):
        super(Node, self).__init__()
        self.setMinimumWidth(100)
        self.setMinimumHeight(50)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        layout = QGraphicsLinearLayout(self)
        layout.setOrientation(Qt.Vertical)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        self.name = name
        self.icon = icon
        self.dragging = True
        self.mouse_start = QPoint()
        self.mouse_delta = QPoint()
        self.last_drag_point = QPoint()
        self.nodes_moved = False
        self.color = QColor(40, 40, 40)
        self.outline_color = QColor(140, 140, 140)
        self.selected_color = self.color

        self.outline_pen = QPen(self.outline_color, 1)
        self.outline_selected_pen = QPen(self.outline_color.lighter(80), 1)
        self.outline_selected_pen.setStyle(Qt.DashLine)

        self.selected = False
        self.dragging = False
        self.graph = graph

        self.icon = NodeHeader(text=self.name, parent=self)
        self.icon.setTransform(QTransform.fromTranslate(-32, -32))

        self.text_item = QGraphicsTextItem(name, self)
        self.text_item.setDefaultTextColor(self.outline_color)
        self.text_item.setFont(QFont('arial', 32))
        rect = self.text_item.boundingRect()
        self.text_item.setPos(QPoint(0, 0))



        for attribute_name in ['parent', 'spaces', 'size', 'side', 'index', 'color']:
            new_attribute = Attribute(attribute_name, self)
            layout.addItem(new_attribute)
            layout.setAlignment(new_attribute, Qt.AlignCenter | Qt.AlignTop)


        self.graph.scene().addItem(self)
        self.graph.selected_nodes.append(self)

        self.setLayout(layout)

    def paint(self, painter, option, widget):
        window_rect = self.windowFrameRect()
        #window_rect.setLeft(20)
        #window_rect.setBottom(window_rect.bottom()+30)
        if self.selected:
            painter.setBrush(self.color)
            painter.setPen(self.outline_selected_pen)

        else:
            painter.setBrush(self.selected_color)
            painter.setPen(self.outline_pen)

        painter.drawRoundedRect(window_rect, 5, 5)

    def get_translation(self):
        transform = self.transform()
        size = self.size()
        return QPointF(transform.dx()+(size.width()*0.5), transform.dy()+(size.height()*0.5))


    def set_translation(self, graphPos):
        size = self.size()
        self.setTransform(QTransform.fromTranslate(graphPos.x()-(size.width()*0.5), graphPos.y()-(size.height()*0.5)), False)

    def translate(self, x, y):
        super(Node, self).moveBy(x, y)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            modifiers = event.modifiers()
            if modifiers == Qt.ShiftModifier:
                self.selected = not self.selected
            else:
                self.selected = True
            self.dragging = True
            self.mouse_start = self.mapToScene(event.pos())
            self.mouse_delta = self.mouse_start - self.get_translation()
            self.last_drag_point = self.mouse_start
            self.nodes_moved = False
            self.update()

        else:
            super(Node, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging:
            mouse_down_position = self.mapToScene(event.pos())
            delta = mouse_down_position - self.last_drag_point
            #for node in self.graph.selected_nodes:
            self.translate(delta.x(), delta.y())
            self.last_drag_point = mouse_down_position
            self.nodes_moved = True
        else:
            super(Node, self).mouseMoveEvent(event)


    def mouseReleaseEvent(self, event):
        if self.dragging:
            if self.nodes_moved:
                new_position = self.mapToScene(event.pos())
                delta = new_position - self.mouse_start
            self.setCursor(Qt.ArrowCursor)
            self.dragging = False
        else:
            super(Node, self).mouseReleaseEvent(event)