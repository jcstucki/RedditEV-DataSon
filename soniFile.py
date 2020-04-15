import ctcsound
from ctcsound import *
from random import randint
from fileManagement import *

global spacing
spacing = 0


# EXAMPLE Csound SCORE CODE
ex_sco= """
f1 0 4096 10 1 ; sine wave
f2 0 4096 10 0.5 0.5 ;sine and first harmonic
f3 0 4096 10 0.25 0.25 0.25 0.25 ; sine, first, second harmonic

;instrument	strt	dur 	freq 	wave  	amp 	attack	release
i1			0	 	4 		630 	1		2000 	1		4
"""

# Define our orchestras

orchestra = """

sr = 44100
ksmps = 32
nchnls = 2
0dbfs = 6

instr 1
	istrt = p2
	idur = p3
	ifreq = p4
	iwave = p5
	iamp = p6
	iattack = p7
	irelease = p8

	;ADSR
	k1 linen iamp, iattack, idur, irelease
	;oscilators
	a1 oscil k1, ifreq, iwave

	; these reference the entry within the score instrument as seen below
	; < THIS IS A COMMENT
	out a1
	fout 'audio.wav'
endin
"""

## CLASS DEFINITIONS## We only use these for when we are creating an amagamated score (bunch of note data at time, not pushing single note values)
class Note(object):
	def __init__(self, *args): #runs on object initilization, gives object body *args is multiple things given
		self.inputFields = list(args) #self referes to the object __init__ call
	def __str__(self): #runs when object is called as a string
		retVal = "i" # creates instrument line
		for i in range(len(self.inputFields)): #how long is your pfields
			"""if(i == 4):
				retVal += " " + midi2pch(self.pfields[i]) #MIDI conversion
			else:"""
			retVal += str(self.inputFields[i]) + " " #appends the notes pvalues to a string
		return retVal #returns the p values as a string for csound to read

class WaveTable(object):
	def __init__(self, *args):
		self.inputFields = list(args)

	def __str__(self):
		retVal = "f"
		for i in range(len(self.inputFields)):
			retVal += str(self.inputFields[i]) + " "
		return retVal
##Class Definitions ##

## SCORE AND WAVETABLE "FILE" CREATION AND WRITE ##
def createWavetable(howmany):
	wavetable = []
	for i in range (1, howmany+1):
		wavetable.append(WaveTable(i, "0", "4096", "10", "1"))
	return wavetable

def createNotes(instrument,start,duration,frequency,wavetable,amplitude,attack,release):
	notes = []
	notes.append(Note(instrument, start, duration, frequency, wavetable, amplitude, attack, release))
	return notes

def createScore(wavetable,notes):
	sco = ""
	wavetable = createWavetable(1)
	notes = createNote(1,800)
	for w in wavetable:
		sco += "%s\n"%w
	for n in notes:
		sco += "%s\n"%n #this implicitly calls the __str__ method on the note class (Lol, it works, i dont comprehend
	print (sco)
	#Compile score from note and wavetable objects
	return sco
## SCORE AND WAVETABLE "FILE" CREATION AND WRITE ##


## DIRECT PUSH TO CSOUND ##
def createNoteFromFifoData(splitData,spacing):

	try: #Word total might be zero (unlikely but can happen and don't want it to cause an exception)
		percentEmotionPerComment = (int(splitData[4])+int(splitData[5]))/(int(splitData[3])) # Happy plus Negative over word total = percentage of emotion per comment
	except:
		percentEmotionPerComment = 0

	emotionalWordsPerComment = int(splitData[4]) + int(splitData[5]) #positive plus negative words in the comment

	try: #might be a  DIVIDE BY ZERO ERROR because there might be zero emotional words in the comment
		negativeWordPercentage = int(splitData[5]) / emotionalWordsPerComment
	except:
		negativeWordPercentage = 0 #If no emotional words, set zero

	try:#might be a  DIVIDE BY ZERO ERROR because there might be zero emotional words in the comment
		positiveWordPercentage = int(splitData[4]) / emotionalWordsPerComment
	except:
		positiveWordPercentage = 0



	instrument = 1
	start = spacing
	attack = 0.08 - 0.004*int(splitData[9]) #mapped to verbs, more verbs = faster attack
	release = 0.02 + 0.05 * int(splitData[6]) #mapped to adjectives, more = longer release
	duration = 0.1 + 0.01 * int(splitData[3]) + attack + release #mapped to number of words in the comment, also have to add attack and release time so doesn't cut off beginning or tail

	if negativeWordPercentage > 0.5: #is it a more negative comment? create negative tone
		wavetable = 2
		frequency = 569 - 60*int(splitData[5])
		amplitude = 6 * percentEmotionPerComment

	elif positiveWordPercentage > 0.5: #is it a more positive comment? create positive tone
		wavetable = 3
		frequency = 780 * int(splitData[4]) + 10*int(splitData[8])
		amplitude = 1.5 * percentEmotionPerComment

	else: #if both of above = 0 or are 50/50 play neutral tone
		wavetable = 1
		frequency = 440 #* (int(splitData[3])/10)
		amplitude = 0.1


	print('Emotional % of word Total =', percentEmotionPerComment)
	print('Negative % =',negativeWordPercentage)
	print('Positive % =',positiveWordPercentage)


	#append data to list to be sent to CSound
	line = []
	line.append('i'+str(instrument))
	line.append(start)
	line.append(duration)
	line.append(frequency)
	line.append(wavetable)
	line.append(amplitude)
	line.append(attack)
	line.append(release)
	noteVal = ' '.join(str(x) for x in line) # turn data into strings and join together in a CSound readable format



	return noteVal #return the CSound readable string


createPipe('stream.fifo') #creates the .fifo file so that the commentPullPraw can dump data into it

c = ctcsound.Csound() #creates csound instance
c.setOption("-odac") #csound options
thread = CsoundPerformanceThread(c.csound()) #new thread passing csound object

c.compileOrc(orchestra) #compile orch from string
#c.readScore(createScore(createWavetable,createNotes)) #read score from strings
c.start() #when compiling from strings this must be called before perform
thread.play() #starts thread running seperately, asyncronous takes back to main CsoundPerformanceThread


c.readScore('f 0 z \n') #innitializes "starts" csound running continuously, FOREVER WHEEEEEEE
c.readScore("f1 0 4096 10 1") #creates a "global" wavetable just a sine wave
c.readScore("f2 0 4096 10 1 0.5 0.3 0.25 0.2 0.167 0.14 0.125 .111") #creates global sawtooth
c.readScore("f3 0 16384 10 1 0 0.3 0 0.2 0 0.14 0 .111") #square wave global wavetable

oldline = "" #have to create innitial string for new string comparisson

while True:
	try:
		line = readFifoLine('stream.fifo') #grab the latest data from the pipe
		#print(line)
		if (len(line) != 0): #Pipe returns blank line if EOF(but continues to run), so we have to check if it actually has data in the pipe

			if line != oldline: #makes sure that the data we are reading isn't a previously read data point (prevents double reads if soniFile faster than the pipe, which it is)
				splitData = line.split(',') #unformats piped data
				print(splitData)

				spacing += 0.1 #increment our spacing factor so sounds smoother, changes "speed" (not really speed, higher values = more desync)
				c.readScore(createNoteFromFifoData(splitData, spacing)) #pushes de-formatted piped data into analyzation and note creation function then pushes directly into CSound instance
				oldline = line #have to rewrite old line for double-read prevention

	except:
		print(e)
		print('Thrown Exception, stopping CSound')
		thread.join() #wait for other thread to complete
		c.stop()
		c.cleanup()
