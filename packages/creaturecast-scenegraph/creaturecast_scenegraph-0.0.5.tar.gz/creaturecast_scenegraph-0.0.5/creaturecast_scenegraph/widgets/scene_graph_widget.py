import code
import pprint
import functools
from qtpy.QtCore import *
from qtpy.QtWidgets import *
from qtpy.QtGui import *


import py_maya_core.m_object_factory as mfy
import py_maya_core.scene_root as rot
import creaturecast_scenegraph.models.scene_model as smd

from creaturecast_scenegraph.widgets.QProgressIndicator import QProgressIndicator

import requests
import json

build_rig_adress = 'http://creaturecast-library.herokuapp.com/add_library_items'
chunk_size = 8192


class SceneGraphWidget(QFrame):

    nodes_selected = Signal(list)

    def __init__(self, *args, **kwargs):
        super(SceneGraphWidget, self).__init__(*args, **kwargs)

        self.view = SceneView(self)

        self.vertical_splitter = SplitterWidget(Qt.Orientation.Vertical, self)
        self.horizontal_splitter = SplitterWidget(Qt.Orientation.Horizontal, self)
        self.vertical_splitter.setSizes([0, 0, 0])
        self.horizontal_splitter.setSizes([0, 0, 0])

        # connect spliters
        self.vertical_splitter.addWidget(self.horizontal_splitter)
        self.horizontal_splitter.addWidget(self.view)
        # create layouts
        self.main_layout = QVBoxLayout(self)
        self.horizontal_layout = QHBoxLayout(self)

        # connect layouts

        self.main_layout.addLayout(self.horizontal_layout)
        self.horizontal_layout.addStretch()
        self.main_layout.addWidget(self.vertical_splitter)
        # set properties
        self.main_layout.setContentsMargins(5, 5, 5, 5)

        self.view.items_selected.connect(self.set_selected_variable)
        self.view.items_selected.connect(self.nodes_selected.emit)


        self.view.setModel(smd.SceneModel(rot.scene_root))


        import py_maya_core.scene_root as srt
        import py_maya.biped.biped as bpd
        biped = bpd.BipedTemplate(parent=srt.scene_root)
        biped.create()


    def set_details_visibility(self, nodes):
        if nodes:
            self.details_button.setChecked(True)
        else:
            self.details_button.setChecked(False)


    def toggle_m_objects(self, value):
        model = self.view.model()
        model.root.is_valid = value
        if value:
            for x in mfy.build_m_objects(*model.root.children):
                pass
        else:
            for x in mfy.unbuild_m_objects(*model.root.children):
                pass

    def set_selected_variable(self, selected_nodes):
        self.update_locals(selected_nodes=selected_nodes)

    def update_locals(self, **kwargs):
        pass
        #self.console.input_console.interpreter.locals.update(kwargs)


def progress(count, *args, **kwargs):
    widget = QProgressDialog(*args+(0, count), **kwargs)
    widget.show()
    c = 0
    for v in range(count):
        QCoreApplication.instance().processEvents()
        if widget.wasCanceled():
            raise StopIteration
        c+=1
        widget.setValue(c)
        yield(v)


class SplitterWidget(QSplitter):

    def __init__(self, *args, **kwargs):
        super(SplitterWidget, self).__init__(*args, **kwargs)
        self.setHandleWidth(8)
        self.setFrameShadow(QFrame.Plain)
        self.setFrameShape(QFrame.NoFrame)
        self.setContentsMargins(0, 0, 0, 0)


class ConsoleWidget(QWidget):
    def __init__(self, *args, **kwargs):
        interpreter = kwargs.pop('interpreter', code.InteractiveConsole())
        super(ConsoleWidget, self).__init__(*args, **kwargs)

        # create widgets
        #self.output_console = OutputConsole()
        #self.input_console = InputConsole(
        #    appname="NodeView Python Terminal",
        #    interpreter=interpreter,
        #    stdout=self.output_console.stdin
        #)
        self.splitter = QSplitter(Qt.Orientation.Vertical, self)
        self.splitter.setSizes([1000, 0])
        # create layouts
        self.top_layout = QVBoxLayout(self)

        # connect layouts
        self.top_layout.addWidget(self.splitter)
        #self.splitter.addWidget(self.input_console)
        #self.splitter.addWidget(self.output_console)

        # set properties
        #self.input_console.setContentsMargins(0, 0, 0, 0)
        #self.output_console.setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)
        self.top_layout.setContentsMargins(0, 0, 0, 0)

        # connect signals
        #self.input_console.CODE_EXECUTED.connect(self.output_console.read_stdin)


