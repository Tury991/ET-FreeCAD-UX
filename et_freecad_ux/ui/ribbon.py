"""Small session-only renderer; Qt is the facade supplied by the host."""


class RibbonController:
    def __init__(self, gui, groups, on_disable):
        self.gui, self.groups, self.on_disable = gui, groups, on_disable
        self.bar = None
        self.saved_sizes = []
        self.close_filter = None
        self.activation_timer = None

    def schedule(self, callback):
        """Run after FreeCAD has restored the newly activated workbench bars."""
        from PySide import QtCore
        self.cancel_pending()
        self.watch_close(QtCore)
        timer = QtCore.QTimer(self.gui.getMainWindow())
        self.activation_timer = timer
        timer.setSingleShot(True)

        def ready():
            self.cancel_pending()
            if self.gui.activeWorkbench().name() == 'ETUXWorkbench':
                callback()

        timer.timeout.connect(ready)
        timer.start(0)

    def cancel_pending(self):
        timer, self.activation_timer = self.activation_timer, None
        if timer is not None:
            timer.stop()
            timer.deleteLater()

    def watch_close(self, core):
        if self.close_filter is not None:
            return
        controller = self

        class CloseFilter(core.QObject):
            def eventFilter(self, obj, event):
                if event.type() == core.QEvent.Close:
                    controller.deactivate()
                return False

        window = self.gui.getMainWindow()
        self.close_filter = CloseFilter(window)
        window.installEventFilter(self.close_filter)

    def activate(self):
        if self.bar is not None:
            return
        from PySide import QtCore, QtWidgets
        from et_freecad_ux.adapters.ribbon import resolve_toolbar_actions
        window = self.gui.getMainWindow()
        resolved = resolve_toolbar_actions(window, self.groups, QtWidgets)
        if window.findChildren(QtWidgets.QToolBar, 'ETUX_RibbonPrototype'):
            raise RuntimeError('Ribbon ET UX già presente')
        bar = QtWidgets.QToolBar('ET UX Ribbon sperimentale', window)
        self.bar = bar
        try:
            bar.setObjectName('ETUX_RibbonPrototype')
            bar.setMovable(False)
            bar.setFloatable(False)
            container = QtWidgets.QWidget(bar)
            outer = QtWidgets.QVBoxLayout(container)
            outer.setContentsMargins(2, 2, 2, 2)
            tabs = QtWidgets.QTabWidget(container)
            tabs.setObjectName('ETUX_RibbonTabs')
            tabs.setDocumentMode(True)
            for label, actions, native_bar in resolved:
                scroll = QtWidgets.QScrollArea(tabs)
                scroll.setWidgetResizable(True)
                scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
                scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
                page = QtWidgets.QWidget(scroll)
                grid = QtWidgets.QGridLayout(page)
                grid.setContentsMargins(4, 2, 4, 2)
                grid.setSpacing(2)
                for index, (command, action) in enumerate(actions):
                    button = QtWidgets.QToolButton(page)
                    button.setObjectName('ETUX_Ribbon_' + command)
                    button.setDefaultAction(action)
                    button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
                    button.setIconSize(QtCore.QSize(20, 20))
                    grid.addWidget(button, index % 2, index // 2)
                grid.setColumnStretch((len(actions) + 1) // 2, 1)
                scroll.setWidget(page)
                tabs.addTab(scroll, label)
            restore = QtWidgets.QToolButton(tabs)
            restore.setText('Toolbar standard')
            restore.setToolTip('Disattiva il prototipo e ripristina le toolbar ET UX')
            restore.clicked.connect(self.on_disable)
            tabs.setCornerWidget(restore)
            outer.addWidget(tabs)
            container.setMinimumWidth(180)
            container.setFixedHeight(116)
            container.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
            bar.addWidget(container)
            window.addToolBar(QtCore.Qt.TopToolBarArea, bar)
            # Keep native visibility flags intact: FreeCAD caches them on switch.
            # Collapse only our own bars, leaving other workbenches untouched.
            for _, _, native_bar in resolved:
                self.saved_sizes.append((native_bar, native_bar.minimumSize(), native_bar.maximumSize()))
                native_bar.setMinimumSize(0, 0)
                native_bar.setMaximumSize(0, 0)
            bar.show()
            self.watch_close(QtCore)
        except Exception:
            self.deactivate()
            raise

    def deactivate(self):
        self.cancel_pending()
        if self.close_filter is not None:
            close_filter, self.close_filter = self.close_filter, None
            try:
                self.gui.getMainWindow().removeEventFilter(close_filter)
                close_filter.deleteLater()
            except RuntimeError:
                pass
        bar, self.bar = self.bar, None
        for native_bar, minimum, maximum in self.saved_sizes:
            try:
                native_bar.setMinimumSize(minimum)
                native_bar.setMaximumSize(maximum)
            except RuntimeError:
                pass  # Host may already have destroyed widgets during shutdown.
        self.saved_sizes = []
        if bar is not None:
            try:
                bar.hide()
                self.gui.getMainWindow().removeToolBar(bar)
                bar.setParent(None)
                bar.deleteLater()
            except RuntimeError:
                pass
