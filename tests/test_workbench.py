"""Host-contract checks without installing FreeCAD or Qt."""
import importlib
import subprocess
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from et_freecad_ux.adapters.freecad import AboutCommand, register_commands
from et_freecad_ux.core.catalog import ABOUT_COMMAND, HELP_COMMAND, GROUPS, NATIVE_COMMANDS
from et_freecad_ux.ui.workbench import ICON, create_workbench_class


class HostWorkbench:
    def __init__(self):
        self.toolbars = []
        self.menus = []

    def appendToolbar(self, name, commands):
        self.toolbars.append((name, commands))

    def appendMenu(self, name, commands):
        self.menus.append((name, commands))


class WorkbenchTests(unittest.TestCase):
    def test_modules_import_without_host_or_qt(self):
        result = subprocess.run([sys.executable, '-c',
            'import et_freecad_ux.core.catalog, et_freecad_ux.ui.workbench, '
            'et_freecad_ux.ui.ribbon, et_freecad_ux.adapters.ribbon; '
            'import sys; assert not any(n in sys.modules for n in '
            '("FreeCAD", "FreeCADGui", "PySide", "PySide2", "PySide6"))'],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_registration_is_idempotent_across_reload(self):
        registry = {}
        gui = SimpleNamespace(listCommands=lambda: list(registry),
                              addCommand=lambda name, command: registry.setdefault(name, command))
        app = Mock()
        register_commands(app, gui)
        original = registry[ABOUT_COMMAND]
        module = importlib.import_module('et_freecad_ux.adapters.freecad')
        importlib.reload(module).register_commands(app, gui)
        self.assertIs(registry[ABOUT_COMMAND], original)
        self.assertEqual(len(registry), 2)

    def test_initialize_and_activation_do_not_duplicate_ui(self):
        gui = Mock()
        gui.listCommands.return_value = list(NATIVE_COMMANDS) + [ABOUT_COMMAND, HELP_COMMAND, 'ETUX_ToggleRibbon']
        wb = create_workbench_class(HostWorkbench)()
        with patch.dict(sys.modules, {'FreeCAD': Mock(), 'FreeCADGui': gui, 'PartDesignGui': Mock(), 'SketcherGui': Mock()}):
            wb.Initialize()
            wb.Initialize()
            for _ in range(3):
                wb.Activated()
                wb.Deactivated()
        self.assertEqual(wb.toolbars, [("ET UX " + g.label, list(g.commands)) for g in GROUPS])
        self.assertEqual(wb.menus, [(["ET UX", g.label], list(g.commands)) for g in GROUPS] +
                         [(['ET UX', 'Ribbon sperimentale'], ['ETUX_ToggleRibbon'])])
        gui.addCommand.assert_not_called()
        self.assertEqual(wb.GetClassName(), 'Gui::PythonWorkbench')
        self.assertTrue(Path(ICON).is_file())

    def test_about_works_without_document_and_is_read_only(self):
        app = SimpleNamespace(Console=Mock())
        command = AboutCommand(app)
        self.assertTrue(command.IsActive())
        self.assertIn('MenuText', command.GetResources())
        command.Activated()
        app.Console.PrintMessage.assert_called_once()
