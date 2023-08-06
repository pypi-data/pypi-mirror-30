import unittest
import collections
from fontTools.misc.py23 import basestring
from fontParts.base import FontPartsError


class TestPoint(unittest.TestCase):

    def getPoint_generic(self):
        contour, unrequested = self.objectGenerator("contour")
        unrequested.append(contour)
        contour.appendPoint((0, 0), "move")
        contour.appendPoint((101, 202), "line")
        point = contour.points[1]
        return point

    # ----
    # Type
    # ----

    def test_get(self):
        point = self.getPoint_generic()
        # get
        self.assertEqual(
            point.type,
            "line"
        )

    def test_set_move(self):
        point = self.getPoint_generic()
        point.type = "move"
        self.assertEqual(
            point.type,
            "move"
        )

    def test_set_curve(self):
        point = self.getPoint_generic()
        point.type = "curve"
        self.assertEqual(
            point.type,
            "curve"
        )

    def test_set_wcurve(self):
        point = self.getPoint_generic()
        point.type = "qcurve"
        self.assertEqual(
            point.type,
            "qcurve"
        )

    def test_set_offcurve(self):
        point = self.getPoint_generic()
        point.type = "offcurve"
        self.assertEqual(
            point.type,
            "offcurve"
        )

    def test_set_invalid_point_type_string(self):
        point = self.getPoint_generic()
        with self.assertRaises(ValueError):
            point.type = "xxx"

    def test_set_invalid_point_type_int(self):
        point = self.getPoint_generic()
        with self.assertRaises(TypeError):
            point.type = 123

    # ----------
    # Identifier
    # ----------

    def test_identifier_get_none(self):
        point = self.getPoint_generic()
        self.assertIsNone(point.identifier)

    def test_identifier_generated_type(self):
        point = self.getPoint_generic()
        point.generateIdentifier()
        self.assertIsInstance(point.identifier, basestring)

    def test_identifier_consistency(self):
        point = self.getPoint_generic()
        point.generateIdentifier()
        # get: twice to test consistency
        self.assertEqual(point.identifier, point.identifier)

    def test_identifier_cannot_set(self):
        # identifier is a read-only property
        point = self.getPoint_generic()
        with self.assertRaises(FontPartsError):
            point.identifier = "ABC"

    # ----
    # Hash
    # ----

    def test_hash(self):
        point = self.getPoint_generic()
        self.assertEqual(
            isinstance(point, collections.Hashable),
            False
        )

    # --------
    # Equality
    # --------

    def test_object_equal_self(self):
        point_one = self.getPoint_generic()
        self.assertEqual(
            point_one,
            point_one
        )

    def test_object_not_equal_other(self):
        point_one = self.getPoint_generic()
        point_two = self.getPoint_generic()
        self.assertNotEqual(
            point_one,
            point_two
        )

    def test_object_equal_self_variable_assignment(self):
        point_one = self.getPoint_generic()
        a = point_one
        self.assertEqual(
            point_one,
            a
        )

    def test_object_not_equal_other_variable_assignment(self):
        point_one = self.getPoint_generic()
        point_two = self.getPoint_generic()
        a = point_one
        self.assertNotEqual(
            point_two,
            a
        )

    # ---------
    # Selection
    # ---------

    def test_selected_true(self):
        point = self.getPoint_generic()
        try:
            point.selected = False
        except NotImplementedError:
            return
        point.selected = True
        self.assertEqual(
            point.selected,
            True
        )

    def test_selected_false(self):
        point = self.getPoint_generic()
        try:
            point.selected = False
        except NotImplementedError:
            return
        self.assertEqual(
            point.selected,
            False
        )
