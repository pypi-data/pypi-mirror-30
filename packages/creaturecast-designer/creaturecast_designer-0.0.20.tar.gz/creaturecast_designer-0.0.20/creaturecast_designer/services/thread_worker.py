import collections
from qtpy.QtCore import *


class GeneratorWorker(QObject):

    start = Signal()
    data = Signal(object)
    failed = Signal()
    success = Signal()
    end = Signal()

    def __init__(self, generator, *args, **kwargs):
        super(GeneratorWorker, self).__init__()
        self.generator = generator
        self.args = args
        self.kwargs = kwargs

    @Slot()
    def run(self):
        for x in self.generator(*self.args, **self.kwargs):
            self.data.emit(x)
            self.success.emit()


class FunctionWorker(QObject):

    start = Signal()
    data = Signal(object)
    failed = Signal()
    success = Signal()
    end = Signal()

    def __init__(self, worker_function, *args, **kwargs):
        super(FunctionWorker, self).__init__()
        self.worker_function = worker_function
        self.args = args
        self.kwargs = kwargs

    @Slot()
    def run(self):
        return_value = self.worker_function(*self.args, **self.kwargs)
        self.data.emit(return_value)
        self.success.emit()
        self.end.emit()

