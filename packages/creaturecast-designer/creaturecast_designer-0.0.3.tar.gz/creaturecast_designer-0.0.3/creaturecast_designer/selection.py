from creaturecast_designer.extensions import PySignal

class NodeSelecton(object):

    selection_changed = PySignal.ClassSignal()

    def __init__(self):
        super(NodeSelecton, self).__init__()
        self.selected_items = []

    def select_nodes(self, *args):
        self.selected_items = list(args)
        self.selection_changed.emit(self.selected_items)

node_selection = NodeSelecton()

