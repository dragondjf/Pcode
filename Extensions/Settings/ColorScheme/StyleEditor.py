import os
from PyQt4 import QtCore, QtGui, QtXml
from PyQt4.Qsci import QsciScintilla

from Extensions.Settings.ColorScheme.ColorChooser import ColorChooser


class StyleEditor(QtGui.QWidget):

    paperChanged = QtCore.pyqtSignal()

    def __init__(self, useData, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.useData = useData

        mainLayout = QtGui.QHBoxLayout()
        self.setLayout(mainLayout)
        mainLayout.setMargin(0)

        properties = self.loadDefaultProperties()
        self.propertyListWidget = QtGui.QListWidget()
        self.propertyListWidget.setSortingEnabled(True)
        for key, value in properties.items():
            if key != "Paper":
                self.propertyListWidget.addItem(QtGui.QListWidgetItem(key))
        self.propertyListWidget.itemSelectionChanged.connect(
            self.newPropertySelected)
        mainLayout.addWidget(self.propertyListWidget)

        vbox = QtGui.QVBoxLayout()
        mainLayout.addLayout(vbox)

        label = QtGui.QLabel("Background")
        label.setStyleSheet("background: lightgrey; padding: 2px;")
        vbox.addWidget(label)

        self.backgroundColorChooser = ColorChooser()
        self.backgroundColorChooser.colorChanged.connect(self.updateBackground)
        vbox.addWidget(self.backgroundColorChooser)

        label = QtGui.QLabel("Foreground")
        label.setStyleSheet("background: lightgrey; padding: 2px;")
        vbox.addWidget(label)

        self.foregroundColorChooser = ColorChooser()
        self.foregroundColorChooser.colorChanged.connect(self.updateForeground)
        vbox.addWidget(self.foregroundColorChooser)

        ### Additional settings for elements that need them -------------------

        self.extra_settings_stack = QtGui.QStackedLayout()
        vbox.addLayout(self.extra_settings_stack)

        # empty stack for display when current property has no need of extra
        # settings
        stackWidget = QtGui.QWidget()
        self.extra_settings_stack.addWidget(stackWidget)

        ### CALLTIP Highlight Color

        stackWidget = QtGui.QWidget()
        stackBox = QtGui.QVBoxLayout()
        stackBox.setMargin(0)
        stackWidget.setLayout(stackBox)
        self.extra_settings_stack.addWidget(stackWidget)

        label = QtGui.QLabel("Highlight Text")
        label.setStyleSheet("background: lightgrey; padding: 2px;")
        stackBox.addWidget(label)

        hbox = QtGui.QHBoxLayout()
        stackBox.addLayout(hbox)

        self.callTipHighlightColorChooser = ColorChooser()
        self.callTipHighlightColorChooser.colorChanged.connect(
            self.updateCalltipHighlight)
        hbox.addWidget(self.callTipHighlightColorChooser)

        ### MARGIN FONT

        stackWidget = QtGui.QWidget()
        stackBox = QtGui.QVBoxLayout()
        stackBox.setMargin(0)
        stackWidget.setLayout(stackBox)
        self.extra_settings_stack.addWidget(stackWidget)

        label = QtGui.QLabel("Margin Font")
        label.setStyleSheet("background: lightgrey; padding: 2px;")
        stackBox.addWidget(label)

        self.fontButton = QtGui.QPushButton("Font")
        self.fontButton.clicked.connect(self.fontChanged)
        stackBox.addWidget(self.fontButton)

        ### ----------------------------------------------------------------
        vbox.addStretch(1)

        self.paperBG = QtGui.QButtonGroup()

        label = QtGui.QLabel("Paper")
        label.setStyleSheet("background: lightgrey; padding: 2px;")
        vbox.addWidget(label)

        hbox = QtGui.QHBoxLayout()
        vbox.addLayout(hbox)

        self.paperPlainButton = QtGui.QRadioButton("Plain")
        self.paperBG.addButton(self.paperPlainButton)
        self.paperPlainButton.toggled.connect(self.paperScopeChanged)
        hbox.addWidget(self.paperPlainButton)

        self.paperCustomButton = QtGui.QRadioButton("Custom")
        self.paperBG.addButton(self.paperCustomButton)
        self.paperCustomButton.setChecked(True)
        self.paperCustomButton.toggled.connect(self.paperScopeChanged)
        hbox.addWidget(self.paperCustomButton)

        self.paperColorChooser = ColorChooser()
        self.paperColorChooser.colorChanged.connect(self.updatePaper)
        hbox.addWidget(self.paperColorChooser)

        self.setCurrentProperty("Default", "Python")

        self.paperColorChooser.setColor(self.currentProperties["Paper"][1])
        if self.currentProperties["Paper"][0] == "Plain":
            self.paperColorChooser.setDisabled(True)

        self.propertyListWidget.setCurrentRow(0)

    def paperScopeChanged(self):
        if self.paperBG.checkedButton().text() == 'Plain':
            self.paperColorChooser.setDisabled(True)
        else:
            self.paperColorChooser.setDisabled(False)
        self.currentProperties["Paper"][
            0] = self.paperBG.checkedButton().text()
        self.paperColorChooser.setColor(self.currentProperties["Paper"][1])
        self.paperChanged.emit()

    def loadDefaultProperties(self):
        properties = {"Edge Line": ['#aa557f', '#ffc6c2'],
                      "Number Margin": ['#ffffff', '#949494', "Courier New", 8, False, False],
                      "Fold Margin": ['#ffffff', '#ffffff'],
                      "Fold Markers": ['#ffffff', '#bababa'],
                      "Active Line": ['#d4ffd4', '#101010'],
                      "Selection": ['#aaddff', '#1e1e1e'],
                      "White Spaces": ['#ffffff', '#000000'],
                      "Matched Braces": ['#CCCCCC', '#000000'],
                      "Unmatched Braces": ['#ff5555', '#000000'],
                      "Calltips": ["#000000", "#ffffff", "#FF3333"],
                      "Indentation Guide": ['#ffffff', '#a8a8a8'],
                      "Warnings": ['#000000', '#ffffa9'],
                      "Errors": ['#000000', '#ffaaa7'],
                      "Paper": ['Plain', '#7FE87F']}
        return properties

    def newPropertySelected(self):
        self.currentPropertyName = \
            self.propertyListWidget.currentItem().text()
        self.currentPropertyAttrib = \
            self.currentProperties[
                self.currentPropertyName]

        self.backgroundColorChooser.setColor(self.currentPropertyAttrib[0])
        self.foregroundColorChooser.setColor(self.currentPropertyAttrib[1])

        if self.currentPropertyName == "Calltips":
            self.callTipHighlightColorChooser.setColor(
                self.currentPropertyAttrib[2])
            self.extra_settings_stack.setCurrentIndex(1)
        elif self.currentPropertyName == "Number Margin":
            self.extra_settings_stack.setCurrentIndex(2)
        else:
            self.extra_settings_stack.setCurrentIndex(0)

    def updateBackground(self, color):
        self.currentPropertyAttrib[0] = color

    def updateNumberMarginFont(self):
        self.currentProperties["Number Margin"][2] = self.fontBox.currentText()
        self.currentProperties["Number Margin"][
            3] = self.fontSizeBox.currentText()

    def showLineBackground(self):
        color = QtGui.QColor(self.backgroundHexLine.text())
        if color.isValid():
            self.updateBackground(color)

    def updateCalltipHighlight(self, color):
        self.currentPropertyAttrib[2] = color

    def updateForeground(self, color):
        self.currentPropertyAttrib[1] = color

    def updatePaper(self, color):
        self.currentProperties["Paper"][1] = color
        self.paperChanged.emit()

    def setCurrentProperty(self, propertyName, groupName):
        self.currentProperties = self.loadProperties(propertyName, groupName)
        if self.currentProperties["Paper"][0] == "Plain":
            self.paperPlainButton.setChecked(True)
        else:
            self.paperCustomButton.setChecked(True)

    def fontChanged(self):
        currentfont = QtGui.QFont(self.currentPropertyAttrib[
                                  2], self.currentPropertyAttrib[3])
        currentfont.setBold(self.currentPropertyAttrib[4])
        currentfont.setItalic(self.currentPropertyAttrib[5])
        font = QtGui.QFontDialog().getFont(currentfont, self)
        if font[1]:
            font = font[0]
            name = font.rawName()
            size = font.pointSize()
            bold = font.bold()
            italic = font.italic()
            self.currentPropertyAttrib[2] = name
            self.currentPropertyAttrib[3] = size
            self.currentPropertyAttrib[4] = bold
            self.currentPropertyAttrib[5] = italic

    def applyChanges(self, viewWidget):

        viewWidget.setSelectionBackgroundColor(
            QtGui.QColor(self.currentProperties["Selection"][0]))
        viewWidget.setSelectionForegroundColor(
            QtGui.QColor(self.currentProperties["Selection"][1]))

        viewWidget.setIndentationGuidesBackgroundColor(
            QtGui.QColor(self.currentProperties["Indentation Guide"][0]))
        viewWidget.setIndentationGuidesForegroundColor(
            QtGui.QColor(self.currentProperties["Indentation Guide"][1]))

        viewWidget.setCallTipsBackgroundColor(
            QtGui.QColor(self.currentProperties["Calltips"][0]))
        viewWidget.setCallTipsForegroundColor(
            QtGui.QColor(self.currentProperties["Calltips"][1]))
        viewWidget.setCallTipsHighlightColor(QtGui.QColor(
            self.currentProperties["Calltips"][2]))

        ## Margins colors
        # line numbers margin
        viewWidget.setMarginsBackgroundColor(
            QtGui.QColor(self.currentProperties["Number Margin"][0]))
        viewWidget.setMarginsForegroundColor(
            QtGui.QColor(self.currentProperties["Number Margin"][1]))

        marginFont = QtGui.QFont(self.currentProperties["Number Margin"][2],
                                 self.currentProperties["Number Margin"][3])
        marginFont.setBold(self.currentProperties["Number Margin"][4])
        marginFont.setItalic(self.currentProperties["Number Margin"][5])
        viewWidget.setMarginsFont(marginFont)

        # folding margin colors (foreground, background)
        viewWidget.setFoldMarginColors(
            QtGui.QColor(self.currentProperties["Fold Margin"][0]),
            QtGui.QColor(self.currentProperties["Fold Margin"][1]))

        ## Edge Mode shows a vertical bar at specific number of chars
        viewWidget.setEdgeColor(QtGui.QColor(
            self.currentProperties["Edge Line"][1]))

        ## Folding visual : we will use boxes
        viewWidget.setFoldMarkersColors(
            QtGui.QColor(self.currentProperties["Fold Markers"][0]),
            QtGui.QColor(self.currentProperties["Fold Markers"][1]))

        ## Braces matching
        viewWidget.setMatchedBraceBackgroundColor(
            QtGui.QColor(self.currentProperties["Matched Braces"][0]))
        viewWidget.setMatchedBraceForegroundColor(
            QtGui.QColor(self.currentProperties["Matched Braces"][1]))
        viewWidget.setUnmatchedBraceBackgroundColor(
            QtGui.QColor(self.currentProperties["Unmatched Braces"][0]))
        viewWidget.setUnmatchedBraceForegroundColor(
            QtGui.QColor(self.currentProperties["Unmatched Braces"][1]))

        ## Editing line color
        viewWidget.setCaretWidth(2)
        viewWidget.setCaretLineBackgroundColor(
            QtGui.QColor(self.currentProperties["Active Line"][0]))
        viewWidget.setCaretForegroundColor(
            QtGui.QColor(self.currentProperties["Active Line"][1]))

        viewWidget.setWhitespaceBackgroundColor(
            QtGui.QColor(self.currentProperties["White Spaces"][0]))
        viewWidget.setWhitespaceForegroundColor(
            QtGui.QColor(self.currentProperties["White Spaces"][1]))

        viewWidget.annotationWarningStyle = QsciScintilla.STYLE_LASTPREDEFINED + 1
        viewWidget.SendScintilla(QsciScintilla.SCI_STYLESETFORE,
                                 viewWidget.annotationWarningStyle, QtGui.QColor(self.currentProperties["Warnings"][0]))
        viewWidget.SendScintilla(QsciScintilla.SCI_STYLESETBACK,
                                 viewWidget.annotationWarningStyle, QtGui.QColor(self.currentProperties["Warnings"][1]))

        viewWidget.annotationErrorStyle = viewWidget.annotationWarningStyle + 1
        viewWidget.SendScintilla(QsciScintilla.SCI_STYLESETFORE,
                                 viewWidget.annotationErrorStyle, QtGui.QColor(self.currentProperties["Errors"][0]))
        viewWidget.SendScintilla(QsciScintilla.SCI_STYLESETBACK,
                                 viewWidget.annotationErrorStyle, QtGui.QColor(self.currentProperties["Errors"][1]))

        return self.currentProperties["Paper"]

    def loadProperties(self, style_name, groupName):
        if style_name == "Default":
            properties = self.loadDefaultProperties()

            return properties

        dom_document = QtXml.QDomDocument()
        path = os.path.join(self.useData.appPathDict[
                            "stylesdir"], groupName, style_name + ".xml")
        file = open(path, "r")
        dom_document.setContent(file.read())
        file.close()

        properties = {}

        rootElement = dom_document.documentElement()
        propertyElement = rootElement.firstChild()
        propertyElement = propertyElement.nextSiblingElement().toElement()
        node = propertyElement.firstChild()
        while node.isNull() is False:
            tag = node.toElement()
            name = tag.text()
            background = tag.attribute("background")
            foreground = tag.attribute("foreground")

            properties[name] = [background, foreground]
            if name == "Calltips":
                properties[name].append(tag.attribute("highLight"))
            if name == "Number Margin":
                properties[name].append(tag.attribute("font"))
                properties[name].append(int(tag.attribute("size")))
                bold = (tag.attribute("bold") == "True")
                properties[name].append(bold)
                italic = (tag.attribute("italic") == "True")
                properties[name].append(italic)
            node = node.nextSibling()

        return properties