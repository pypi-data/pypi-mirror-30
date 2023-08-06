import functools
import sys
from os.path import expanduser
from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

import creaturecast_designer.stylesheets as sst
import creaturecast_designer.widgets.loading_page as lpg
import creaturecast_designer.widgets.side_bar as sbr
import creaturecast_designer.widgets.login_widget as lgn
import creaturecast_designer.widgets.user_widget as uwd
import creaturecast_designer.widgets.user_header as uhd
import creaturecast_designer.widgets.icon as ico
import creaturecast_designer.widgets.connecting_widget as cwd
import creaturecast_designer.widgets.extensions_widget as exw
import creaturecast_designer.environment as env
dock_options = QMainWindow.AnimatedDocks | QMainWindow.AllowNestedDocks | QMainWindow.AllowTabbedDocks | QMainWindow.VerticalTabs
#| QMainWindow.AllowNestedDocks | QMainWindow.AllowTabbedDock

home_directory = expanduser("~").replace('\\', '/')
creaturecast_directory = '%screaturecast' % home_directory
extensions_directory = '%s/extensions' % creaturecast_directory
if extensions_directory not in sys.path:
    sys.path.append(extensions_directory)

class DockAreaWidget(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(DockAreaWidget, self).__init__(*args, **kwargs)


class DockStackWidget(QWidget):

    def __init__(self, *args, **kwargs):
        super(DockStackWidget, self).__init__(*args, **kwargs)
        self.user_widget = uwd.UserWidget(self)
        self.dock_area_widget = DockAreaWidget(self)
        self.extensions_widget = exw.ExtensionsWidget(self)

        self.dock_area_widget.setWindowFlags(Qt.Widget)
        self.stacked_layout = QStackedLayout(self)
        self.stacked_layout.addWidget(self.user_widget)
        self.stacked_layout.addWidget(self.dock_area_widget)
        self.stacked_layout.addWidget(self.extensions_widget)

        env.user_handler.user_changed.connect(self.set_user)

    def set_user(self, user_data):
        self.stacked_layout.setCurrentIndex(0)


class DesignerWidget(QWidget):

    item_font = QFont('', 12, False)

    def __init__(self, *args, **kwargs):
        super(DesignerWidget, self).__init__(*args, **kwargs)
        self.side_bar = sbr.SidebarWidget(self)
        self.dock_stack_widget = DockStackWidget(self)
        self.extensions_button = QPushButton(ico.get_icon('extensions'), 'Extensions', parent=self)
        self.extensions_button.setIconSize(QSize(25, 25))
        self.extensions_button.setFlat(True)
        self.settings_button = QPushButton(ico.get_icon('tool'), 'Settings', parent=self)
        self.settings_button.setIconSize(QSize(25, 25))
        self.settings_button.setFlat(True)
        #self.extensions_button.set_image(med.get_icon_path('extensions'))
        self.user_header = uhd.UserHeader(self)
        self.user_header.setMaximumWidth(215)
        self.user_header.setMinimumWidth(215)
        self.main_layout = QVBoxLayout(self)
        self.tools_layout = QHBoxLayout(self)
        self.body_layout = QHBoxLayout(self)
        self.side_bar_layout = QVBoxLayout(self)

        self.main_layout.addLayout(self.body_layout)
        self.main_layout.addLayout(self.tools_layout)
        self.tools_layout.addStretch()
        self.tools_layout.addWidget(self.extensions_button)
        self.tools_layout.addWidget(self.settings_button)
        self.tools_layout.addSpacerItem(QSpacerItem(32, 32))
        self.tools_layout.addStretch()
        self.body_layout.addLayout(self.side_bar_layout)
        self.side_bar_layout.addWidget(self.user_header)
        self.side_bar_layout.addWidget(self.side_bar)
        self.body_layout.addWidget(self.dock_stack_widget)

        self.side_bar.item_selection.connect(self.setup_widgets)
        self.user_header.clicked.connect(functools.partial(self.dock_stack_widget.stacked_layout.setCurrentIndex, 0))
        self.extensions_button.clicked.connect(self.show_extensions_widget)

        self.dock_widgets = []

        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)
        self.tools_layout.setContentsMargins(0,0,0,0)
        self.tools_layout.setSpacing(0)
        self.body_layout.setContentsMargins(0,0,0,0)
        self.body_layout.setSpacing(0)

    def show_extensions_widget(self):
        self.dock_stack_widget.stacked_layout.setCurrentIndex(2)
        self.dock_stack_widget.extensions_widget.get_tools()


    def setup_widgets(self, items):

        for dock_widget in self.dock_widgets:
            dock_widget.setVisible(False)
        if items:
            self.dock_stack_widget.stacked_layout.setCurrentIndex(1)

        for item in items:
            if item.get('dock_widget', None):
                item['dock_widget'].setVisible(True)
            else:
                dock_area_widget = self.dock_stack_widget.dock_area_widget
                loading_page = lpg.LoadingPage(self)
                dock_widget = PaintedDock(item['name'], dock_area_widget)
                dock_widget.setWidget(loading_page)
                dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
                dock_widget.setFont(self.item_font)
                dock_area_widget.addDockWidget(Qt.RightDockWidgetArea, dock_widget, Qt.Horizontal)
                item['dock_widget'] = dock_widget

                QApplication.processEvents()

                module_string = '.'.join(item['class_location'].split('.')[0:-1])
                class_string = item['class_location'].split('.')[-1]

                ''''
                if not 'C:/Users/User/creaturecast/modules' in sys.path:
                    raise Exception('No Sys path')
                import os
                if not os.path.exists('C:/Users/User/creaturecast/modules'):
                    raise Exception('No Modules path')
                if not module_string.split('.')[0] in os.listdir('C:/Users/User/creaturecast/modules'):
                    print 'No Module', module_string
                if not os.path.exists('%s/%s/__init__.py' %('C:/Users/User/creaturecast/modules', module_string.split('.')[0])):
                    print 'No __innit__ ', '%s/%s/__init__.py' %('C:/Users/User/creaturecast/modules', module_string.split('.')[0])

                print module_string
                '''
                module = __import__(module_string, fromlist=['.'])

                widget = module.__dict__[class_string](self)

                dock_widget.setWidget(widget)
                self.dock_widgets.append(dock_widget)

                if hasattr(widget, 'nodes_selected'):
                    if isinstance(widget.nodes_selected, Signal):
                        widget.nodes_selected.connect(self.nodes_selected.emit)

                if hasattr(widget, 'add_nodes'):
                    self.nodes_selected.connect(widget.add_nodes)



