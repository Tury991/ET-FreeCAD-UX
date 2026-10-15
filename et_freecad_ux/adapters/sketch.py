"""Owned public GUI observer for a temporary native Sketcher handoff.

Only document/object names are retained. No model, task or preference writes.
Qt and FreeCAD are injected/lazily imported from the host.
"""


class SketchRibbonSession:
    def __init__(self, gui, ribbon):
        self.gui, self.ribbon = gui, ribbon
        self.window = gui.getMainWindow()
        self.name = 'ETUXWorkbench'
        self.departing = False
        self.edit = None
        self.previous_tab = None
        self.timer = None
        self.observing = self.connected = False

    def start(self):
        try:
            self.gui.addDocumentObserver(self)
            self.observing = True
            self.window.workbenchActivated.connect(self.workbench_changed)
            self.connected = True
            document = self.gui.activeDocument()
            editing = document.getInEdit() if document else None
            if editing is not None:
                self.slotInEdit(editing)
        except Exception:
            self.stop()
            raise

    def stop(self):
        self.cancel_pending()
        if self.connected:
            self.connected = False
            self.window.workbenchActivated.disconnect(self.workbench_changed)
        if self.observing:
            self.observing = False
            self.gui.removeDocumentObserver(self)
        self.edit = self.previous_tab = None
        self.departing = False

    def cancel_pending(self):
        timer, self.timer = self.timer, None
        if timer is not None:
            timer.stop()
            timer.timeout.disconnect(self.apply)
            timer.deleteLater()

    def queue(self):
        from PySide import QtCore
        self.cancel_pending()
        self.timer = QtCore.QTimer(self.window)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.apply)
        self.timer.start(0)

    def departed(self):
        # Native setEdit switches workbench before emitting InEdit. Give that
        # synchronous operation one event-loop turn to identify the handoff.
        self.departing = True
        self.queue()

    def workbench_changed(self, name):
        previous_name, self.name = self.name, name
        if name == 'ETUXWorkbench':
            self.departing = False
            self.queue()
        elif name == 'SketcherWorkbench' and previous_name == 'ETUXWorkbench' and self.edit is None:
            self.departing = True
            self.queue()
        else:
            # Includes a deliberate switch away during editing. Never return
            # or resurrect here; a later explicit ET UX activation owns its UI.
            self.ribbon.deactivate()

    @staticmethod
    def sketch_key(view_provider):
        obj = view_provider.Object
        if obj.isDerivedFrom('Sketcher::SketchObject'):
            return obj.Document.Name, obj.Name
        return None

    def slotInEdit(self, view_provider):
        key = self.sketch_key(view_provider)
        if key and (self.name == 'ETUXWorkbench' or
                    (self.name == 'SketcherWorkbench' and self.departing)):
            self.edit = key
            self.departing = False
            self.previous_tab = self.ribbon.tabs.currentIndex()
            self.queue()

    def slotResetEdit(self, view_provider):
        if self.edit == self.sketch_key(view_provider):
            self.edit = None
            self.departing = False
            self.queue()

    def slotActivateDocument(self, document):
        if self.edit and (document is None or document.Document.Name != self.edit[0]):
            self.ribbon.deactivate()

    def slotDeletedDocument(self, document):
        if self.edit and document.Document.Name == self.edit[0]:
            self.ribbon.deactivate()

    def apply(self):
        self.cancel_pending()
        if not self.observing or self.ribbon.bar is None:
            return
        if self.name == 'SketcherWorkbench':
            document = self.gui.activeDocument()
            editing = document.getInEdit() if document else None
            if not self.edit or editing is None or self.sketch_key(editing) != self.edit:
                self.ribbon.deactivate()
                return
        elif self.name != 'ETUXWorkbench':
            self.ribbon.deactivate()
            return
        if self.edit and self.name == 'SketcherWorkbench':
            self.ribbon.show_for_sketch()
        else:
            self.ribbon.bar.show()
        tabs = self.ribbon.tabs
        if self.edit:
            for index in range(tabs.count()):
                if tabs.tabText(index) == 'Sketch':
                    tabs.setCurrentIndex(index)
                    break
        elif self.previous_tab is not None:
            tabs.setCurrentIndex(self.previous_tab)
            self.previous_tab = None
