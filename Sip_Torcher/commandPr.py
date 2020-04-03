import re
import sys
import mylogger
my_logger=mylogger.create_logger('commandPr.py',stream=0,logFile='AutoFramework.log', logLevel='debug')

class sippCore:
    def __init__ ( self, templist):
      self.__rawList = templist
      self.__sippList = []
      self.__scenarioTimer = 10
      self.__tcname = 'NA'
      self.__sippLofFnAndLogchk = []
      self.__adminlist = []
      self.__rtpcmdval= 'NA'

      for line in self.__rawList:
        #Code to extract sipp command to be executed in commandline
        sippmatch = re.match("sipp:", line)
        if sippmatch:
           sippcmd = line.rsplit(":")
           if len(sippcmd) >= 2:
              if sippcmd[1]:
                 self.__sippList.append(str(':'.join(sippcmd[1:])))
              else:
                 my_logger.debug("sipp: line contains no command")
           else:
              my_logger.debug("sipp: line contains no or more than one command separated by colon")

        #Code to extract sipp timer value for the testcase
        timermatch = re.match("timer:", line)
        if timermatch:
           timercmd = line.rsplit(":")
           if len(timercmd) == 2:
              if timercmd[1]:
                 self.__scenarioTimer = int(timercmd[1])
              else:
                 my_logger.debug("timer: line contains no value")
                 self.__scenarioTimer = 10
           else:
              my_logger.debug("timer: line contains no or more than one value")
              self.__scenarioTimer = 10

        #Extract Test Case Name
        tcmatch = re.match("test case:", line.lower())
        if tcmatch:
           tccmd = line.rsplit(":")
           if len(tccmd) == 2:
              if tccmd[1]:
                 self.__tcname = str(tccmd[1])
              else:
                 my_logger.debug("Test Case: line contains no value")
                 self.__tcname = 'NA'
           else:
              my_logger.debug("Test Case: line contains no or more than one value")
              self.__tcname = 'NA'

        #Extract RTP list
        #print("Rtp cmd :",line)
        rtpmatch = re.match("verifyrtp:", line.lower())
        if rtpmatch:
           rtpcmd = line.split(":",1)
           if len(rtpcmd) >= 1:
              if rtpcmd[1]:
                 self.__rtpcmdval = str(rtpcmd[1])
              else:
                 my_logger.debug("Verifyrtp: line contains no value")
                 self.__rtpcmdval = 'NA'
           else:
              my_logger.debug("Verifyrtp: line contains no or more than one value")
              self.__rtpcmdval= 'NA'


        #Extract Admin List
        adminmatch = re.match("admin:", line.lower())
        if adminmatch:
           admincmd = line.split(":",1)
           if len(admincmd)>1:
              if admincmd[1]:
                 self.__adminlist.append(str(admincmd[1]))
              else:
                 my_logger.error("admin: line contains no value")
           else:
              my_logger.error("admin: line contains no or more than one value")

           

          

    def __del__ (self):
      self.__rawList = []
      self.__sippList = []
      self.__scenarioTimer = 0
      #self.__sippList.append(sippcmd)
      #print("sippCore objet Destroyed:")

    def getSippCommands(self):
      '''
      This function will  return sipp command to be run in command line
      '''
      return self.__sippList
      
    def getScenarioTimer(self):
      '''
      This function will  return the global timer value of all the sipp command line
      '''
      return self.__scenarioTimer
 
    def getTestcaseName(self):
      '''
      This function will  return the global timer value of all the sipp command line
      '''
      return self.__tcname
 
    def setLogfileAndLogcheckerMap(self, tmppid, sippcmd):
      '''
      This function stores logchecker with corresponding log files in order
      For Example: logchecker in index 1 and log filename in index2
      '''
      #Logic
      #Match sippcmd in self.__rawList, if th match get its xml and decide what could its log file name
      # Iterate the list either end of self.__rawList or next sipp line hits
      # During each iteration if logfile: line found append it in list and then append log file name

    def getAdminList(self):
      '''
      This function will  return the global timer value of all the sipp command line
      '''
      return self.__adminlist

    def getRTPcheckstr(self):
      '''
      This function will  return rtp command 
      '''
      return self.__rtpcmdval

    def getLogCheckList(self):
        '''
        This function returns the parameters of log check file, null if none specified
        '''
        newlist = []
        loglist = []
        list1 = self.__rawList
        for i in range(0,len(list1)):
            sippmatch = re.match("sipp:", list1[i])
            if sippmatch: #check if end of the list already reached
               newlist = []
               #newlist.append(list1[i])
               if i+1 == len(list1):
                  #newlist.append(pp)
                  #print(newlist)
                  loglist.append(newlist)
                  break
               list2 = list1[i+1:]
               for line in list2:
                   match = re.match("sipp:", line)
                   if match:
                      #print(newlist)
                      break
                   else:
                      if re.match("logcheck:", line):
                         line=line[9:]
                         newlist.append(line)
               loglist.append(newlist)
               #print(newlist)
        #my_logger.debug("Log Check list:",loglist)
        return loglist

