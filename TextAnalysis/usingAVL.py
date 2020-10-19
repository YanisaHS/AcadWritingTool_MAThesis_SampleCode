# This file is going to use the AVL to see if any academic words can be suggested
# Looked at this for some info: https://pypi.org/project/spacy-wordnet/

# What I'm planning to do is:
#   Import the files
#   Use spaCy or NLTK to get synsets (WordNet)
#   If any of the words in the synset were in the file, suggest academic words from AVL

import spacy
from spacy_wordnet.wordnet_annotator import WordnetAnnotator
from word_forms.word_forms import get_word_forms

# Make sure input is what you want before running (there are diff sample texts to choose from)
inputWriting = open('/Users/yanisa/Code_GitHub/MAThesis_YourAcadWritingFriend/miscInputFiles_WordListsPhrasesEtc/manuallyWrittenText.txt').read()

def useAVLFunction(inputWriting):
    acadCoreAVL = open('/Users/yanisa/Code_GitHub/MAThesis_YourAcadWritingFriend/miscInputFiles_WordListsPhrasesEtc/acadCore_AVL.txt').read()
    stopWordsFile = open('/Users/yanisa/Code_GitHub/MAThesis_YourAcadWritingFriend/codeFiles/acadWritingFeaturesAnalysisFiles/acadWordLists/avlStopWords.txt').read().split('\n')

    dictWithAVLSuggestionsPerInputWord = {}
    # Load a spacy model and run my writing sample through (turns it into a Doc object)
    nlp = spacy.load('en_core_web_sm')
    nlp.add_pipe(WordnetAnnotator(nlp.lang), after='tagger')
    inputWritingTokenized = nlp(inputWriting)

    # Make my AVL into a list with each word as an element
    # Then make it into a set so it's more efficient (looks up hash value rather than the actual word each time)
    acadCoreAVL_Set = set(acadCoreAVL.split('\n'))

    # Prepare stop words list so it ignores anything that has YANISA
    stopWordsList = []
    for eachLine in stopWordsFile:
        if 'YANISA' in eachLine:
            continue
        else:
            stopWordsList.append(eachLine)

    # Check to see if any of the synsets match with an academic word from the AVL AND have the same POS
    for word in inputWritingTokenized:
        # Check the POS - only move forward if they are one of the WN synset POS-tags
        if word.pos_ != 'NOUN' and \
        word.pos_ != 'ADJ' and \
        word.pos_ != 'ADV' and \
        word.pos_ != 'VERB':
            continue
        # If word is already in the AVL, skip it so it doesn't provide a suggestion
        if word.text.lower() in acadCoreAVL_Set:
            continue    
        # If word is in stop words list, skip it too
        if word.text.lower() in stopWordsList:
            continue

        # Check the spacy POS and give it a hacky code that matches the wordnet synset output
        spacyPOS = word.pos_
        if spacyPOS == 'NOUN':
            spacyToWordNetPOS = 'n'
        if spacyPOS == 'VERB':
            spacyToWordNetPOS = 'v'
        if spacyPOS == 'ADJ':
            spacyToWordNetPOS = 'a'
        if spacyPOS == 'ADV':
            spacyToWordNetPOS = 'r'

        # Get the word index from spacy to be used later
        #   index is used in the file that calls this, so it doesn't duplicate suggestions where MWEs are
        # wordIndex = word.i

        # Get the synsets from WordNet for each word in the writing sample
        inputWritingSynsets = word._.wordnet.synsets()

        # Cleaning the synsets out so I only get the actual word
        #   synsets print like: Synset('synset.n.01')
        for eachSynset in inputWritingSynsets:
            cleanOutFrontOfSynset = str(eachSynset).replace('Synset(\'', '')
            splitEachSynset = str(cleanOutFrontOfSynset).split('.')
            actualWordInSynset = splitEachSynset[0]
            posInSynset = splitEachSynset[1]

            # Keep the synset and original word if a word in the synset is in the AVL 
            #   and the synset word has the same POS as the orig word in the writing sample
            #   and the suggested and orig words are not identical
            #   and the suggested and orig words are not lemmas
            synsetToAddToDict = ''
            actualWordInSynsetStringLower = str(actualWordInSynset).lower()
            wordStringLower = str(word).lower()
            if actualWordInSynset.lower() in acadCoreAVL_Set and \
            posInSynset == spacyToWordNetPOS and \
            actualWordInSynsetStringLower != wordStringLower and \
            actualWordInSynsetStringLower not in wordStringLower and \
            wordStringLower not in actualWordInSynsetStringLower:
                # Removes super short words so my bottom script can run (e.g. 'am', 'is')
                if len(word.text) >= 3:

                    # Use word_forms to make sure suggestion has the correct word form
                    # e.g. so 'publishing' (rather than 'publish') is suggested for 'writing',
                    # but 'publish' is still suggested for 'write'
                    wordFormsEachSynonym = get_word_forms(actualWordInSynsetStringLower)
                    # For each POS, get the word forms, and keep the one which has the appropriate ending
                    if posInSynset == 'n':
                        nounSet = wordFormsEachSynonym[posInSynset]
                        if word.text[-1] == 's':
                            for eachSyn in nounSet:
                                if eachSyn[-1] == 's':
                                    synsetToAddToDict = eachSyn
                        else:
                            synsetToAddToDict = actualWordInSynsetStringLower
                    if posInSynset == 'r':
                        # No adv endings added
                        synsetToAddToDict = actualWordInSynsetStringLower
                    if posInSynset == 'a':
                        # No adj endings added
                        synsetToAddToDict = actualWordInSynsetStringLower
                    if posInSynset == 'v':
                        verbSet = wordFormsEachSynonym[posInSynset]
                        if word.text[-3:] == 'ing':
                            for eachSyn in verbSet:
                                if eachSyn[-3:] == 'ing':
                                    synsetToAddToDict = eachSyn
                        elif word.text[-1] == 'd':
                            for eachSyn in verbSet:
                                if eachSyn[-1] == 'd':
                                    synsetToAddToDict = eachSyn
                        elif word.text[-1] =='s':
                            for eachSyn in verbSet:
                                if eachSyn[-1] == 's':
                                    synsetToAddToDict = eachSyn
                    # TODO add other verb endings
                        else:
                            synsetToAddToDict = actualWordInSynsetStringLower

                    if word not in dictWithAVLSuggestionsPerInputWord:
                        # Set dict so word is key and synonym is the first element in a list in the dict (as the value)
                        # The list thing is for if/when I add more synonyms to the orig word
                        dictWithAVLSuggestionsPerInputWord[word] = [synsetToAddToDict]
                    else:
                        dictWithAVLSuggestionsPerInputWord[word].append(synsetToAddToDict)
                    #print('AVL Suggested Word: ' + str(actualWordInSynset))
                    #print('Original Word: ' + str(word))
    return dictWithAVLSuggestionsPerInputWord

