#!/usr/bin/python3
import telnetlib
import time

import pandas as pd
import os



def telnetService(ip):
    print("\n***************************CHECKING TELNET SERVICE********************************\n")
    try:
        telnetlib.Telnet(ip, 24)
        print("Telnet Service active on GS : " + ip + "\n")
        print("**********************DONE WITH TELNET SERVICE CHECK***************************\n\n")
        return 'success'

    except:
        print("Telnet Service not active on GS : " + ip + "\n")
        print("*******************TELNET SERVICE FAILED. ABORTING THE TEST********************\n")
        exit(1)
        return 'failure'


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
    ip_list = list(ip_list["IP"])[0]
    return ip_list


get_data = None
data = None
lr, vmr, ip = lineRate(), vmr(), ip()


def pingTest(ip):
    print("\n****************************CHECKING GS PINGABILITY**********************************\n")
    response = os.system("ping -c 5 " + ip)
    if response == 0:
        print("\n Network Active on GS : " + ip + "\n")
        print("\n************************DONE WITH PINGABILITY TEST********************************\n")
        return 'success'
    else:
        print("\n Network Problem with GS : " + ip + "\n")
        print("*************************PINGABILITY FAILED. ABORTING THE TEST***********************\n")
        exit(1)
        return 'failure'


def callState(ip):
    global get_data
    print("\n************************CHECKING FOR ACTIVE CALL IF ANY********************************\n")
    tn = telnetlib.Telnet(ip, 24)
    command = ["\n", "getcallstate"]
    for i in range(len(command)):
        tn.write((command[i] + "\n").encode('ascii'))
        time.sleep(5)
        get_data = tn.read_very_eager()
    if b"connect" in get_data:
        cmd = "hangup all"
        tn.write((cmd + "\n").encode('ascii'))
        print("Active call detected, disconnected the ongoing call.\n")
    else:
        print("No active calls.\n")
    print("****************************DONE WITH ACTIVE CALL CHECK***********************************\n\n")
    tn.close()


def GS_call(GS_IP, VMR, LR):
    ##Dialing GS in to VMR using format  'dial auto @bandwidth @VMR'
    print(VMR)
    print(LR)
    cmd_1 = "dial manual " + str(int(LR)) + " " + str(int(VMR))
    print(cmd_1)
    print("\nDialing " + str(VMR) + " on GS " + GS_IP + " with LR " + str(LR) + "\n")
    try:
        tn = telnetlib.Telnet(GS_IP, 24)
        tn.write((cmd_1 + "\n").encode('ascii'))
    except Exception as e:
        print(e)
    print("Call connecting  on GS :" + GS_IP + " with LR:" + LR + " to Conf " + str(VMR))
    time.sleep(5)

    ##Fetching GS statistics using GS REST API Commands


def getStatistics(gs_ip):
    tn = telnetlib.Telnet(gs_ip, 24)
    tn.write(b"advnetstats 0 \n")
    tn.write(b"netstats 0 \n")
    time.sleep(5)

    ##Read GS telnet session output to a txt file MyFile.txt

    data9 = tn.read_very_eager()
    output = data9.decode('ascii')
    tn.close()
    return output


##Writing  GS statistics from MyFile.txt to Dictionary 'call_statistics'


def write_actual_stats_to_dict(tlnet_output):
    call_statistics = {}
    a = tlnet_output.split(' ')
    for y in a:
        lines_subset = y.split(":")
        if len(lines_subset) == 2 and lines_subset[1] != "":
            key, values = lines_subset[0], lines_subset[1]
            call_statistics[key] = values
    return call_statistics


##Converting excel 'expected_data.xlsx' with expected results  to  dictionary 'expected_statistics'................

def write_expected_stats_to_dict():
    file_path = 'expected_data.xlsx'
    df = pd.read_excel(file_path, encoding='utf-16')
    expected_statistics = df.set_index('index').to_dict()
    return expected_statistics


def post_dial_call_status(arg):
    global data
    active_count = 0
    tn = telnetlib.Telnet(arg, 24)
    cmd = ["\n", "getcallstate"]
    for i in range(len(cmd)):
        tn.write((cmd[i] + "\n").encode('ascii'))
        time.sleep(5)
        data = tn.read_very_eager()
    if b"connect" in data:
        print("\nCall status on GS " + arg + ": active")
        active_count += 1
        return 0

    else:
        print("\nCall status on GS " + arg + ": inactive")
        return 1


##Function to validate GS statistics (Actual Call  Statistics(From Telent Output),Expected Call statistic(From Excel Expected_Result.xlsx)

