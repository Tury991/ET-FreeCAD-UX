"""Real GUI capabilities, lifecycle, native Body command and feature dispatch."""
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtWidgets, QtCore
from et_freecad_ux.core.catalog import GROUPS, NATIVE_COMMANDS

Gui.showMainWindow()
if Gui.Control.activeDialog():
    raise RuntimeError('Concludi o annulla il task aperto prima dello smoke test.')
previous_selection = [(s.DocumentName, s.ObjectName, tuple(s.SubElementNames))
                      for s in Gui.Selection.getSelectionEx()]
previous = Gui.activeWorkbench().name()
previous_doc = App.ActiveDocument.Name if App.ActiveDocument else None
doc = None
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
        assert [a.text() for a in menus[0].actions()] == [g.label for g in GROUPS]
        Gui.activateWorkbench(previous)
    Gui.activateWorkbench('ETUXWorkbench')
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
    assert pad and pad.Profile[0] == sketch
    assert Gui.activeDocument().getInEdit() is not None
    doc.recompute()
    assert pad.Shape.isValid() and len(pad.Shape.Solids) == 1
    # End the temporary task; no task interaction or viewport rendering claim.
    Gui.activeDocument().resetEdit()
    Gui.Control.closeDialog()
    print('ETUX_GUI_SMOKE_OK native_commands={} groups=4 body=True sketch_dispatch=True pad_dispatch=True'.format(len(NATIVE_COMMANDS)), flush=True)
finally:
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
