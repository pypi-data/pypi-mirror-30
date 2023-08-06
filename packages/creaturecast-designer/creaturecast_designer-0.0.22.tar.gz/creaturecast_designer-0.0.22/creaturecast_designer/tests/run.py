import sys
import creaturecast_designer.widgets.designer_widget as dwd
from qtpy.QtWidgets import QApplication
import creaturecast_designer.services.get_stylesheet as stl

app = QApplication(sys.argv)
app.setStyleSheet(stl.get_stylesheet('slate'))
mainWin = dwd.DesignerWindow()
mainWin.show()
sys.exit(app.exec_())