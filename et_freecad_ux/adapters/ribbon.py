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
