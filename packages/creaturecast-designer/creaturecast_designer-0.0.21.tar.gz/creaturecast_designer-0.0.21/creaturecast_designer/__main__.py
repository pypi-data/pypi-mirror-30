import sys
import widgets.designer_widget as dwd
from qtpy.QtWidgets import QApplication
import services.get_stylesheet as stl

app = QApplication(sys.argv)
app.setStyleSheet(stl.get_stylesheet('slate'))
mainWin = dwd.DesignerWindow()
mainWin.show()
sys.exit(app.exec_())