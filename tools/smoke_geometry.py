"""Native FreeCAD geometry and document checks; never collected without the host."""
import tempfile
import unittest
from pathlib import Path

import FreeCAD as App
import Part


class GeometryTests(unittest.TestCase):
    def setUp(self):
        self.previous = App.ActiveDocument.Name if App.ActiveDocument else None
        self.doc = App.newDocument("ETUXGeometrySmoke")

    def tearDown(self):
        if self.doc and self.doc.Name in App.listDocuments():
            App.closeDocument(self.doc.Name)
        if self.previous in App.listDocuments():
            App.setActiveDocument(self.previous)

    def box(self):
        box = self.doc.addObject("Part::Box", "Box")
        box.Length, box.Width, box.Height = 2, 3, 4
        self.doc.recompute()
        return box

    def test_box_is_valid_with_expected_volume(self):
        box = self.box()
        self.assertTrue(box.Shape.isValid())
        self.assertEqual(len(box.Shape.Solids), 1)
        self.assertAlmostEqual(box.Shape.Volume, 24.0, places=7)

    def test_boolean_cut_is_valid_with_expected_volume(self):
        result = Part.makeBox(2, 3, 4).cut(Part.makeBox(1, 2, 4))
        self.assertFalse(result.isNull())
        self.assertTrue(result.isValid())
        self.assertAlmostEqual(result.Volume, 16.0, places=7)

    def test_parametric_edit_undo_redo(self):
        self.doc.UndoMode = 1
        box = self.box()
        self.doc.openTransaction("ETUX smoke edit")
        box.Length = 5
        self.doc.recompute()
        self.doc.commitTransaction()
        self.assertAlmostEqual(box.Shape.Volume, 60.0, places=7)
        self.doc.undo()
        self.doc.recompute()
        self.assertAlmostEqual(box.Shape.Volume, 24.0, places=7)
        self.doc.redo()
        self.doc.recompute()
        self.assertAlmostEqual(box.Shape.Volume, 60.0, places=7)

    def test_fcstd_roundtrip_preserves_geometry(self):
        self.box()
        with tempfile.TemporaryDirectory(prefix="etux-geometry-") as directory:
            path = Path(directory) / "Geometry.FCStd"
            self.doc.saveAs(str(path))
            self.assertGreater(path.stat().st_size, 0)
            App.closeDocument(self.doc.Name)
            self.doc = None
            self.doc = App.openDocument(str(path))
            self.doc.recompute()
            box = self.doc.getObject("Box")
            self.assertIsNotNone(box)
            self.assertTrue(box.Shape.isValid())
            self.assertAlmostEqual(box.Length.Value, 2.0, places=7)
            self.assertAlmostEqual(box.Shape.Volume, 24.0, places=7)
