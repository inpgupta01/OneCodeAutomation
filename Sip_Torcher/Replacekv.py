#!/usr/local/bin/python3.2
import re
import os
import mylogger
import string

my_logger=mylogger.create_logger("Replacekv.py",stream=0,logFile='AutoFramework.log', logLevel='info')

      
def replacekvmain(tsname):
    if not os.path.exists(tsname):
       my_logger.error('File: %s does not exist', tsname)
       return False
    kvfile=open(tsname,"r")
    kvlist=[]
    kvdict={}
    for line in kvfile:
        strline = str(line)
        strline = strline.replace("\n","")
        strline = strline.lstrip()
        strline = strline.lstrip("\t")
        commentline = re.match("#", strline)
        if commentline: continue
        if not strline: continue
        match = re.match("test case:", strline.lower())
        if match:
           my_logger.info('Test Case line encountered that means Key Value section is over')
           break
        strline = strline.replace(" ","")
        eqmatch=re.search("=",strline)
        if not eqmatch:
           continue
        kvlist.append(strline)
    kvfile.close()
    for i in kvlist:
        tempf=i.rsplit("=")
        if (len(tempf)!=2):
           my_logger.info('Key Value mismatch: %s', str(tempf))
           return False
        kvdict['['+tempf[0]+']']= tempf[1] 
    my_logger.info('Key value list is: %s', str(kvdict))
    kvfile=open(tsname,"r")
    runfile=open("runfile.txt","w")
    for line in kvfile:
        commentline = re.match("#", line)
        if commentline: continue
        for k in kvdict.keys():
            #print(k+'->'+kvdict[k])
            if k in line:
               line=line.replace(k,kvdict[k])	
        runfile.write(line)
    runfile.close()
    kvfile.close() 
    return True



if __name__== '__main__':
    #import sys
    kvResult = False
    kvResult = replacekvmain('ppnn')
    if kvResult:
       print("Pass")
    else:
       print("Fail")


