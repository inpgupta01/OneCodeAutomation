#!/usr/local/bin/python3.2
import re
import mylogger
import string
import os.path

my_logger=mylogger.create_logger("logverifier.py",stream=0,logFile='AutoFramework.log', logLevel='debug')

def usage():
    my_logger.info('Usage:')
    my_logger.info('logcheck:Method:<SIP Method[|SIP Method]> Mocc:<Occurence No| last> [Header:<SIP-header>  Hocc:<any|integer> Hstring:<Value of SIP-header>] [SDP:<True|False>] [Hsdp:<SIP-header> Hsdpocc:<any|integer> Hsdpstr:<Value of SIP-header>]')

hoccdict={}
sdphoccdict={}
class check_exp:
    def __init__(self):
        self.methodDict = {}
        self.sdp_mentioned = False
        self.sdp = False
        self.header_dict ={} 
        self.sdp_dict = {}
    def info(self):
        my_logger.info('SIP Method Dictionary: {0}'.format(self.methodDict))
        my_logger.info('SDP Mentioned: {0}'.format(self.sdp_mentioned))
        my_logger.info('SDP: {0}'.format(self.sdp))
        my_logger.info('SIP header list: {0}'.format(self.header_dict))
        my_logger.info('SDP list: {0}'.format(self.sdp_dict))
    def setDefaultValue(self):
        self.methodDict = {}
        self.sdp_mentioned = False
        self.sdp = False
        self.header_dict ={}
        self.sdp_dict = {}


expinst1=check_exp()

def validaten_set(current_list):
    my_logger.info("Going to check arg:%s\n",str(current_list))
    expinst1.setDefaultValue()
    methodcount=0
    headerfound = False
    headername = ''
    headeroccfound = False
    hstringfound = False
    methodString=''
    SDPheaderfound = False
    SDPheadername = ''
    SDPheaderoccfound = False
    SDPhstringfound = False
    for i in current_list:
      tmpline=i.replace(" ","")
      if not tmpline: continue
      tmplist=tmpline.rsplit(":")
      if(len(tmplist)==2):
         my_logger.debug('List of length 2: %s',str(tmplist))
         #Check for Method
         if(tmplist[0].lower() == 'method'):
           methodcount=methodcount+1
           methodString=tmplist[1].lower()
           if methodcount>1:
              my_logger.error('More than one Metrhod not allowed')
              return False
         if(tmplist[0].lower() == 'mocc'):
           if methodString:
              methodList=methodString.rsplit("|")
              methodOccList=tmplist[1].rsplit("|")
              defaultOcc=''
              if methodOccList:
                 defaultOcc=methodOccList[0]
              else:
                 my_logger.error('No Occurance defined for Method:')
                 return False

              for ml in methodList:
                  if methodOccList:
                     myOcc=methodOccList.pop(0)
                  else:
                     myOcc=defaultOcc
                  if re.match('last',myOcc.lower()): 
                     expinst1.methodDict[ml]=0
                  elif(re.match(r'\d',myOcc)):
                     expinst1.methodDict[ml]=int(myOcc)
                  else:
                     my_logger.error('Wrong value: %s',myOcc)
                     return False
           else:
              my_logger.error('Found Mocc before Method')
              return False

         #Processing of multiple header
         if(tmplist[0].lower() == 'header'):
            headerfound = True
            headername = tmplist[1]
            headeroccfound = False
            hstringfound = False

         if(tmplist[0].lower() == 'hocc'):
            if headerfound:
               if(re.match(r'\d',tmplist[1])):
                  headername = headername + '_' + tmplist[1]
                  headeroccfound = True
                  hstringfound = False
               elif re.match('any',tmplist[1].lower()):
                  headername = headername + '_' + '0'
                  headeroccfound = True
                  hstringfound = False
               else:
                  my_logger.error('Wrong value: %s sor key: %s',tmplist[1],tmplist[0])
                  return False
            else:
               my_logger.error('No Header defined for Hocc: %s',tmplist[1])
               return False
         if(tmplist[0].lower() == 'hstring'):
            if headerfound and headeroccfound:
               expinst1.header_dict[headername]=tmplist[1]
               headername = ''
               hstringfound = True
               headerfound = False
               headeroccfound = False
            else:
               my_logger.error('No Header or Hocc defined for Hstring: %s',tmplist[1])
               headername = ''
               headerfound = False
               headeroccfound = False
               return False

         #Processing for SDP
         if(tmplist[0].lower() == 'sdp'):
            expinst1.sdp_mentioned = True
            if(tmplist[1].lower() == 'true'):
               expinst1.sdp = True
              
         #Processing of multiple header
         if(tmplist[0].lower() == 'hsdp'):
            SDPheaderfound = True
            SDPheadername = tmplist[1]
            SDPheaderoccfound = False
            SDPhstringfound = False

         if(tmplist[0].lower() == 'hsdpocc'):
            if SDPheaderfound:
               if(re.match(r'\d',tmplist[1])):
                  SDPheadername = SDPheadername + '_' + tmplist[1]
                  SDPheaderoccfound = True
                  SDPhstringfound = False
               elif re.match('any',tmplist[1].lower()):
                  SDPheadername = SDPheadername + '_' + '0'
                  SDPheaderoccfound = True
                  SDPhstringfound = False
               else:
                  my_logger.error('Wrong value: %s sor key: %s',tmplist[1],tmplist[0])
                  return False
            else:
               my_logger.error('No Hsdp defined for Hsdpocc: %s',tmplist[1])
               return False
         if(tmplist[0].lower() == 'hsdpstr'):
            if SDPheaderfound and SDPheaderoccfound:
               expinst1.sdp_dict[SDPheadername]=tmplist[1]
               SDPheadername = ''
               SDPhstringfound = True
               SDPheaderfound = False
               SDPheaderoccfound = False
            else:
               my_logger.error('No Hsdp or Hsdpocc defined for Hsdpstr: %s',tmplist[1])
               SDPheadername = ''
               SDPheaderfound = False
               SDPheaderoccfound = False
               return False
      else:
         my_logger.error('Wrong syntax %s\n',str(tmplist))
         return False

    if methodcount==0:
       my_logger.error('No Method found' )
       return False
    if headerfound:
       if(headeroccfound==False or hstringfound==False):
          my_logger.error('No Hocc or Hstring while Header Present')
          return False

    if SDPheaderfound:
       if(SDPheaderoccfound==False or SDPhstringfound==False):
          my_logger.error('No Hsdpocc or Hsdpstr while Header Present')
          return False
    expinst1.info()
    return True

