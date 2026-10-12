"""Small host adapter. Importing this module does not require FreeCAD."""
from et_freecad_ux import __version__
from et_freecad_ux.core.catalog import ABOUT_COMMAND


class AboutCommand:
    """Read-only initial command; no document mutation or selection prerequisite."""

    def __init__(self, app):
        self.app = app

    def GetResources(self):
        return {
            "MenuText": "Informazioni su ET FreeCAD UX",
            "ToolTip": "Mostra versione e scopo nel pannello Report",
        }

    def IsActive(self):
        return True

    def Activated(self):
        self.app.Console.PrintMessage(
            "ET FreeCAD UX {} — base modulare sperimentale; "
            "nessuna modifica al motore CAD o alle preferenze globali.\n".format(
                __version__
            )
        )


def register_commands(app, gui):
    """Idempotent within the current GUI registry, including module reloads."""
    if ABOUT_COMMAND not in gui.listCommands():
        gui.addCommand(ABOUT_COMMAND, AboutCommand(app))
