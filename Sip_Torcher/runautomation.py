#!/usr/bin/python

###################################################################
##                                                               ##
##   May 20 2013; Added Pause Flag and stop Flag                 ##
##   May 24 2013; Added Failed Reason to Report                  ##
###################################################################
import time
import testSuiteReader
import WorkerM
import commandPr
import sys
import mylogger
import os.path
import logverifier
import prepReport
import Replacekv
import re

def main():
    ''' Runs Testsuite '''
    my_logger=mylogger.create_logger(sys.argv[0],stream=0,logFile='AutoFramework.log', logLevel='debug')
    my_logger.info(sys.argv[0] + ' execution started')
    testsuitefile=''
    if len(sys.argv) < 2:
        print('\nNo test suite provided Using default: sipptestsuite.txt')
        testsuitefile='sipptestsuite.txt'
    else:
        print('\nUsing testsuite: ' + sys.argv[1])
        my_logger.info('Using testsuite: %s', sys.argv[1])
        testsuitefile=sys.argv[1]
    if not os.path.exists(testsuitefile):
        my_logger.error('file %s does not exist',testsuitefile)
        print('Test suite file ' + testsuitefile +' does not exist')
        exit(1)

    print("\nTo STOP execution use command: touch stop_automation") 
    my_logger.info('To STOP execution use command: touch stop_automation') 
    print("To PAUSE execution use command: touch pause_automation") 
    my_logger.info('To PAUSE execution use command: touch pause_automation') 
    print("To UNPAUSE execution use command: rm pause_automation\n\n\n") 
    my_logger.info('To UNPAUSE execution use command: rm pause_automation\n\n\n') 

    if not Replacekv.replacekvmain(testsuitefile):
        my_logger.error('Exiting runner... Problem in processing key value')
        exit(1)

    suite1 = testSuiteReader.testSuite("runfile.txt")
    testcase = suite1.getTestCase()
    report = prepReport.writeReport()
    adminFailed = False
    regFailed = False
    stopFile = "stop_automation"
    pauseFile = "pause_automation"
    

    while len(testcase) >0:
      if os.path.exists(pauseFile):
         print("Pause Flag Seen")
         while os.path.exists(pauseFile):
               print("Continuing with pause ........")
               time.sleep(5)
               if os.path.exists(stopFile):
                  os.remove(pauseFile)
                  break
      if os.path.exists(stopFile):
         os.remove(stopFile)
         my_logger.info("Exiting from automation framework: stop flag seen")
         print("Exiting from automation framework: stop flag seen")
         break


      disunitObj = commandPr.sippCore(testcase)
      sippList = disunitObj.getSippCommands()
      scenarioTimer = disunitObj.getScenarioTimer()
      tcName = disunitObj.getTestcaseName()
      logCheckList =  disunitObj.getLogCheckList()
      myadminlist = disunitObj.getAdminList()
      sippjobs = []
      logfn = []
      resultList = []
      failReason = ''
      my_logger.info('Test Case: %s',tcName)
      my_logger.info('==========')
      regMatch = re.match("reg", tcName)
      #adminFailed = False

      #Skip code id registration Failed
      if regFailed and not regMatch:
         my_logger.error("Registration Failed, So Test Cases Skipped Until next registration")
         failReason = 'Prev Reg Failed'
         report.writeSkip(tcName, failReason)
         testcase = suite1.getTestCase()
         del disunitObj
         del sippList
         del scenarioTimer         
         continue

      #Execute sipp scenarios in different process
      for line in sippList:
          #print("Executing main sipp:",line)
          p = WorkerM.sippWorker(line)
          sippjobs.append(p)
          my_logger.info("================SIPP Start called==============")
          p.start()
          if regMatch:
             time.sleep(4)
      #Set and Get Logfile Mames
      #log file names stored in logfn list, if log file is not available None will be the entry.
      time.sleep(1)
      for j in sippjobs:
          logfilenametmp = j.setnGetLogFN()
          logfn.append(logfilenametmp)

      #Check sipp and RTPverifier if alive even after timer expires
      my_logger.debug('waiting %d seconds or all processes to exit',scenarioTimer) 
      for i in range (1, scenarioTimer, 2):
          loopFlag = False
          time.sleep(2)
          for j in sippjobs:
              loopFlag = loopFlag or j.is_alive() 

          if not loopFlag:
              my_logger.debug('All sipp exited before timer expiry')
              break

      #Kill sipp if alive even after timer expires
      for j in sippjobs:
          if j.is_alive():
             my_logger.debug('Process %d is still alive',j.pid)
             resultList.append(False)
             j.killchild()
             failReason = 'SIPp Killed'
          else:
             resultList.append(True) 



      my_logger.debug('Waiting to join for all child process')
      for j in sippjobs:
          j.join()

          for j in sippjobs:
             pidfile = str(j.pid)+'_STAFtmpuse'
             if os.path.exists(pidfile):
                os.remove(pidfile)
                failReason = 'Error returned by SIPp'
                resultList.append(False)
                errorfile=j.getLogFN()
                if errorfile:
                   if re.search('_messages.log',errorfile):
                      errorfile = errorfile.replace('_messages.log','_errors.log')
                      if os.path.exists(errorfile):
                         my_logger.error("Go through Error file: %s to know why sipp returned error",errorfile)
                         pass
                      else:
                         my_logger.error("sipp Error File does not exist")
                         pass
                else:
                    my_logger.error("sipp log file does not exist")
                if j.isBYEComplete():
                   #continue
                   pass
                else:
                   j.prepCleanup()
                   j.doCleanup()

     
 
      if regMatch and not report.getResult(resultList):
         regFailed = True
      else:
         regFailed = False
         #skip until you find a reg again     
      # Logfile Verification Part
      if( (not regMatch) and (report.getResult(resultList)) ):
         my_logger.debug('All Log File Names: %s',str(logfn))
         my_logger.debug('Length of log file name List: %s',str(len(logfn)))
         my_logger.debug('SIPP and corresponding log check parameters:')    
         for xx in logCheckList:
             my_logger.debug('%s',str(xx))    
         #my_logger.debug('SIPP and corresponding log check parameters: %s',str(logCheckList))
         my_logger.debug('Length of parameter List: %s',str(len(logCheckList)))
         if((len(logfn)!=len(logCheckList)) and (report.getResult(resultList))):       
           my_logger.debug('****Logfilename and sipp command list are not same or testcase is already failed: Operation Skipped ****')
         else:
           #my_logger.debug('Logfile Verification Started')
           logindex = 0
           for pp in logCheckList:
               for qq in pp:
                   if not logfn[logindex]:
                      my_logger.debug('No log file available skipped logcheck: %s',str(qq))
                      resultList.append(False)
                      break
                   tmplist = []
                   tmplist.append(logfn[logindex])
                   tmplist.extend(qq.split())
                   logcheckResult = logverifier.runnermain(' '.join(tmplist))
                   if not logcheckResult: 
                      failReason = 'Logcheck Failed'
                   resultList.append(logcheckResult)
               logindex = logindex + 1

      #Write Pass or Fail in Report File
      report.write(tcName,resultList,failReason)  
      #Following line should be placed at the end of while loop
      testcase = suite1.getTestCase()
      del disunitObj
      del sippList
      del scenarioTimer
      time.sleep(3) #sleep to cleanup socket closer times
    del report
    my_logger.info(sys.argv[0] + ' execution completed')

if __name__ == "__main__":
    main()
