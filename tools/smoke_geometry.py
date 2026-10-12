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

    def mechanical_profile(self):
        import Sketcher
        body = self.doc.addObject('PartDesign::Body', 'Body')
        sketch = body.newObject('Sketcher::SketchObject', 'Sketch')
        circle = sketch.addGeometry(Part.Circle(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 5), False)
        radius = sketch.addConstraint(Sketcher.Constraint('Radius', circle, 5.0))
        self.doc.recompute()
        return body, sketch, radius

    def mechanical_pad(self):
        body, sketch, radius = self.mechanical_profile()
        pad = body.newObject('PartDesign::Pad', 'Pad')
        pad.Profile, pad.Length = sketch, 10
        self.doc.recompute()
        return body, sketch, pad, radius

    def test_body_creation(self):
        body = self.doc.addObject('PartDesign::Body', 'Body')
        self.assertEqual(body.TypeId, 'PartDesign::Body')
        self.assertIs(body.Document, self.doc)

    def test_sketch_creation_in_body(self):
        body, sketch, radius = self.mechanical_profile()
        self.assertIn(sketch, body.Group)
        self.assertEqual(sketch.TypeId, 'Sketcher::SketchObject')
        self.assertEqual(sketch.solve(), 0)
        self.assertEqual(sketch.ConstraintCount, 1)

    def test_parametric_pad_creation(self):
        import math
        body, sketch, pad, radius = self.mechanical_pad()
        self.assertEqual(pad.Profile[0], sketch)
        self.assertEqual(body.Tip, pad)
        self.assertTrue(pad.Shape.isValid())
        self.assertEqual(len(pad.Shape.Solids), 1)
        self.assertAlmostEqual(pad.Shape.Volume, math.pi * 25 * 10, places=6)

    def test_sketch_dimension_recomputes_pad_with_undo_redo(self):
        import math
        self.doc.UndoMode = 1
        body, sketch, pad, radius = self.mechanical_pad()
        self.doc.openTransaction('Change sketch radius')
        sketch.setDatum(radius, App.Units.Quantity('7 mm'))
        self.doc.recompute()
        self.doc.commitTransaction()
        self.assertTrue(pad.Shape.isValid())
        self.assertAlmostEqual(pad.Shape.Volume, math.pi * 49 * 10, places=6)
        self.doc.undo()
        self.doc.recompute()
        self.assertAlmostEqual(pad.Shape.Volume, math.pi * 25 * 10, places=6)
        self.doc.redo()
        self.doc.recompute()
        self.assertAlmostEqual(pad.Shape.Volume, math.pi * 49 * 10, places=6)
