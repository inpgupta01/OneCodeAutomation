#!/usr/bin/python3

##Below function will upgrade Media Relay Server using MRc and MRE RPMs
import os
import posixpath
import sys

import paramiko
from paramiko import AuthenticationException, BadHostKeyException
from paramiko.ssh_exception import NoValidConnectionsError

mr_ip = str(sys.argv[1])
controller_job = str(sys.argv[2])
engine_job = str(sys.argv[3])

def checking_pre_requisites(mr_ip):
    print("*****************************************************************************************")
    print("Condition 1:Check if Remote Server is up and running")
    print("*****************************************************************************************")

    hostname = mr_ip
    print("\nPinging MR IP " + hostname + " to check if server is up and running \n")
    response = os.system("ping -c 3 " + hostname)
    # Ping Host and then check the response...
    if response == 0:
        print(hostname + ' is up and running ....\n\n')
        print("*****************************************************************************************")
        print("Condition 2.Checking SSH connectivity")
        print("*****************************************************************************************")

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(mr_ip, username='root', password='kitten')
            print("SSH Connection : PASS\n")
            try:
                print("*****************************************************************************************")
                print("Condition 3: Existence of directory /var/log/media-relay in Remote Server")
                print("*****************************************************************************************\n")
                sftp = ssh.open_sftp()
                sftp.chdir("/var/log/poly/media-relay")
                ssh.close()
                print("Directory /var/log/poly/media-relay exists in remote server : YES \n")
            except IOError as e:
                print("Media Relay Directory is not existing at path /var/log/poly in the server %s exits" % e)
                exit()
        except AuthenticationException:
            print("Authentication failed, please verify your credentials: %s")
            exit()
        except BadHostKeyException as badHostKeyException:
            print("Unable to verify server's host key: %s" % badHostKeyException)
            exit()

        except NoValidConnectionsError as e:
            print("\n Unable to establish SSH connection: %s" % e)
            exit()

    else:
        print("\nFail to ping machine " + mr_ip + ".Please check if server is up and running ")
        exit()


def server_upgrade(rmx_ip, ssh):
    print("MR Installation Started.......\n")

    cmd_1 = "cd /tmp/"
    cmd_2 = "chmod 777 Media*"
    cmd_3 = "yum -y erase media-relay-controller.noarch"
    cmd_4 = "yum -y erase media-relay-engine.x86_64"
    cmd_5 = "yum -y install /tmp/MediaRelayEngine/media-relay-engine-*"
    cmd_6 = "yum -y install /tmp/MediaRelayController/media-relay-controller-*"
    cmd_7 = "chmod a+w /opt/poly/media-relay/engine/config/environment"

    stdin, stdout, stderr = ssh.exec_command(
        cmd_1 + '&&' + cmd_2 + '&&' + cmd_3 + '&&' + cmd_4 + '&&' + cmd_5 + '&&' + cmd_6 + '&&' + cmd_7)

    for line in stdout:
        print(line)

    ##Update ip config for MRE
    try:
        sftp = ssh.open_sftp()
        f = sftp.open('/opt/poly/media-relay/engine/config/environment', 'w')
        f.write('COD_RE_PUBLIC_IP=' + rmx_ip + '\n')
        f.write('COD_RC_IP=' + rmx_ip + '\n')
        f.write('COD_RC_PORT = 8089')
        f.close()
    except:
        print("Something wrong with sftp")

    ## Run MRC and MRE processes in RMX and disable firewall settings

    cmd_8 = "service media-relay-engine start"
    cmd_9 = "service media-relay-controller start"
    cmd_10 = "systemctl stop firewalld"
    cmd_11 = "systemctl disable firewalld"

    stdin, stdout, stderr = ssh.exec_command(cmd_8 + '&&' + cmd_9 + '&&' + cmd_10 + '&&' + cmd_11)
    for line in stdout:
        print(line)


