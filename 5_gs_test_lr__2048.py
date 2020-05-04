#!/usr/bin/python3
from Pre_Requisite import *
from validation_gs_call import *
import pandas as pd
import time
import telnetlib

get_data = None


def lineRate():
    col_list = ["Line Rate"]
    lr_list = pd.read_csv('Resource.csv', usecols=col_list)
    return list(lr_list["Line Rate"])


def vmr():
    col_list = ["VMR"]
    vmr_list = pd.read_csv('Resource.csv', usecols=col_list)
    return list(vmr_list["VMR"])


def ip():
    col_list = ["IP"]
    ip_list = pd.read_csv('Resource.csv', usecols=col_list)
    ip_list = list(ip_list["IP"])
    return ip_list


lr, vmr, ip = lineRate(), vmr(), ip()
final_list = []


def retrieveList(arg1):
    global final_list
    final_list = preconditions(arg1, ip)


def calling(ep_ip, vmr_no, bandwidth):
    host = str(ep_ip)
    meeting_room = str(vmr_no)
    line_rate = str(bandwidth)
    command = 'dial manual ' + line_rate + ' ' + meeting_room + ' [sip]'
    tn = telnetlib.Telnet(host, 24)
    tn.write((command + "\n").encode('ascii'))
    tn.close()
    time.sleep(3)


def hangup():
    for i in final_list:
        ep = str(i)
        command = 'hangup all'
        tn = telnetlib.Telnet(ep, 24)
        tn.write((command + "\n").encode('ascii'))
        print("Endpoint " + ep + " is disconnecting from the conference.")
        tn.close()
        time.sleep(3)


def check_call_status(arg):
    active_count = 0
    for ep in final_list:
        tn = telnetlib.Telnet(ep, 24)
        cmd = ["\n", "getcallstate"]
        for i in range(len(cmd)):
            tn.write((cmd[i] + "\n").encode('ascii'))
            time.sleep(5)
            global get_data
            get_data = tn.read_very_eager()
        if b"connect" in get_data:
            print("Call status on GS " + ep + ": active")
            active_count += 1

        else:
            print("Call status on GS " + ep + ": inactive")
    if active_count == arg:
        print("Call connected successfully on all GS")
        return 0

    else:
        print("Call connected successfully on " + str(arg - active_count))
        return 1


def main_function(arg):
    retrieveList(arg)

    error_list = []

    print("###########TEST CASE STARTED FOR LR " + str(lr[0]) + "############################\n\n")
    fail_per_lr = 0
    # Connecting calls on GS

    print("#####################Connecting calls on GS############## \n ")
    for ep in final_list:
        print("Endpoint " + str(ep) + " is connecting to VMR " + str(int(vmr[0])) + " at line rate " + str(
            int(lr[0])) + " kbps.")
        calling(ep, int(vmr[0]), int(lr[0]))
        time.sleep(3)

    print("#####################Call Connection completed on GS EPs############## \n\n ")
    time.sleep(10)
    # Checking call status after connection

    print("############Validating Call Status on GS EPs##########\n")
    connection_status = check_call_status(arg)
    if connection_status == 0:
        print("Call connection successful on all GS Result: [PASS]")
    else:
        print("Not all EPs successfully connected to conference..Check logs for Eps Disconnection cause Result: ["
              "FAIL] ")
        print("##########Test Case failed for LR " + str(lr[0]) + " ##########")
        fail_per_lr += 1
        hangup()
        exit(1)
    print("############Completed Call Status Validation on GS EPs#############\n\n")
    time.sleep(10)
    # Start Statistics Validation(Remote Stream Count,Resolution Count,bit Rate Count and Health status of each call

    print(" ####################Validating Call Statistics on GS EPs ################\n ")
    validation_result, error_list = validation(final_list, lr[0], arg, error_list)
    if validation_result == 0:
        print("Validation is successful for all GS EPs Result: [PASS]")
    else:
        print("Validation is failed for some GS..Please check logs for further issues Result: [FAIL]")
        fail_per_lr += 1
        print(error_list)
    print(" ####################Completed Call Statistics  Validation on GS EPs############\n\n")
    time.sleep(10)
    hangup()

    if fail_per_lr == 0:

        print("\n\n#################################################################")
        print("\nOver All Test Result for " + str(lr[0]) + " GS Test : PASS\n")
        print("#################################################################")
        exit(0)
    else:
        print("#################################################################")
        print("Over All Test Result for " + str(lr[0]) + " GS Test : FAIL\n")
        print("#################################################################")
        exit(1)


main_function(5)
