__version__ = '0.0.20'
__description__ = 'A gui for downloading launching and managing creaturecast tools'
__author__ = 'Paxton Gerrish'
__email__ = 'creaturecastlabs@gmail.com'
__url__ = 'https://github.com/Paxtongerrish/creaturecast_designer.git'



def run():
    import sys
    import widgets.designer_widget as dwd
    from qtpy.QtWidgets import QApplication
    import services.get_stylesheet as stl
    app = QApplication(sys.argv)
    app.setStyleSheet(stl.get_stylesheet('slate'))
    mainWin = dwd.DesignerWindow()
    mainWin.show()
    sys.exit(app.exec_())
