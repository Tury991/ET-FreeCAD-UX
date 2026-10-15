"""Optional modern Ribbon; Qt is the facade supplied by the host."""


class RibbonController:
    def __init__(self, gui, groups, on_disable, mode="classic", on_mode=None):
        self.gui, self.groups, self.on_disable = gui, groups, on_disable
        self.mode, self.on_mode = mode, on_mode
        self.buttons, self.pages, self.mode_actions = [], [], []
        self.container = self.tabs = None
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
                elif event.type() in (core.QEvent.PaletteChange, core.QEvent.ApplicationPaletteChange,
                                       core.QEvent.FontChange, core.QEvent.StyleChange):
                    controller.sync_host_style()
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
            self.container, self.tabs = container, tabs
            tabs.setUsesScrollButtons(True)
            # Styling is confined to this ET UX subtree. Palette roles follow
            # host light/dark/high-contrast themes, including disabled controls.
            container.setObjectName('ETUX_RibbonSurface')
            from et_freecad_ux.core.ribbon import ribbon_sections, DENSITIES
            action_map = {command: action for _, actions, _ in resolved for command, action in actions}
            class RibbonButton(QtWidgets.QToolButton):
                def focusInEvent(self, event):
                    super().focusInEvent(event)
                    parent = self.parentWidget()
                    while parent is not None and not isinstance(parent, QtWidgets.QScrollArea):
                        parent = parent.parentWidget()
                    if parent is not None:
                        parent.ensureWidgetVisible(self)

            for label, sections in ribbon_sections(action_map):
                scroll = QtWidgets.QScrollArea(tabs)
                scroll.setWidgetResizable(True)
                scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
                scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
                page = QtWidgets.QWidget(scroll)
                row = QtWidgets.QHBoxLayout(page)
                row.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
                for title, actions, primary in sections:
                    if not actions:
                        continue
                    section = QtWidgets.QFrame(page)
                    section.setProperty('etuxSection', True)
                    section.setObjectName('ETUX_Section_' + title)
                    column = QtWidgets.QVBoxLayout(section)
                    commands = QtWidgets.QGridLayout()
                    for index, (command, action) in enumerate(actions):
                        button = RibbonButton(section)
                        button.setObjectName('ETUX_Ribbon_' + command)
                        button.setDefaultAction(action)
                        button.setFocusPolicy(QtCore.Qt.StrongFocus)
                        button.setAccessibleName(action.text().replace('&', ''))
                        button.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
                        button.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon if primary
                                                  else QtCore.Qt.ToolButtonTextBesideIcon)
                        commands.addWidget(button, 0 if primary else index % 2,
                                           index if primary else index // 2)
                        self.buttons.append((button, primary))
                    column.addLayout(commands)
                    column.addStretch()
                    caption = QtWidgets.QLabel(title, section)
                    caption.setAlignment(QtCore.Qt.AlignHCenter)
                    column.addWidget(caption)
                    row.addWidget(section)
                row.addStretch()
                scroll.setWidget(page)
                tabs.addTab(scroll, label)
                self.pages.append(page)
            options = QtWidgets.QToolButton(tabs)
            options.setText('Ribbon')
            options.setToolTip('Densità ET UX e ritorno alle toolbar standard')
            options.setPopupMode(QtWidgets.QToolButton.InstantPopup)
            options.setFocusPolicy(QtCore.Qt.StrongFocus)
            menu = QtWidgets.QMenu(options)
            for item in DENSITIES:
                action = menu.addAction(item.label)
                action.setCheckable(True)
                action.triggered.connect(lambda checked=False, key=item.key: self.on_mode(key)
                                         if self.on_mode else self.set_density(key))
                self.mode_actions.append((item.key, action))
            menu.addSeparator()
            restore = menu.addAction('Toolbar standard')
            restore.triggered.connect(self.on_disable)
            options.setMenu(menu)
            tabs.setCornerWidget(options)
            outer.addWidget(tabs)
            container.setMinimumWidth(180)
            container.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
            self.sync_host_style()
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

    def sync_host_style(self):
        """FreeCAD toolbars may have an explicit palette: use the window's.

        Only our container receives palette/font writes; the filter belongs to
        this controller and is removed with the Ribbon.
        """
        if self.container is not None:
            window = self.gui.getMainWindow()
            from PySide import QtWidgets
            # Qt scroll/tab viewports and styled children can have explicit
            # palettes/fonts that block normal parent propagation.
            for widget in [self.container] + self.container.findChildren(QtWidgets.QWidget):
                widget.setPalette(window.palette())
                widget.setFont(window.font())
            self.container.setAutoFillBackground(True)
            from PySide import QtGui
            palette = window.palette()
            colors = {
                'surface': palette.color(QtGui.QPalette.Window).name(),
                'text': palette.color(QtGui.QPalette.WindowText).name(),
                'button': palette.color(QtGui.QPalette.Button).name(),
                'button_text': palette.color(QtGui.QPalette.ButtonText).name(),
                'disabled': palette.color(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText).name(),
                'border': palette.color(QtGui.QPalette.Mid).name(),
                'accent': palette.color(QtGui.QPalette.Highlight).name(),
                'selected_text': palette.color(QtGui.QPalette.HighlightedText).name(),
            }
            # Resolve colors again on palette events: Qt stylesheet palettes can
            # otherwise cache the old foreground even after setPalette().
            sheet = """
                QWidget#ETUX_RibbonSurface { background: @surface; color: @text; }
                QWidget#ETUX_RibbonSurface QTabBar::tab {
                    padding: 6px 14px; background: @surface; color: @text;
                    border-bottom: 3px solid transparent; }
                QWidget#ETUX_RibbonSurface QTabBar::tab:selected {
                    font-weight: bold; border-bottom-color: @accent; }
                QWidget#ETUX_RibbonSurface QTabBar:focus { border: 1px dotted @accent; }
                QWidget#ETUX_RibbonSurface QToolButton {
                    padding: 4px; border: 2px solid transparent; border-radius: 4px;
                    color: @button_text; background: transparent; }
                QWidget#ETUX_RibbonSurface QToolButton:disabled { color: @disabled; }
                QWidget#ETUX_RibbonSurface QToolButton:hover:enabled {
                    border-color: @border; background: @button; }
                QWidget#ETUX_RibbonSurface QToolButton:focus { border-color: @accent; }
                QWidget#ETUX_RibbonSurface QLabel { color: @text; }
                QWidget#ETUX_RibbonSurface QFrame[etuxSection="true"] {
                    border-right: 1px solid @border; }
                QWidget#ETUX_RibbonSurface QMenu { color: @text; background: @surface; }
                QWidget#ETUX_RibbonSurface QMenu::item:selected {
                    color: @selected_text; background: @accent; }
            """
            for name, color in sorted(colors.items(), key=lambda item: -len(item[0])):
                sheet = sheet.replace('@' + name, color)
            self.container.setStyleSheet(sheet)
            self.set_density(self.mode)

    def set_density(self, key):
        """Update existing controls: keep actions, current tab, focus and task."""
        from et_freecad_ux.core.ribbon import density
        style = density(key)
        self.mode = style.key
        if self.bar is None:
            return
        from PySide import QtCore, QtWidgets
        for button, primary in self.buttons:
            icon = style.primary_icon if primary else style.secondary_icon
            button.setMinimumSize(0, 0)
            button.setIconSize(QtCore.QSize(icon, icon))
            button.ensurePolished()
            button.setMinimumSize(button.minimumSizeHint().expandedTo(
                QtCore.QSize(0, 44 if primary else 32)))
            button.updateGeometry()
        for page in self.pages:
            page.setMinimumSize(0, 0)
            row = page.layout()
            row.setContentsMargins(style.padding, style.padding, style.padding, style.padding)
            row.setSpacing(style.spacing)
            for section in page.findChildren(QtWidgets.QFrame):
                section.setMinimumSize(0, 0)
                column = section.layout()
                if column is not None:
                    column.setContentsMargins(style.padding, style.padding, style.padding, style.padding)
                    column.setSpacing(style.spacing)
                    column.itemAt(0).layout().setSpacing(style.spacing)
                    column.itemAt(0).layout().invalidate()
                    column.invalidate()
                    column.activate()
            row.invalidate()
            row.activate()
            page.setMinimumSize(row.minimumSize())
        for mode, action in self.mode_actions:
            action.setChecked(mode == self.mode)
        # Include actual translated labels/font metrics and scrollbar thickness;
        # logical Qt units are already scaled by the host. Never cap text height.
        area = max([style.command_height] + [page.minimumHeight() for page in self.pages])
        scrollbar = self.container.style().pixelMetric(QtWidgets.QStyle.PM_ScrollBarExtent)
        self.tabs.setMinimumHeight(0)
        self.container.setMinimumHeight(0)
        self.tabs.setMinimumHeight(area + self.tabs.tabBar().sizeHint().height() + scrollbar + 8)
        self.container.layout().invalidate()
        self.container.setMinimumHeight(self.container.layout().minimumSize().height())
        self.container.updateGeometry()

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
        self.buttons, self.pages, self.mode_actions = [], [], []
        self.container = self.tabs = None
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
