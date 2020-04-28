##Below function will upgrade Media Relay Server using MRc and MRE RPMs
import os
import posixpath
import paramiko
from paramiko import AuthenticationException, BadHostKeyException
from paramiko.ssh_exception import NoValidConnectionsError

###Function to check pre-requisites for MR Upgradation......


def checking_pre_requisites(mr_ip):
    print("*****************************************************************************************")
    print("Condition 1:Check if Remote Server is up and running")
    print("*****************************************************************************************")

    hostname = mr_ip
    print("\nPinging MR IP " + hostname + " to check if server is up and running \n")
    response = os.system("ping -n 3 " + hostname)
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

        except AuthenticationException:
            print("Authentication failed, please verify your credentials: %s")

        except BadHostKeyException as badHostKeyException:
            print("Unable to verify server's host key: %s" % badHostKeyException)

        except NoValidConnectionsError as e:
            print("\n Unable to establish SSH connection: %s" % e)

    else:
        print("\nFail to ping machine " + mr_ip + ".Please check if server is up and running ")
        exit()


def put_dir(source, dst, ssh):
    print("RPM packages copying started to remote Server in /tmp location\n\n")
    source = os.path.expandvars(source).rstrip('\\').rstrip('/')
    dst = os.path.expandvars(dst).rstrip('\\').rstrip('/')
    for root, dirs, files in os.walk(source):
        for file in files:
            try:
                sftp = ssh.open_sftp()
                sftp.put(os.path.join(root, file),
                         posixpath.join(dst, ''.join(root.rsplit(source))[1:].replace('\\', '/'), file))
            except:
                print("something wrong with sftp")


## Function to  upgrade MR  and configuring file with required parameters....

def server_upgrade(rmx_ip, ssh):
    print("MR Installation Started.......\n")

    cmd_1 = "cd /tmp"
    cmd_2 = "chmod 777 media-*"
    cmd_3 = "yum -y erase media-relay-controller.noarch"
    cmd_4 = "yum -y erase media-relay-engine.x86_64"
    cmd_5 = "yum -y install media-relay-engine-*"
    cmd_6 = "yum -y install media-relay-controller-*"
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
    cmd_11 = "systemctl stop firewalld"

    stdin, stdout, stderr = ssh.exec_command(cmd_8 + '&&' + cmd_9 + '&&' + cmd_10 + '&&' + cmd_11)
    for line in stdout:
        print(line)


## Function to validate if downloaded rpms are installed successfully....


def validation(ssh):
    print("Validation Started...\n")
    cmd_1 = 'find /tmp -name \'media-relay-controller*\''
    cmd_2 = 'find /tmp -name \'media-relay-engine*\''
    cmd_3 = 'rpm -qa|grep media-relay-controller'
    cmd_4 = 'rpm -qa|grep media-relay-engine'
    a = []
    stdin, stdout, stderr = ssh.exec_command(cmd_1 + '&&' + cmd_2 + '&&' + cmd_3 + '&&' + cmd_4)
    for line in stdout:
        a.append(line)
    controller_build_version = str(a[0])[5:-5]
    engine_build_version = str(a[1])[5:-5]
    controller_installed_version = str(a[2])[0:-1]
    engine_installed_version = str(a[3])[0:-1]
    if engine_build_version == engine_installed_version and controller_build_version == controller_installed_version:
        print("Validation is successful as downloaded rpms and installed rpms version are same..... \n\n\n")
        print("MR successfully upgraded with :-\n")
        print("Media Controller Version : "+controller_installed_version)
        print("Media Relay Engine version : "+engine_installed_version)
        print("*********************************************************************************************************")
        print("Step 5 : Removing copied RPMs from /tmp directory.....\n")
        print("*********************************************************************************************************")
        cmd_5 = 'rm -rf /tmp/media-relay-*'
        stdin_1, stdout_1, stderr_1 = ssh.exec_command(cmd_5)
        print("\nRPMs removed successfully from /tmp directory ")
        print("Test Upgrade : PASS")


    else:
        print("Validation failed...\n Please check logs for further information ")
        print("Test Upgrade : FAIL")


#####Function which will take 'MR IP' and 'RPM Directory'  as input and will proceed Installation and Validation process

def mr_upgrade(mr_ip, dir):
    print("Step 1: Checking pre-requisites for MR upgrdation :\n")
    print("**********************************************************************************************")
    checking_pre_requisites(mr_ip)
    print("All pre-requisites are validated and system looks good to proceed with installation\n")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(mr_ip, username='root', password='kitten')
    print("Step 2: Copy RPMs to Remote Server at /tmp location\n")
    print("***********************************************************************************************")
    put_dir(dir, '/tmp', ssh)
    print("File successfully copied in Remote Server at /tmp location.......\n")
    print("Step 3: MR Installation \n ")
    print("************************************************************************************************")
    server_upgrade(mr_ip, ssh)
    print("MR Installation Completed Successfully\n ")
    print("Step 4: Start Validation\n")
    print("*************************************************************************************************")
    validation(ssh)
    ssh.close()
    print("\n**************************************************************************************************")
    print("Upgrade test has been completed")
    print("**************************************************************************************************")

