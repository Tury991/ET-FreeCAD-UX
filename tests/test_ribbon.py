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


class ModernRibbonTests(unittest.TestCase):
    def test_all_verified_commands_once_and_same_order_for_densities(self):
        from et_freecad_ux.core.ribbon import ribbon_sections, DENSITIES
        actions = {command: object() for group in GROUPS for command in group.commands}
        layouts = [ribbon_sections(actions) for _ in DENSITIES]
        self.assertEqual(layouts[0], layouts[1])
        flattened = [c for _, groups in layouts[0] for _, commands, _ in groups for c, _ in commands]
        self.assertEqual(len(flattened), len(actions))
        self.assertEqual(set(flattened), set(actions))
        self.assertEqual([tab for tab, _ in layouts[0]], ['Features', 'Sketch', 'Reference', 'Tools'])
        for _, groups in layouts[0]:
            for _, commands, _ in groups:
                for command, action in commands:
                    self.assertIs(action, actions[command])

    def test_missing_capabilities_never_create_new_commands(self):
        from et_freecad_ux.core.ribbon import ribbon_sections
        sentinel = object()
        layout = ribbon_sections({'PartDesign_Pad': sentinel})
        self.assertEqual([(c, a) for _, groups in layout for _, commands, _ in groups for c, a in commands],
                         [('PartDesign_Pad', sentinel)])

    def test_density_persists_in_addon_namespace_and_invalid_value_falls_back(self):
        from et_freecad_ux.adapters.ribbon import read_density, write_density, PREFERENCE_PATH
        data = {}
        params = SimpleNamespace(GetString=lambda key, default: data.get(key, default),
                                 SetString=lambda key, value: data.__setitem__(key, value))
        app = Mock()
        app.ParamGet.return_value = params
        self.assertEqual(read_density(app), 'classic')
        write_density(app, 'compact')
        self.assertEqual(read_density(app), 'compact')
        self.assertEqual(data, {'RibbonDensity': 'compact'})
        self.assertEqual({call.args for call in app.ParamGet.call_args_list}, {(PREFERENCE_PATH,)})
        data['RibbonDensity'] = 'unknown'
        self.assertEqual(read_density(app), 'classic')
        with self.assertRaises(ValueError):
            write_density(app, 'unknown')

    def test_mode_change_when_disabled_needs_no_qt_and_applies_on_next_activation(self):
        from et_freecad_ux.adapters.ribbon import read_density
        app = Mock()
        data = {}
        app.ParamGet.return_value = SimpleNamespace(
            GetString=lambda key, default: data.get(key, default),
            SetString=lambda key, value: data.__setitem__(key, value))
        wb = create_workbench_class(object)()
        wb._etux_ribbon = None
        with patch.dict(sys.modules, {'FreeCAD': app, 'PySide': None}):
            for key in ('compact', 'classic') * 5:
                wb.setRibbonDensity(key)
                self.assertEqual(read_density(app), key)
                self.assertEqual(wb._etux_ribbon_density, key)
        controller = RibbonController(Mock(), (), Mock())
        with patch.dict(sys.modules, {'PySide': None}):
            controller.set_density('compact')
        self.assertEqual(controller.mode, 'compact')

    def test_missing_qt_fails_with_native_fallback(self):
        wb = create_workbench_class(object)()
        wb._etux_ribbon = None
        wb._etux_groups = GROUPS
        app = Mock()
        with patch.dict(sys.modules, {'FreeCAD': app, 'FreeCADGui': Mock(), 'PySide': None}):
            wb.setRibbonEnabled(True)
        self.assertFalse(wb._etux_ribbon_enabled)
        self.assertIsNone(wb._etux_ribbon.bar)
        self.assertEqual(wb._etux_ribbon.saved_sizes, [])
        app.Console.PrintWarning.assert_called_once()

    def test_density_update_failure_restores_native_ui(self):
        wb = create_workbench_class(object)()
        wb._etux_ribbon = Mock()
        wb._etux_ribbon.set_density.side_effect = RuntimeError('deleted widget')
        with patch.dict(sys.modules, {'FreeCAD': Mock(), 'FreeCADGui': Mock()}):
            wb.setRibbonDensity('compact')
        self.assertFalse(wb._etux_ribbon_enabled)
        wb._etux_ribbon.deactivate.assert_called_once()

    def test_focus_callbacks_are_removed_before_widget_destruction(self):
        controller = RibbonController(Mock(), (), Mock())
        button, focus_filter, bar = Mock(), Mock(), Mock()
        controller.buttons = [(button, True)]
        controller.focus_filter = focus_filter
        controller.bar = bar
        events = []
        button.removeEventFilter.side_effect = lambda f: events.append('disconnect')
        bar.deleteLater.side_effect = lambda: events.append('destroy')
        controller.deactivate()
        controller.deactivate()
        self.assertEqual(events, ['disconnect', 'destroy'])
        focus_filter.deleteLater.assert_called_once()
        self.assertIsNone(controller.focus_filter)