def build_download(ssh, controller_version, engine_version):
    controller_Job = controller_version
    engine_job = engine_version

    ##Downloading controller build

    cmd_1 = "mkdir -p /tmp/MediaRelayController/ && cd /tmp/MediaRelayController/ && rm -rf *"
    cmd_2 = "curl  --output artifacts.zip --globoff --header \'PRIVATE-TOKEN: E6U9GiSdxHz3Mn3MGQ_z\' --header \'JOB-TOKEN: $CI_JOB_TOKEN\' https://onecode.polycom-labs.com/api/v4/projects/1104/jobs/" + controller_Job \
            + "/artifacts && unzip artifacts.zip "
    cmd_3 = "mkdir -p /tmp/MediaRelayEngine/ && cd /tmp/MediaRelayEngine/ && rm -rf *"
    cmd_4 = "curl  --output artifacts.zip --globoff --header \'PRIVATE-TOKEN: E6U9GiSdxHz3Mn3MGQ_z\' --header \'JOB-TOKEN: $CI_JOB_TOKEN\' https://onecode.polycom-labs.com/api/v4/projects/1304/jobs/" + engine_job \
            + "/artifacts && unzip artifacts.zip "
    stdin, stdout, stderr = ssh.exec_command(
        cmd_1 + '&&' + cmd_2 + '&&' + cmd_3 + '&&' + cmd_4)
    for line in stdout:
        print(line)


def validation(ssh):
    print("Validation Started...\n")
    cmd_1 = 'find /tmp/MediaRelayController -name \'media-relay-controller*\''
    cmd_2 = 'find /tmp/MediaRelayEngine -name \'media-relay-engine*\''
    cmd_3 = 'rpm -qa|grep media-relay-controller'
    cmd_4 = 'rpm -qa|grep media-relay-engine'
    cmd_5 = 'systemctl is-active media-relay-controller.service'
    cmd_6 = 'systemctl is-active media-relay-engine.service'
    a = []
    stdin, stdout, stderr = ssh.exec_command(
        cmd_1 + '&&' + cmd_2 + '&&' + cmd_3 + '&&' + cmd_4 + '&&' + cmd_5 + '&&' + cmd_6)
    for line in stdout:
        a.append(line)
    print(a)

    controller_build_version = str(a[0])[26:-5]
    engine_build_version = str(a[1])[22:-5]
    controller_installed_version = str(a[2])[0:-1]
    engine_installed_version = str(a[3])[0:-1]

    if engine_build_version == engine_installed_version and controller_build_version == controller_installed_version and \
            str(a[4][0:-1]) == 'active' and str(a[5][0:-1]) == 'active':
        print("Validation is successful as downloaded rpms and installed rpms version are same..... \n\n\n")
        print(
            "MR successfully upgraded with  MRC version \'" + controller_installed_version + "\' and MRE version \'" + engine_installed_version + "\'\n")
        print(
            "*********************************************************************************************************")
        #print("Step 5 : Removing copied RPMs from /tmp directory.....\n")
        print(
            "*********************************************************************************************************")
        #cmd_7 = 'rm -rf /tmp/*'
        #stdin, stdout, stderr = ssh.exec_command(cmd_7)
        #print("\nRPMs removed successfully from /tmp/Media* directory ")
        return 0


    else:
        print("Validation failed...\n Please check logs for further information ")
        #cmd_8 = 'rm -rf /tmp/*'
        #stdin, stdout, stderr = ssh.exec_command(cmd_8)
        #print("\nRPMs removed successfully from /tmp/Media* directory ")
        return 1


def mr_upgrade():
    print("Step 1: Checking pre-requisites for MR upgrade :\n")
    print("**********************************************************************************************")
    checking_pre_requisites(mr_ip)
    print("All pre-requisites are validated and system looks good to proceed with installation\n")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(mr_ip, username='root', password='kitten')
    print("Step 2: Downloading latest version from  repository and copying in location/tmp \n")
    build_download(ssh, str(controller_job), str(engine_job))
    print("Step 3: MR Installation \n ")
    print("************************************************************************************************")
    server_upgrade(mr_ip, ssh)
    print("MR Installation Completed Successfully\n ")
    print("Step 4: Start Validation\n")
    print("*************************************************************************************************")
    final_result = validation(ssh)
    ssh.close()
    print("\n**************************************************************************************************")
    print("Upgrade test has been completed")
    print("**************************************************************************************************")
    print(final_result)
    if final_result == 0:
        sys.exit(0)
    else:
        sys.exit(1)
    
mr_upgrade()