class SceneView(QTreeView):
    items_selected = Signal(list)
    item_clicked = Signal(object)

    def __init__(self, *args, **kwargs):
        super(SceneView, self).__init__(*args, **kwargs)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setDropIndicatorShown(True)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.installEventFilter(self)
        self.setIconSize(QSize(25, 25))
        self.setHeaderHidden(True)
        self.setFocusPolicy(Qt.NoFocus)

        self.busy_widget = QProgressIndicator(self)
        self.busy_widget.setAnimationDelay(70)
        self.busy_widget.setVisible(False)



    def setModel(self, model):
        super(SceneView, self).setModel(model)
        if model:
            selectionModel = self.selectionModel()
            selectionModel.selectionChanged.connect(self.emit_selected_items)

    def emit_selected_items(self, *args):
        model = self.model()
        new_selection, old_selection = args

        old_indices = [i for i in self.selectedIndexes() if i.column() == 0]
        new_indices = [i for i in new_selection.indexes() if i.column() == 0]
        print [model.get_item(x) for x in old_indices]
        self.items_selected.emit([model.get_item(x) for x in old_indices])

    def mousePressEvent(self, event):

        index = self.indexAt(event.pos())
        item = self.model().get_item(index)
        if item:
            self.item_clicked.emit(item)

        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.RightButton:

                menu = QMenu(self)


                menu.addAction(
                    "Create Rig",
                    functools.partial(self.create_rig, item)
                )


                menu.exec_(self.mapToGlobal(event.pos()))

        super(SceneView, self).mousePressEvent(event)


    def resizeEvent(self, event):
        size = event.size()
        #size.setHeight(float(size.height()) * 0.5)
        #size.setWidth(float(size.width()) * 0.5)
        self.busy_widget.resize(size)
        event.accept()


    def create_rig(self, data):
        self.setDisabled(True)

        self.busy_widget.startAnimation()
        self.busy_widget.setVisible(True)

        self.worker = CreateRigWorker(build_rig_adress)
        #self.worker.update_progress.connect(self.set_progress)
        self.worker.finished.connect(functools.partial(self.busy_widget.setVisible, False))
        #self.worker.failed.connect(self.reset)
        self.worker.start()

        self.worker.success.connect(self.build_nodes)

    def build_nodes(self, data):

        node_data = json.loads(data)

        if not node_data['success']:
            raise Exception('Server Error.\n%s' % node_data['message'])

        pprint.pprint(node_data['data'])
        self.setDisabled(False)

    @staticmethod
    def create_template(rig):
        template = rig.create_template()
        rig.delete()
        template.set_parent(rot.scene_root)

    '''
    def eventFilter(self, sender, event):
        if (event.type() == QEvent.ChildAdded):
            pass
        if (event.type() == QEvent.ChildRemoved):
            pass
        return False

    def map_index_to_source(self, index):
        if isinstance(self.model(), QSortFilterProxyModel):
            index = self.model().mapToSource(index)
        return index

    def map_index_from_source(self, index):
        if isinstance(self.model(), QSortFilterProxyModel):
            index = self.model().mapFromSource(index)
        return index



    def get_model(self):
        model = self.model()
        while isinstance(model, QSortFilterProxyModel):
            model = model.sourceModel()
        return model

    def error_dialog(self, message):
        QMessageBox.warning(self, 'Error', message)

    '''
    def frame_node(self, index):

        index = self.map_index_from_source(index)
        self.clearSelection()
        self.set_expanded_descendants(QModelIndex(), False)
        self.scrollTo(index)

    def frame_nodes(self, indices):
        #self.clearSelection()
        #self.set_expanded_descendants(QModelIndex(), False)

        for index in indices:
            index = self.map_index_from_source(index)
            self.set_expanded_parents(index, True)
            self.select_item(index)
            self.scrollTo(index)


    def set_expanded_parents(self, index, value):
        index = self.map_index_from_source(index)

        model = self.get_model()
        for i in model.get_ancestors(index):
            self.setExpanded(i, value)

    def set_expanded_descendants(self, index, value):
        index = self.map_index_from_source(index)
        model = self.get_model()
        if model:
            for i in model.get_descendants(index):
                self.setExpanded(i, value)

    def select_item(self, index):
            self.selectionModel().select(
                index,
                QItemSelectionModel.Select |
                QItemSelectionModel.Rows
            )






if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)

    mainWin = SceneGraphWidget()
    mainWin.resize(900, 600)
    mainWin.show()

    sys.exit(app.exec_())
