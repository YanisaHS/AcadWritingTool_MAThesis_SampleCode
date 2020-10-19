# This file will code some things from the Longman Grammar book

import spacy

# Make a class to have all my result information so it can highlight correctly on the final page
# This class would contain all the info needed for that 
class ResultsInformationForSuggestionLocations:
    def __init__(self, suggestion, startIndex, endIndex):
        self.suggestion = suggestion
        self.startIndex = startIndex
        self.endIndex = endIndex

# Make sure input is what you want before running (there are diff sample texts to choose from)
inputWriting = open('/Users/yanisa/Code_GitHub/MAThesis_YourAcadWritingFriend/miscInputFiles_WordListsPhrasesEtc/manuallyWrittenText.txt').read()

# spacy stuff
nlp = spacy.load('en_core_web_sm')
inputWritingTagged = nlp(inputWriting)

# Longman p.65: Approx 60% of all content words (i.e. advs, adjs, verbs, nouns) in academic prose are nouns
# This function will determine the proportion of nouns in the text
def calculateNounsFunction(inputWritingTagged):
    nounList = []
    adverbList = []
    adjectiveList = []
    verbList = []
    for eachWord in inputWritingTagged:
        if eachWord.pos_ == 'NOUN':
            nounList.append(eachWord)
        if eachWord.pos_ == 'ADV':
            adverbList.append(eachWord)
        if eachWord.pos_ == 'ADJ':
            adjectiveList.append(eachWord)
        if eachWord.pos_ == 'VERB':
            verbList.append(eachWord)
    totalNumberContentWords = len(nounList) + len(adverbList) + len(adjectiveList) + len(verbList)
    percentageNounsAsContentWords = len(nounList) / totalNumberContentWords
    return percentageNounsAsContentWords
    #print(percentageNounsAsContentWords)

# Longman p.235-256: Pronouns are very uncommon (practically absent) in academic prose (look like they take up approx <15% of all nouns)
# This function will determine the percentage of nouns which are pronouns
def percentageOfNounsAsPronounsFunction(inputWritingTagged):
    nounsList = []
    pronounsList = []
    for word in inputWritingTagged:
        if word.pos_ == 'NOUN':
            nounsList.append(word)
        if word.pos_ == 'PRON':
            pronounsList.append(word)
    percentageOfPronouns = len(pronounsList) / (len(nounsList) + len(pronounsList))
    return percentageOfPronouns
    #print(percentageOfPronouns)

# Longman p.316-317: dual gender reference (e.g. he or she/etc..) more common in academic prose
# This function will look for any instances of 'he' or 'she' which are pronouns, and suggest 'he or she', 'she or he', 's/he', etc...
# Also looks at 'him' and 'her'
def dualGenderReferenceFunction(inputWritingTagged):
    listOfSuggestions = []
    for word in inputWritingTagged:
        if word.pos_ == 'PRON' \
        and (word.text.lower() == 'he' \
        or word.text.lower() == 'she'):
            suggestion = str(word) + ' - Suggest he or she, s/he, she or he, etc..... here'
            putThingsIntoClass = ResultsInformationForSuggestionLocations(suggestion, word.idx, (word.idx + len(word.text)))
            listOfSuggestions.append(putThingsIntoClass)
            #print(str(word) + ' - Suggest he or she, s/he, she or he, etc..... here')
        if word.pos_ == 'PRON' \
        and (word.text.lower() == 'him' \
        or word.text.lower() == 'her'):
            suggestion = str(word) + ' - Suggest him/her, etc...'
            putThingsIntoClass = ResultsInformationForSuggestionLocations(suggestion, word.idx, (word.idx + len(word.text)))
            listOfSuggestions.append(putThingsIntoClass)
            #print(str(word) + ' - Suggest him/her, etc...')
            # TODO 'her' doesn't come up for some reason?
    return listOfSuggestions
        # TODO will first have to check that it doesn't already say 'he or she' etc........ do that later :P



#print(calculateNounsFunction(inputWritingTagged))
#print(percentageOfNounsAsPronounsFunction(inputWritingTagged))
#print(dualGenderReferenceFunction(inputWritingTagged))


# Ones to maybe include or make note:
# Longman p.589-596: Nouns as pre-modifiers are common in acad prose
#   dep parsing w/ spacy and see if noun chunk has multiple nounse ? Not sure what suggestion would be
# Something with hedges from Hyland book