#!/usr/bin/python3

import paramiko
import sys

Host = str(sys.argv[1])
username = "root"
password = "Polycom1"
#Version = str(sys.argv[3])
Job = str(sys.argv[2])
#path = "https://onecode.polycom-labs.com/octopus/media-controller/-/jobs/"+Job+"/artifacts/raw/media-relay-controller-0.0.1-"+Version+".noarch.rpm"


ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(Host, username=username, password=password)
#stdin, stdout, stderr = ssh.exec_command("mkdir -p /tmp/MediaRelayController/ && cd /tmp/MediaRelayController/ && rm -rf * && wget "+path+" && yum remove media-relay-controller -y && yum localinstall /tmp/MediaRelayController/media-relay** -y ",get_pty=True)

stdin, stdout, stderr = ssh.exec_command("mkdir -p /tmp/MediaRelayController/ && cd /tmp/MediaRelayController/ && rm -rf *  &&  curl  --output artifacts.zip --globoff --header 'PRIVATE-TOKEN: E6U9GiSdxHz3Mn3MGQ_z' --header 'JOB-TOKEN: $CI_JOB_TOKEN' 'https://onecode.polycom-labs.com/api/v4/projects/1104/jobs/"+Job+"/artifacts' && unzip artifacts.zip && yum remove media-relay-controller -y && yum localinstall /tmp/MediaRelayController/media-* -y && service media-relay-controller restart && systemctl list-units --type service --all | grep media &&  systemctl is-active media-relay-controller.service", get_pty=True)

#stdin, stdout, stderr = ssh.exec_command("systemctl is-active media-relay-controller.service ",get_pty=True)

for cmd in stdout:
    print(cmd)
    if cmd == "active" :
        print("############################################\n\n\n             RPM STATUS PASSED\n\n\n##########################################")
    else:
        print("############################################\n\n\n             RPM STATUS FAILED\n\n\n##########################################")


ssh.close
