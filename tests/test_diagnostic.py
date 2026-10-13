"""Diagnostic errors must be useful without exporting private host details."""
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

spec = importlib.util.spec_from_file_location('etux_diagnostic_test',
    Path(__file__).resolve().parents[1] / 'tools/diagnose_freecad.py')
diagnostic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diagnostic)


class DiagnosticTests(unittest.TestCase):
    def setup_host(self, registered=True):
        app = SimpleNamespace(Version=lambda: ['1', '1', '3'])
        gui = Mock()
        gui.listWorkbenches.return_value = ['ETUXWorkbench'] if registered else []
        gui.Control.activeDialog.return_value = False
        gui.activeWorkbench.return_value.name.return_value = 'PartDesignWorkbench'
        gui.getWorkbench.return_value._etux_ribbon_enabled = False
        core = Mock()
        core.qVersion.return_value = '6.8.3'
        core.QObject = type('QObject', (), {'__module__': 'PySide6.QtCore'})
        return app, gui, (core, Mock())

    def test_missing_registration_is_not_masked_by_manual_loader(self):
        app, gui, qt = self.setup_host(False)
        report = diagnostic.run(app, gui, qt)
        self.assertEqual(report['status'], 'fail')
        self.assertEqual(report['errors'][0]['code'], 'workbench_not_loaded')
        gui.addWorkbench.assert_not_called()
        gui.activateWorkbench.assert_not_called()

    def test_native_task_blocks_without_changing_session(self):
        app, gui, qt = self.setup_host()
        gui.Control.activeDialog.return_value = True
        self.assertEqual(diagnostic.run(app, gui, qt)['status'], 'blocked')
        gui.activateWorkbench.assert_not_called()

    def test_failure_does_not_leak_paths_models_or_tracebacks(self):
        app, gui, qt = self.setup_host()
        secret = 'C:/Users/PrivateName/Documents/SecretModel.FCStd'
        gui.activateWorkbench.side_effect = RuntimeError(secret)
        report = diagnostic.run(app, gui, qt)
        serialized = json.dumps(report)
        self.assertEqual(report['status'], 'fail')
        for forbidden in ('PrivateName', 'SecretModel', 'C:/Users', 'Traceback'):
            self.assertNotIn(forbidden, serialized)
        self.assertEqual(report['errors'][0]['error_type'], 'RuntimeError')
        gui.getWorkbench.return_value.setRibbonEnabled.assert_called_with(False)
