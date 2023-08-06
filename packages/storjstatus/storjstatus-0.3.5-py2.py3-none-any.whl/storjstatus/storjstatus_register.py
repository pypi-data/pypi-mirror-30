#!/usr/bin/env python3

import argparse
import getpass
import json
import os
import os.path
import requests
import socket
import ctypes
from crontab import CronTab
from os import scandir
from random import randint
from storjstatus import storjstatus_common

### Vars
FORCE = False
PARSER = None
ENV = None

def init_register():
    global FORCE
    global PARSER

    storjstatus_common.setup_env()
    header()
    cmdargs()

    args = PARSER.parse_args()

    if args.arg_force:
        FORCE = True;

    checks()

    if not args.arg_email:
        email = input('Enter your StorjStatus email address: ')
    else:
        email = args.arg_email
        print('Using email :' + email)

    if not args.arg_password:
        password = getpass.getpass('Enter your StorjStatus password: ')
    else:
        password = args.arg_password
        print('Using password : ****')

    if not args.arg_name:
        name = input('Enter a name for this server (min 3 characters) [' + guess_hostname() + ']: ')
        name = name or guess_hostname()
    else:
        name = args.arg_name
        print('Using server name :' + name + '.')

    if not args.arg_config_dir:
        config_dir = input('Enter your Storjshare config directory [' + guess_config_dir() + ']: ')
        config_dir = config_dir or guess_config_dir()
    else:
        config_dir = args.arg_config_dir
        print('Using config directory :' + config_dir + '.')

    # Final check on vars
    if not email or len(email) < 5:
        print_error('Email address is invalid.')

    if not password or len(password) < 6:
        print_error('Password is invalid.')

    if not name or len(name) < 3:
        print_error('Server name must be at least 3 characters.')

    if not config_dir or len(config_dir) < 1:
        print_error('Config Directory is invalid.')

    if not os.path.isdir(config_dir):
        print_error('Config Directory does not exist or is not a directory.')

    path, dirs, files = os.walk(config_dir).__next__()
    if (len(files) < 1):
        print_error('Unable to find any files in the Config Directory.')

    # Get api creds
    key, secret = api_creds(email, password)

    # Server id
    serverid = server_guid(key, secret, name)

    # Save settings
    save_settings(key, secret, serverid, config_dir)

    cron_job()

    print()
    print("Setup complete. You will see your statistics appear on your dashboard over the next 30 mins.")


def checks():
    global FORCE

    if storjstatus_common.get_os_type() == "linux":
        try:
            if os.geteuid() != 0:
                print_error('Please run this script with root privileges.')
        except AttributeError:
            print_error('Error checking user access level.')
    elif storjstatus_common.get_os_type() == "win":
        try:
            if  ctypes.windll.shell32.IsUserAnAdmin() != 1:
                print_error('Please run this script with Administrator privileges.')
        except AttributeError:
            print_error('Error checking user access level.')
    else:
        print_error('Unsupported Os type.')

    if FORCE == True:
        print("Forcing regeneration of config and crontab. Note cron times may change.")

    elif os.path.isfile(storjstatus_common.CONFIGFILE):
        print_error('Server config file already exists.')
        exit(1)

    # Check strojshare exists
    try:
        code, result = storjstatus_common.check_strojshare()
    except FileNotFoundError:
        print_error("Unable to find the Storj Share Daemon. Please ensure it's on your PATH variable.")

    if code != "OK":
        print_error(result, False)


def header():
    print('####################################################')
    print('         StorjStatus Server Registration')
    print('                Version: ' + storjstatus_common.get_version())
    print('####################################################')
    print()


def cmdargs():
    global PARSER

    PARSER = argparse.ArgumentParser(prog='storjstatus-register', add_help=True)
    PARSER.add_argument('--email', '-e', help="Your StorjStatus registered email address", type=str, action='store', dest='arg_email', nargs='?')
    PARSER.add_argument('--password', '-p', help="Your StorjStatus password", type=str, action='store', dest='arg_password', nargs='?')
    PARSER.add_argument('--server-name', '-n', help="Name for this server to use in the dashboard", type=str, action='store', dest='arg_name', nargs='?')
    PARSER.add_argument('--config-dir', '-c', help="The location to your local Storjshare config file", type=str, action='store', dest='arg_config_dir', nargs='?')
    PARSER.add_argument('--force', '-f', help="This will regenerate the cron and config file if it already exists", action='store_true', dest='arg_force')


def guess_config_dir():
    user = getpass.getuser()

    if storjstatus_common.get_os_type() == "win":
        return expanduser("~") + '.storjshare\configs'

    elif storjstatus_common.get_os_type() == "linux":
        if user == 'root':
            return '/root/.config/storjshare/configs'
        else:
            return '/home/' + user + '/.config/storjshare/configs'


def guess_hostname():
    return socket.gethostname()


