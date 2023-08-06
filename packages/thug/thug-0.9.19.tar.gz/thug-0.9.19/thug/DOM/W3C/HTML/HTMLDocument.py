#!/usr/bin/env python

import logging
import six
import six.moves.urllib.parse as urlparse
import bs4 as BeautifulSoup

from thug.DOM.W3C.Document import Document
from thug.DOM.W3C.HTML.HTMLBodyElement import HTMLBodyElement
from .text_property import text_property
from .xpath_property import xpath_property


log = logging.getLogger("Thug")


class HTMLDocument(Document):
    title       = xpath_property("/html/head/title/text()")
    # body        = xpath_property("/html/body[1]", readonly = True)
    images      = xpath_property("//img", readonly = True)
    applets     = xpath_property("//applet", readonly = True)
    # forms       = xpath_property("//form", readonly = True)
    links       = xpath_property("//a[@href]", readonly = True)
    anchors     = xpath_property("//a[@name]", readonly = True)
    innerHTML   = text_property()

    def __init__(self, doc, win = None, referer = None, lastModified = None, cookie = ''):
        Document.__init__(self, doc)

        self._win           = win
        self._body          = HTMLBodyElement(self.doc, self.doc.find('body'))
        self._referer       = referer
        self._lastModified  = lastModified
        self._cookie        = cookie
        self._html          = None
        self._readyState    = "loading"
        self._domain        = urlparse.urlparse(self._win.url).hostname if self._win else ''
        self.current        = None

        self.__init_personality()

    def __init_personality(self):
        if log.ThugOpts.Personality.isIE():
            self.__init_personality_IE()
            return

        if log.ThugOpts.Personality.isFirefox():
            self.__init_personality_Firefox()
            return

        if log.ThugOpts.Personality.isChrome():
            self.__init_personality_Chrome()
            return

        if log.ThugOpts.Personality.isSafari():
            self.__init_personality_Safari()
            return

        if log.ThugOpts.Personality.isOpera():
            self.__init_personality_Opera()

    def __init_personality_IE(self):
        from thug.DOM.W3C.DocumentCompatibleInfoCollection import DocumentCompatibleInfoCollection

        if log.ThugOpts.Personality.browserMajorVersion < 8:
            self._compatible = None
        else:
            self._compatible = DocumentCompatibleInfoCollection(self.doc, [])

        if log.ThugOpts.Personality.browserMajorVersion > 7:
            self.implementation.createHTMLDocument = self.implementation._createHTMLDocument

        if log.ThugOpts.Personality.browserMajorVersion < 11:
            self.all = self._all
            self.createStyleSheet = self._createStyleSheet

    def __init_personality_Firefox(self):
        self.implementation.createHTMLDocument = self.implementation._createHTMLDocument

    def __init_personality_Chrome(self):
        self.all = self._all
        self.implementation.createHTMLDocument = self.implementation._createHTMLDocument

    def __init_personality_Safari(self):
        self.all = self._all
        self.implementation.createHTMLDocument = self.implementation._createHTMLDocument

    def __init_personality_Opera(self):
        self.implementation.createHTMLDocument = self.implementation._createHTMLDocument

    def __getattr__(self, attr):
        if attr in ('getBoxObjectFor', ) and not log.ThugOpts.Personality.isFirefox():
            raise AttributeError

        if self._win and getattr(self._win, "doc", None):
            if attr in self._win.doc.DFT.handled_on_events:
                return None

            if attr in self._win.doc.DFT._on_events:
                return None

        _attr = self.getElementById(attr)
        if _attr:
            return _attr

        log.info("[HTMLDocument] Undefined: %s", attr)
        raise AttributeError

    def getWindow(self):
        return self._win

    def setWindow(self, win):
        self._win = win

    window = property(getWindow, setWindow)

    @property
    def body(self):
        return self._body

    @property
    def tag(self):
        return self

    @property
    def _node(self):
        return self

    @property
    def referrer(self):
        if self._referer:
            return str(self._referer)

        return ""

    @property
    def forms(self):
        from .HTMLCollection import HTMLCollection
        from thug.DOM.W3C.DOMImplementation import DOMImplementation

        return HTMLCollection(self.doc, [DOMImplementation.createHTMLElement(self.doc, f) for f in self.doc.find_all('form')])

    @property
    def styleSheets(self):
        from .HTMLCollection import HTMLCollection
        from thug.DOM.W3C.DOMImplementation import DOMImplementation

        return HTMLCollection(self.doc, [DOMImplementation.createHTMLElement(self.doc, f) for f in self.doc.find_all('style')])

    @property
    def lastModified(self):
        return self._lastModified

    def getCookie(self):
        return self._cookie

    def setCookie(self, value):
        self._cookie = value

    cookie = property(getCookie, setCookie)

    def getDomain(self):
        return self._domain

    def setDomain(self, value):
        self._domain = value

    domain = property(getDomain, setDomain)

    @property
    def URL(self):
        return self._win.url if self._win else ''

    @property
    def documentElement(self):
        from .HTMLElement import HTMLElement
        return HTMLElement(self, self.doc.find('html'))

    # FIXME
    @property
    def readyState(self):
        return self._readyState

    @property
    def compatMode(self):
        return "CSS1Compat"

    def getCompatible(self):
        return self._compatible

    def setCompatible(self, compatible):
        from .HTMLDocumentCompatibleInfo import HTMLDocumentCompatibleInfo
        from thug.DOM.W3C.DocumentCompatibleInfoCollection import DocumentCompatibleInfoCollection

        _compatibles = list()

        if log.ThugOpts.Personality.isIE() and log.ThugOpts.Personality.browserMajorVersion >= 8:
            for s in compatible.split(';'):
                try:
                    (useragent, version) = s.split('=')
                except ValueError:
                    # Ignore the http-equiv X-UA-Compatible content if its
                    # format is not correct
                    return

                for v in version.split(','):
                    p = HTMLDocumentCompatibleInfo(useragent, v)
                    _compatibles.append(p)

            self._compatible = DocumentCompatibleInfoCollection(self.doc, _compatibles)

    compatible = property(getCompatible, setCompatible)

    @property
    def documentMode(self):
        # version = log.ThugOpts.Personality.browserVersion
        major   = log.ThugOpts.Personality.browserMajorVersion

        if major < 8:
            return 7 if self.compatMode in ("CSS1Compat", ) else 5

        self.window.doc.DFT.force_handle_meta_x_ua_compatible()

        engine = 0

        for index in range(self.compatible.length):
            item = self.compatible.item(index)
            if not item.userAgent.lower() in ("ie", ):
                continue

            _version = item.version.lower()
            if _version in ('edge', ):
                engine = major
                break

            mode_version = _version

            if _version.startswith('emulateie'):
                mode_version = _version.split("emulateie")[1]

            try:
                mode_version = int(mode_version)
            except ValueError:
                continue

            if mode_version not in (5, 7, 8, 9, 10):
                continue

            if mode_version <= major and mode_version >= engine:
                engine = mode_version

        if not engine:
            engine = min(major, 10)

        return engine

    def open(self, mimetype = 'text/html', replace = False):
        self._html = six.StringIO()

        return self

    def close(self):
        if self._html is None:
            return

        html = self._html.getvalue()
        self._html.close()
        self._html = None

        self.doc = BeautifulSoup.BeautifulSoup(html, "html5lib")

    def write(self, html):
        log.HTMLClassifier.classify(log.ThugLogging.url if log.ThugOpts.local else self.URL, html)

        if self._html:
            self._html.write(unicode(html))
            return

        tag  = self.current
        body = self.doc.find('body')

        if tag.parent is None:
            parent = body
        else:
            parent = body if body and tag.parent.name in ('html', ) else tag.parent

        if isinstance(html, six.integer_types):
            html = unicode(html)

        for t in BeautifulSoup.BeautifulSoup(html, "html.parser").contents:
            if isinstance(t, six.string_types):
                child = list(parent.children)[-1]

                if isinstance(child, BeautifulSoup.NavigableString):
                    child.string.replace_with(child.string + t)
                if isinstance(child, BeautifulSoup.Tag):
                    child.append(t)

            if isinstance(t, BeautifulSoup.Tag):
                parent.insert(len(parent.contents), t)

            name = getattr(t, "name", None)
            if name in ('script', None):
                continue

            try:
                handler = getattr(self._win.doc.DFT, "handle_%s" % (name, ), None)
            except Exception:
                handler = getattr(log.DFT, "handle_%s" % (name, ), None)

            if handler:
                handler(t)

    def writeln(self, text):
        self.write(text + "\n")

    # DOM Level 2 moves getElementbyId in Document object inherited by
    # HTMLDocument
    #
    # def getElementById(self, elementId):
    #    tag = self.doc.find(id = elementId)
    #    return DOMImplementation.createHTMLElement(self.doc, tag) if tag else None

    def getElementsByName(self, elementName):
        from .HTMLCollection import HTMLCollection

        tags = self.doc.find_all(attrs = {'name': elementName})
        return HTMLCollection(self.doc, tags)

    @property
    def _all(self):
        from .HTMLAllCollection import HTMLAllCollection

        s = [p for p in self.doc.find_all(text = False)]
        return HTMLAllCollection(self.doc, s)

    def _createStyleSheet(self, URL = None, index = None):
        # Creates a styleSheet object and inserts it into the current document.
        # The createStyleSheet method is only supported by Internet Explorer.
        # In other browsers, use the createElement method to create a new link
        # or style element, and the insertBefore or appendChild method to insert
        # it into the document.
        #
        # URL Optional. String that specifies the URL of a style file. If an
        # URL is specified, a new link element is inserted into the current
        # document that imports the style file. If this parameter is not specified
        # or an empty string is set, then an empty style element is inserted into
        # the current document.
        #
        # index Optional. Integer that specifies the position of the new styleSheet
        # object in the styleSheets collection of the document. This parameter
        # also has effect on the source position of the inserted link or style
        # element. If this parameter is not specified, the new styleSheet object
        # is inserted at the end of the styleSheets collection and the new link or
        # style element is inserted after the other link and style elements in
        # source order.

        _type = 'style' if not URL else 'link'

        obj = self.createElement(_type)
        if _type in ('link', ):
            obj.href = URL
            obj.rel = "stylesheet"

        head = self.getElementsByTagName("head")[0]
        if head is None:
            return obj

        if index is None:
            head.appendChild(obj)
            return obj

        length  = len(head.childNodes)
        matches = 0
        pos     = 0

        while pos < length:
            if head.childNodes[pos].tagName.lower() in (_type, ):
                matches += 1

            if matches > index:
                head.insertBefore(obj, head.childNodes[pos])
                break

            pos += 1

        if matches <= index:
            head.appendChild(obj)

        return obj
