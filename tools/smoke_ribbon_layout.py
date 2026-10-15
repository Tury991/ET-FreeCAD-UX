"""Real Qt layout checks, called inside the isolated native GUI smoke.

Synthetic light/dark palettes, not a certification of FreeCAD themes or Windows.
Optional ETUX_SCREENSHOT_DIR captures actual offscreen Ribbon widgets only.
"""
from pathlib import Path
import os
import sys


def contrast(first, second):
    def luminance(color):
        values = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        values = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in values]
        return sum(v * weight for v, weight in zip(values, (0.2126, 0.7152, 0.0722)))
    a, b = sorted((luminance(first), luminance(second)))
    return (b + 0.05) / (a + 0.05)


def run(wb, gui):
    from PySide import QtCore, QtGui, QtWidgets
    from et_freecad_ux.core.ribbon import SECTIONS
    from et_freecad_ux.adapters.ribbon import read_density
    import FreeCAD as App
    window = gui.getMainWindow()
    controller = wb._etux_ribbon
    bar, tabs = controller.bar, controller.tabs
    original_mode = controller.mode
    original_size = window.size()
    application = QtWidgets.QApplication.instance()
    original_app_palette = application.palette()
    original_palette = window.palette()
    original_font = window.font()
    params = App.ParamGet('User parameter:BaseApp/Preferences/Mod/ETFreeCADUX')
    original_preference = params.GetString('RibbonDensity', '')
    snapshot = tuple((b, b.defaultAction()) for b, _ in controller.buttons)
    output = os.environ.get('ETUX_SCREENSHOT_DIR')
    cases = 0
    pixel_ratio = window.devicePixelRatioF()
    try:
        for theme, background, foreground, accent in (
                ('light', '#ffffff', '#17283c', '#175eac'),
                ('dark', '#202936', '#eef3fa', '#77baff')):
            assert contrast(foreground, background) >= 4.5
            assert contrast(accent, background) >= 3
            palette = QtGui.QPalette(original_palette)
            for role in (QtGui.QPalette.Window, QtGui.QPalette.Base, QtGui.QPalette.Button):
                palette.setColor(role, QtGui.QColor(background))
            for role in (QtGui.QPalette.WindowText, QtGui.QPalette.Text, QtGui.QPalette.ButtonText):
                palette.setColor(QtGui.QPalette.Active, role, QtGui.QColor(foreground))
                palette.setColor(QtGui.QPalette.Inactive, role, QtGui.QColor(foreground))
                palette.setColor(QtGui.QPalette.Disabled, role, QtGui.QColor('#778394'))
            palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(accent))
            palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor('#ffffff' if theme == 'light' else '#17283c'))
            application.setPalette(palette)
            window.setPalette(palette)
            gui.updateGui()
            assert controller.container.palette().color(QtGui.QPalette.Window).name() == background
            assert controller.buttons[0][0].palette().color(QtGui.QPalette.ButtonText).name() == foreground
            for font_scale in (1.0, 1.25, 1.5):
                font = QtGui.QFont(original_font)
                font.setPointSizeF(original_font.pointSizeF() * font_scale)
                window.setFont(font)
                gui.updateGui()
                assert controller.buttons[0][0].font().pointSizeF() == font.pointSizeF()
                heights = {}
                for mode in ('classic', 'compact', 'classic', 'compact'):
                    wb.setRibbonDensity(mode)
                    assert read_density(App) == mode
                    assert controller.bar is bar
                    assert tuple((b, b.defaultAction()) for b, _ in controller.buttons) == snapshot
                    for width, height in ((1920, 1080), (1600, 900), (1366, 768), (480, 600)):
                        window.resize(round(width / pixel_ratio), round(height / pixel_ratio))
                        for index in range(tabs.count()):
                            tabs.setCurrentIndex(index)
                            gui.updateGui()
                            scroll = tabs.widget(index)
                            page = scroll.widget()
                            assert page.height() <= scroll.viewport().height(), (mode, page.height(), scroll.viewport().height())
                            assert scroll.horizontalScrollBar().maximum() >= max(0, page.width() - scroll.viewport().width())
                            buttons = page.findChildren(QtWidgets.QToolButton)
                            for button in buttons:
                                assert button.width() >= button.minimumSizeHint().width(), button.text()
                                assert button.height() >= button.minimumSizeHint().height(), button.text()
                                assert button.isEnabled() == button.defaultAction().isEnabled()
                                assert button.toolTip() == button.defaultAction().toolTip()
                                assert button.focusPolicy() == QtCore.Qt.StrongFocus
                                if button.isEnabled():
                                    button.setFocus()
                                else:
                                    scroll.ensureWidgetVisible(button)
                                gui.updateGui()
                                point = button.mapTo(scroll.viewport(), QtCore.QPoint(button.width() // 2, button.height() // 2))
                                assert scroll.viewport().rect().contains(point), (mode, width, button.text(), point)
                            cases += 1
                        heights[mode] = controller.container.minimumHeight()
                    # Actual QWidget capture with synthetic inherited palette.
                    if output and font_scale == 1.0:
                        tabs.setCurrentIndex(0)
                        tabs.widget(0).horizontalScrollBar().setValue(0)
                        window.resize(1366, 768)
                        gui.updateGui()
                        Path(output).mkdir(parents=True, exist_ok=True)
                        assert bar.grab().save(str(Path(output) / (mode + '-' + theme + '.png')))
                assert heights['compact'] < heights['classic'], heights
        # Tab arrows use Qt's native tab navigation and leave command order intact.
        tabs.setCurrentIndex(0)
        tabs.tabBar().setFocus()
        event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Right, QtCore.Qt.NoModifier)
        QtWidgets.QApplication.sendEvent(tabs.tabBar(), event)
        assert tabs.currentIndex() == 1
        assert [tabs.tabText(i) for i in range(tabs.count())] == [label for label, _ in SECTIONS]
        tabs.setCurrentIndex(2)
        gui.updateGui()
        enabled = [b for b in tabs.widget(2).widget().findChildren(QtWidgets.QToolButton) if b.isEnabled()]
        assert len(enabled) >= 2
        enabled[0].setFocus()
        event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Tab, QtCore.Qt.NoModifier)
        QtWidgets.QApplication.sendEvent(enabled[0], event)
        gui.updateGui()
        assert QtWidgets.QApplication.focusWidget() == enabled[1]
        menu = tabs.cornerWidget().menu()
        menu.actions()[0].trigger()
        assert controller.mode == 'classic'
        menu.actions()[1].trigger()
        assert controller.mode == 'compact'
        assert sum(a.isChecked() for _, a in controller.mode_actions) == 1
        print('ETUX_MODERN_LAYOUT_OK cases={} themes=2 font_scales=3 dpr={}'.format(cases, pixel_ratio), file=sys.__stdout__, flush=True)
    finally:
        application.setPalette(original_app_palette)
        window.setPalette(original_palette)
        window.setFont(original_font)
        window.resize(original_size)
        wb.setRibbonDensity(original_mode)
        if original_preference:
            params.SetString('RibbonDensity', original_preference)
        else:
            params.RemString('RibbonDensity')
        tabs.setCurrentIndex(0)