def save_settings(api_key, api_secret, server_guid, storj_config):
    if storjstatus_common.get_os_type() == "win":
        save_settings_win(api_key, api_secret, server_guid, storj_config)
    elif storjstatus_common.get_os_type() == "linux":
        save_settings_linux(api_key, api_secret, server_guid, storj_config)


def save_settings_linux(api_key, api_secret, server_guid, storj_config):
    settings = {
        'api_key': api_key,
        'api_secret': api_secret,
        'server_guid': server_guid,
        'storj_config': storj_config,
    }

    # Create folder if doesn't exist
    if not os.path.exists(os.path.dirname(storjstatus_common.CONFIGFILE)):
        try:
            os.makedirs(os.path.dirname(storjstatus_common.CONFIGFILE))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                print('Error creating directory ' + os.path.dirname(storjstatus_common.CONFIGFILE))
                exit(1)

    # Output settings
    settings_output = json.dumps(settings, sort_keys=True, indent=4)
    settings_file = open(storjstatus_common.CONFIGFILE, 'w')
    settings_file.write(settings_output)
    settings_file.close()


def save_settings_win(api_key, api_secret, server_guid, storj_config):
    try:
        import winreg
        local_machine = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        config = winreg.OpenKey(local_machine, storjstatus_common.CONFIGREG)

        winreg.SetValueEx(config, "api_key", 0, winreg.REG_SZ, api_key)
        winreg.SetValueEx(config, "api_secret", 0, winreg.REG_SZ, api_secret)
        winreg.SetValueEx(config, "server_guid", 0, winreg.REG_SZ, server_guid)
        winreg.SetValueEx(config, "storj_config", 0, winreg.REG_SZ, storj_config)
    except AttributeError:
        print_error("There was a problem writing to the Windows Registry")


def api_creds(email, password):
    json_request = {
        'email': email,
        'password': password
    }

    headers = {'content-type': 'application/json'}
    resp = requests.post(storjstatus_common.APIENDPOINT + "authentication", json=json_request, headers=headers)
    if not resp.status_code == 200:
        print_error("value returned when authenticating : " + resp.json()['description'])

    print("Obtained API key from server")
    key = resp.json()['key']
    secret = resp.json()['secret']

    return key, secret


def server_guid(key, secret, name):
    json_request = {
        'name': name
    }

    headers = {'content-type': 'application/json', 'api-key' : key, 'api-secret' : secret}
    resp = requests.post(storjstatus_common.APIENDPOINT + "server", json=json_request, headers=headers)
    if not resp.status_code == 200:
        print(resp.content)
        print_error("value returned when creating server : " + resp.json()['description'])

    serverid = resp.json()['serverId']
    print("Obtained server GUID from server : " + serverid)

    return serverid


def cron_job():
    if storjstatus_common.get_os_type() == "win":
        print()
        print('************* Windows scheduling unsupported ************')
        print()
        print('Please set up a manual schedule for "storjstatus-send" every 15 minutes.')

    elif storjstatus_common.get_os_type() == "linux":
        cron_job_linux()

def cron_job_linux():
    tmp_cron = '/tmp/storjstatus.cron'

    result = storjstatus_common.subprocess_result(['which', 'storjstatus-send'])

    if 'storjstatus-send' in result[0].decode('utf-8'):
        send_command = result[0].decode('utf-8').replace('\n', '') + ' >> /var/log/storjstatus.log 2>&1'

        if os.path.isfile('/etc/crontab'):
            cron_path = '/etc/crontab'
        elif os.path.isfile('/etc/anacrontab'):
            cron_path = '/etc/anacrontab'
        else:
            cron_path = tmp_cron

        cron = CronTab(tabfile=cron_path, user=False)
        # Check for existing cronjob and remove
        cron.remove_all(comment='storjstatus')

        # Add new cron
        job = cron.new(command=send_command, user='root', comment='storjstatus')
        minute = randint(0, 59)
        job.minute.on(minute)

        minute = cron_minute(minute)
        job.minute.also.on(minute)

        minute = cron_minute(minute)
        job.minute.also.on(minute)

        minute = cron_minute(minute)
        job.minute.also.on(minute)

        if cron_path == tmp_cron:
            print('*************************WARNING************************************')
            print('Could not find your system cronfile, please add a cron manually for:')
            print('             ' + job.render())
            print('*************************WARNING************************************')

    else:
        print_error('There was an error finding the storjstatus-send command. Check your storjstatus installation.')


def cron_minute(minute):
    add = 15
    next_minute = minute + add
    if next_minute > 59:
            next_minute = next_minute - 60

    return next_minute


def print_error(error_message, show_help=True):
    print()
    print("ERROR : " + error_message)
    print()

    if show_help:
        PARSER.print_help()

    exit(1)


if __name__ == '__main__':
    init_register()
