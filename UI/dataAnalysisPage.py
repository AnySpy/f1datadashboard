from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsProxyWidget, QVBoxLayout, QHBoxLayout, QWidget, QFrame, QLabel, QPushButton, QSizePolicy
from PySide6.QtCore import Qt, Signal, QPointF, QSize
from PySide6.QtGui import QPainter
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from graphs.placement_over_time import placement_figure_for_session

# TODO: Add a proper dropdown for graph addition

class DragHeader(QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setFixedHeight(28)
        self.setStyleSheet("background-color: #3a3a3a; color: white;")
        self.setCursor(Qt.CursorShape.SizeAllCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 4, 0)
        layout.addWidget(QLabel(title))
        layout.addStretch()

        self.close_btn = QPushButton("x")
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.setCursor(Qt.CursorShape.ArrowCursor)
        layout.addWidget(self.close_btn)

        self._press_global = None
        self._press_item_pos = None

    def _proxy(self):
        return self.window().graphicsProxyWidget()

    def mousePressEvent(self, event):
        proxy = self._proxy()
        if event.button() == Qt.MouseButton.LeftButton and proxy:
            self._press_global = event.globalPosition()
            self._press_item_pos = proxy.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        proxy = self._proxy()
        if self._press_global is not None and proxy:
            delta = event.globalPosition() - self._press_global
            if self._press_item_pos is not None:
                proxy.setPos(self._press_item_pos + QPointF(delta.x(), delta.y()))
            event.accept()

    def mouseReleaseEvent(self, event):
        self._press_global = None

class ResizeGrip(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(16, 16)
        self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        self.setStyleSheet("background-color: #555;")
        self._press_global = None
        self._press_size = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._press_global = event.globalPosition()
            self._press_size = self.window().size()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._press_global is not None:
            delta = event.globalPosition() - self._press_global
            panel = self.window()
            if self._press_size is not None:
                new_w = max(panel.minimumWidth(), self._press_size.width() + int(delta.x()))
                new_h = max(panel.minimumHeight(), self._press_size.height() + int(delta.y()))
                panel.resize(new_w, new_h)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._press_global = None

class GraphPanel(QFrame):
    close_requested = Signal()

    def __init__(self, title: str, canvas: QWidget, parent=None):
        super().__init__(parent)
        self.setObjectName("graphPanel")
        self.setStyleSheet("#graphPanel { background-color: #1e1e1e; }")
        self.setMinimumSize(300, 200)

        self.header = DragHeader(title)
        self.header.close_btn.clicked.connect(self.close_requested)

        canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        canvas.setMinimumSize(1, 1)  # let the layout shrink it

        grip_row = QHBoxLayout()
        grip_row.setContentsMargins(0, 0, 0, 0)
        grip_row.addStretch()
        grip_row.addWidget(ResizeGrip())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.header)
        layout.addWidget(canvas, 1)
        layout.addLayout(grip_row)

class GraphCanvasView(QGraphicsView):
    def __init__(self, scene: QGraphicsScene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setStyleSheet("background-color: #16161f; border: none;")

class GraphCanvasContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(-2000, -2000, 4000, 4000)
        self.view = GraphCanvasView(self.scene)
        layout.addWidget(self.view)

        self.active_graphs: dict[str, QGraphicsProxyWidget] = {}
        self._z_counter = 0

        fig_object = FigureCanvasQTAgg(placement_figure_for_session(1))
        self.add_graph("Placement over Time", fig_object, 100, 100)

    def add_graph(self, graph_id: str, canvas: QWidget, x: float, y: float,
                  size: QSize = QSize(800, 500)):
        if graph_id in self.active_graphs:
            return

        panel = GraphPanel(graph_id, canvas)
        panel.resize(size)
        panel.close_requested.connect(lambda gid=graph_id: self.remove_graph(gid))

        proxy = QGraphicsProxyWidget()
        proxy.setWidget(panel)
        proxy.setPos(x, y)
        self.scene.addItem(proxy)
        self.active_graphs[graph_id] = proxy
        self._bring_to_front(proxy)

        panel.installEventFilter(self)
        panel.setProperty("proxy_ref", graph_id)

    def eventFilter(self, obj, event):
        from PySide6.QtCore import QEvent
        if event.type() == QEvent.Type.MouseButtonPress:
            gid = obj.property("proxy_ref")
            if gid in self.active_graphs:
                self._bring_to_front(self.active_graphs[gid])
        return super().eventFilter(obj, event)

    def _bring_to_front(self, proxy):
        self._z_counter += 1
        proxy.setZValue(self._z_counter)

    def remove_graph(self, graph_id: str):
        proxy = self.active_graphs.pop(graph_id, None)
        if proxy:
            self.scene.removeItem(proxy)
            proxy.deleteLater()