import subprocess
import os
import sys
import getpass
import requests
import json
import sys

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_err(s):
    print(bcolors.FAIL + str(s) + bcolors.ENDC)

def run():
    if sys.platform != 'darwin':
        print('This program works on macOS only.')
        return 1

    knownPlugins, customDeleteFiles = None, None
    data_url = 'https://raw.githubusercontent.com/thy2134/MacSAFER/master/plugins.json'

    if len(sys.argv) > 1 and sys.argv[1].startswith('--data-url='):
        data_url = sys.argv[1].replace('--data-url=', '')

    print('Trying to fetch data from URL', data_url, '...')

    try:
        json_datas = requests.get(data_url)
    except Exception as e:
        print_err('Error fetching plugin data!')
        print_err(e)
        return 1        
    if json_datas.status_code != 200:
        print_err('Error fetching plugin data!')
        return 1
    
    try:
        json_data = json.loads(json_datas.text)
        customDeleteFiles = json_data['customDeleteFiles']
        knownPlugins = json_data['knownPlugins']
    except:
        print_err('Error while loading data!')
        print_err('Response data =>')
        print_err(json_datas.text)
        return 1
    
    print('Successfully initalized data from URL', data_url, '.')
    loaded = {
        'App': {},
        'File': {}
    }


    p = subprocess.Popen(['whoami'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    whoami = p.stdout.readline().decode('utf-8')
    is_root = (whoami == 'root\n')

    password = ''
    if not is_root:
        password = getpass.getpass('Password:')
        echo = subprocess.Popen(['echo', password], stdout=subprocess.PIPE).stdin
        (_, err) = subprocess.Popen(['sudo', '-S', 'ls'], stdin=echo, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        if len(err) > 0:
            print('Authentication failed')
            return 1

    for key in knownPlugins.keys():
        if os.path.exists(knownPlugins[key]):
            loaded['App'][key] = knownPlugins[key]
        
    for key in customDeleteFiles:
        for item in customDeleteFiles[key]:
            if os.path.exists(item):
                if key not in loaded['File'].keys():
                    loaded['File'][key] = []
                loaded['File'][key].append(item)

    count = len(loaded['App'].keys()) + len(loaded['File'].keys())
    print('Found', count, 'software' + ('s' if count > 1 else ''))
    if count <= 0:
        return 0
    for (key, value) in loaded['App'].items():
        print(key, '=>', value)

    for (key, value) in loaded['File'].items():
        for item in value:
            print(key, '=>', item)

    yn = input('Deleting ' + str(count) + ' items. Continue? [Y/n]')
    if yn != '' and yn != 'Y':
        print('Aborting...')
        return 0

    for (key, value) in loaded['App'].items():
        print('Deleting', key)
        echo = subprocess.Popen(['echo', password], stdout=subprocess.PIPE).stdin
        p = subprocess.Popen(['sudo', '-S', value], stdin=echo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()


    for (key, value) in loaded['File'].items():
        for item in value:
            print('Deleting', key, 'at', item)
            echo = subprocess.Popen(['echo', password], stdout=subprocess.PIPE).stdin
            p = subprocess.Popen(['sudo', '-S', "rm", "-rf", item], stdin=echo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.wait()