class DesignerStackWidget(QWidget):

    def __init__(self, *args, **kwargs):
        super(DesignerStackWidget, self).__init__(*args, **kwargs)

        self.login_widget = lgn.LoginWidget(self)
        self.designer_widget = DesignerWidget(self)
        self.connecting_widget = cwd.ConnectingWidget(self)
        self.stacked_layout = QStackedLayout(self)

        self.stacked_layout.addWidget(self.login_widget)
        self.stacked_layout.addWidget(self.designer_widget)
        self.stacked_layout.addWidget(self.connecting_widget)

        self.login_widget.start_login.connect(self.start_login)
        env.user_handler.user_changed.connect(self.set_user)
        self.designer_widget.dock_stack_widget.user_widget.log_out.connect(self.logged_out)
        self.connecting_widget.canceled.connect(self.logged_out)

    def start_login(self, *args, **kwargs):
        self.stacked_layout.setCurrentIndex(2)
        self.connecting_widget.start_animation()

    def logged_out(self, *args, **kwargs):
        self.stacked_layout.setCurrentIndex(0)

    def set_user(self, user_data):
        self.stacked_layout.setCurrentIndex(1)



class DesignerWindow(QMainWindow):
    item_font = QFont('', 12, False)
    nodes_selected = Signal(list)

    def __init__(self, *args, **kwargs):
        super(DesignerWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle('Creaturecast Designer')
        self.central_widget = DesignerStackWidget(self)
        self.setCentralWidget(self.central_widget)
        self.setProperty('stylesheet_preset', 'main_window')





class ToolButton(QLabel):

    clicked = Signal()

    def __init__(self, *args, **kwargs):
        super(ToolButton, self).__init__(*args, **kwargs)
        self.image_size = QSize(32, 32)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    def mousePressEvent(self, event):
        self.clicked.emit()

    def set_image_size(self, size):
        self.image_size = size

    def sizeHint(self, *args, **kwargs):
        return self.image_size

    def set_image(self, path):
        height = self.image_size.height()
        width = self.image_size.width()

        user_image = QImage(path)

        user_image = user_image.scaled(
            height,
            width,
            Qt.IgnoreAspectRatio,
            Qt.SmoothTransformation
        )

        user_pixmap = QPixmap.fromImage(user_image)

        self.setPixmap(user_pixmap)




class PaintedDock(QDockWidget):
    def __init__(self, *args, **kwargs):
        super(PaintedDock, self).__init__(*args, **kwargs)



'''
class DesignerWidget(QWidget):
    item_font = QFont('', 12, False)
    nodes_selected = Signal(list)

    def __init__(self, *args, **kwargs):
        super(DesignerWidget, self).__init__(*args, **kwargs)

        #Create Widgets


        #Create Layouts

        self.stacked_layout = QStackedLayout(self)
        self.horizontal_layout = QHBoxLayout()

        #Connect Layouts

        self.stacked_layout.addWidget(self.log_in_widget)
        self.stacked_layout.ad(self.)
        self.horizontal_layout.addWidget(self.side_bar)
        self.horizontal_layout.addWidget(self.stacked_widget)
        #self.main_stack_layout.addWidget(self.dock_area_widget)

        #Signals
        self.log_in_widget.logged_in.connect(self.set_user)
        self.user_widget.log_out.connect(self.logged_out)
        #self.side_bar.item_selection.connect(self.setup_widgets)

        self.dock_widgets = []


        self.stacked_layout_2 = QStackedLayout(self.stacked_widget)

        self.dock_layout = QHBoxLayout(self.dock_area)
        self.dock_layout.addWidget(self.dock_central_widget)


        #Connect Layouts

        self.stacked_layout.addWidget(self.main_widget)
        self.stacked_layout.addWidget(self.log_in_widget)
        self.stacked_layout.setCurrentIndex(1)
        self.horizontal_layout.addWidget(self.side_bar)
        self.horizontal_layout.addWidget(self.stacked_widget)
        self.stacked_layout_2.addWidget(self.user_widget)
        self.stacked_layout_2.addWidget(self.dock_area)



        #Set Properties
        self.setCentralWidget(self.central_widget)


        self.setContentsMargins(0, 0, 0, 0)
        self.horizontal_layout.setContentsMargins(0, 0, 0, 0)
        self.horizontal_layout.setContentsMargins(0, 0, 0, 0)
        self.stacked_layout.setContentsMargins(5, 10, 0, 5)
        self.dock_widgets = []

        #Signals
        self.side_bar.log_out.connect(self.logged_out)


    def set_user(self, user_data):
        self.stacked_layout.setCurrentIndex(1)
        self.main_stack_layout.setCurrentIndex(0)

        self.side_bar.user_widget.set_user(user_data)
        self.side_bar.load_tools(user_data)
        self.user_widget.set_user(user_data)


    def logged_out(self, *args, **kwargs):
        self.stacked_layout.setCurrentIndex(0)



    def setup_widgets(self, items):

        for dock_widget in self.dock_widgets:
            dock_widget.setVisible(False)
        if items:
            self.main_stack_layout.setCurrentIndex(1)

        for item in items:
            if item.get('dock_widget', None):
                item['dock_widget'].setVisible(True)
            else:
                loading_page = lpg.LoadingPage(self)
                dock_widget = PaintedDock(item['name'], self.dock_area_widget)
                dock_widget.setWidget(loading_page)
                dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
                dock_widget.setFont(self.item_font)
                self.dock_area_widget.addDockWidget(Qt.RightDockWidgetArea, dock_widget, Qt.Horizontal)
                item['dock_widget'] = dock_widget

                QApplication.processEvents()

                module_string = '.'.join(item['class_location'].split('.')[0:-1])
                class_string = item['class_location'].split('.')[-1]

                if not 'C:/Users/User/creaturecast/modules' in sys.path:
                    raise Exception('No Sys path')
                import os
                if not os.path.exists('C:/Users/User/creaturecast/modules'):
                    raise Exception('No Modules path')
                if not module_string.split('.')[0] in os.listdir('C:/Users/User/creaturecast/modules'):
                    print 'No Module', module_string
                if not os.path.exists('%s/%s/__init__.py' %('C:/Users/User/creaturecast/modules', module_string.split('.')[0])):
                    print 'No __innit__ ', '%s/%s/__init__.py' %('C:/Users/User/creaturecast/modules', module_string.split('.')[0])

                print module_string

                print 'Importing %s...' % class_string, module_string
                module = __import__(module_string, fromlist=['.'])
                print 'Instanciating %s.%s.' % (module_string, class_string)

                widget = module.__dict__[class_string](self)
                print 'Dockingating %s...' % class_string

                dock_widget.setWidget(widget)
                self.dock_widgets.append(dock_widget)


                if hasattr(widget, 'nodes_selected'):
                    if isinstance(widget.nodes_selected, Signal):
                        widget.nodes_selected.connect(self.nodes_selected.emit)

                if hasattr(widget, 'add_nodes'):
                    self.nodes_selected.connect(widget.add_nodes)

                if hasattr(widget, 'go_to_tool'):
                    if isinstance(widget.go_to_tool, Signal):
                        widget.go_to_tool.connect(self.go_to_tool)

                if hasattr(widget, 'new_tool'):
                    if isinstance(widget.new_tool, Signal):
                        widget.new_tool.connect(self.side_bar.build_model)

                if hasattr(widget, 'delete_tool'):
                    if isinstance(widget.delete_tool, Signal):
                        widget.delete_tool.connect(self.side_bar.build_model)

    def go_to_tool(self, table_item):
        model = self.side_bar.list_view.model()
        for row, item in enumerate(model.items):
            if item.class_location == table_item.class_location:
                index = model.index(row, 0, QModelIndex())
                self.side_bar.list_view.clearSelection()
                self.side_bar.list_view.selectionModel().select(index, QItemSelectionModel.Select)
'''

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    app.setStyleSheet(sst.get_stylesheet('slate'))
    mainWin = DesignerWindow()
    mainWin.show()
    sys.exit(app.exec_())
