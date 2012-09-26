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


class Window(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent, QtCore.Qt.Drawer |
                                     QtCore.Qt.WindowStaysOnTopHint)

        self.createLayout()
        self.createTrayIcon()

        QtCore.QMetaObject.connectSlotsByName(self)

        self.setWindowIcon(QtGui.QIcon(':/icon.png'))
        self.setWindowTitle("Google Translate")
        self.resize(800, 220)

        # list of required and unrequired div names
        self.exception_items = ['#gt-ft',
                                '#select-document',
                                '#gt-res-tip',
                                '#select_document']
        self.required_items = ['#gt-form-c']

        # open links in system's browser
        self.webView.page().mainFrame().page().setLinkDelegationPolicy(
            QtWebKit.QWebPage.DelegateAllLinks)

        self.setContextMenuPolicy(QtCore.Qt.NoContextMenu)

    def createLayout(self):
        self.verticalLayout = QtGui.QVBoxLayout()
        # no borders around translator
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.webView = QtWebKit.QWebView()
        self.webView.setObjectName("webView")
        self.webView.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.webView.setUrl(QtCore.QUrl("http://translate.google.com"))
        self.verticalLayout.addWidget(self.webView)
        self.setLayout(self.verticalLayout)

    def createTrayIcon(self):
        self.trayIconMenu = QtGui.QMenu(self)
        self.quitAction = QtGui.QAction(QtGui.QIcon(":/close.png"),
                                        'Quit', self,
                                        triggered=QtGui.qApp.quit)
        self.trayIconMenu.addAction(self.quitAction)

        self.trayIcon = QtGui.QSystemTrayIcon(QtGui.QIcon(":/icon.png"), self)
        self.trayIcon.setContextMenu(self.trayIconMenu)
        self.trayIcon.activated.connect(self.iconActivated)
        self.trayIcon.show()

    def iconActivated(self, reason):
        if reason == QtGui.QSystemTrayIcon.Trigger:
            self.setVisible(not self.isVisible())

    def closeEvent(self, event):
        '''on close window becomes hidden and can be restored via tray icon'''
        if self.trayIcon.isVisible():
            self.hide()
            event.ignore()

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
        '''open link in external browser'''
        QtGui.QDesktopServices.openUrl(url)

    def on_webView_loadFinished(self, ok):
        # if user is trying to open link to another resource
        url = str(self.webView.url().toString())
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
            self.trayIcon.showMessage('Google Translate started',
                                      'Press on tray icon to reveal it',
                                      QtGui.QSystemTrayIcon.NoIcon, 5000)


if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    QtGui.QApplication.setQuitOnLastWindowClosed(False)

    window = Window()
    window.hide()
    sys.exit(app.exec_())
