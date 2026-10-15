"""Resolve existing native actions, never create command proxies."""


def resolve_toolbar_actions(window, groups, widgets):
    resolved = []
    for group in groups:
        bars = window.findChildren(widgets.QToolBar, 'ET UX ' + group.label)
        if len(bars) != 1:
            raise RuntimeError('Toolbar ET UX non univoca: ' + group.label)
        actions = bars[0].actions()
        if len(actions) != len(group.commands):
            raise RuntimeError('Azioni toolbar incomplete: ' + group.label)
        for command, action in zip(group.commands, actions):
            name = action.objectName()
            # Native Undo/Redo menu actions have no objectName on tested hosts.
            if name != command and not (not name and command in ('Std_Undo', 'Std_Redo')):
                raise RuntimeError('Ordine/identità azioni toolbar non supportato: ' + group.label)
        resolved.append((group.label, tuple(zip(group.commands, actions)), bars[0]))
    return tuple(resolved)


class ToggleRibbonCommand:
    def __init__(self, gui):
        self.gui = gui

    def GetResources(self):
        return {'MenuText': 'Attiva/disattiva Ribbon sperimentale',
                'ToolTip': 'Alterna Ribbon e toolbar native ET UX per questa sessione'}

    def IsActive(self):
        return self.gui.activeWorkbench().name() == 'ETUXWorkbench'

    def Activated(self):
        wb = self.gui.activeWorkbench()
        wb.setRibbonEnabled(not wb._etux_ribbon_enabled)


PREFERENCE_PATH = 'User parameter:BaseApp/Preferences/Mod/ETFreeCADUX'


def read_density(app):
    from et_freecad_ux.core.ribbon import density
    return density(app.ParamGet(PREFERENCE_PATH).GetString('RibbonDensity', 'classic')).key


def write_density(app, key):
    from et_freecad_ux.core.ribbon import DENSITIES
    if key not in tuple(item.key for item in DENSITIES):
        raise ValueError('Densità Ribbon non valida: ' + str(key))
    app.ParamGet(PREFERENCE_PATH).SetString('RibbonDensity', key)


class RibbonDensityCommand(ToggleRibbonCommand):
    def __init__(self, gui, key):
        super().__init__(gui)
        self.key = key

    def GetResources(self):
        from et_freecad_ux.core.ribbon import density
        return {'MenuText': density(self.key).label,
                'ToolTip': 'Memorizza la densità della sola Ribbon ET UX; applicazione immediata'}

    def Activated(self):
        self.gui.activeWorkbench().setRibbonDensity(self.key)
