"""Session behavior/failure paths; native integration is in the GUI smoke."""
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from et_freecad_ux.adapters.sketch import SketchRibbonSession


def sketch(document='Piece', name='Sketch'):
    return SimpleNamespace(Object=SimpleNamespace(
        isDerivedFrom=lambda kind: kind == 'Sketcher::SketchObject',
        Document=SimpleNamespace(Name=document), Name=name))


class SketchSessionTests(unittest.TestCase):
    def setUp(self):
        self.gui, self.ribbon = Mock(), Mock()
        self.gui.activeDocument.return_value = None
        self.session = SketchRibbonSession(self.gui, self.ribbon)
        self.session.queue = Mock()
        self.ribbon.tabs.currentIndex.return_value = 2

    def test_explicit_return_to_etux_during_sketch_detects_existing_editor(self):
        self.gui.activeDocument.return_value = SimpleNamespace(getInEdit=lambda: sketch())
        self.session.start()
        self.assertEqual(self.session.edit, ('Piece', 'Sketch'))
        self.assertEqual(self.session.previous_tab, 2)

    def test_native_handoff_requires_departure_and_sketch_edit(self):
        s = self.session
        s.departed()
        s.workbench_changed('SketcherWorkbench')
        self.assertIsNone(s.edit)
        s.slotInEdit(sketch())
        self.assertEqual(s.edit, ('Piece', 'Sketch'))
        self.assertEqual(s.previous_tab, 2)
        self.assertFalse(s.departing)
        self.ribbon.deactivate.assert_not_called()

    def test_workbench_signal_precedes_old_deactivated_hook(self):
        s = self.session
        s.workbench_changed('SketcherWorkbench')
        self.assertTrue(s.departing)
        s.departed()
        s.slotInEdit(sketch())
        self.assertEqual(s.edit, ('Piece', 'Sketch'))
        self.ribbon.deactivate.assert_not_called()

    def test_manual_switch_without_edit_does_not_keep_ribbon(self):
        s = self.session
        s.start()
        s.departed()
        s.workbench_changed('SketcherWorkbench')
        self.gui.activeDocument.return_value = SimpleNamespace(getInEdit=lambda: None)
        s.apply()
        self.ribbon.deactivate.assert_called_once()
        self.ribbon.bar.show.assert_not_called()

    def test_voluntary_switch_during_edit_releases_surface(self):
        s = self.session
        s.edit = ('Piece', 'Sketch')
        s.workbench_changed('PartDesignWorkbench')
        self.ribbon.deactivate.assert_called_once()
        self.gui.activateWorkbench.assert_not_called()

    def test_document_switch_and_close_release_only_active_session(self):
        s = self.session
        s.edit = ('Piece', 'Sketch')
        other = SimpleNamespace(Document=SimpleNamespace(Name='Other'))
        s.slotDeletedDocument(other)
        self.ribbon.deactivate.assert_not_called()
        s.slotActivateDocument(other)
        self.ribbon.deactivate.assert_called_once()

    def test_reset_ignores_other_objects_and_restores_previous_tab(self):
        s = self.session
        s.start()
        s.slotInEdit(sketch())
        s.slotResetEdit(sketch(name='Other'))
        self.assertIsNotNone(s.edit)
        s.slotResetEdit(sketch())
        s.apply()
        self.ribbon.tabs.setCurrentIndex.assert_called_once_with(2)
        self.assertIsNone(s.edit)
        self.assertIsNone(s.previous_tab)

    def test_stop_is_idempotent_and_releases_timer_observer_signal(self):
        s = self.session
        s.start()
        timer = s.timer = Mock()
        s.edit = ('Piece', 'Sketch')
        s.stop()
        s.stop()
        timer.stop.assert_called_once()
        timer.deleteLater.assert_called_once()
        self.gui.removeDocumentObserver.assert_called_once_with(s)
        s.window.workbenchActivated.disconnect.assert_called_once_with(s.workbench_changed)
        self.assertIsNone(s.edit)

    def test_partial_registration_failure_removes_observer(self):
        s = self.session
        s.window.workbenchActivated.connect.side_effect = RuntimeError('missing signal')
        with self.assertRaises(RuntimeError):
            s.start()
        self.gui.removeDocumentObserver.assert_called_once_with(s)
        self.assertFalse(s.observing)

    def test_unrelated_edit_cannot_borrow_ribbon(self):
        s = self.session
        s.name = 'SketcherWorkbench'
        s.slotInEdit(sketch())
        self.assertIsNone(s.edit)
        self.assertIsNone(s.previous_tab)
