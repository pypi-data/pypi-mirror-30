import sys
import widgets.scene_graph_widget as swd
from qtpy.QtWidgets import QApplication
import creaturecast_scenegraph.services.get_stylesheet as stl

app = QApplication(sys.argv)
app.setStyleSheet(stl.get_stylesheet('slate'))
mainWin = swd.SceneGraphWidget()
mainWin.show()
sys.exit(app.exec_())