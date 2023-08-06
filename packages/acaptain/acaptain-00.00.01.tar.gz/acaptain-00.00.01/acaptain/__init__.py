print("starting main acaptain module")
from subprocess import check_call as run 
from getopt import getopt, GetoptError
import time
import pkg_resources
RELEASE = 'master' # default release 
SRC_DIR = "$HOME/.src" # checkout directory 
UPDATE_CMD = ( # base command 
'pip3 install mbpackage'
)


import json
from urllib.request import urlopen
import subprocess
import os
import sys
import psutil
import logging
import pip

from distutils.version import StrictVersion
def restart_program():
    """Restarts the current program, with file objects and descriptors
       cleanup
    """

    try:
        p = psutil.Process(os.getpid())
        for handler in p.get_open_files() + p.connections():
            os.close(handler.fd)
    except:
        print("error")

    python = sys.executable
    os.execl(python, python, *sys.argv)


def versions(package_name):
    url = "https://pypi.python.org/pypi/%s/json" % (package_name,)
    resp_text =urlopen(url).read().decode('UTF-8')
    data = json.loads(resp_text)
    #data = json.load(urlopen(url).decode('utf-8'))
    versions = data["releases"].keys()
    print(versions)
    print(max(sorted(versions)))
    #versons=sorted(versions[StrictVersion])
    return max(sorted(versions))


def main():
    while True:
        print("checking for new versions:")
    
        myversions=versions('mbtestpackage')
        thisversion=pkg_resources.get_distribution('mbtestpackage').version
        thisv=thisversion.split('.')    
        myv=myversions.split('.')
        thisv=int(thisv[0])*10000+int(thisv[1])*100+int(thisv[2])
        myv=int(myv[0])*10000+int(myv[1])*100+int(myv[2])
        print(myv)
        print(thisv)
        if thisv==myv:
            print("theyarethesame")
        elif thisv>myv:
            print("updatepypi!")
        else:
            print("newversionavailable!")
            pip.main(["install", "-I", "--no-binary", ":all:", "--no-cache-dir","mbtestpackage"])
            restart_program()
        time.sleep(5)
    

def mydb():
    import acaptain.db
    print("db started")
def myss():
    import acaptain.ss
    print("ss started")
def myui():
    import acaptain.ui
    print("ui started")



print("Alectryon Captain imported")
