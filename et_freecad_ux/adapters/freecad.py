"""Small host adapter. Importing this module does not require FreeCAD."""
from et_freecad_ux import __version__
from et_freecad_ux.core.catalog import ABOUT_COMMAND, HELP_COMMAND


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
            "ET FreeCAD UX {} — Mechanical Workspace; "
            "nessuna modifica al motore CAD o alle preferenze globali.\n".format(
                __version__
            )
        )


def register_commands(app, gui):
    """Idempotent within the current GUI registry, including module reloads."""
    commands = ((ABOUT_COMMAND, AboutCommand(app)),
                (HELP_COMMAND, WorkspaceHelpCommand(app, gui)))
    for name, command in commands:
        if name not in gui.listCommands():
            gui.addCommand(name, command)


class WorkspaceHelpCommand:
    """Read host capabilities on demand; never retain documents or selections."""
    def __init__(self, app, gui):
        self.app, self.gui = app, gui

    def GetResources(self):
        return {'MenuText': 'Guida Mechanical Workspace',
                'ToolTip': 'Workflow, prerequisiti e comandi mancanti nel pannello Report'}

    def IsActive(self):
        return True

    def Activated(self):
        from et_freecad_ux.core.catalog import NATIVE_COMMANDS
        missing = [c for c in NATIVE_COMMANDS if c not in self.gui.listCommands()]
        self.app.Console.PrintMessage(
            'ET UX: crea un documento (Tools), un Body (Features), poi uno sketch '
            'sul piano XY (Sketch). Disegna e vincola il profilo, chiudi lo sketch '
            'e selezionalo per Pad/Pocket/Revolution. Per Fillet/Chamfer seleziona '
            'gli spigoli. Attiva il Body desiderato con doppio clic nell’albero. '
            'Concludi o annulla il task corrente prima di avviare una nuova feature. '
            'I pulsanti seguono i prerequisiti nativi di FreeCAD.\n')
        if missing:
            self.app.Console.PrintWarning('ET UX: comandi non disponibili: {}. '
                'Verifica installazione e versione FreeCAD.\n'.format(', '.join(missing)))


def load_native_commands(app, loader=None):
    """Load only required public GUI modules, without switching workbenches."""
    if loader is None:
        from importlib import import_module
        loader = import_module
    for module in ('PartDesignGui', 'SketcherGui'):
        try:
            loader(module)
        except (ImportError, RuntimeError) as error:
            app.Console.PrintWarning('ET UX: impossibile caricare {}: {}. '
                'Gli altri strumenti restano disponibili.\n'.format(module, error))


def workspace_groups(app, gui):
    from et_freecad_ux.core.catalog import NATIVE_COMMANDS, available_groups
    available = set(gui.listCommands())
    missing = tuple(c for c in NATIVE_COMMANDS if c not in available)
    if missing:
        app.Console.PrintWarning('ET UX: comandi non disponibili, omessi dai menu '
            'e dalle toolbar: {}. Consulta Tools → Guida Mechanical Workspace.\n'
            .format(', '.join(missing)))
    return available_groups(available)
