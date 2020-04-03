import sys
import os.path
import mylogger
import re

def tagmain():
    ''' Replace To tag of subscrive in CSV file '''
    my_logger=mylogger.create_logger(sys.argv[0],stream=0,logFile='AutoFramework.log', logLevel='debug')
    if len(sys.argv) <= 2:
        my_logger.error('Error in xml: Insufficient arguments')
        exit(1)
    if not os.path.exists(sys.argv[2]):
       my_logger.error('Error: file %s does not exist',sys.argv[2])
       exit(1)

    arg1=sys.argv[1]
    if not arg1:
       my_logger.error('Error: user and totag is null')
       exit(1)
    userlist=arg1.split(";")
    if len(userlist) < 1:
       my_logger.error('Error: correct key and to tag separated by semicolon is not spectfied',sys.argv[1])
       exit(1)
    user=userlist[0] 
    csvinfilename=sys.argv[2]
    readcsv=open(csvinfilename,"r")
    EntryFound=False
    
    filecont=[]
    for line in readcsv:
        filecont.append(line)
    readcsv.close()

    writecsv=open(csvinfilename,"w")
    for line in filecont:
         usermatch=re.match(user, line)
         if usermatch:
            writecsv.write(arg1+"\n")
            EntryFound=True
         else:
            writecsv.write(line)
    if not EntryFound:
        writecsv.write(arg1+"\n")
            
    writecsv.close()
if __name__ == "__main__":
    tagmain()

