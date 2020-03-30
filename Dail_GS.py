#!/usr/bin/python/

import telnetlib
import time

HOST =  '10.206.100.187'
print(HOST)
cmd_1 = "dial manual 1920 7002 [sip]"
print(cmd_1)
tn = telnetlib.Telnet(HOST, 24)
print(tn)
tn.write((cmd_1+"\n").encode('ascii'))
tn.close()
