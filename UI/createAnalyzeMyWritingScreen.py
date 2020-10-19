# This file has all the code for how to use the Analyze My Writing screen

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QTextEdit
from PyQt5.QtGui import QIcon, QTextCursor, QColor, QTextBlock
import spacy
import sys
from .analyzeMyWritingScreen import Ui_MainWindow
from acadWritingFeaturesAnalysisFiles.spellingAndGrammarCheck import languageCheckFunction
from acadWritingFeaturesAnalysisFiles.acadMWEs.usingAcadMWEs import MWEAnalyzer
from acadWritingFeaturesAnalysisFiles.acadWordLists.usingAVL import useAVLFunction
# TODO make the file below into a class so I don't have to import each indiv function
from acadWritingFeaturesAnalysisFiles.acadGrammarStuff.longmanGrammarStuff import calculateNounsFunction, percentageOfNounsAsPronounsFunction, dualGenderReferenceFunction

class AnalyzeMyWritingScreenWindow(QMainWindow):
    def __init__(self):
        super(AnalyzeMyWritingScreenWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # Make object for MWEAnalyzer class (MWE check part)
        self.mweAnalyzerObject = MWEAnalyzer()
        # Set up language check button click
        self.ui.pushButton_2.clicked.connect(self.runLanguageCheckFunction)
        self.ui.pushButton.clicked.connect(self.runAcadWritingCheckFunction)
        # Connect the function which highlights the corresponding suggestion when each suggestion is clicked
        #   .itemSelectionChanged is a PyQT thing
        self.ui.listWidget.itemSelectionChanged.connect(self.findHighlightedSuggestionFromList)
        self.selection = None
        self.listOfSelections = []
    
    # This function is what highlights all the suggestions when either of the language suggestion buttons is clicked
    def highlightingFunction(self, startIndex, endIndex):
        self.selection = QTextEdit.ExtraSelection()
        lineColor = QColor(QtCore.Qt.cyan)
        self.selection.format.setBackground(lineColor)
        textCursor = self.ui.textEdit.textCursor()
        # hard coding the positions for now w/ testing
        textCursor.setPosition(startIndex)
        # .KeepAnchor is so it treats the first selection (startIndex) is "kept" as an anchor
        #   so it highlights from the anchor and doesn't just set a new "anchor" with the endIndex
        textCursor.setPosition(endIndex, QTextCursor.KeepAnchor)
        self.selection.cursor = textCursor
        self.listOfSelections.append(self.selection)    

    # This function is what highlights & scrolls the user to the appropriate suggestion in their input writing when they click
    #   on the suggestion in the list on the right
    # Once the user clicks the list item (suggestion), assign the cursor to the correct highlighting in the text, scroll the view
    #   down to wherever the correct suggestion is, highlight it in a different color, and repaint/refresh the text edit view so
    #   all these changes are applied
    def findHighlightedSuggestionFromList(self):
        itemSelectedByUser = self.ui.listWidget.currentItem()
        # .row() has to be called because it returns a QModelIndex item (?), which must be built to be able to have columns
        #   and rows (??) - I only have rows though so just fix it with .row()
        itemSelectedByUser_Index = self.ui.listWidget.indexFromItem(itemSelectedByUser).row()
        for selection in self.listOfSelections:
            # set each back to cyan - this is so when it loops around, it first sets everything to cyan, then does its thing
            #   in case the user clicked on the list, then clicked it again, so it clears all previous highlighting except cyan
            lineColor = QColor(QtCore.Qt.cyan)
            selection.format.setBackground(lineColor)
        # Since might be a couple items that do not have a specific highlighted spot (e.g. the % of nouns), check to make sure
        #   the item index isn't greater than the list of selections
        #   if its index is greater, that means it is a selection which doesn't have a highlight and 
        #   should be ignored/it shouldn't look for its corresponding highlight because there is none
        if itemSelectedByUser_Index < len(self.listOfSelections):
            # Match highlighted text selection to its corresponding list selection (clicked by user)
            matchHighlightToListSelection = self.listOfSelections[itemSelectedByUser_Index]
            # then make it red so it stands out
            matchHighlightToListSelection.format.setBackground(QColor(QtCore.Qt.red))
            # make cursor the same as in the highlighting function, then scroll to it (if necessary)
            #   get the position of it and make a new variable - don't take the actual one or it treats it as a highlight
            #   rather than a position and won't take the red
            textCursor = matchHighlightToListSelection.cursor
            actualTextCursor = self.ui.textEdit.textCursor()
            actualTextCursor.setPosition(textCursor.position())
            # set cursor
            self.ui.textEdit.setTextCursor(actualTextCursor)
            # scroll if necessary
            self.ui.textEdit.ensureCursorVisible()
        # Re-set it so it's updated to the current state of the suggestions (w/ colors, etc.) & repaint
        self.ui.textEdit.setExtraSelections(self.listOfSelections)
        self.ui.textEdit.repaint()
        
    # When the Grammar/English Language button is clicked, it will read the text & run my grammar script
    def runLanguageCheckFunction(self):
        self.listOfSelections = []
        self.ui.listWidget.clear()
        inputAsPlainText = self.ui.textEdit.toPlainText()
        matches = languageCheckFunction(inputAsPlainText)
        for eachMatch in matches:
            stringMatch = str(eachMatch)
            # To add them into the list thing on the right
            makeQItem = QListWidgetItem(stringMatch)
            self.ui.listWidget.addItem(makeQItem)
            # To make the highlighting correct off of the indices
            startIndex = eachMatch.startIndex
            endIndex = eachMatch.endIndex
            self.highlightingFunction(startIndex, endIndex)
        self.ui.textEdit.setExtraSelections(self.listOfSelections)
        # .repaint() so it forces the ui to redraw the widget w/ the new highlighting
        self.ui.textEdit.repaint()
            
    # When the Check My Writing button is clicked, it will read the text & run my acad writing (grammar, MWEs, acad language) scripts
    def runAcadWritingCheckFunction(self):
        self.listOfSelections = []
        #lineColor = QColor(QtCore.Qt.red)
        #self.selection.format.setBackground(lineColor)
        #self.ui.textEdit.setExtraSelections([self.selection])
        self.ui.listWidget.clear()
        inputAsPlainText = self.ui.textEdit.toPlainText()

        # MWE check
        matchesMWESuggestionsAndExacts = self.mweAnalyzerObject.gettingSuggestionsFunction(inputAsPlainText)
        listOfSuggestedMWEs = matchesMWESuggestionsAndExacts[0]
        listOfExactMWEs = matchesMWESuggestionsAndExacts[1]
        for eachMatchMWE in listOfSuggestedMWEs:
            # To add them into the list thing on the right
            stringMatch = str(eachMatchMWE)
            makeQItem = QListWidgetItem(stringMatch)
            self.ui.listWidget.addItem(makeQItem)
            # To make the highlighting correct off of the indices
            startIndexMWEOrigWord = eachMatchMWE.startOfWordIndex
            endIndexMWEOrigWord = startIndexMWEOrigWord + len(' '.join(eachMatchMWE.listOfWordsWritingSample))
            self.highlightingFunction(startIndexMWEOrigWord, endIndexMWEOrigWord)
        
        # Acad Vocab List
        matchesAVL = useAVLFunction(inputAsPlainText)
        # Have to add .items() so it gives me a list of items (tuples) - matchesAVL is a dict in this case
        #   .items() has to happen so I can actually turn the dict into something I can loop over here
        for eachMatchAVL in matchesAVL.items():
            isAValidAVLSuggestion = True
            # This part is to make sure the MWEs are prioritized first
            #   so any exact MWE matches to the lists OR any suggested MWEs are off limits to make AVL suggestions on
            for eachMWE in listOfSuggestedMWEs:
                firstWordIndex = eachMWE.index
                lastWordIndex = firstWordIndex + len(eachMWE.listOfWordsWritingSample)
                # 0 is to open up the key for eachMatchAVL (dict w/ keys as word as a spacy obj),
                #  the .i is to get the word index
                if eachMatchAVL[0].i >= firstWordIndex \
                and eachMatchAVL[0].i <= lastWordIndex:
                    isAValidAVLSuggestion = False
                    break
            # Prioritizing anything that was an exact MWE in the original text
            for eachMWE in listOfExactMWEs:
                firstWordIndex = eachMWE.index
                lastWordIndex = firstWordIndex + len(eachMWE.listOfWordsWritingSample)
                # 0 is to open up the key for eachMatchAVL (dict w/ keys as word as a spacy obj),
                #  the .i is to get the word index
                if eachMatchAVL[0].i >= firstWordIndex \
                and eachMatchAVL[0].i <= lastWordIndex:
                    isAValidAVLSuggestion = False
                    break
            # Checking to see which words were not re-labeled as 'False' - those ones are the valid suggestions
            #   So if any words make it past here, it means they were not tossed out in either of the MWE lists (labeled False)
            if isAValidAVLSuggestion == True:
                stringMatch = ('Original Word: ' + str(eachMatchAVL[0]) + '\nSuggested Word(s): ' + str(eachMatchAVL[1]))
                # To add them into the list thing on the right
                makeQItem = QListWidgetItem(stringMatch)
                self.ui.listWidget.addItem(makeQItem)
                # To make the highlighting correct off of the indices
                startIndexAVLOrigWord = eachMatchAVL[0].idx
                endIndexAVLOrigWord = startIndexAVLOrigWord + len(eachMatchAVL[0].text)
                self.highlightingFunction(startIndexAVLOrigWord, endIndexAVLOrigWord)
        
        # Acad Grammar Stuff
        # spacy stuff
        nlp = spacy.load('en_core_web_sm')
        inputWritingTagged = nlp(inputAsPlainText)
        # actual stuff
        matchesLongman = dualGenderReferenceFunction(inputWritingTagged)
        for eachMatchLongman in matchesLongman:
            # To add them into the list thing on the right
            makeQItem = QListWidgetItem(eachMatchLongman.suggestion)
            self.ui.listWidget.addItem(makeQItem)
            # To make the highlighting correct off of the indices
            startIndex = eachMatchLongman.startIndex
            endIndex = eachMatchLongman.endIndex
            self.highlightingFunction(startIndex, endIndex)
        # These ones that don't have a specific highlighted spot at the bottom - so they're always last on the list
        percentageNouns = calculateNounsFunction(inputWritingTagged)
        makeQItem = QListWidgetItem(str(percentageNouns))
        self.ui.listWidget.addItem(makeQItem)
        percentagePronouns = percentageOfNounsAsPronounsFunction(inputWritingTagged)
        makeQItem = QListWidgetItem(str(percentagePronouns))
        self.ui.listWidget.addItem(makeQItem)
        self.ui.textEdit.setExtraSelections(self.listOfSelections)
        # .repaint() so it forces the ui to redraw the widget w/ the new highlighting
        self.ui.textEdit.repaint()
        