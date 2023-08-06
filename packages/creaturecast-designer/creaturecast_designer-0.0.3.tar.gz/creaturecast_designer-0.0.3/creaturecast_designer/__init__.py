__version__ = '0.0.3'
__description__ = 'A gui for downloading launching and managing creaturecast tools'
__author__ = 'Paxton Gerrish'
__email__ = 'creaturecastlabs@gmail.com'
__url__ = 'https://github.com/Paxtongerrish/creaturecast_designer.git'

import sys
import creaturecast_designer.extensions
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import creaturecast_designer.stylesheets as sst
import creaturecast_designer.widgets.designer_widget as dwd

def run():

    app = QApplication(sys.argv)
    app.setStyleSheet(sst.get_stylesheet('slate'))
    mainWin = dwd.DesignerWindow()
    mainWin.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()