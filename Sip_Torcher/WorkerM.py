import subprocess
import multiprocessing
import time
import sys
import os
import re
import mylogger
from subprocess import PIPE, Popen
import string
import os.path

my_logger=mylogger.create_logger('WorkerM.py',stream=0,logFile='AutoFramework.log', logLevel='debug')

class sippWorker(multiprocessing.Process):
    def __init__(self, argdata):
      self.__devnull = open('/dev/null', 'w')
      #self.__sipperrorfile = open('SippError.log','a')
      self.__sippcmd = argdata
      self.__sippLogFile = ''
      self.__Callid = ''
      if not re.search(' -trace_msg',argdata):
         argdata = argdata+" -trace_msg"
      if not re.search(' -aa',argdata):
         argdata = argdata+" -aa"
      if not re.search(' -trace_err',argdata):
         argdata = argdata+" -trace_err"
      if not re.search(' -trace_screen',argdata):
         argdata = argdata+" -trace_screen"
      self.__sippcmd = argdata
      multiprocessing.Process.__init__(self, None, '', None, argdata, '')

    def __del__ (self):
      self.__devnull.close()
      #self.__sipperrorfile.close()

    def run(self):
      sippcmd = ''.join(self._args)
      my_logger.debug('Started process %s id %d',self.name, self.pid)
      my_logger.info('Going to run: %s', sippcmd)
      #self.__sipperrorfile.write(sippcmd)
      retcode = subprocess.call(sippcmd, shell=True, stdout=self.__devnull, stderr=self.__devnull)
      if retcode != 0:
         my_logger.info('Return Code:%d PPID:%d', retcode,self.pid)
         try:
            open(str(self.pid)+'_STAFtmpuse', 'w').close()
         except Exception as e:
            my_logger.error("could not create file: %s",str(self.pid))
            my_logger.info('Return Code:%d %s', retcode, sippcmd)
            my_logger.error("Exception: %s",str(e))

      if retcode == 255:
          my_logger.error('could not start sipp. Check existance of xml file or other paramaters of sipp instance: %s',sippcmd)
      return 

    def killchild(self):
        str_list = ["ps -ef  | awk '$3 ~ /",str(self.pid),"/ { print $2 }'| xargs -i kill -9 {}"]
        cmdstr = ''.join(str_list)
        my_logger.debug('Killing child of Parent %s PID: %d', self.name, self.pid)
        my_logger.debug('Executing Shell command: %s',cmdstr)
        subprocess.call(cmdstr, shell=True)
        return

    def setnGetLogFN(self):
        my_logger.debug('Shell command: ps --no-headers -o pid --ppid %d', self.pid)
        p = Popen('ps --no-headers -o pid --ppid %d' % self.pid, shell = True, stdout = PIPE, stderr = PIPE)
        stdout, stderr = p.communicate() 
        mychildpid = [int(p) for p in stdout.split()]
        if len(mychildpid) != 1:
           my_logger.debug('Could not get pid of sipp process, PPID %d',self.pid)
           mychildpidstr = ''
           self.__sippLogFile = ''
           return ''
        else:
           mychildpidstr = str(mychildpid[0])

        my_logger.debug('checking \s([a-zA-Z0-9_]+)\.xml in command: %s',self.__sippcmd)
        match =  re.search("\s([a-zA-Z0-9_]+)\.xml", self.__sippcmd)
        if match:
           self.__sippLogFile = match.group(1)+"_"+mychildpidstr+"_messages.log"
           if self.__sippLogFile:
              my_logger.debug('Logfile Name: %s', self.__sippLogFile)
              return self.__sippLogFile
           else:
              my_logger.error('No logfile available, may be xml file is not given or sipp did not start or xml file does not exist')
              return ''

    def getLogFN(self):
        return self.__sippLogFile

    def isBYEComplete(self):
        '''
        This function check if BYE transaction, returns true if completed
        Function also returns true if log file does not exist, to indicate no further cleanup is required
        '''
        my_logger.info('Checking BYE transaction for PPID: %d',self.pid)
        file_name = self.__sippLogFile
        if not file_name:
           my_logger.info('No logfile available to check bye transaction: Skip check')
           return True
        else:
           my_logger.info('Checking BYE transaction in file: %s', file_name)

        recv_bye = False
        if (os.path.isfile(file_name)):
        ##Check if file with file_name exists
            try:
                sipp_logfile = open(file_name , 'r')
                msg = []
                FirstSep = True
                Endmsg = False
                Startmsg = False

                for line in sipp_logfile:
                  if(line.isspace()):
                     continue

                  if(re.match('--------', line)or re.match('SCTP Notification', line)):
                     if FirstSep:
                        FirstSep = False
                     else:
                        Endmsg = True
                        Startmsg = False
                        indx = 0
                        for msgline in msg:
                          if(re.match('BYE sip', msgline)):
                            my_logger.info('Matched received method BYE line: %s', msgline)
                            sipp_logfile.close()
                            return True
                          if(re.match('SIP\/2\.0\s200\sOK', msgline)):
                            #print("Matched Received 200 OK: ", msg[indx:])
                            for subline in msg[indx:]:
                                #print(subline)
                                if(re.match('CSeq:\s[0-9]+\sBYE', subline)):
                                  my_logger.info('Matched header in 200 OK: %s',subline)
                                  sipp_logfile.close()
                                  return True
                          indx = indx + 1
                     msg = []

                  if Startmsg:
                     msg.append(line)

                  #sentflag = re.match("[TCPUDLS]+\smessage sent.*", line)
                  if(re.match("[TCPUDLS]+\smessage received.*", line)):
                     Startmsg = True
                #doing it again for the message at the end of file if no separator os present
                indx = 0
                for msgline in msg:
                  if(re.match('BYE sip', msgline)):
                    my_logger.info('Matched received method BYE line: %s', msgline)
                    #print("Matched received method BYE line:", msgline)
                    sipp_logfile.close()
                    return True
                  if(re.match('SIP\/2\.0\s200\sOK', msgline)):
                    for subline in msg[indx:]:
                        if(re.match('CSeq:\s[0-9]+\sBYE', subline)):
                          my_logger.info('Matched header in 200 OK: %s',subline)
                          #print("Matched header in 200 OK:",subline)
                          sipp_logfile.close()
                          return True
                  indx = indx + 1

                #For Loop Ends here
                sipp_logfile.close()
                my_logger.info('No BYE Transaction found in %s',file_name)
                return False
            except Exception as inst:
                err_str = 'Problem occurred while reading the SIPP log file \'{0}\'.'.format(file_name)
                err_str = err_str + '\nPlease check the permissions of the file. Also,please check the contents of the file.'
                my_logger.exception("")
                #sipp_logfile.close()
                #raise Exception(err_str)
                return True
        else:
           err_str = 'SIPP log File: \'{0}\' does not exist.'.format(file_name)
           my_logger.debug('SIPP log File: %s does not exist',file_name)
           #print(err_str)
           #sipp_logfile.close()
           return True


    def prepCleanup(self):
        '''
        This Function Checks the log file determines the callid, from tag, to tag, route pattern
        and patches it to cleanup.xml and uses it to send bye
        '''
        my_logger.info('Doing Cleanup for %s', self.__sippLogFile)
        file_name = self.__sippLogFile
        #file_name = "uas.log"
        cleanupScriptFN="cleanupcall.xml"
        templateFN="cleanupcall.raw"
        if not file_name:
           my_logger.debug('No logfile available to create BYE cleanup script: Skip check')
           return True
        else:
           my_logger.debug('Preparing Cleanup script file: %s', cleanupScriptFN)
        if (os.path.isfile(file_name)):
        ##Check if file with file_name exists
            try:
                file = open(file_name , 'r')
                msg = []
                msgtmp = []
                FirstMsg = True
                recvd = False
                sent = False
                uac = False
                tmpline1 = ""

                From = ""
                To = ""
                Callid = ""
                Contact = ""
                RecordRoute = ""
                RequestURI = ""
                RRlist = []
                readytosend = False
                UserNum = ""

                for line in file:
                    if readytosend:
                       break
                    if(line.isspace()):
                       continue
                    if FirstMsg:
                       if(re.match('--------', line)):
                          FirstMsg = False
                          continue
                    if(re.match("[TCPUDLS]+\smessage received.*", line)):
                       tmpline1 = line
                       recvd = True
                       #print("Received:",line)
                       #print("recvd =",recvd)

                    if(re.match("[TCPUDLS]+\smessage sent.*", line)):
                       tmpline1 = line
                       sent = True
                       #print("Sent:",line)
                       #print("sent =",sent )

                    msgtmp.append(line)

                    if(re.match('--------', line)) and recvd and (not readytosend):
                       #print("rcvd:",tmpline1,line)
                       recvd = False
                       sent = False
                       msg = msgtmp
                       msgtmp = []
                       #print("Msg list is:")
                       #print(msg)
                       for subline in msg:
                           if(re.match('INVITE\s', subline)):
                              #print(subline)
                              RRlist = []
                              #it is an UAS, stort contact line
                              for line1 in msg[0:]:
                                  if(re.match('Contact:\s.*', line1)):
                                     #print("rcvINVMatched Contact",line1)
                                     Contact = line1.replace("\n","")
                                  #Extract Record Route
                                  if(re.match('Record-Route:\s.*', line1)):
                                     #print("rcvINV Matched RR",line1)
                                     RRtemp = line1.replace("\n","")
                                     RRtemp = RRtemp+","
                                     RRlist.append(RRtemp)

                           if(re.match('SIP\/2\.0\s200\sOK', subline)):
                              #print(subline)
                              #print("recvd:200OK",subline)
                              for header in msg[0:]:
                                  #We have received 200 OK with CSeq: n INVITE, So its an UAC
                                  if(re.match('CSeq:\s[0-9]+\sINVITE', header)):
                                     RRlist = []
                                     uac = True
                                     #Take the whole message and extract headers
                                     for line1 in msg[0:]:
                                         #Extract From line
                                         if(re.match('From:\s.*', line1)):
                                            From = line1.replace("\n","")
                                            #print("rccv200OK",From)
                                         #Extract To line
                                         if(re.match('To:\s.*', line1)):
                                            To = line1.replace("\n","")
                                         #Extract Callid line
                                         if(re.match('Call-ID:\s.*', line1)):
                                            Callid = line1.replace("\n","")
                                         #Extract Contact
                                         if(re.match('Contact:\s.*', line1)):
                                            Contact = line1.replace("\n","")
                                         #Extract Record Route
                                         if(re.match('Record-Route:\s.*', line1)):
                                            RRtemp = line1.replace("\n","")
                                            RRtemp = RRtemp+","
                                            RRlist.append(RRtemp)
                                     readytosend = True
                                     break
                           if readytosend:
                              break

                    if readytosend:
                       break

                    if(re.match('--------', line)) and sent and not readytosend:
                       #print("sent:",tmpline1,line)
                       recvd = False
                       sent = False
                       msg = msgtmp
                       msgtmp = []
                       for subline in msg:
                           if(re.match('SIP\/2\.0\s200\sOK', subline)):
                              #print(subline)
                              for header in msg[0:]:
                                  #We have sent 200 OK with CSeq: n INVITE, So its an UAS
                                  if(re.match('CSeq:\s[0-9]+\sINVITE', header)):
                                     uac = False
                                     #Take the whole message and extract headers
                                     for line1 in msg[0:]:
                                         #Extract From line
                                         if(re.match('From:\s.*', line1)):
                                            From = line1.replace("\n","")
                                            #print("sent200OK",From)
                                            #print(From)
                                         #Extract To line
                                         if(re.match('To:\s.*', line1)):
                                            To = line1.replace("\n","")
                                         #Extract Callid line
                                         if(re.match('Call-ID:\s.*', line1)):
                                            Callid = line1.replace("\n","")
                                     readytosend = True
                                     break
                              if readytosend:
                                 break
                    if readytosend:
                       break
            except Exception as inst:
                   raise Exception("log File reading problem")
        else:
            print("Could not read file",file_name)


        RecordRoute = ''.join(RRlist)
        RecordRoute = RecordRoute.rstrip(',')
        my_logger.debug('RecordRoute: %s', RecordRoute)

        match = re.match('.*\<(.*)\>', Contact)
        if match:
           RequestURI = match.group(1)
           my_logger.debug('RequestURI: %s', RequestURI)
        match = re.match('Call-ID:\s(.*)', Callid)
        if match:
           Callid = match.group(1)
           self.__Callid = Callid
           my_logger.debug('Call ID: %s', Callid)

        tmpline = re.sub("Record-Route: ", "",RecordRoute)
        Routelist = tmpline.split(",")

        if not uac:
           #Exchange From and To
           tmpto = re.sub("From:", "To:",From)
           tmpfrom = re.sub("To:", "From:",To)
           To = tmpto
           From = tmpfrom
        my_logger.debug('To:%s',To)
        my_logger.debug('From:%s',From)
        #Get user number for authentication in Cleanup script
        match = re.match('.*sip:([0-9]+)@.*', From) 
        if match:
           UserNum =  match.group(1)

        file.close()

        if (os.path.isfile(templateFN)):
           try:
              templateFile = open(templateFN , 'r')
              cleanupFile= open(cleanupScriptFN , 'w')
              for line in templateFile:
                  line=re.sub("__REQURI__",RequestURI,line)
                  line=re.sub("__FROM__",From,line)
                  line=re.sub("__TO__",To,line)
                  line=re.sub("__USERNUM__",UserNum,line)
                  if re.search("__RR__",line):
                     if uac:
                        for x in reversed(Routelist):
                            cleanupFile.write("      Route: "+x+"\n")
                            #print("Route: ",x)
                     else:
                        for x in Routelist:
                            cleanupFile.write("      Route: "+x+"\n")
                            #print("Route: ",x)
                  else:
                     cleanupFile.write(line)
              cleanupFile.close()
              templateFile.close()
           except Exception as inst:
                  raise Exception("File reading problem")

        else:
            print("Could not read file",templateFN)
        return True

    def doCleanup(self):
        '''
        This function sends BYE to clear call state
        '''
        cmdstr = self.__sippcmd
        my_logger.debug('cmdstr:%s',cmdstr)
        match=re.match('.*\s([A-Za-z0-9_]+\.xml).*',cmdstr)
        if match:
           xmlFN=match.group(1)
           cmdstr=re.sub(xmlFN,"cleanupcall.xml",cmdstr)
           cmdstr=cmdstr+" -cid_str "+self.__Callid
            
        cmdstr=cmdstr+" -recv_timeout 5000"
        my_logger.debug('Cleanup Command:%s',cmdstr)
        retcode=subprocess.call(cmdstr, shell=True, stdout=self.__devnull, stderr=self.__devnull)
        if retcode == 255:
           my_logger.info('could not start cleanup %s',cmdstr)
        return

