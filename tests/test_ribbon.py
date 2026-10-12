"""Failure and lifecycle contracts without pretending to validate Qt rendering."""
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from et_freecad_ux.adapters.ribbon import resolve_toolbar_actions
from et_freecad_ux.core.catalog import GROUPS
from et_freecad_ux.ui.workbench import create_workbench_class
from et_freecad_ux.ui.ribbon import RibbonController


class RibbonTests(unittest.TestCase):
    def test_reordered_native_actions_fail_before_mutating_bars(self):
        bar = Mock()
        actions = [Mock() for _ in GROUPS[0].commands]
        for action, command in zip(actions, reversed(GROUPS[0].commands)):
            action.objectName.return_value = command
        bar.actions.return_value = actions
        window = Mock()
        window.findChildren.return_value = [bar]
        with self.assertRaises(RuntimeError):
            resolve_toolbar_actions(window, GROUPS, SimpleNamespace(QToolBar=object))
        bar.setMaximumSize.assert_not_called()

    def test_pending_activation_is_cancelled_on_deactivation(self):
        controller = RibbonController(Mock(), (), Mock())
        timer = Mock()
        controller.activation_timer = timer
        controller.deactivate()
        controller.deactivate()
        timer.stop.assert_called_once()
        timer.deleteLater.assert_called_once()
        self.assertIsNone(controller.activation_timer)

    def test_missing_or_ambiguous_toolbar_fails_safely(self):
        window = Mock()
        for bars in ([], [Mock(), Mock()]):
            window.findChildren.return_value = bars
            with self.assertRaises(RuntimeError):
                resolve_toolbar_actions(window, GROUPS, SimpleNamespace(QToolBar=object))

    def test_incomplete_actions_fail_before_hiding(self):
        bar = Mock()
        bar.actions.return_value = []
        window = Mock()
        window.findChildren.return_value = [bar]
        with self.assertRaises(RuntimeError):
            resolve_toolbar_actions(window, GROUPS, SimpleNamespace(QToolBar=object))
        bar.hide.assert_not_called()

    def test_deactivate_restores_original_sizes_once_without_visibility_writes(self):
        controller = RibbonController(Mock(), (), Mock())
        visible, hidden = Mock(), Mock()
        controller.saved_sizes = [(visible, 'min1', 'max1'), (hidden, 'min2', 'max2')]
        controller.bar = Mock()
        bar = controller.bar
        controller.deactivate()
        controller.deactivate()
        visible.setMinimumSize.assert_called_once_with('min1')
        hidden.setMaximumSize.assert_called_once_with('max2')
        visible.setVisible.assert_not_called()
        hidden.setVisible.assert_not_called()
        bar.deleteLater.assert_called_once()

    def test_failed_renderer_disables_opt_in_and_restores(self):
        wb = create_workbench_class(object)()
        wb._etux_ribbon = Mock()
        wb._etux_ribbon.activate.side_effect = RuntimeError('Qt unavailable')
        app = Mock()
        with patch.dict(sys.modules, {'FreeCAD': app, 'FreeCADGui': Mock()}):
            wb.setRibbonEnabled(True)
        self.assertFalse(wb._etux_ribbon_enabled)
        wb._etux_ribbon.deactivate.assert_called_once()
        app.Console.PrintWarning.assert_called_once()
