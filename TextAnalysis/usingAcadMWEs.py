# This file will look at all the MWEs and see if they're being used correctly

import copy, re

# Filepaths for MWE lists in buildTreeFunction

# Make sure input is what you want before running (there are diff sample texts to choose from)
inputWriting = open('/Users/yanisa/Code_GitHub/MAThesis_YourAcadWritingFriend/miscInputFiles_WordListsPhrasesEtc/manuallyWrittenText.txt').read()

### CLASSES ###
# First, make a class which stores each of the results (potential almost MWEs) from the writing sample and their traits
class AcadMWECandidate:
    def __init__(self, index, firstWord, startOfWordIndex):
        # Parameters & Properties
        self.index = index
        self.listOfWordsWritingSample = [firstWord]
        self.listOfWordsSuggestedMWE = [firstWord]
        self.startOfWordIndex = startOfWordIndex

        # Properties - only properties
        self.numExtraWords = 0
    
    # So it will print nicely
    def __repr__(self):
        finalPrint = '\nOrig: ' + ' '.join(self.listOfWordsWritingSample) + '\nSuggested: ' + ' '.join(self.listOfWordsSuggestedMWE)
        return finalPrint

# The stuff in this class all goes into the above class (AcadMWECandidate) to actually run the program
class MWEAnalyzer:
    def __init__(self):
        # Properties
        self.dictOfRootWords = self.buildTreeFunction()
        self.listToBeSuggested = []
        self.listOfExactMWEMatchesInText = []
        self.inputWritingAsList = []
        self.inputWritingAsListRemoveSomePunct = []

    def gettingSuggestionsFunction(self, inputWriting):
        # Clear the list here so everytime it prints it doesn't print the entire thing again and just prints the added ones
        #   in case the user clicked the button multiple times, so it doesn't re-print duplicates
        self.listToBeSuggested = []
        # Same for this list - list is clear here
        self.listOfExactMWEMatchesInText = []
        # Making the input writing into a list - split on the spaces to get each word
        # Note: this means punctuation is included in words that have it attached - want . ! ? so suggestions dont span sentences
        self.inputWritingAsList = inputWriting.replace('\n', ' ').split(' ')
        # Clean out all punctuation
        # TODO commas?
        interimInputWritingAsListRemoveSomePunct = re.sub(r'[^\w\s]','', inputWriting.replace('\n', ' '))
        self.inputWritingAsListRemoveSomePunct = interimInputWritingAsListRemoveSomePunct.split(' ')

        startOfWordIndex = 0 # to have the baseline
        # Using range because I want to be getting the number (index) the word is on to navigate the tree structure
        for eachWordToBeIndexed in range(0, len(self.inputWritingAsList)):
            actualWordText = self.inputWritingAsList[eachWordToBeIndexed]
            actualWordTextLower = self.inputWritingAsListRemoveSomePunct[eachWordToBeIndexed].lower()
            if actualWordTextLower in self.dictOfRootWords:
                # Make currentResult & currentLevel variables, then go into the function
                currentLevel = self.dictOfRootWords[actualWordTextLower]
                currentResult = AcadMWECandidate(eachWordToBeIndexed, actualWordText, startOfWordIndex)
                self.acadMWESuggestionFinderFunction(currentResult, currentLevel)
            # getting the index of the next word
            #   This is so it can be counting the index as it goes through the text (+1 is for the space)
            startOfWordIndex = startOfWordIndex + len(actualWordText) + 1
        newListNoDuplicates = self.duplicateRemover(self.listToBeSuggested)
        return newListNoDuplicates, self.listOfExactMWEMatchesInText

    def buildTreeFunction(self):
        acadCollocationList = open('/Users/yanisa/Code_GitHub/MAThesis_YourAcadWritingFriend/miscInputFiles_WordListsPhrasesEtc/acadCollocationList.txt').read()
        acadFormulasList = open('/Users/yanisa/Code_GitHub/MAThesis_YourAcadWritingFriend/miscInputFiles_WordListsPhrasesEtc/acadFormulasList.txt').read()
        multiWordExpressionsListLiu = open('/Users/yanisa/Code_GitHub/MAThesis_YourAcadWritingFriend/miscInputFiles_WordListsPhrasesEtc/MWElist_LiuStudy.txt').read()

        # Split each of the MWE lists on the \n and put them all into one list, then into one set
        # Made the set in case there are duplicates between the different lists
        interimListToBeMadeSet = []
        splitACL = acadCollocationList.split('\n')
        interimListToBeMadeSet.extend(splitACL)
        splitAFL = acadFormulasList.split('\n')
        interimListToBeMadeSet.extend(splitAFL)
        splitMWELiu = multiWordExpressionsListLiu.split('\n')
        interimListToBeMadeSet.extend(splitMWELiu)
        setWithAllMWELists = set(interimListToBeMadeSet)

        # Building the tree
        # This dict contains all the root (i.e. first) words .. eg if this has 'academic', it will recursively contain everything
        #   that started with 'academic'
        dictOfRootWords = {}
        for eachMWE in setWithAllMWELists:
            # Ignore anything w/ my name - added my name onto anything I am unsure what to do about them yet
            if 'YANISA' in eachMWE:
                continue
            # Split on the spaces to get each word (this is fine because no punct in my lists)
            listOfIndivWords = eachMWE.split(' ')
            # Create new variable to keep track of which level we're on
            currentLevel = dictOfRootWords
            for eachWordToBeIndexed in listOfIndivWords:
                if eachWordToBeIndexed in currentLevel:
                    currentLevel = currentLevel[eachWordToBeIndexed]
                else:
                    # This next line assigns the value to be the next dict (or empty, if it was the last word in the MWE)
                    currentLevel[eachWordToBeIndexed] = {}
                    currentLevel = currentLevel[eachWordToBeIndexed]
        return dictOfRootWords
        # An explanation of the code block above:
        # Example MWEs: abstract concept, academic study, and academic success
        # First, it will look at abstract, add it to the dict, and build a tree under 'abstract' (only one tree since one starts w/ 'abstract)
        # Next, it would add the 'academic' element in dict, and build a tree w/ -study and -success
        # The final dict would have two trees (abstract & academic), but the second tree (academic) would have two branches in it (study & success)

    # This function starts once a potential acad MWE is found and determines if a suggestion should be made
    # Suggestions will be made for potential incorrect MWEs which:
    #   - Contain the full MWE AND
    #   - Contain words in between what would make up the MWE AND
    #   - Are 1-2 words longer than the original acad MWE
    # Example: if 'in the academic like circles' was in the orig writing, it would flag a suggestion of 'academic circles' (an acad MWE)
    # This function will also go through to see if the writing meets more than one suggested MWE
    def acadMWESuggestionFinderFunction(self, currentResult, currentLevel):
        # First set a max length to look for that the potential MWE could be - allows a max of 2 extra words in MWE
        if currentResult.numExtraWords > 2:
            return
        # If we've hit the end of the MWE - we may have a successful suggestion
        if len(currentLevel) == 0:
            # First make sure they don't equal the same (e.g. so 'academic community' isn't suggested for 'academic community')
            if len(currentResult.listOfWordsWritingSample) != len(currentResult.listOfWordsSuggestedMWE):
                # If they aren't the same, it's a suggestion
                self.listToBeSuggested.append(currentResult)
                #print('Suggestion found!')
            else:
                # If it finds an exact match in the MWE list
                self.listOfExactMWEMatchesInText.append(currentResult)
            return
        # If a sentence or phrase ending punct was found NOT in the last word (it's okay if the MWE ends the sentence)
        # Also checking to remove suggestions that may occur over punctuation
        checkingForPunct = re.sub(r'[^\w\s]','', currentResult.listOfWordsWritingSample[-1])
        if len(checkingForPunct) != len(currentResult.listOfWordsWritingSample[-1]):
            return
        # If we're not yet to the end of the MWE
        else:
            calculatingIndexOfNextWord = currentResult.index + len(currentResult.listOfWordsWritingSample)
            if calculatingIndexOfNextWord >= len(self.inputWritingAsList):
                return
            else:
                nextWord = self.inputWritingAsList[calculatingIndexOfNextWord]
                nextWordLower = self.inputWritingAsListRemoveSomePunct[calculatingIndexOfNextWord]
                currentResult.listOfWordsWritingSample.append(nextWord)
                # Now checking if the next word is the next word in the MWE, or if it's a potential extra word
                # Also checking to see if there is more than one MWE which matches the potential MWE from writing sample
                if nextWordLower in currentLevel:
                    # Copy is going to assume the next word is NOT in the orig MWE (in case one fits more than one potential MWE)
                    copyOfCurrentResult = copy.deepcopy(currentResult)
                    copyOfCurrentResult.numExtraWords = copyOfCurrentResult.numExtraWords + 1
                    self.acadMWESuggestionFinderFunction(copyOfCurrentResult, currentLevel)
                    # Now going back to before the copy happened - have to add word to both lists
                    currentLevel = currentLevel[nextWordLower]
                    currentResult.listOfWordsSuggestedMWE.append(nextWord)
                    self.acadMWESuggestionFinderFunction(currentResult, currentLevel)
                # Checking if next word is a potential "extra" word (might still be a MWE - not sure yet)
                else:
                    currentResult.numExtraWords = currentResult.numExtraWords + 1
                    self.acadMWESuggestionFinderFunction(currentResult, currentLevel)

    # This function is to remove suggestions which are encapsulated within another suggestion
    #   example: 'in the academic like circles' should ONLY suggest 'in academic circles'
    #   NOT 'in academic circles' AND 'academic circles' since the second is encapsulated in the first
    def duplicateRemover(self, listToBeSuggested):
        noEncapsulatedSuggestionList = []
        # Make a double loop so it compares everything in otherSuggestion (inner loop) to eachSuggestion (outer loop)
        #   Comparing to make sure first MWE isn't inside any comparison MWEs
        for eachSuggestion in listToBeSuggested:
            isNotEncapsulatedInAnother = True
            for otherSuggestion in listToBeSuggested:
                # To ignore when they equal (i.e. the first element in the list)
                if eachSuggestion == otherSuggestion:
                    continue
                # Get the start and end point (numbers) so we know where exactly they start and end inside the orig text
                firstMWEStart = eachSuggestion.index
                firstMWEEnd = eachSuggestion.index + len(eachSuggestion.listOfWordsWritingSample)
                comparisonMWEStart = otherSuggestion.index
                comparisonMWEEnd = otherSuggestion.index + len(otherSuggestion.listOfWordsWritingSample)
                # If the comparison MWE's start and end are within the first MWE's start and end, mark it False
                #   so the first MWE doesn't get added to the final list
                if comparisonMWEStart >= firstMWEStart \
                and comparisonMWEEnd <= firstMWEEnd:
                    isNotEncapsulatedInAnother = False
                    break
            # Only ones that are not inside another added to final list
            if isNotEncapsulatedInAnother == True:
                noEncapsulatedSuggestionList.append(eachSuggestion)
        return noEncapsulatedSuggestionList


#variable = MWEAnalyzer()
#print(variable.gettingSuggestionsFunction(inputWriting))