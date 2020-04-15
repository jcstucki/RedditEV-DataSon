#file management functions
import os
import stat

#fifo class
class FIFO(object):

    def __init__(self, filePath): #runs at object innitialization
        self.filePath = filePath
        print('Created '+filePath)
        pass

    def __str__(self): #So when we call the DataStream object as a string, it will return  a fifo line Yay!
        fifo = open(self.filePath,'r', encoding='utf8')
        line = fifo.readline()
        fifo.close()
        return line

    def createInboundFIFO(self): #This must be called within the file doing the reading
        try:
            os.mkfifo(self.filePath)
            print('Made Fifo With Filename:' + self.filePath)
        except:
            print('Fifo Exists, filePath:'+ self.filePath)
        pass

    def writeOutboundFIFO(self, data): #Can we start to write to the fifo before its created on the inbound file? Need to test
        fifo = open(self.filePath,'w')
        fifo.write(data)
        fifo.close()
        pass

    def readInboundFIFO(self): # So we can read the fifo line without calling the DataStram obj as a str, just gives options
        fifo = open(self.filePath,'r', encoding='utf8')
        line = fifo.readline()
        fifo.close()
        return line

    def doesFIFOExist():
        pass

    def removeFIFO():
        pass


# File Class
class FileClass(object):
    """docstring for FileClass."""
    def __init__(self, arg):
        #super(FileClass, self).__init__() #This is for child class inheritance. Allows for __init__ reference based upon Parent Class????
        self.arg = arg
        self.fileSize = fileSize

    def createFile(self, filePath):
        pass

    def writeFile(self, filePath):
        pass

    def appendFile(self, filePath):
        pass

    def readFile(self, filePath):
        return allLines

    def copyFile(self, filePath, copyPath):
        pass

    def doesFileExist():
        return bool



## FIFO RECIEVE##
def createPipe(fifoname):
    try:
        os.mkfifo(fifoname)
        print('Made Fifo: '+fifoname)
    except:
        print('Fifo exists')
    finally:
        print('Waiting for stream to start')

def readFifoLine(fifoname):
    fifo = open(fifoname,'r')
    line = fifo.readline()
    fifo.close()
    return line

def writeFifo(fifoname,data):
    fifo = open(fifoname,'w')
    fifo.write(data)
    #print(data)
    fifo.close()

## FIFO ##


def appendFile(fileName,lineData):
    #fileName =
    f = open(fileName,"a")
    f.write(lineData)
    f.write('\n') #appends a newline ch to line so there is a new line, have to get rid of this when reading the data
    f.close()

def copyFile(filename):
    readDataRaw = fileToList(filename)
    fp = open('process'+filename,'w')
    fp.writelines(readDataRaw)
    fp.close()

def clearFile(fileName):
    open(fileName,'w').close() #opening in write mode clears the file

def fileToList(filename):
    fp = open(filename,'r',encoding='utf8') #need encoding for some files. So sure.
    rawData = fp.readlines()
    noNewLineData=[]
    for line in rawData: #iterates over item in the list
        noNewLineData.append(line[0:-1]) #appends the line (MINUS THE /n NEWLINE CHARACTER) to the new readDatalist
    fp.close()
    return noNewLineData

def lineToList(line):
    lineData=[]
    lineData = line.split(',') # pull the string from the line being read and split it into a new list
    return lineData
