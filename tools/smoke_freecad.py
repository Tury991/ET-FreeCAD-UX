"""Real GUI capabilities, lifecycle, native Body command and feature dispatch."""
from pathlib import Path
import runpy
import sys
import os

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtWidgets, QtCore
from et_freecad_ux.core.catalog import GROUPS, NATIVE_COMMANDS
from et_freecad_ux.core.ribbon import SECTIONS

Gui.showMainWindow()
if Gui.Control.activeDialog():
    raise RuntimeError('Concludi o annulla il task aperto prima dello smoke test.')
previous_selection = [(s.DocumentName, s.ObjectName, tuple(s.SubElementNames))
                      for s in Gui.Selection.getSelectionEx()]
previous = Gui.activeWorkbench().name()
previous_doc = App.ActiveDocument.Name if App.ActiveDocument else None
doc = None
other = None
from et_freecad_ux.adapters.ribbon import PREFERENCE_PATH, read_density
density_params = App.ParamGet(PREFERENCE_PATH)
previous_density_value = density_params.GetString('RibbonDensity', '')
previous_density = read_density(App)
try:
    if 'ETUXWorkbench' not in Gui.listWorkbenches():
        runpy.run_path(str(ROOT / 'InitGui.py'), init_globals={'Workbench': Gui.Workbench})
    for _ in range(3):
        Gui.activateWorkbench('ETUXWorkbench')
        assert Gui.activeWorkbench().name() == 'ETUXWorkbench'
        assert set(NATIVE_COMMANDS).issubset(Gui.listCommands()), set(NATIVE_COMMANDS) - set(Gui.listCommands())
        Gui.runCommand('ETUX_About', 0)
        window = Gui.getMainWindow()
        for group in GROUPS:
            bars = window.findChildren(QtWidgets.QToolBar, 'ET UX ' + group.label)
            assert len(bars) == 1, (group.label, len(bars))
            assert len(bars[0].actions()) == len(group.commands)
        menu_actions = window.menuBar().actions()
        menus = [a.menu() for a in menu_actions if a.text() == 'ET UX']
        assert len(menus) == 1
        assert [a.text() for a in menus[0].actions()] == [g.label for g in GROUPS] + ['Ribbon sperimentale']
        Gui.activateWorkbench(previous)
    Gui.activateWorkbench('ETUXWorkbench')
    wb = Gui.activeWorkbench()
    def drain():
        # Minimal host startup leaves application timers pending. Exercise owned
        # deferred deletion without running unrelated loader/startup timers.
        QtCore.QCoreApplication.sendPostedEvents(None, QtCore.QEvent.DeferredDelete)
    drain()
    native_bars = [window.findChildren(QtWidgets.QToolBar, 'ET UX ' + g.label)[0] for g in GROUPS]
    native_docks = set(window.findChildren(QtWidgets.QDockWidget))
    other = QtWidgets.QToolBar('ETUX unrelated smoke sentinel', window)
    other.setObjectName('ETUX_SmokeSentinel')
    window.addToolBar(other)
    other.show()
    native_bars[-1].hide()
    drain()
    original_visibility = [not b.isHidden() for b in native_bars]
    original_sizes = [(b.minimumSize(), b.maximumSize()) for b in native_bars]
    for _ in range(5):
        native_actions = {c: a for g, bar in zip(GROUPS, native_bars) for c, a in zip(g.commands, bar.actions())}
        Gui.runCommand('ETUX_ToggleRibbon', 0)
        ribbon = wb._etux_ribbon.bar
        assert ribbon is not None
        wb.setRibbonEnabled(True)
        assert len(window.findChildren(QtWidgets.QToolBar, 'ETUX_RibbonPrototype')) == 1
        tabs = ribbon.findChild(QtWidgets.QTabWidget, 'ETUX_RibbonTabs')
        assert [tabs.tabText(i) for i in range(tabs.count())] == [label for label, _ in SECTIONS]
        for command, action in native_actions.items():
            current = ribbon.findChild(QtWidgets.QToolButton, 'ETUX_Ribbon_' + command).defaultAction()
            assert current == action, (command, current.objectName(), action.objectName(), current.text(), action.text())
        assert all(b.maximumSize() == QtCore.QSize(0, 0) for b in native_bars)
        assert [not b.isHidden() for b in native_bars] == original_visibility
        assert not other.isHidden() and other.maximumWidth() > 0
        window.resize(480, 600)
        drain()
        Gui.runCommand('ETUX_ToggleRibbon', 0)
        drain()
        assert not window.findChildren(QtWidgets.QToolBar, 'ETUX_RibbonPrototype')
        assert wb._etux_ribbon.buttons == [] and wb._etux_ribbon.pages == []
        assert wb._etux_ribbon.mode_actions == [] and wb._etux_ribbon.container is None
        assert [not b.isHidden() for b in native_bars] == original_visibility, ([not b.isHidden() for b in native_bars], original_visibility)
        assert [(b.minimumSize(), b.maximumSize()) for b in native_bars] == original_sizes
    native_bars[-1].show()
    wb.setRibbonEnabled(True)
    # Cancel activation before its queued callback can run.
    Gui.activateWorkbench(previous)
    Gui.activateWorkbench('ETUXWorkbench')
    Gui.activateWorkbench(previous)
    Gui.updateGui()
    assert wb._etux_ribbon.activation_timer is None
    assert wb._etux_ribbon.bar is None
    Gui.activateWorkbench('ETUXWorkbench')
    Gui.updateGui()
    for _ in range(5):
        Gui.activateWorkbench(previous)
        drain()
        assert not window.findChildren(QtWidgets.QToolBar, 'ETUX_RibbonPrototype')
        Gui.activateWorkbench('ETUXWorkbench')
        Gui.updateGui()
        drain()
        assert len(window.findChildren(QtWidgets.QToolBar, 'ETUX_RibbonPrototype')) == 1
    # Trigger a real native action through its Ribbon button.
    ribbon_doc = App.newDocument('ETUXRibbonDispatch')
    doc = ribbon_doc
    Gui.updateGui()
    Gui.Command.update()
    tabs = wb._etux_ribbon.bar.findChild(QtWidgets.QTabWidget, 'ETUX_RibbonTabs')
    tabs.setCurrentIndex(0)
    button = wb._etux_ribbon.bar.findChild(QtWidgets.QToolButton, 'ETUX_Ribbon_PartDesign_Body')
    # FreeCAD updates native QAction enablement on its command timer.
    # Give the real event loop a bounded turn; do not setEnabled in the product.
    loop = QtCore.QEventLoop()
    QtCore.QTimer.singleShot(350, loop.quit)
    loop.exec_()
    assert button.isEnabled()
    wb._etux_ribbon.bar.findChild(QtWidgets.QToolButton, 'ETUX_Ribbon_PartDesign_Body').click()
    assert ribbon_doc.getObject('Body') is not None
    runpy.run_path(str(ROOT / 'tools' / 'smoke_ribbon_layout.py'))['run'](wb, Gui)
    App.closeDocument(ribbon_doc.Name)
    doc = None
    wb.setRibbonEnabled(False)
    drain()
    assert all(not b.isHidden() for b in native_bars)
    assert set(window.findChildren(QtWidgets.QDockWidget)) == native_docks
    # Missing host surface must fall back without hiding the remaining bars.
    native_bars[0].setObjectName('ETUX_SmokeMissingToolbar')
    try:
        wb.setRibbonEnabled(True)
        assert not wb._etux_ribbon_enabled
        assert wb._etux_ribbon.bar is None
        assert all(not b.isHidden() for b in native_bars)
    finally:
        native_bars[0].setObjectName('ET UX Sketch')
    window.removeToolBar(other)
    other.setParent(None)
    other.deleteLater()
    other = None
    print('ETUX_RIBBON_SMOKE_OK toggles=5 switches=5 native_actions=26', file=sys.__stdout__, flush=True)
    doc = App.newDocument('ETUXMechanicalGuiSmoke')
    Gui.runCommand('PartDesign_Body', 0)
    body = doc.getObject('Body')
    assert body and body.TypeId == 'PartDesign::Body'
    assert Gui.activeDocument().activeView().getActiveObject('pdbody') == body
    # Dispatch NewSketch on an explicitly selected origin plane.
    Gui.Selection.addSelection(doc.getObject('XY_Plane'))
    Gui.runCommand('PartDesign_NewSketch', 0)
    sketch = doc.getObject('Sketch')
    assert sketch and sketch in body.Group
    assert Gui.activeDocument().getInEdit() is not None
    Gui.activeDocument().resetEdit()
    Gui.Control.closeDialog()
    Gui.activateWorkbench('ETUXWorkbench')
    # Populate the sketch deterministically without interactive drawing.
    import Part, Sketcher
    sketch.addGeometry(Part.Circle(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 5), False)
    sketch.addConstraint(Sketcher.Constraint('Radius', 0, 5.0))
    doc.recompute()
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(sketch)
    Gui.Command.update()
    assert Gui.Command.get('PartDesign_Pad').isActive()
    Gui.runCommand('PartDesign_Pad', 0)
    pad = doc.getObject('Pad')
    task_before = Gui.Control.activeDialog()
    for mode in ('compact', 'classic') * 3:
        wb.setRibbonDensity(mode)
        assert Gui.Control.activeDialog() == task_before
        assert doc.getObject('Pad') == pad
    assert pad and pad.Profile[0] == sketch
    assert Gui.activeDocument().getInEdit() is not None
    doc.recompute()
    assert pad.Shape.isValid() and len(pad.Shape.Solids) == 1
    # End the temporary task; no task interaction or viewport rendering claim.
    Gui.activeDocument().resetEdit()
    Gui.Control.closeDialog()
    print('ETUX_GUI_SMOKE_OK native_commands={} groups=4 body=True sketch_dispatch=True pad_dispatch=True'.format(len(NATIVE_COMMANDS)), file=sys.__stdout__, flush=True)
