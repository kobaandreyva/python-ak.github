#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
from netmiko import ConnectHandler
import netmiko.ssh_exception
import time
from datetime import timedelta, datetime
import os
import subprocess
import sys

now_time = datetime.today().replace(microsecond=0).strftime('%Y-%m-%d_%H-%M-%S')
path = 'juniper' + now_time + '/'


def reboot_card_juniper(dev_ip, commands):
    with ConnectHandler(ip=dev_ip, username ='ak', password='bd76DG37', device_type = 'juniper_junos'  ) as ssh:
        try:
            ssh.session_preparation()
            for command in commands:
                result = ssh.send_command(command)
            os.mkdir(path)
            with open(path + dev_ip + '_' + now_time + '.csv','a') as f:
                f.write(result)
        except netmiko.ssh_exception.NetMikoAuthenticationException as err_auth:
            print(err_auth + '{} for user ak_python'.format(dev_ip))
    return None

if __name__ == "__main__":
    pid = str(os.getpid())
    pidfile = "/tmp/cpu-check.pid"
    if os.path.isfile(pidfile):
        print('script already working')
        sys.exit()
    with open(pidfile, 'w') as f:
        f.write(pid)
    try:
        juniper_ips = ['10.8.50.243', '10.8.54.1']
        for ip in juniper_ips:
            result_card_1 = subprocess.run('snmpwalk -v 2c -c public {} .1.3.6.1.4.1.2636.3.1.13.1.8.20.1.1.0'.format(ip),  shell=True, stdout=subprocess.PIPE,  encoding='utf-8')
            cpu_card1 = result_card_1.stdout.split()[-1]
            result_card_2 = subprocess.run('snmpwalk -v 2c -c public {} .1.3.6.1.4.1.2636.3.1.13.1.8.20.1.2.0'.format(ip),  shell=True, stdout=subprocess.PIPE,  encoding='utf-8')
            cpu_card2 = result_card_2.stdout.split()[-1]
            print(cpu_card1, cpu_card2)
            if cpu_card1 >= '96':
                time.sleep(60)
                result_card_1_repeat = subprocess.run('snmpwalk -v 2c -c public {} .1.3.6.1.4.1.2636.3.1.13.1.8.20.1.1.0'.format(ip),  shell=True, stdout=subprocess.PIPE,  encoding='utf-8')
                cpu_card1_repeat = result_card_1_repeat.stdout.split()[-1]
                if cpu_card1_repeat >= '96':
                    reboot_card_juniper(ip, ['request chassis pic fpc-slot 0 pic-slot 0 offline', 'request chassis pic fpc-slot 0 pic-slot 0 online'])
            if cpu_card2 >= '96':
                time.sleep(60)
                result_card_2_repeat = subprocess.run('snmpwalk -v 2c -c public {} .1.3.6.1.4.1.2636.3.1.13.1.8.20.1.2.0'.format(ip),  shell=True, stdout=subprocess.PIPE,  encoding='utf-8')
                cpu_card2_repeat = result_card_2_repeat.stdout.split()[-1]
                if cpu_card2_repeat >= '96':
                    reboot_card_juniper(ip, ['request chassis pic fpc-slot 0 pic-slot 2 offline', 'request chassis pic fpc-slot 0 pic-slot 2 online'])

    finally:
        os.unlink(pidfile)

