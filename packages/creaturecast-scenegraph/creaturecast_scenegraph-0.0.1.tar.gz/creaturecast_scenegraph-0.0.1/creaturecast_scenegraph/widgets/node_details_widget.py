from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import creaturecast_designer.media as med


class ValueLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super(ValueLineEdit, self).__init__(*args, **kwargs)

class NodeDetailsWidget(QWidget):

    def __init__(self, *args, **kwargs):
        super(NodeDetailsWidget, self).__init__(*args, **kwargs)
        self.item = None
        self.main_layout = QVBoxLayout(self)
        self.horizontal_layout = QHBoxLayout(self)
        self.header = ProjectHeader(self)
        self.header.show()
        self.form_layout = QFormLayout()
        self.form_layout.setSpacing(5)
        self.form_layout.setLabelAlignment(Qt.AlignRight)
        #self.form_layout.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.main_layout.addWidget(self.header)
        self.main_layout.addLayout(self.horizontal_layout)
        self.main_layout.addStretch()
        self.horizontal_layout.addLayout(self.form_layout)
        self.delete_button = QPushButton('DELETE\nItem', self)
        #self.delete_button.setStyleSheet('border: 1px solid #FF0000;')

        self.main_layout.addWidget(self.delete_button)
        #self.main_layout.setContentsMargins(0, 0, 0, 0)
        #self.horizontal_layout.setContentsMargins(0, 0, 0, 0)


    #def setVisible(self, *args, **kwargs):
    #    super_class_function = super(NodeDetailsWidget, self).setVisible
    #    if self.item:
    #        super_class_function(*args, **kwargs)
    #    else:
    #        super_class_function(False)

    def clear_form(self):
        for i in reversed(range(self.form_layout.count())):
            self.form_layout.itemAt(i).widget().deleteLater()

    def set_item(self, *items):
        item = flatten_nodes(*items)[0]
        self.header.set_node(item)
        keys = item.data.keys()
        self.clear_form()
        self.delete_button.setText('DELETE\n"%s"' % item.data['name'])
        for key in item.__dict__:
            if key not in ['_sa_instance_state', 'data']:
                value = item.__dict__[key]
                #if isinstance(value, basestring):
                widget = ValueLineEdit(self)
                widget.setText(str(value))
                self.form_layout.addRow(key, widget)




class KeyView(QTableView):
    def __init__(self, *args, **kwargs):
        super(KeyView, self).__init__(*args, **kwargs)
        self.verticalHeader().hide()
        self.horizontalHeader().hide()
        self.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
        self.verticalHeader().setResizeMode(QHeaderView.ResizeToContents)
        self.setShowGrid(False)
        #self.setGridSize(5)
        self.horizontalHeader().setStretchLastSection(False)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)


class RaisedFrame(QFrame):
    def __init__(self, *args, **kwargs):
        super(RaisedFrame, self).__init__(*args, **kwargs)
        self.setFrameStyle(QFrame.Panel)
        self.setAutoFillBackground(True)
        #p = self.palette()
        #p.setColor(self.backgroundRole(), QColor(80, 80, 80))
        #self.setPalette(p)
        self.setFrameShadow(QFrame.Raised)



class CloseLabel(QLabel):

    pressed = Signal()

    def __init__(self, *args, **kwargs):
        super(CloseLabel, self).__init__(*args, **kwargs)
        close_image = QImage(med.get_icon_path('close'))
        close_pixmap = QPixmap.fromImage(close_image.scaled(18, 18, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        self.setPixmap(close_pixmap)

    def mousePressEvent(self, event):
        super(CloseLabel, self).mousePressEvent(event)
        self.pressed.emit()

class TightLayoutV(QVBoxLayout):
    def __init__(self, *args, **kwargs):
        super(TightLayoutV, self).__init__(*args, **kwargs)
        self.setSpacing(0)
        #self.setMargin(0)
        self.setContentsMargins(0, 0, 0, 0)

class TightLayoutH(QHBoxLayout):
    def __init__(self, *args, **kwargs):
        super(TightLayoutH, self).__init__(*args, **kwargs)
        self.setSpacing(0)
        #self.setMargin(0)
        self.setContentsMargins(0, 0, 0, 0)


class ProjectHeader(QWidget):

    cancel = Signal()

    def __init__(self, *args, **kwargs):
        super(ProjectHeader, self).__init__(*args, **kwargs)

        #Create Widgets
        self.icon_label = QLabel(self)

        self.icon_size = QSize(64, 64)
        self.name_label = QLabel('', parent=self)
        self.name_label.setVisible(False)

        self.name_font = QFont("arial", 14, True)
        self.name_font.setWeight(45)
        self.name_font.setBold(True)
        self.name_font.setLetterSpacing(QFont.PercentageSpacing, 88)
        self.name_label.setFont(self.name_font)



        #Layouts
        self.h_layout = QHBoxLayout(self)

        self.h_layout.setSpacing(4)

        self.h_layout.setContentsMargins(10, 0, 10, 0)

        self.h_layout.addStretch()
        self.h_layout.addWidget(self.icon_label)
        self.h_layout.addWidget(self.name_label)
        self.h_layout.addStretch()

        #p = self.palette()
        #p.setColor(self.backgroundRole(), QColor(90, 90, 90))
        #self.setPalette(p)
        self.node = None

        #self.cancel_button.pressed.connect(self.cancel.emit)

        self.setMaximumHeight(64)
        self.setMinimumHeight(64)

    def set_node(self, *args):
        args = flatten_nodes(*args)
        node = args[0]
        default_image = QImage(med.get_icon_path(node.data['icon']))
        default_pixmap = QPixmap.fromImage(default_image.scaled(64, 64, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        self.icon_label.setPixmap(default_pixmap)
        self.name_label.setText(node.data.get('pretty_name', node.data['name']))


def flatten_nodes(*args):
    flattened_args = []
    for arg in args:
        if isinstance(arg, (list, tuple, set)):
            flattened_args.extend(flatten_nodes(*[x for x in arg]))
        elif isinstance(arg, dict):
            flattened_args.extend(flatten_nodes(*arg.values()))
        else:
            flattened_args.append(arg)
    return flattened_args
