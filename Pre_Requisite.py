import telnetlib
import os
import time


def ping_test(gs_ip):
    print("\n ###################### CHECK GS_IP PINGABILITY ############################### \n")
    response = os.system("ping -c 1 " + gs_ip)
    if response == 0:
        print("\n Network Active on GS : " + gs_ip + "\n")
        return 'success'
    else:
        print("\n Network Error with GS : " + gs_ip + "\n")
        return 'failure'


def telnet_check(gs_ip):
    print("\n ###################### CHECK TELNET CONNECTIVITY ############################### \n")
    try:
        telnetlib.Telnet(gs_ip, 24)
        print("Telnet successfully done on " + gs_ip)
        return 'success'
    except:
        print("Telnet failed on " + gs_ip)
        return 'failure'


def check_call_state(gs_ip):
    print("###################### CHECK FOR ACTIVE CALL IF ANY ############################### \n")
    tn = telnetlib.Telnet(gs_ip, 24)
    cmd = ["\n", "getcallstate"]
    for i in range(len(cmd)):
        tn.write((cmd[i] + "\n").encode('ascii'))
        time.sleep(5)
        get_data = tn.read_very_eager()
    if b"connect" in get_data:
        cmd = "hangup all"
        tn.write((cmd + "\n").encode('ascii'))
    else:
        print("No active calls \n")
    print("###################### ACTIVE CALL CHECK & HANGUP DONE ############################### \n\n")
    tn.close()


def preconditions(args, ip):
    final_count = 0
    final_list = []
    for i in ip:
        if final_count < args:
            ep_ip = i
            ping_result = ping_test(ep_ip)
            if ping_result == 'success':
                telnet_result = telnet_check(ep_ip)
                if telnet_result == 'success':
                    check_call_state(ep_ip)
                    final_count += 1
                    final_list.append(ep_ip)
                else:
                    continue
            else:
                continue
        else:
            break

    if len(final_list) == args:
        return final_list
    else:
        print("Not enough EPs to proceed the test ")
        exit(1)



