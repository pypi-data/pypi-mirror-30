import unittest2 as unittest
from fontParts.base.deprecated import RemovedWarning


class TestDeprecated(unittest.TestCase):

    # ----
    # Font
    # ----

    def test_font_removed_getParent(self):
        font, _ = self.objectGenerator("font")
        with self.assertRaises(RemovedWarning):
            font.getParent()

    def test_font_removed_generateGlyph(self):
        font, _ = self.objectGenerator("font")
        with self.assertRaises(RemovedWarning):
            font.generateGlyph()

    def test_font_removed_compileGlyph(self):
        font, _ = self.objectGenerator("font")
        with self.assertRaises(RemovedWarning):
            font.compileGlyph()

    def test_font_removed_getGlyphNameToFileNameFunc(self):
        font, _ = self.objectGenerator("font")
        with self.assertRaises(RemovedWarning):
            font.getGlyphNameToFileNameFunc()

    def test_font_deprecated_update(self):
        # As changed() is defined by the environment, only test if a Warning is issued.
        font, _ = self.objectGenerator("font")
        with self.assertWarnsRegex(DeprecationWarning, "Font.changed()"):
            font.update()

    def test_font_deprecated_setChanged(self):
        # As changed() is defined by the environment, only test if a Warning is issued.
        font, _ = self.objectGenerator("font")
        with self.assertWarnsRegex(DeprecationWarning, "Font.changed()"):
            font.setChanged()

    def test_font_removed_setParent(self):
        font, _ = self.objectGenerator("font")
        with self.assertRaises(RemovedWarning):
            font.setParent(font)

    # ------
    # Anchor
    # ------

    def getAnchor(self):
        glyph, _ = self.objectGenerator("glyph")
        glyph.appendAnchor("anchor 0", (0, 0))
        return glyph

    def test_anchor_deprecated__generateIdentifer(self):
        anchor, _ = self.objectGenerator("anchor")
        with self.assertWarnsRegex(DeprecationWarning, "Anchor._generateIdentifier()"):
            anchor._generateIdentifier()
        self.assertEqual(
            anchor._generateIdentifier(),
            anchor._getIdentifier()
        )

    def test_anchor_deprecated_generateIdentifer(self):
        anchor, _ = self.objectGenerator("anchor")
        with self.assertWarnsRegex(DeprecationWarning, "Anchor.generateIdentifier()"):
            anchor.generateIdentifier()
        self.assertEqual(
            anchor.generateIdentifier(),
            anchor.getIdentifier()
        )

    def test_anchor_deprecated_getParent(self):
        glyph = self.getAnchor()
        anchor = glyph.anchors[0]
        with self.assertWarnsRegex(DeprecationWarning, "Anchor.getParent()"):
            anchor.getParent()
        self.assertEqual(
            anchor.getParent(),
            anchor.glyph
        )

    def test_anchor_deprecated_update(self):
        # As changed() is defined by the environment, only test if a Warning is issued.
        anchor, _ = self.objectGenerator("anchor")
        with self.assertWarnsRegex(DeprecationWarning, "Anchor.changed()"):
            anchor.update()

    def test_anchor_deprecated_setChanged(self):
        # As changed() is defined by the environment, only test if a Warning is issued.
        anchor, _ = self.objectGenerator("anchor")
        with self.assertWarnsRegex(DeprecationWarning, "Anchor.changed()"):
            anchor.setChanged()

    def test_anchor_removed_setParent(self):
        glyph = self.getAnchor()
        anchor = glyph.anchors[0]
        with self.assertRaises(RemovedWarning):
            anchor.setParent(glyph)

    def test_anchor_removed_draw(self):
        glyph = self.getAnchor()
        pen = glyph.getPen()
        anchor = glyph.anchors[0]
        with self.assertRaises(RemovedWarning):
            anchor.draw(pen)

    def test_anchor_removed_drawPoints(self):
        glyph = self.getAnchor()
        pen = glyph.getPen()
        anchor = glyph.anchors[0]
        with self.assertRaises(RemovedWarning):
            anchor.drawPoints(pen)

    # -----
    # Layer
    # -----

    def test_layer_deprecated_getParent(self):
        font, _ = self.objectGenerator("font")
        for name in "ABCD":
            font.newLayer("layer " + name)
        layer = font.layers[0]
        with self.assertWarnsRegex(DeprecationWarning, "Layer.font"):
            layer.getParent()
        self.assertEqual(layer.getParent(), layer.font)

    def test_layer_deprecated_update(self):
        # As changed() is defined by the environment, only test if a Warning is issued.
        layer, _ = self.objectGenerator("layer")
        with self.assertWarnsRegex(DeprecationWarning, "Layer.changed()"):
            layer.update()

    def test_layer_deprecated_setChanged(self):
        # As changed() is defined by the environment, only test if a Warning is issued.
        layer, _ = self.objectGenerator("layer")
        with self.assertWarnsRegex(DeprecationWarning, "Layer.changed()"):
            layer.setChanged()

    def test_layer_removed_setParent(self):
        font, _ = self.objectGenerator("font")
        for name in "ABCD":
            font.newLayer("layer " + name)
        layer = font.layers[0]
        with self.assertRaises(RemovedWarning):
            layer.setParent(font)

    # --------
    # Features
    # --------

    def test_features_deprecated_getParent(self):
        font, _ = self.objectGenerator("font")
        features = font.features
        features.text = "# Test"
        with self.assertWarnsRegex(DeprecationWarning, "Features.font"):
            features.getParent()
        self.assertEqual(features.getParent(), features.font)

    def test_features_deprecated_update(self):
        # As changed() is defined by the environment, only test if a Warning is issued.
        features, _ = self.objectGenerator("features")
        with self.assertWarnsRegex(DeprecationWarning, "Features.changed()"):
            features.update()

    def test_features_deprecated_setChanged(self):
        # As changed() is defined by the environment, only test if a Warning is issued.
        features, _ = self.objectGenerator("features")
        with self.assertWarnsRegex(DeprecationWarning, "Features.changed()"):
            features.setChanged()

    def test_feature_removed_setParent(self):
        font, _ = self.objectGenerator("font")
        features = font.features
        features.text = "# Test"
        with self.assertRaises(RemovedWarning):
            features.setParent(font)

    def test_feature_removed_round(self):
        feature, _ = self.objectGenerator("features")
        with self.assertRaises(RemovedWarning):
            feature.round()

    # -----
    # Image
    # -----

    def getImage_glyph(self):
        from fontParts.test.test_image import testImageData
        glyph, _ = self.objectGenerator("glyph")
        glyph.addImage(data=testImageData)
        image = glyph.image
        return image

    def test_image_deprecated_getParent(self):
        image = self.getImage_glyph()
        with self.assertWarnsRegex(DeprecationWarning, "Image.glyph"):
            image.getParent()
        self.assertEqual(image.getParent(), image.glyph)

    def test_image_deprecated_update(self):
        # As changed() is defined by the environment, only test if a Warning is issued.
        image, _ = self.objectGenerator("image")
        with self.assertWarnsRegex(DeprecationWarning, "Image.changed()"):
            image.update()

    def test_image_deprecated_setChanged(self):
        # As changed() is defined by the environment, only test if a Warning is issued.
        image, _ = self.objectGenerator("image")
        with self.assertWarnsRegex(DeprecationWarning, "Image.changed()"):
            image.setChanged()

    def test_image_removed_setParent(self):
        glyph, _ = self.objectGenerator("glyph")
        image = self.getImage_glyph()
        with self.assertRaises(RemovedWarning):
            image.setParent(glyph)

    # ----
    # Info
    # ----

    def test_info_deprecated_getParent(self):
        font, _ = self.objectGenerator("font")
        info = font.info
        info.unitsPerEm = 1000
        with self.assertWarnsRegex(DeprecationWarning, "Info.font"):
            info.getParent()
        self.assertEqual(info.getParent(), info.font)

    def test_info_deprecated_update(self):
        # As changed() is defined by the environment, only test if a Warning is issued.
        info, _ = self.objectGenerator("info")
        with self.assertWarnsRegex(DeprecationWarning, "Info.changed()"):
            info.update()

    def test_info_deprecated_setChanged(self):
        # As changed() is defined by the environment, only test if a Warning is issued.
        info, _ = self.objectGenerator("info")
        with self.assertWarnsRegex(DeprecationWarning, "Info.changed()"):
            info.setChanged()

    def test_info_removed_setParent(self):
        font, _ = self.objectGenerator("font")
        info, _ = self.objectGenerator("info")
        info.unitsPerEm = 1000
        with self.assertRaises(RemovedWarning):
            info.setParent(font)
