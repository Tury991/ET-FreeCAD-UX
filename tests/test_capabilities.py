"""Failure paths and pure capability resolution; these are not CAD host tests."""
import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from et_freecad_ux.core.catalog import GROUPS, NATIVE_COMMANDS, ABOUT_COMMAND, HELP_COMMAND
from et_freecad_ux.adapters.freecad import load_native_commands, workspace_groups, WorkspaceHelpCommand


class CapabilityTests(unittest.TestCase):
    def test_missing_commands_are_omitted_and_reported(self):
        app = SimpleNamespace(Console=Mock())
        gui = SimpleNamespace(listCommands=lambda: [ABOUT_COMMAND, HELP_COMMAND, 'Std_New'])
        groups = workspace_groups(app, gui)
        self.assertEqual([g.label for g in groups], ['Sketch', 'Features', 'Reference', 'Tools'])
        self.assertEqual(groups[-1].commands, ('Std_New', HELP_COMMAND, ABOUT_COMMAND))
        self.assertFalse(any(g.commands for g in groups[:-1]))
        self.assertIn('PartDesign_Pad', app.Console.PrintWarning.call_args[0][0])

    def test_public_module_failure_keeps_loading_other_module(self):
        app = SimpleNamespace(Console=Mock())
        loader = Mock(side_effect=[ImportError('missing'), None])
        load_native_commands(app, loader)
        self.assertEqual([c.args[0] for c in loader.call_args_list], ['PartDesignGui', 'SketcherGui'])
        app.Console.PrintWarning.assert_called_once()

    def test_complete_host_preserves_order_without_warning(self):
        app = SimpleNamespace(Console=Mock())
        gui = SimpleNamespace(listCommands=lambda: list(NATIVE_COMMANDS) + [ABOUT_COMMAND, HELP_COMMAND])
        self.assertEqual(workspace_groups(app, gui), GROUPS)
        app.Console.PrintWarning.assert_not_called()

    def test_help_without_document_reports_missing_feature(self):
        app = SimpleNamespace(Console=Mock())
        command = WorkspaceHelpCommand(app, SimpleNamespace(listCommands=lambda: []))
        self.assertTrue(command.IsActive())
        command.Activated()
        self.assertIn('Body', app.Console.PrintMessage.call_args[0][0])
        self.assertIn('PartDesign_Pad', app.Console.PrintWarning.call_args[0][0])
