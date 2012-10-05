#!/usr/bin/env python

###################################################################
## This script is written for educational purposes only,
## all rights of translation services reserved by Google.
## Icons provided by following authors:
## -close icon by New Mooon, http://code.google.com/u/newmooon/
##  (http://www.iconfinder.com/icondetails/28414/16/close_gtk_icon)
## -book icon by Double-J designs - http://www.doublejdesign.co.uk/
##  (http://www.iconfinder.com/icondetails/69442/48/_icon)
###################################################################

from PyQt4 import QtCore, QtGui, QtWebKit
# here be icons
import qrc_resource


class WebView(QtWebKit.QWebView):
    def __init__(self, parent=None):
        super(WebView, self).__init__()
        self.disableAction(QtWebKit.QWebPage.SetTextDirectionDefault)
        self.disableAction(QtWebKit.QWebPage.SetTextDirectionLeftToRight)
        self.disableAction(QtWebKit.QWebPage.SetTextDirectionRightToLeft)
        self.disableAction(QtWebKit.QWebPage.Forward)
        self.disableAction(QtWebKit.QWebPage.Back)

    def disableAction(self, action):
        menu = self.page().action(action)
        menu.setVisible(False)
        menu.setEnabled(False)

    def contextMenuEvent(self, event):
        result = self.page().mainFrame().hitTestContent(event.pos())
        if result.linkUrl().isEmpty():
            super(WebView, self).contextMenuEvent(event)


class Window(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.createLayout()
        self.createMenuBar()

        QtCore.QMetaObject.connectSlotsByName(self)

        self.setWindowIcon(QtGui.QIcon(':/icon.png'))
        self.setWindowTitle("Google Translate")
        self.resize(800, 250)

        # list of required divs names
        self.required_items = ['#gt-form-c']
        # exceptions for some child elements of required divs
        self.exception_items = ['#gt-ft',
                                '#select-document',
                                '#gt-res-tip',
                                '#select_document']

        # open links in system's browser
        self.webView.page().mainFrame().page().setLinkDelegationPolicy(
            QtWebKit.QWebPage.DelegateAllLinks)

    def createLayout(self):
        # no borders around translator
        self.webView = WebView()
        self.webView.setObjectName("webView")
        self.webView.setUrl(QtCore.QUrl("http://translate.google.com"))
        self.setCentralWidget(self.webView)

    def createMenuBar(self):
        self.menuBar = self.menuBar()

        self.quitAction = QtGui.QAction(QtGui.QIcon(":/close.png"),
                                        'Quit', self,
                                        triggered=QtGui.qApp.quit)
        self.onTopAction = QtGui.QAction('Always on top', self,
                                         toggled=self.swapAlwaysOnTop)
        self.onTopAction.setCheckable(True)
        self.onTopAction.setChecked(False)

        fileMenu = self.menuBar.addMenu('&File')
        fileMenu.addAction(self.quitAction)

        self.viewMenu = self.menuBar.addMenu('&View')
        self.viewMenu.addAction(self.onTopAction)

    def swapAlwaysOnTop(self, alwaysOnTop):
        visible = self.isVisible()
        if alwaysOnTop:
            self.setWindowFlags(self.windowFlags() |
                                QtCore.Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() &
                                ~QtCore.Qt.WindowStaysOnTopHint)
        self.setVisible(visible)

    def getElements(self, tag, required_items, exception_elements=[],
                    add_parent=False):
        '''form a list of elements based on their id`s'''
        required_elements = []
        for item in required_items:
            for element in self.document.findAll(item):
                required_elements.append(element)
                if add_parent:
                    required_elements.append(element.parent())
                # children must be appended to list too
                children = element.findAll(tag)
                for child in children:
                    # if some children are in exception list then ignore them
                    if not child in exception_elements:
                        required_elements.append(child)
        return required_elements

    def on_webView_linkClicked(self, url):
        #open link in external browser'''
        QtGui.QDesktopServices.openUrl(url)

    def on_webView_loadFinished(self, ok):
        # if user is trying to open link to another resource
        url = unicode(self.webView.url().toString())
        g_domain = "http://translate.google"
        if (not url.startswith(g_domain) or
                (url.startswith(g_domain) and "/translate?" in url)):
            # redirect back to google translate and open link in browser
            QtGui.QDesktopServices.openUrl(self.webView.url())
            self.webView.setUrl(QtCore.QUrl("http://translate.google.com"))

        frame = self.webView.page().mainFrame()
        self.document = frame.documentElement()

        # form list of corresponding div elements
        exception_elements = self.getElements('div', self.exception_items)
        required_elements = self.getElements('div', self.required_items,
                                             exception_elements, True)

        # delete any divs that are not required
        delete_elements = self.document.findAll('div')
        for element in delete_elements:
            if not element in required_elements:
                element.removeFromDocument()

        if not self.isVisible():
            self.show()


if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)

    window = Window()
    sys.exit(app.exec_())