def retMsg(logfn):
    my_logger.info('Reading log File: %s',logfn)
    if not os.path.exists(logfn):
       my_logger.error('Logfile: %s does not exist',logfn)
       return []
    logfnhandle=open(logfn , 'r')
    RecordNow=False
    msgRcvd=False
    DBL = True
    methodoccdict={}
    #methodlist=expinst1.methodname.split("|") 
    returnlist=[] 
    tmprlist=[]
    print(expinst1)
    for i in iter(expinst1.methodDict):
        methodoccdict[i]=0
    
    for line in logfnhandle:
        #line=line.replace('\n',"")
        
        #Remov Blank Line If Required
        if DBL:
           line1=line
           line1.replace("\n"," ")
           line1.replace("\t"," ")
           if line1.isspace():
              if not line1:
               print('BL found')
              continue

        #Indication of End of received message
        if(re.match('socket_write_primitive', line)):
           if RecordNow:
              nonendnewlinelist=[]
              removenl=True
              my_logger.debug('tmprlist is'+tmprlist)
              for p in reversed(tmprlist):
                  q=p
                  if removenl:
                     q=q.replace("\n"," ")
                     q=q.replace("\t"," ")
                     if q.isspace():
                        continue
                     else:
                        removenl=False
                  nonendnewlinelist.append(p)
              #tmprlist=reversed(nonendnewlinelist)
              tmprlist=[]
              for k in reversed(nonendnewlinelist):
                  tmprlist.append(k) 
              returnlist.append(tmprlist) 
              my_logger.debug('returnlist is'+returnlist)
              tmprlist=[]
           RecordNow=False  
           msgRcvd=False

        if msgRcvd:
           print('Going to match Method: '+expinst1.methodname+'with line'+line)
           for mthd in iter(expinst1.methodDict):
               tmpmthd=mthd
               my_logger.debug('Entering match')
               if(re.match(r'\d+',mthd)):
                  tmpmthd='sip/2.0 '+mthd
               if(re.match(tmpmthd, line.lower())):
                  print("Match Found")
                  if(expinst1.methodDict[mthd] == 0):
                    RecordNow=True
                  else:
                     methodoccdict[mthd] = methodoccdict[mthd] + 1
                     if(expinst1.methodDict[mthd] ==  methodoccdict[mthd]):
                        print("......Match Found.........")
                        RecordNow=True
          #print(line,end="")

        if RecordNow:
           tmprlist.append(line) 
           #print(line,end="")


        if msgRcvd:
           ContMatch=re.match('Content-Length:\s+([1-9]+)', line)
           if ContMatch:
              if ContMatch.group(1):
                 #print("Length",ContMatch.group(1))
                 DBL=False
        #Indication of received Message
        if(re.match('SCTP message received ', line)): 
           print("========")
           msgRcvd=True
           RecordNow=False
           DBL=True
    if tmprlist:
       removenl=True
       nonendnewlinelist=[]
       #Remove last newline of tmprlist
       for p in reversed(tmprlist):
           q=p
           if removenl:
              q=q.replace("\n"," ")
              q=q.replace("\t"," ")
              if q.isspace():
                 continue
              else:
                 removenl=False
           nonendnewlinelist.append(p)
       tmprlist=[]
       for k in reversed(nonendnewlinelist):
           tmprlist.append(k)
       returnlist.append(tmprlist)
    logfnhandle.close()

    #Processing for Last occurence of method when list contains all occurrence
    tmprtnlist=[]
    for mthd in iter(expinst1.methodDict):
        tmpmthd=mthd
        for i in reversed(returnlist):
            if i[0]:
               j=i[0]
               if(re.match(r'\d+',mthd)):
                 tmpmthd='sip/2.0 '+mthd
               if(re.match(tmpmthd, j.lower())):
                  tmprtnlist.append(i)
                  break
                 
    returnlist=[]
    for i in reversed(tmprtnlist):
        returnlist.append(i)
    return returnlist

