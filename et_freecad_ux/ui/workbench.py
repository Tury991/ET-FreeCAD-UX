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
            self._etux_groups = workspace_groups(App, Gui)
            for group in self._etux_groups:
                self.appendToolbar("ET UX " + group.label, list(group.commands))
                self.appendMenu(["ET UX", group.label], list(group.commands))
            from et_freecad_ux.adapters.ribbon import ToggleRibbonCommand
            if 'ETUX_ToggleRibbon' not in Gui.listCommands():
                Gui.addCommand('ETUX_ToggleRibbon', ToggleRibbonCommand(Gui))
            self.appendMenu(['ET UX', 'Ribbon sperimentale'], ['ETUX_ToggleRibbon'])
            self._etux_ribbon_enabled = False
            self._etux_ribbon = None
            self._etux_initialized = True

        def Activated(self):
            if self._etux_ribbon_enabled:
                try:
                    self._etux_ribbon.schedule(lambda: self.setRibbonEnabled(True))
                except Exception as error:
                    self.setRibbonEnabled(False)
                    import FreeCAD as App
                    App.Console.PrintWarning('ET UX: riattivazione Ribbon fallita, toolbar native: {}\n'.format(error))

        def Deactivated(self):
            if self._etux_ribbon is not None:
                self._etux_ribbon.deactivate()

        def setRibbonEnabled(self, enabled):
            import FreeCAD as App
            import FreeCADGui as Gui
            self._etux_ribbon_enabled = bool(enabled)
            if not enabled:
                if self._etux_ribbon is not None:
                    self._etux_ribbon.deactivate()
                return
            try:
                if self._etux_ribbon is None:
                    from et_freecad_ux.ui.ribbon import RibbonController
                    self._etux_ribbon = RibbonController(
                        Gui, self._etux_groups, lambda: self.setRibbonEnabled(False))
                self._etux_ribbon.activate()
            except Exception as error:
                self._etux_ribbon_enabled = False
                if self._etux_ribbon is not None:
                    self._etux_ribbon.deactivate()
                App.Console.PrintWarning('ET UX: Ribbon non disponibile, toolbar native: {}\n'.format(error))

        def GetClassName(self):
            return "Gui::PythonWorkbench"

    return ETUXWorkbench
