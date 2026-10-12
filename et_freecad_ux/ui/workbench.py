"""Standard FreeCAD workbench, with no global toolbar or menu replacement."""
from pathlib import Path

from et_freecad_ux.adapters.freecad import register_commands, load_native_commands, workspace_groups


ICON = str(Path(__file__).resolve().parents[2] / "Resources" / "icons" / "etux.svg")


def create_workbench_class(base):
    """Receive FreeCAD's Workbench base rather than depending on loader globals."""

    class ETUXWorkbench(base):
        MenuText = "ET FreeCAD UX"
        ToolTip = "Mechanical Workspace: Sketch, Features, Reference, Tools"
        Icon = ICON

        def Initialize(self):
            if getattr(self, "_etux_initialized", False):
                return
            import FreeCAD as App
            import FreeCADGui as Gui

            load_native_commands(App)
            register_commands(App, Gui)
            for group in workspace_groups(App, Gui):
                self.appendToolbar("ET UX " + group.label, list(group.commands))
                self.appendMenu(["ET UX", group.label], list(group.commands))
            self._etux_initialized = True

        def Activated(self):
            # Future observers/widgets must be owned here and released below.
            pass

        def Deactivated(self):
            # No persistent host state is changed in this initial version.
            pass

        def GetClassName(self):
            return "Gui::PythonWorkbench"

    return ETUXWorkbench
