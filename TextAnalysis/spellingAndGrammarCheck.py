# This file is going to do a basic grammar and spelling check

import language_check 

# Make a class just to put the info I want and print only those items
#   so I don't have to take all the info that language_check outputs
class SpellingGrammarCheckResults:
    def __init__(self, errorMessage, suggestion, errorStart, errorLength, startIndex, endIndex):
        # Possible error - 'msg'
        self.errorMessage = errorMessage
        # Suggested replacements/suggestion to resolve the possible error - 'replacements'
        self.suggestion = self.cleanSuggestionText(suggestion)
        # Where the error starts - 'offset'
        self.errorStart = errorStart
        # How long the error is - 'errorlength'
        self.errorLength = errorLength

        # Things for the highlighting function later
        # Adding them for clarity/consistency with other files - technically I have these from error start/len above
        self.startIndex = startIndex
        self.endIndex = endIndex
    
    # This is so it prints normal
    def __repr__(self):
        finalPrint = 'Error Message: {0}\nSuggestion: {1}'.format(self.errorMessage, self.suggestion)
        return finalPrint

    # Clean the text on the suggestion so it doesn't print like a list
    def cleanSuggestionText(self, suggestion):
        makeString = str(suggestion)
        fixedSuggestion = makeString.replace('[\'', '').replace('\']', '')
        return fixedSuggestion
    
    # TODO make function using regex to replace ones w/ commas/etc. for multiple suggestions so it says "or"


inputWriting = open('/Users/yanisa/Code_GitHub/MAThesis_YourAcadWritingFriend/miscInputFiles_WordListsPhrasesEtc/manuallyWrittenText.txt').read()

# Getting basic errors w/ error messages
def languageCheckFunction(inputWriting):
    englishLangCheck = language_check.LanguageTool('en-US')
    matches = englishLangCheck.check(inputWriting)
    # Only return the messages I want so it isn't full of junk
    listOfMatchInfoIWant = []
    for eachMatch in matches:
        errorMessage = eachMatch.msg
        suggestion = str(eachMatch.replacements)
        errorStart = eachMatch.offset
        errorLength = eachMatch.errorlength
        # Adding these ones also for clarity/consistency with other files
        startIndex = eachMatch.offset
        endIndex = startIndex + errorLength
        putThingsInClass = SpellingGrammarCheckResults(errorMessage, suggestion, errorStart, errorLength, startIndex, endIndex)
        listOfMatchInfoIWant.append(putThingsInClass)
    print(listOfMatchInfoIWant)
    return listOfMatchInfoIWant

#languageCheckFunction(inputWriting)