print(useAVLFunction(inputWriting))



### WORKING ON NOW ###
# Lemmas: make list of lemmas for AVL list, then when the function finds a word that could be suggested, 
#   it also has to check against lemmas to ensure the last two letters (or w/e) are the same ???
#   maybe use the spacy POS tag things to see if it's the root form: https://spacy.io/api/annotation
# The suggestion in spacy - their tags must also match - lemmatize AVL and orig word - OR
#   tag orig word, and compare it to a list which contains all the word forms for each word in AVL THEN
#   it must match with all their forms (write --> writing, writes, wrote, written) - give me the one which has the same tag



### YANISA THINGS TO CONSIDER ###
# Also should have it only pick maybe 2 suggested words max? (based on which ones are higher on the acad word list?)
#   or could do them all (or a higher #), but have it ask 'Did you mean ___, ___, ___, ___, or ___?' (could have direct dict.com links?)
# Consider only taking noun suggestions.......? (if there are too many)
#   verb suggestions get a lot of extra things .. eg sugges "use" for orig "apply"
# Change how words like "have" in "have been" are approached, since "have" might stay? (bigrams/trigrams?)
# Make sure all my stuff w/ .lower is okay - everything isn't only looking for lowercase/etc
# If orig word is capitalized at beginning, should capitalize suggestion
# Can lower the number of AVL words if it seems like there are so many? Look at freqs
