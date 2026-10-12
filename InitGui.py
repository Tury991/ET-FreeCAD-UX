"""Register the Python workbench when FreeCAD loads GUI extensions."""
import FreeCADGui as Gui

from et_freecad_ux.ui.workbench import create_workbench_class

# FreeCAD supplies Workbench in the InitGui execution namespace.
Gui.addWorkbench(create_workbench_class(Workbench)())
