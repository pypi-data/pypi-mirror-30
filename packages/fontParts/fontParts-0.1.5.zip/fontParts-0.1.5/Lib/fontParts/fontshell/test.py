from fontParts.test import testEnvironment
from fontParts.fontshell.font import RFont
from fontParts.fontshell.info import RInfo
from fontParts.fontshell.groups import RGroups
from fontParts.fontshell.kerning import RKerning
from fontParts.fontshell.features import RFeatures
from fontParts.fontshell.layer import RLayer
from fontParts.fontshell.glyph import RGlyph
from fontParts.fontshell.contour import RContour
from fontParts.fontshell.segment import RSegment
from fontParts.fontshell.bPoint import RBPoint
from fontParts.fontshell.point import RPoint
from fontParts.fontshell.anchor import RAnchor
from fontParts.fontshell.component import RComponent
from fontParts.fontshell.image import RImage
from fontParts.fontshell.lib import RLib
from fontParts.fontshell.guideline import RGuideline


# defcon does not have prebuilt support for
# selection states, so we simulate selection
# behavior with a small subclasses for testing
# purposes only.

def _get_selected(self):
    if isinstance(self, NLTestSegment):
        for point in self.points:
            if point.selected:
                return True
        return False
    elif isinstance(self, NLTestBPoint):
        point = self._point.naked()
        return point.name == "selected"
    elif isinstance(self, NLTestPoint):
        return self.name == "selected"
    else:
        if not hasattr(self.naked(), "_testSelected"):
            return False
        return self.naked()._testSelected


def _set_selected(self, value):
    if isinstance(self, NLTestSegment):
        for point in self.points:
            point.selected = value
    elif isinstance(self, NLTestBPoint):
        point = self._point.naked()
        if value:
            point.name = "selected"
        else:
            point.name = None
    elif isinstance(self, NLTestPoint):
        if value:
            self.name = "selected"
        else:
            self.name = None
    else:
        self.naked()._testSelected = value


class NLTestPoint(RPoint):

    _get_selected = _get_selected
    _set_selected = _set_selected


class NLTestBPoint(RBPoint):

    _get_selected = _get_selected
    _set_selected = _set_selected


class NLTestSegment(RSegment):

    _get_selected = _get_selected
    _set_selected = _set_selected


class NLTestGuideline(RGuideline):

    _get_selected = _get_selected
    _set_selected = _set_selected


class NLTestImage(RImage):

    _get_selected = _get_selected
    _set_selected = _set_selected


class NLTestAnchor(RAnchor):

    _get_selected = _get_selected
    _set_selected = _set_selected


class NLTestComponent(RComponent):

    _get_selected = _get_selected
    _set_selected = _set_selected


class NLTestContour(RContour):

    segmentClass = NLTestSegment
    bPointClass = NLTestBPoint
    pointClass = NLTestPoint
    _get_selected = _get_selected
    _set_selected = _set_selected


class NLTestGlyph(RGlyph):

    contourClass = NLTestContour
    componentClass = NLTestComponent
    anchorClass = NLTestAnchor
    guidelineClass = NLTestGuideline
    _get_selected = _get_selected
    _set_selected = _set_selected


class NLTestLayer(RLayer):

    glyphClass = NLTestGlyph
    _get_selected = _get_selected
    _set_selected = _set_selected


class NLTestFont(RFont):

    layerClass = NLTestLayer
    guidelineClass = NLTestGuideline
    _get_selected = _get_selected
    _set_selected = _set_selected


classMapping = dict(
    font=NLTestFont,
    info=RInfo,
    groups=RGroups,
    kerning=RKerning,
    features=RFeatures,
    layer=NLTestLayer,
    glyph=NLTestGlyph,
    contour=NLTestContour,
    segment=NLTestSegment,
    bPoint=NLTestBPoint,
    point=NLTestPoint,
    anchor=NLTestAnchor,
    component=NLTestComponent,
    image=NLTestImage,
    lib=RLib,
    guideline=NLTestGuideline,
)


def fontshellObjectGenerator(cls):
    unrequested = []
    obj = classMapping[cls]()
    return obj, unrequested


if __name__ == "__main__":
    import sys
    if {"-v", "--verbose"}.intersection(sys.argv):
        verbosity = 2
    else:
        verbosity = 1
    testEnvironment(fontshellObjectGenerator, verbosity=verbosity)