def validation(expected_value, actual_value, lr, data_mismatch):
    for i in expected_value:
        if i == lr:
            for key in expected_value[i]:
                if key != 'tvfr' and key != 'rvfr' and key != 'rvru' and key != 'tvru':
                    if str(expected_value[i][key]) == actual_value[key]:
                        print("Matching value for " + '\'' + key + '\'' + "-" + "Expected Value :" + str(
                            expected_value[i][key]) + " Actual Value : " + actual_value[key] + " RESULT:[PASS]")
                    else:
                        print("Value mismatched for " + '\'' + key + '\'' + "-" + " Expected Value : " + str(
                            expected_value[i][key]) + " Actual Value:" + actual_value[
                                  key] + "RESULT:[FAIL]")
                        data_mismatch += 1

                else:
                    max_frame_rate = expected_value[i][key]
                    min_frame_rate = expected_value[i][key] // 2

                    if key == 'tvfr' or key == 'rvfr':

                        if min_frame_rate <= int(actual_value[key]) <= max_frame_rate:
                            print(key + " looks good as Actual Frame Rates :" + str(
                                actual_value[key]) + " is between " +
                                  str(max_frame_rate) + " and " + str(min_frame_rate) + " RESULT:[PASS]")
                        else:
                            print(key + " does not look good as Actual Frame Rates :" + str(
                                actual_value[key]) + " is not in between  " + str(max_frame_rate) + " and " + str(
                                min_frame_rate) + " RESULT:[FAIL]")
                            data_mismatch += 1

    ### Validating tvru<tvr and rvru<rvr from acutal statistics
    if int(actual_value['tvru']) <= (int(actual_value['tvr']) + 10):
        print(
            "Transmission Rate Used (tvru) " + actual_value['tvru'] + " <= Max Transmission Rate(tvr): " + actual_value[
                'tvr'] + " Upto +10 kbps is acceptable RESULT:[PASS]")
    else:
        print("Transmission Rate Used(tvru) " + actual_value['tvru'] + " exceeds Max Transmission Rate(tvr):" +
              actual_value[
                  'tvr'] + " RESULT:[FAIL]")
        data_mismatch += 1
    if int(actual_value['rvru']) <= (int(actual_value['rvr']) + 10):
        print(
            "Receiving Rate Used(rvru) " + actual_value['rvru'] + " < Max Transmission Rate(rvr): " + actual_value[
                'rvr'] + " Upto +10 kbps is acceptable RESULT:[PASS]")
    else:
        print("Receiving Rate Used " + actual_value['rvru'] + " exceeds Max Transmission Rate(rvr) :" + actual_value[
            'rvr'] + "RESULT:[FAIL]")
        data_mismatch += 1
    return data_mismatch


def call_hangup_5(ip):
    cmd = "hangup all"
    tn = telnetlib.Telnet(ip, 24)
    tn.write((cmd + "\n").encode('ascii'))
    print("\nEndpoint " + ip + " is disconnecting\n")
    tn.close()
    time.sleep(3)


def test_loopback():
    pingTest(ip)
    time.sleep(2)
    telnetService(ip)
    time.sleep(2)
    callState(ip)
    time.sleep(2)
    parameter_mismatch = 0
    pass_count = 0
    fail_count = 0
    for i in range(len(vmr)):
        LR = str(lr[i])
        vmr_no = str(vmr[i])
        ep_ip = str(ip)
        print("*************************************")
        print("Loop back test started for LR " + str(lr[i]))
        print("************************************")
        print("\n\n************************************")
        print("Step 1:Connect Call on GS ")
        print("************************************")
        GS_call(ep_ip, vmr_no,LR)
        call_status = post_dial_call_status(ep_ip)
        if call_status == 1:
            exit(1)
        gs_output = getStatistics(ep_ip)
        get_actual_statistics = write_actual_stats_to_dict(gs_output)
        get_expected_statistics = write_expected_stats_to_dict()
        print("\n\n************************************")
        print("Step 2:Statistics Validation \n ")
        print("************************************")
        print("\nStarting Group Series Statistics Validation for LR " + str(lr[i]) + " kbps.............\n")
        data_mismatched = validation(get_expected_statistics, get_actual_statistics, int(LR), parameter_mismatch)
        call_hangup_5(ep_ip)
        if data_mismatched == 0:

            print("************************************************************")
            print("Test Result for Loopback Test with " + str(LR) + ": [PASS]")
            print("************************************************************")
            pass_count += 1
        else:
            print("*************************************************************************************************")
            print("Test Result for Loopback Test with " + str(LR) + ": [FAIL](" + str(
                data_mismatched) + " feilds mismatched)")
            print("*************************************************************************************************")

            fail_count += 1

        print("\n\n------------------Test Completed for " + str(lr[i]) + "-------------------------\n")
    print("****************************************************************")
    print("OVERALL LOOPBACK TESTING RESULT:\n")
    print("****************************************************************")
    print("TOTAL LR EXECUTED:" + str(len(vmr)))
    print("\nPASS : " + str(pass_count))
    print("\nFAIL : " + str(fail_count))
    if fail_count == 0:
        exit(0)
    else:
        exit(1)
test_loopback()