def checkIt(mymsg):
    tmphoccdict = {}
    matchDict={}
    tmpsdphoccdict={}
    matchsdpDict={}
    SDPCont=[]
    foundSDPinMsg=False
    thisMethod="none"
    firstLineofMsg=mymsg[0]
    if(re.match('sip/2.0 ',firstLineofMsg.lower())):
       thisMethod=firstLineofMsg.split(None,1)[1]+" Response"
    else:
       thisMethod=firstLineofMsg.split(None,1)[0] + " Request"
    
    for i in iter(expinst1.header_dict):
        tmphoccdict[i]=0
        matchDict[i]=False
        foundSDPinMsg=False
    for i in iter(expinst1.sdp_dict):
        tmpsdphoccdict[i]=0
        matchsdpDict[i]=False

    if expinst1.sdp_mentioned:
       matchDict['sdp']=False
    for i in mymsg:
        if foundSDPinMsg:
           SDPCont.append(i)
        #Is SDP Present Processing
        if i=='\n':
           foundSDPinMsg=True
           if expinst1.sdp:
              matchDict['sdp']=True
        #Header Processing
        for j in iter(expinst1.header_dict):
            hdronly=j.rsplit("_")
            if(re.match(hdronly[0].lower(),i.lower())):
               tmphoccdict[j]=tmphoccdict[j]+1
               my_logger.info('Found Header %s Occurance:%d ',hdronly[0],tmphoccdict[j])
               if(re.search(expinst1.header_dict[j],i)):
                  if(hoccdict[j]==0):
                      matchDict[j]=True
                      my_logger.info('Match %s Found in Occurance:%d in header %s',expinst1.header_dict[j],tmphoccdict[j],hdronly[0])
                      break
                  elif(hoccdict[j]==tmphoccdict[j]):
                      my_logger.info('Match %s Found in Occurance:%d in header %s',expinst1.header_dict[j],tmphoccdict[j],hdronly[0])
                      matchDict[j]=True        
                      break
    my_logger.debug('Header Match Dictionary is: %s',str(matchDict))
    #SDP Processing
    if SDPCont:
       for i in SDPCont:
           for j in iter(expinst1.sdp_dict):
               hdronly=j.rsplit("_")
               if(re.match(hdronly[0].lower(),i.lower())):
                  tmpsdphoccdict[j]=tmpsdphoccdict[j]+1
                  my_logger.info('Found SDP Header %s Occurance:%d ',hdronly[0],tmpsdphoccdict[j])
                  if(re.search(expinst1.sdp_dict[j],i)):
                     if(sdphoccdict[j]==0):
                        matchsdpDict[j]=True
                        my_logger.info('Match %s Found in Occurance:%d in SDPheader %s',expinst1.sdp_dict[j],tmpsdphoccdict[j],hdronly[0])
                        break
                     elif(sdphoccdict[j]==tmpsdphoccdict[j]):
                         matchsdpDict[j]=True
                         my_logger.info('Match %s Found in Occurance:%d in SDPheader %s',expinst1.sdp_dict[j],tmpsdphoccdict[j],hdronly[0])
                         break
    my_logger.debug('SDP Header Match Dictionary is: %s',str(matchsdpDict))
    Result=True
    for i in iter(matchDict):
        Result=Result and matchDict[i]
        if not matchDict[i]:
            my_logger.info("----> Could not find specified match for Header %s in %s",i.split('_')[0],thisMethod)
            pass
    for i in iter(matchsdpDict):
        Result=Result and matchsdpDict[i]
        if not matchsdpDict[i]:
            my_logger.info("----> Could not find specified match for SDP Header %s in %s",i.split('_')[0],thisMethod)
            pass

              
        #print(i,end="")
    #print("====")
    return Result

