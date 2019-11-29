import json
import paramiko
import urllib.request
from bs4 import BeautifulSoup as bs
import re
import time

start = time.perf_counter()

build = None
path = None

with open('SoftMcu_Details.txt') as file:
    my_dict = json.load(file)
    host = my_dict["host"]
    username = my_dict["username"]
    password = my_dict["password"]
    target_version = my_dict["target_version"]
file.close()


def svn_build():
    data = str(CurrentBuild.read())
    data_0 = data[:-3]
    data_1 = data_0[2:]

    intermediate_url = data_1+"/"

    build_num = data_1[4:]

    prefix = "plcm-caxis-mcu-"
    extension = ".upg"
    soft_mcu_build = prefix+build_num+extension

    build_path = BaseUrl+intermediate_url+soft_mcu_build
    return soft_mcu_build, build_path


def gradle_build():
    soup = bs(urllib.request.urlopen(Base_Url),features="html.parser")

    for link in soup.findAll('a')[-1]:
        new_url = str(Base_Url+link)

    soup_0 = bs(urllib.request.urlopen(new_url),features="html.parser")
    link = str(soup_0.findAll('a',text=re.compile('plcm-caxis-mcu-')))
    Data = link[41:]
    soft_mcu_build = Data[:-5]
    build_path = new_url+soft_mcu_build
    return soft_mcu_build, build_path


try:
    if target_version == '8.7.5' or target_version == '8.8.0':
        BaseUrl = "http://10.223.1.88/Carmel-Versions/SVN/Builds/prod/"+target_version+"/trunk/"
        CurrentBuild = urllib.request.urlopen("http://10.223.1.88/Carmel-Versions/SVN/Builds/prod/"+target_version+"/trunk/CurrentBuild.txt")
        build, path = svn_build()

    elif target_version == '8.8.1' or target_version == '8.9.0':
        Base_Url = "http://10.206.10.5/RMX-Data/RMX-BUILDS/candidate/"+target_version+"/"
        build, path = gradle_build()

    else:
        print("Release doesn't exist")
        exit()

except TimeoutError as e:
    print("The server isn't reachable")

except urllib.error.URLError as e:
    print("The connection failed because the host didn't respond.")


def softmcu_upgrade(mcu_ip):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(mcu_ip, username=username, password=password)
    stdin, stdout, stderr = ssh.exec_command("cat /opt/mcu/mcms/ProductType")
    for ProductType in stdout:
        print(ProductType)

        if ProductType == 'SOFT_MCU_EDGE':
            print("\nBuild Path : "+path)
            print("\nBuild Number : "+build)
            stdin, stdout, stderr = ssh.exec_command("yum install wget -y && cd /opt/polycom/rpp/bin/uf && wget "+path+" && ./mounting.py "+build+" /tmp/rmx_version_bin && cd /tmp/rmx_version_bin/scripts && ./install && reboot",get_pty=True)
            for line in stdout:
                print(line)
        else:
            print("The product type isn't SOFT_MCU_EDGE")
            exit()

    ssh.close()


softmcu_upgrade(host)

print("\nThe system went for a reboot. Please wait for the system to come up\n")

finish = time.perf_counter()
print(f'Upgrade finished in {round(finish-start, 2)} second(s)')