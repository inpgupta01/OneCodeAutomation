#!/usr/bin/python3

import os
import sys


def host():
    hostname = str(sys.argv[1])
    response = os.system("ping -c 3 " + hostname)

    if response == 0:
        print(hostname + ' is up and running ....\n\n')
        print("*****************************************************************************************")
        print("Condition 2.Checking SSH connectivity")
        print("*****************************************************************************************")
        sys.exit(0)

    else:
        print("Validation failed...\n Please check logs for further information ")
        # cmd_8 = 'rm -rf /tmp/*'
        # stdin, stdout, stderr = ssh.exec_command(cmd_8)
        # print("\nRPMs removed successfully from /tmp/Media* directory ")
        sys.exit(0)


host()
