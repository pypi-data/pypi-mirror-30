import os
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

import creaturecast_designer.widgets.progress_indicator as prg
import creaturecast_designer.widgets.pixmap_label as pxl

class ConnectingWidget(QFrame):

    canceled = Signal()
    logged_in = Signal(object)
    font = QFont('', 9, False)
    button_font = QFont('', 12, False)

    def __init__(self, *args, **kwargs):
        super(ConnectingWidget, self).__init__(*args, **kwargs)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.creaturecast_label = pxl.PixmapLabel('/images/Creaturecast.png', self)
        self.creaturecast_label.setAlignment(Qt.AlignCenter)
        self.creaturecast_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.text_label = QLabel('Waiting for web login...', self)
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setFont(self.font)
        self.cancel_button = QPushButton('Cancel', self)
        self.cancel_button.setFont(self.button_font)
        self.busy_widget = BusyWidget(self)


        self.vertical_layout = QVBoxLayout(self)
        self.horizontal_layout = QHBoxLayout()
        self.button_layout = QVBoxLayout()
        self.cancel_layout = QHBoxLayout()
        self.busy_layout = QHBoxLayout()

        self.busy_layout.addStretch()
        self.busy_layout.addWidget(self.busy_widget)
        self.busy_layout.addStretch()

        self.vertical_layout.addLayout(self.horizontal_layout)

        self.horizontal_layout.addLayout(self.button_layout)
        self.button_layout.addStretch()

        self.button_layout.addWidget(self.creaturecast_label)

        self.button_layout.addSpacerItem(QSpacerItem(20, 20))
        self.button_layout.addLayout(self.busy_layout)
        self.button_layout.addWidget(self.text_label)




        self.button_layout.addSpacerItem(QSpacerItem(20, 20))

        self.button_layout.addLayout(self.cancel_layout)

        self.cancel_layout.addStretch()
        self.cancel_layout.addWidget(self.cancel_button)
        self.cancel_layout.addStretch()
        self.button_layout.addStretch()
        self.button_layout.addStretch()

        self.cancel_button.pressed.connect(self.canceled.emit)

    def start_animation(self):
        self.busy_widget.startAnimation()




class BusyWidget(QWidget):

    def __init__(self, *args, **kwargs):
        super(BusyWidget, self).__init__(*args, **kwargs)

        # Initialize Qt Properties
        self.setProperties()

        # Intialize instance variables
        self.circumference = 64
        self.m_angle = 0
        self.m_timerId = -1
        self.m_delay = 40
        self.m_displayedWhenStopped = False
        self.m_color = Qt.white

        # Set size and focus policy
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFocusPolicy(Qt.NoFocus)

        # Show the widget

    def animationDelay(self):
        return self.delay

    def isAnimated(self):
        return (self.m_timerId != -1)

    def isDisplayedWhenStopped(self):
        return self.displayedWhenStopped

    def getColor(self):
        return self.color

    def sizeHint(self):
        return QSize(self.circumference, self.circumference)

    def startAnimation(self):
        self.m_angle = 0

        if self.m_timerId == -1:
            self.m_timerId = self.startTimer(self.m_delay)

    def stopAnimation(self):
        if self.m_timerId != -1:
            self.killTimer(self.m_timerId)

        self.m_timerId = -1
        self.update()

    def setAnimationDelay(self, delay):
        if self.m_timerId != -1:
            self.killTimer(self.m_timerId)

        self.m_delay = delay

        if self.m_timerId != -1:
            self.m_timerId = self.startTimer(self.m_delay)

    def setDisplayedWhenStopped(self, state):
        self.displayedWhenStopped = state
        self.update()

    def setColor(self, color):
        self.m_color = color
        self.update()

    def timerEvent(self, event):
        self.m_angle = (self.m_angle + 30) % 360
        self.update()

    def paintEvent(self, event):
        if (not self.m_displayedWhenStopped) and (not self.isAnimated()):
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        outerRadius = self.circumference * 0.49
        innerRadius = self.circumference * 0.175

        capsuleHeight = outerRadius - innerRadius
        capsuleWidth = capsuleHeight * .25
        capsuleRadius = capsuleWidth / 2

        painter.setBrush(self.m_color)
        for i in range(0, 12):
            color = QColor(self.m_color)

            if self.isAnimated():
                color.setAlphaF(1.0 - (i / 12.0))
            else:
                color.setAlphaF(0.2)

            painter.setPen(Qt.NoPen)
            painter.setBrush(color)
            painter.save()
            center = self.rect().center()
            center.setY(float(center.y()))
            painter.translate(center)
            painter.rotate(self.m_angle - (i * 30.0))
            painter.drawRoundedRect(capsuleWidth * -0.5, (innerRadius + capsuleHeight) * -1, capsuleWidth,
                                    capsuleHeight, capsuleRadius, capsuleRadius)
            painter.restore()

    def setProperties(self):
        self.delay = Property(int, self.animationDelay, self.setAnimationDelay)
        self.displayedWhenStopped = Property(bool, self.isDisplayedWhenStopped, self.setDisplayedWhenStopped)
        self.color = Property(QColor, self.getColor, self.setColor)