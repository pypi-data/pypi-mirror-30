def OpenFont(path, showInterface=True):
    """
    Open font located at **path**. If **showInterface**
    is ``False``, the font should be opened without
    graphical interface. The default for **showInterface**
    is ``True``.

    ::

        from fontParts.world import *

        font = OpenFont("/path/to/my/font.ufo")
        font = OpenFont("/path/to/my/font.ufo", showInterface=False)
    """
    return dispatcher["OpenFont"](path=path, showInterface=showInterface)

def NewFont(familyName=None, styleName=None, showInterface=True):
    """
    Create a new font. **familyName** will be assigned
    to ``font.info.familyName`` and **styleName**
    will be assigned to ``font.info.styleName``. These
    are optional and default to ``None``. If **showInterface**
    is ``False``, the font should be created without
    graphical interface. The default for **showInterface**
    is ``True``.

    ::

        from fontParts.world import *

        font = NewFont()
        font = NewFont(familyName="My Family", styleName="My Style")
        font = NewFont(showInterface=False)
    """
    return dispatcher["NewFont"](familyName=familyName, styleName=styleName, showInterface=showInterface)

def CurrentFont():
    """
    Get the "current" font.
    """
    return dispatcher["CurrentFont"]()

def CurrentGlyph():
    """
    Get the "current" glyph from :func:`CurrentFont`.

    ::

        from fontParts.world import *

        glyph = CurrentGlyph()
    """
    return dispatcher["CurrentGlyph"]()

def CurrentLayer():
    """
    Get the "current" layer from :func:`CurrentGlyph`.

    ::

        from fontParts.world import *

        layer = CurrentLayer()
    """
    return dispatcher["CurrentLayer"]()

def CurrentContours():
    """
    Get the "currently" selected contours from :func:`CurrentGlyph`.

    ::

        from fontParts.world import *

        contours = CurrentContours()

    This returns an immutable list, even when nothing is selected.
    """
    return dispatcher["CurrentContours"]()

def _defaultCurrentContours():
    glyph = CurrentGlyph()
    if glyph is None:
        return ()
    return glyph.selectedContours

def CurrentSegments():
    """
    Get the "currently" selected segments from :func:`CurrentContours`.

    ::

        from fontParts.world import *

        segments = CurrentSegments()

    This returns an immutable list, even when nothing is selected.
    """
    return dispatcher["CurrentSegments"]()

def _defaultCurrentSegments():
    glyph = CurrentGlyph()
    if glyph is None:
        return ()
    segments = []
    for contour in glyph.selectedContours:
        segments.extend(contour.selectedSegments)
    return tuple(segments)

def CurrentPoints():
    """
    Get the "currently" selected points from :func:`CurrentContours`.

    ::

        from fontParts.world import *

        points = CurrentPoints()

    This returns an immutable list, even when nothing is selected.
    """
    return dispatcher["CurrentPoints"]()

def _defaultCurrentPoints():
    glyph = CurrentGlyph()
    if glyph is None:
        return ()
    points = []
    for contour in glyph.selectedContours:
        points.extend(contour.selectedPoints)
    return tuple(points)

def CurrentComponents():
    """
    Get the "currently" selected components from :func:`CurrentGlyph`.

    ::

        from fontParts.world import *

        components = CurrentComponents()

    This returns an immutable list, even when nothing is selected.
    """
    return dispatcher["CurrentComponents"]()

def _defaultCurrentComponents():
    glyph = CurrentGlyph()
    if glyph is None:
        return ()
    return glyph.selectedComponents

def CurrentAnchors():
    """
    Get the "currently" selected anchors from :func:`CurrentGlyph`.

    ::

        from fontParts.world import *

        anchors = CurrentAnchors()

    This returns an immutable list, even when nothing is selected.
    """
    return dispatcher["CurrentAnchors"]()

def _defaultCurrentAnchors():
    glyph = CurrentGlyph()
    if glyph is None:
        return ()
    return glyph.selectedAnchors

def CurrentGuidelines():
    """
    Get the "currently" selected guidelines from :func:`CurrentGlyph`.
    This will include both font level and glyph level guidelines.

    ::

        from fontParts.world import *

        guidelines = CurrentGuidelines()

    This returns an immutable list, even when nothing is selected.
    """
    return dispatcher["CurrentGuidelines"]()

def _defaultCurrentGuidelines():
    guidelines = []
    font = CurrentFont()
    if font is not None:
        guidelines.extend(font.selectedGuidelines)
    glyph = CurrentGlyph()
    if glyph is not None:
        guidelines.extend(glyph.selectedGuidelines)
    return tuple(guidelines)

def AllFonts():
    """
    Get a list of all open fonts.

    * XXX should this include fonts with showInterface=False?
    * XXX define the special sorting methods that must be in the return object.

    ::

        from fontParts.world import *

        fonts = AllFonts()
        for font in fonts:
            # do something
    """
    return dispatcher["AllFonts"]()

def RFont(path=None, showInterface=True):
    return dispatcher["RFont"](path=path, showInterface=showInterface)

def RGlyph():
    return dispatcher["RGlyph"]()

# ----------
# Dispatcher
# ----------

class _EnvironmentDispatcher(object):

    def __init__(self, registryItems):
        self._registry = {item: None for item in registryItems}

    def __setitem__(self, name, func):
        self._registry[name] = func

    def __getitem__(self, name):
        func = self._registry[name]
        if func is None:
            raise NotImplementedError
        return func

dispatcher = _EnvironmentDispatcher([
    "OpenFont",
    "NewFont",
    "AllFonts",
    "CurrentFont",
    "CurrentGlyph",
    "CurrentLayer",
    "CurrentContours",
    "CurrentSegments",
    "CurrentPoints",
    "CurrentComponents",
    "CurrentAnchors",
    "CurrentGuidelines",
    "RFont",
    "RGlyph"
])

# Register the default functions.

dispatcher["CurrentContours"] = _defaultCurrentContours
dispatcher["CurrentSegments"] = _defaultCurrentSegments
dispatcher["CurrentPoints"] = _defaultCurrentPoints
dispatcher["CurrentComponents"] = _defaultCurrentComponents
dispatcher["CurrentAnchors"] = _defaultCurrentAnchors
dispatcher["CurrentGuidelines"] = _defaultCurrentGuidelines

# -------
# fontshell
# -------

try:
    from fontParts import fontshell

    # OpenFont, RFont

    def _fontshellRFont(path=None, showInterface=True):
        return fontshell.RFont(pathOrObject=path, showInterface=showInterface)

    dispatcher["OpenFont"] = _fontshellRFont
    dispatcher["RFont"] = _fontshellRFont

    # NewFont

    def _fontshellNewFont(familyName=None, styleName=None, showInterface=True):
        font = fontshell.RFont(showInterface=showInterface)
        if familyName is not None:
            font.info.familyName = familyName
        if styleName is not None:
            font.info.styleName = styleName
        return font

    dispatcher["NewFont"] = _fontshellNewFont

except ImportError:
    pass
