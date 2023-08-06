import json

from qtpy.QtCore import *
#import py_project.data.projects as ses

import py_maya_core.models.database as dat
import py_maya_core.m_object_factory as mob
import creaturecast_designer.widgets.icon as ico
import creaturecast_designer.models.abstract_models as abm
#import py_project.data.project_objects as pob
#import py_project.data.projects as prj
import py_maya_core.alembic_node as abn
import PySignal as sig
import py_maya_core.python_script_node as psn

class SceneModel(abm.TreeModel):

    error = sig.Signal()

    def __init__(self, *args, **kwargs):
        super(SceneModel, self).__init__(*args, **kwargs)
        self.root.controller.start_parent.connect(self.start_parent_node)
        self.root.controller.end_parent.connect(self.end_parent_node)
        self.root.controller.start_unparent.connect(self.start_unparent_node)
        self.root.controller.end_unparent.connect(self.end_unparent_node)
        self.root.controller.error.connect(self.error.emit)
        self.drag_items = []

    def data(self, index, role):
        item = self.get_item(index)

        if index.column() == 0:

            if role == Qt.DisplayRole or role == Qt.EditRole:
                return item.data['name']

            if role == Qt.DecorationRole:
                return ico.get_icon(item.data.get('icon', 'empty'))

    def start_parent_node(self, child, parent):
        index = self.index_from_item(parent)
        #if not index:
        #    raise Exception('Failed to parent %s to %s. %s was not found in data model' % (child, parent, parent))
        row = len(parent.children)
        self.beginInsertRows(index, row, row)

    def end_parent_node(self, child, parent):
        self.endInsertRows()

    def start_unparent_node(self, parent):
        index = self.index_from_item(parent)
        row = parent.get_index()
        self.beginRemoveRows(index, row, row)

    def end_unparent_node(self, parent):
        self.endRemoveRows()

    #def supportedDragActions(self):
    #    return Qt.DragActions.CopyAction,

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsSelectable

    def mimeTypes(self):
        return [
            'application/py_nodes',
            'application/creaturecast_components',
            'application/python_scripts'
        ]

    def mimeData(self, indexes):
        mimedata = QMimeData()
        items = [self.get_item(x) for x in indexes]
        mimedata.setData(
                'application/py_nodes',
                json.dumps(mob.serialize_nodes(*items))
        )
        self.drag_items = items
        self.dataChanged.emit(indexes[0], indexes[-1])
        return mimedata

    def dropMimeData(self, mimedata, action, row, column, parent_index):

        parent_node = self.get_item(parent_index)

        if mimedata.hasFormat('application/creaturecast_components'):

            data = json.loads(str(mimedata.data('application/creaturecast_components')))
            for component_id in data:
                item = ses.session.query(pob.Component).filter(pob.Component.id == component_id).first()
                print item.extension
                if not item:
                    raise Exception('Unable to find the component specified...')

                elif item.extension == 'abc':
                    abn.AlembicNode(
                        index=0,
                        side=3,
                        root_name=item.name.lower(),
                        parent=parent_node,
                        component=item
                    )

            if mimedata.hasFormat('application/creaturecast_component_versions'):

                data = json.loads(str(mimedata.data('application/creaturecast_component_versions')))
                for component_id in data:
                    item = ses.session.query(pob.Component).filter(pob.Component.id == component_id).first()
                    print item.extension
                    if not item:
                        raise Exception('Unable to find the component specified...')

                if item.extension == 'crg':
                    with open(item.get_path(), mode='r') as f:
                        nodes_data = json.loads(f.read())
                        for x in dat.create_nodes(nodes_data, parent=parent_node):
                            pass

        if mimedata.hasFormat('application/py_nodes'):
            data = json.loads(str(mimedata.data(
                    'application/py_nodes'
            )))
            for x in dat.create_nodes(*data, parent=parent_node):
                pass

        if mimedata.hasFormat('application/python_scripts'):
            data = json.loads(str(mimedata.data(
                    'application/python_scripts'
            )))
            for x in data:
                x['parent'] = parent_node
                new_node = psn.PythonScriptNode(**x)

        #for node in self.drag_items:
        #    node.set_parent(parent_node)

        self.dataChanged.emit(parent_index, parent_index)

        return True


def get_class_from_string(class_string):
    module_string = '.'.join(class_string.split('.')[:-1])
    class_string = class_string.split('.')[-1]
    try:
        module = __import__(module_string, fromlist=['.'])
        return module.__dict__[class_string]
    except:
        module = __import__('py_maya_core.node', fromlist=['.'])
        return module.Node
