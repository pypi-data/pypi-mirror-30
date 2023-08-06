import json

from qtpy.QtCore import *

import creaturecast_designer.models.abstract_models as abm
import py_maya_core.utilities as mut
import py_maya_core.models.data_models as dmd
import py_maya_core.models.session as ses


class NodeLibraryModel(abm.TableModel):

    error = Signal()

    def __init__(self, *args, **kwargs):

        super(NodeLibraryModel, self).__init__(*args, **kwargs)


    def mimeTypes(self):
        return ['application/py_nodes']

    def mimeData(self, indexes):
        mimedata = QMimeData()
        nodes = [self.get_item(x) for x in indexes]
        mimedata.setData(
                'application/py_nodes',
                json.dumps(mut.serialize_nodes(*nodes))
        )
        self.drag_items = nodes
        self.dataChanged.emit(indexes[0], indexes[-1])
        return mimedata

    def dropMimeData(self, mimedata, action, row, column, parent_index):
        print 'foo'
        if mimedata.hasFormat('application/py_nodes'):
            mime_data = json.loads(str(mimedata.data('application/py_nodes')))
            for x in mime_data:
                tool = dmd.DatabaseTool(**x)
                print row, column
                self._data[row][column] = tool
                ses.session.add(tool)
            ses.session.commit()

        self.dataChanged.emit(parent_index, parent_index)

        return True
