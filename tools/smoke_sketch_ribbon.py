"""Native edit lifecycle checks inside the isolated GUI smoke, never at startup."""
import os
from pathlib import Path
import sys


def run(wb, gui, app):
    from PySide import QtCore, QtGui, QtWidgets
    from et_freecad_ux.core.catalog import NATIVE_COMMANDS
    import Part
    window = gui.getMainWindow()
    original_palette = window.palette()
    original_size = window.size()
    window.resize(1366, 768)
    original_mode = wb._etux_ribbon_density
    original_doc = app.ActiveDocument.Name if app.ActiveDocument else None
    document = None
    cases = 0

    def settle():
        gui.updateGui()
        gui.Command.update()
        QtCore.QCoreApplication.sendPostedEvents(None, QtCore.QEvent.DeferredDelete)

    def check_edit(controller, task, key):
        settle()
        assert wb._etux_ribbon is controller and controller.bar is not None
        assert not controller.bar.isHidden() and controller.bar.isVisible()
        assert controller.tabs.tabText(controller.tabs.currentIndex()) == 'Sketch'
        assert gui.Control.activeDialog() == task and task
        assert controller.sketch_session.edit == key
        assert len(window.findChildren(QtWidgets.QToolBar, 'ETUX_RibbonPrototype')) == 1
        for button, _ in controller.buttons:
            assert button.isEnabled() == button.defaultAction().isEnabled()
        for command in ('Sketcher_CreateLine', 'Sketcher_CreateCircle', 'Sketcher_CreateArc',
                        'Sketcher_CreateRectangle', 'Sketcher_Trimming', 'Sketcher_CreateFillet'):
            button = controller.bar.findChild(QtWidgets.QToolButton, 'ETUX_Ribbon_' + command)
            assert button.defaultAction().objectName() == command
            assert gui.Command.get(command).isActive(), command

    try:
        for mode in ('classic', 'compact'):
            for theme in ('light', 'dark'):
                palette = QtGui.QPalette(original_palette)
                palette.setColor(QtGui.QPalette.Window, QtGui.QColor('#ffffff' if theme == 'light' else '#202936'))
                for role in (QtGui.QPalette.WindowText, QtGui.QPalette.ButtonText, QtGui.QPalette.Text):
                    palette.setColor(role, QtGui.QColor('#17283c' if theme == 'light' else '#eef3fa'))
                window.setPalette(palette)
                gui.activateWorkbench('ETUXWorkbench')
                wb.setRibbonEnabled(True)
                wb.setRibbonDensity(mode)
                controller = wb._etux_ribbon
                controller.tabs.setCurrentIndex(0)
                document = app.newDocument('ETUXSketchRibbon')
                gui.runCommand('PartDesign_Body', 0)
                gui.Selection.clearSelection()
                gui.Selection.addSelection(document.getObject('XY_Plane'))
                settle()
                controller.bar.findChild(QtWidgets.QToolButton, 'ETUX_Ribbon_PartDesign_NewSketch').defaultAction().trigger()
                sketch = document.getObject('Sketch')
                assert sketch
                key = (document.Name, sketch.Name)
                task = gui.Control.activeDialog()
                check_edit(controller, task, key)
                borrowed_session = controller.sketch_session
                # The same actions and task survive density changes while editing.
                snapshot = tuple((b, b.defaultAction()) for b, _ in controller.buttons)
                for density in (mode, 'compact', 'classic', mode):
                    wb.setRibbonDensity(density)
                    check_edit(controller, task, key)
                    assert tuple((b, b.defaultAction()) for b, _ in controller.buttons) == snapshot
                # Geometry creation is native test setup, not a product algorithm.
                document.openTransaction('ETUX test line')
                sketch.addGeometry(Part.LineSegment(app.Vector(0, 0, 0), app.Vector(10, 0, 0)), False)
                document.commitTransaction()
                document.undo()
                assert sketch.GeometryCount == 0
                document.redo()
                assert sketch.GeometryCount == 1
                check_edit(controller, task, key)
                # Real native constraint dispatch and transaction ownership.
                gui.Selection.clearSelection()
                gui.Selection.addSelection(sketch, 'Edge1')
                settle()
                horizontal = controller.bar.findChild(QtWidgets.QToolButton, 'ETUX_Ribbon_Sketcher_ConstrainHorizontal')
                # Native command enablement uses the host's command timer.
                loop = QtCore.QEventLoop()
                QtCore.QTimer.singleShot(350, loop.quit)
                loop.exec_()
                assert horizontal.isEnabled()
                horizontal.click()
                assert any(c.Type == 'Horizontal' for c in sketch.Constraints)
                document.undo()
                assert not any(c.Type == 'Horizontal' for c in sketch.Constraints)
                document.redo()
                assert any(c.Type == 'Horizontal' for c in sketch.Constraints)
                gui.Selection.clearSelection()
                check_edit(controller, task, key)
                output = os.environ.get('ETUX_SCREENSHOT_DIR')
                if output:
                    Path(output).mkdir(parents=True, exist_ok=True)
                    assert controller.bar.grab().save(str(Path(output) / ('sketch-' + mode + '-' + theme + '.png')))
                gui.runCommand('Sketcher_LeaveSketch', 0)
                settle()
                assert gui.activeDocument().getInEdit() is None
                assert not gui.Control.activeDialog()
                assert gui.activeWorkbench().name() == 'ETUXWorkbench'
                assert controller.tabs.currentIndex() == 0
                # Reopen existing sketch through the same native action.
                gui.Selection.clearSelection()
                gui.Selection.addSelection(sketch)
                gui.runCommand('Sketcher_EditSketch', 0)
                check_edit(controller, gui.Control.activeDialog(), key)
                assert controller.sketch_session is borrowed_session
                # Voluntary workbench change during the task must win.
                gui.activateWorkbench('PartDesignWorkbench')
                settle()
                assert controller.bar is None and controller.sketch_session is None
                assert not borrowed_session.observing and not borrowed_session.connected
                assert borrowed_session.timer is None and borrowed_session.edit is None
                assert gui.activeDocument().getInEdit() is not None
                gui.runCommand('Sketcher_LeaveSketch', 0)
                settle()
                assert gui.activeWorkbench().name() == 'PartDesignWorkbench'
                assert controller.bar is None
                app.closeDocument(document.Name)
                document = None
                cases += 1
        # Repeated toggle in an active sketch must not resurrect a disabled UI.
        gui.activateWorkbench('ETUXWorkbench')
        settle()
        document = app.newDocument('ETUXSketchCancel')
        body = document.addObject('PartDesign::Body', 'Body')
        sketch = document.addObject('Sketcher::SketchObject', 'Sketch')
        body.addObject(sketch)
        gui.Selection.clearSelection()
        gui.Selection.addSelection(sketch)
        gui.runCommand('Sketcher_EditSketch', 0)
        check_edit(wb._etux_ribbon, gui.Control.activeDialog(), (document.Name, sketch.Name))
        wb.setRibbonEnabled(False)
        settle()
        assert wb._etux_ribbon.sketch_session is None and wb._etux_ribbon.bar is None
        # Exercise native TaskDlgEditSketch::reject via its actual Qt Close
        # button. Sketcher offers Close, not a rollback/Cancel button.
        closes = [box.button(QtWidgets.QDialogButtonBox.Close)
                  for box in window.findChildren(QtWidgets.QDialogButtonBox)
                  if box.isVisible() and box.button(QtWidgets.QDialogButtonBox.Close)]
        assert len(closes) == 1, len(closes)
        closes[0].click()
        settle()
        assert wb._etux_ribbon.bar is None
        assert gui.activeDocument().getInEdit() is None
        gui.activateWorkbench('ETUXWorkbench')
        wb.setRibbonEnabled(True)
        settle()
        controller = wb._etux_ribbon
        session = controller.sketch_session
        # A manual switch to Sketcher with no edit is not an automatic handoff.
        gui.activateWorkbench('SketcherWorkbench')
        settle()
        assert controller.bar is None and not session.observing
        gui.Selection.clearSelection()
        gui.Selection.addSelection(sketch)
        gui.runCommand('Sketcher_EditSketch', 0)
        settle()
        assert controller.bar is None
        # Explicit return to ET UX during an existing task is allowed.
        gui.activateWorkbench('ETUXWorkbench')
        settle()
        check_edit(controller, gui.Control.activeDialog(), (document.Name, sketch.Name))
        session = controller.sketch_session
        other = app.newDocument('ETUXSketchOtherDocument')
        try:
            settle()
            assert controller.bar is None and not session.observing
            assert session.edit is None and session.timer is None
        finally:
            app.closeDocument(other.Name)
            app.setActiveDocument(document.Name)
        if gui.activeDocument().getInEdit():
            gui.runCommand('Sketcher_LeaveSketch', 0)
        gui.activateWorkbench('ETUXWorkbench')
        wb.setRibbonEnabled(True)
        settle()
        gui.Selection.clearSelection()
        gui.Selection.addSelection(sketch)
        gui.runCommand('Sketcher_EditSketch', 0)
        settle()
        session = controller.sketch_session
        app.closeDocument(document.Name)
        document = None
        settle()
        assert session.edit is None
        assert controller.sketch_session is None or controller.sketch_session.edit is None
        print('ETUX_SKETCH_RIBBON_OK cases={} native_commands={} undo_redo=True'.format(cases, len(NATIVE_COMMANDS)), file=sys.__stdout__, flush=True)
    finally:
        wb.setRibbonEnabled(False)
        if document and document.Name in app.listDocuments():
            if gui.activeDocument() and gui.activeDocument().getInEdit():
                gui.activeDocument().resetEdit()
            gui.Control.closeDialog()
            app.closeDocument(document.Name)
        window.setPalette(original_palette)
        window.resize(original_size)
        if original_doc in app.listDocuments():
            app.setActiveDocument(original_doc)
        gui.activateWorkbench('ETUXWorkbench')
        wb.setRibbonDensity(original_mode)
        wb.setRibbonEnabled(True)
        settle()
