from time import strftime
import mylogger
my_logger=mylogger.create_logger('prepReport.py',stream=0,logFile='AutoFramework.log', logLevel='debug')

class writeReport:
    def __init__ (self):
        try:
            tt = strftime("%Y-%m-%d-%H%M%S")
            self.__ReportFilename = "Report-"+str(tt)
            my_logger.info('Report File is: %s',self.__ReportFilename)

            self.__repfile = open(self.__ReportFilename,"w")
            outstr = '{0:10}             {1:6}    {2:25}\n'.format("TESTCASE","RESULT","Failure Reason")
            self.__repfile.write(outstr) 
            outstr = '{0:10}             {1:6}    {2:25}\n'.format("========","======","==============")
            self.__repfile.write(outstr) 
            self.__repfile.close()
         
        except Exception as inst:
            my_logger.info('Exiting.')
    
    def write( self, tcname, temprsltlist, reason):
        repfilep=open(self.__ReportFilename,"a")
        tcresult = True
        for rslt1 in temprsltlist:
            tcresult = tcresult and rslt1

        if tcresult: 
           outstr = '{0:10} ----------> {1:6}\n'.format(tcname,"PASS")
        else:
           outstr = '{0:10} ----------> {1:6}    {2:25}\n'.format(tcname,"FAIL",reason)
        repfilep.write(outstr)
        repfilep.close()


    def writeSkip( self, tcname, reason):
        repfilep=open(self.__ReportFilename,"a")
        outstr = '{0:10} ----------> {1:6}    {2:25}\n'.format(tcname,"SKIP",reason)
        repfilep.write(outstr)
        repfilep.close()

    def getResult( self, temprsltlist):
        tcresult = True
        for rslt1 in temprsltlist:
            tcresult = tcresult and rslt1
        return tcresult

        
    def __del__ (self):
        pass

#if __name__ == "__main__":
#
#   report = writeReport()
#   resultList = [True,False,True,False]
#   report.write('tc1',resultList,"test")
#
#   resultList = [True,True,True]
#   report.write('tc2',resultList,"")
#
#   report.writeSkip('tc3',"provisioning Failed")
#
#   del report