def runnermain(temp_argv):
 try:
    myargs = temp_argv.rsplit(" ")
    if(len(myargs)<3):
       my_logger.error('Insufficient Arguments')
       usage()
       return False
    readfile=myargs[0]
    my_logger.info('Will check sipp log file:%s',readfile)
    gotMsg=[]
    if validaten_set(myargs[1:]):
       gotMsg = retMsg(readfile)
       if not gotMsg:
          my_logger.error('FAIL: Method with specified Occurance does not exist in log file %s',readfile)
          return False
       MatchFound=False

       #Pre header processing
       for i in iter(expinst1.header_dict):
           tmplist=i.rsplit("_")
           occ=int(tmplist[1])
           hoccdict[i]=occ
       #Pre SDP Processing
       for i in iter(expinst1.sdp_dict):
           tmplist=i.rsplit("_")
           occ=int(tmplist[1])
           sdphoccdict[i]=occ

       for i in gotMsg:
           if i:
              MatchFound=checkIt(i)
           if MatchFound:
              my_logger.info('PASS: Match successfull')
              return True
       my_logger.error('FAIL: Match Failed')
       return False
    else:
       usage()
       return False
 #except re.error as e:
 except Exception as e:
    my_logger.error('FAIL: Exception: %s',e.__str__()) 
    return False

if __name__== '__main__':
    #import sys
    logResult = False
    #logResult = runnermain("UAC_TC_13_Attd_Xfer_17165_messages.log Method:NOTIFY Mocc:4 SDP:True Hsdp:sipfrag Hsdpstr:200.OK Hsdpocc:*")
    #logResult = runnermain("UAC_TC_14_CFU_FS_14718_messages.log Method:407 mocc:1")
    logResult =  runnermain("UAC_TC_1_Basic_Update_EM_UAC_Voice_Scenario_Same_Codec_22148_messages.log Method:183 Mocc:1")
    #logResult = runnermain("testuas_26609_messages.log Method:INVITE|BYE Mocc:1 Header:Contact Hocc:1 Hstring:6220000275 SDP:True Hsdp:m Hsdpocc:1 Hsdpstr:AVP")
    if logResult:
       print("Pass")
    else:
       print("Fail")