except Exception:
    import traceback
    os.write(2, traceback.format_exc().encode())
    raise
finally:
    if 'ETUXWorkbench' in Gui.listWorkbenches():
        etux = Gui.getWorkbench('ETUXWorkbench')
        if getattr(etux, '_etux_initialized', False):
            etux.setRibbonEnabled(False)
            etux.setRibbonDensity(previous_density)
            if previous_density_value:
                density_params.SetString('RibbonDensity', previous_density_value)
            else:
                density_params.RemString('RibbonDensity')
    if other is not None:
        window.removeToolBar(other)
        other.setParent(None)
        other.deleteLater()
    Gui.Selection.clearSelection()
    if doc and doc.Name in App.listDocuments():
        if Gui.activeDocument() and Gui.activeDocument().getInEdit():
            Gui.activeDocument().resetEdit()
        Gui.Control.closeDialog()
        App.closeDocument(doc.Name)
    if previous_doc in App.listDocuments():
        App.setActiveDocument(previous_doc)
    Gui.activateWorkbench(previous)
    for document, obj, subelements in previous_selection:
        if document in App.listDocuments() and App.getDocument(document).getObject(obj):
            if subelements:
                for subelement in subelements:
                    Gui.Selection.addSelection(document, obj, subelement)
            else:
                Gui.Selection.addSelection(document, obj)
    # Drain native views before interpreter shutdown, including on failure.
    QtCore.QCoreApplication.sendPostedEvents(None, QtCore.QEvent.DeferredDelete)
    QtWidgets.QApplication.processEvents()
