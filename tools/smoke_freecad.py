"""Run inside a FreeCAD GUI Python session, or with the documented system Python."""
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import FreeCAD as App
import FreeCADGui as Gui

Gui.showMainWindow()
previous = Gui.activeWorkbench().name()
try:
    runpy.run_path(str(ROOT / "InitGui.py"), init_globals={"Workbench": Gui.Workbench})
    assert "ETUXWorkbench" in Gui.listWorkbenches()
    for _ in range(3):
        Gui.activateWorkbench("ETUXWorkbench")
        assert Gui.activeWorkbench().name() == "ETUXWorkbench"
        assert "ETUX_About" in Gui.listCommands()
        Gui.runCommand("ETUX_About", 0)
        from PySide import QtWidgets
        window = Gui.getMainWindow()
        assert len(window.findChildren(QtWidgets.QToolBar, "ET UX")) == 1
        assert any(action.text() == "ET UX" for action in window.menuBar().actions())
        Gui.activateWorkbench(previous)
    print("ETUX_GUI_SMOKE_OK")
finally:
    Gui.activateWorkbench(previous)
