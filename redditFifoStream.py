# Reddit PRAW Wrapper for pulling comment data to list
import praw
import nltk
from nltk import word_tokenize
from fileManagement import *
import subprocess

# Dictionary Definitions
realWords = fileToList('Dictionaries/lotsofwords.txt')
happyWords = fileToList('Dictionaries/happywords.txt')
negativeWords = fileToList('Dictionaries/negativewords.txt') #something wrong with the negative word list ascii structure?????
#fixed it with decoding via utf-8 in my open() command of fileMAnagement.py
adjectives = fileToList('Dictionaries/adjectives.txt')
adverbs = fileToList('Dictionaries/adverbs.txt')
nouns = fileToList('Dictionaries/nouns.txt')
verbs = fileToList('Dictionaries/verbs.txt')

###### REDDIT API PULL #####
def pullComment(subreddit):
    r = praw.Reddit(user_agent='',
                         client_id='', client_secret="")
    for comment in r.subreddit(subreddit).stream.comments(skip_existing=False):
        rawDataArray=[]

        rawDataArray.append(comment.id)
        rawDataArray.append(str(int(comment.created_utc))) #OG returns a float, have to do a double convert because float irrelevant OR IS IT?!?!?!?!?!?!?
        rawDataArray.append(comment.subreddit.display_name)
        rawDataArray.append(comment.submission.id)
        rawDataArray.append(comment.author.name)
        noPunc = stripPunctuation(comment.body)
        rawDataArray.append(noPunc)

        analyzed = analyzeDataLine(noPunc)

        data=[]
        data.append(str(int(comment.created_utc)))
        data.append(comment.author.name)
        data.append(comment.subreddit.display_name)
        for x in range(0,len(analyzed)): #where we iterate over the list of analyzed data to make it into a string for .join to work later
            data.append(analyzed[x])
        formattedDataLine = []
        formattedDataLine = ','.join(data)

        writeFifo('stream.fifo',formattedDataLine) # Since a fifo is NOT a file, just memory file, we need to create it and WRITE to it because it's a pipe not a file that we're appending to
        print(formattedDataLine)
        #except: pass

def stripPunctuation(inputString):
    PERMITTED_CHARS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ\ \'" #leaves in appostrophie, we're using commas to separate data
    output = "".join(c for c in inputString if c in PERMITTED_CHARS) #makes sense, what is the c for c mean?
    #Need to make it so that this replaces all punctuation with a ' ' so that it's not combining words together in order to process more words
    #punctuation modifier
    return output



### WORD ANALYZATION PROCESS ###

def tokenizeString(string):
    tokens = word_tokenize(string)
    numOfTokens = len(tokens)
    return numOfTokens, tokens #returns number of tokens and the tokens themselves

def compareLists(input,reference,returnwords):
    commonWords = set(input).intersection(reference)
    if (returnwords == True) & (len(commonWords) != 0):
        return len(commonWords), commonWords #returns the number of matches as well as the matches
    else:
        return len(commonWords)

def analyzeDataLine(dataLine):
    words = tokenizeString(dataLine)

    real = compareLists(words[1],realWords,False) #tokenize string returns 2 values, we only want to look at the words, not the numnber of words
    happy = compareLists(words[1],happyWords,False)
    negative = compareLists(words[1],negativeWords,False)
    adjective = compareLists(words[1],adjectives,False)
    adverb = compareLists(words[1],adverbs,False)
    noun = compareLists(words[1],nouns,False)
    verb = compareLists(words[1],verbs,False)

    analyzedData = [str(real),str(happy),str(negative),str(adjective),str(adverb),str(noun),str(verb)] #Easier to output from function, we iterate over later to create string
    return analyzedData


### MAIN LOOP ###
try:
    stat.S_ISFIFO(os.stat('stream.fifo').st_mode) #Returns an exception if the stream fifo isn't found to exist in the pwd
    pullComment('all')
except:
    #subprocess.call('rm stream.fifo'.split()) #Kinda doesnt work??????
    print('FIFO Doesnt exist or stream was interupted')
