# coding: utf-8

import time
import random
import os
import json
import re
import sys
import subprocess

sys.path.append(os.getcwd() + "/class/core")
import public

app_debug = False
if public.isAppleSystem():
    app_debug = True


def getPluginName():
    return 'jenkins'


def getPluginDir():
    return public.getPluginDir() + '/' + getPluginName()


def getServerDir():
    return public.getServerDir() + '/' + getPluginName()


def getInitDFile():
    if app_debug:
        return '/tmp/' + getPluginName()
    return '/etc/init.d/' + getPluginName()


def getInitDTpl():
    return getPluginDir() + "/init.d/" + getPluginName() + ".tpl"


def getLog():
    return "/var/log/jenkins/jenkins.log"


def getArgs():
    args = sys.argv[2:]
    tmp = {}
    args_len = len(args)

    if args_len == 1:
        t = args[0].strip('{').strip('}')
        t = t.split(':')
        tmp[t[0]] = t[1]
    elif args_len > 1:
        for i in range(len(args)):
            t = args[i].split(':')
            tmp[t[0]] = t[1]

    return tmp


def checkArgs(data, ck=[]):
    for i in range(len(ck)):
        if not ck[i] in data:
            return (False, public.returnJson(False, '参数:(' + ck[i] + ')没有!'))
    return (True, public.returnJson(True, 'ok'))


def status():
    pn = getPluginName()
    cmd = "ps -ef|grep 'jenkins.war' | grep -v grep | awk '{print $2}'"
    data = public.execShell(cmd)
    if data[0] == '':
        return 'stop'
    return 'start'


def initDreplace():

    file_tpl = getInitDTpl()
    service_path = os.path.dirname(os.getcwd())

    initD_path = getServerDir() + '/init.d'
    if not os.path.exists(initD_path):
        os.mkdir(initD_path)

    file_bin = initD_path + '/' + getPluginName()
    if not os.path.exists(file_bin):
        content = public.readFile(file_tpl)
        content = content.replace('{$SERVER_PATH}', service_path)
        public.writeFile(file_bin, content)
        public.execShell('chmod +x ' + file_bin)

    return file_bin


def runShell(shell):
    data = public.execShell(shell)
    return data


def start():
    file = initDreplace()
    cmd = file + ' start'
    data = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return 'ok'


def stop():
    file = initDreplace()
    data = runShell(file + ' stop')
    if data[1] == '':
        return 'ok'
    return 'fail'


def restart():
    file = initDreplace()
    cmd = file + ' restart'
    data = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return 'ok'


def reload():
    file = initDreplace()
    data = runShell(file + ' reload')

    solr_log = getServerDir() + "/code/logs/walle.log"
    public.writeFile(solr_log, "")

    if data[1] == '':
        return 'ok'
    return 'fail'


def initdStatus():
    initd_bin = getInitDFile()
    if os.path.exists(initd_bin):
        return 'ok'
    return 'fail'


def initdInstall():
    import shutil

    source_bin = initDreplace()
    initd_bin = getInitDFile()
    shutil.copyfile(source_bin, initd_bin)
    public.execShell('chmod +x ' + initd_bin)

    if not app_debug:
        public.execShell('chkconfig --add ' + getPluginName())
    return 'ok'


def initdUinstall():
    if not app_debug:
        public.execShell('chkconfig --del ' + getPluginName())

    initd_bin = getInitDFile()

    if os.path.exists(initd_bin):
        os.remove(initd_bin)
    return 'ok'


def prodConf():
    return getServerDir() + "/code/walle/config/settings_prod.py"


def initEnv():
    cmd = "cd " + getServerDir() + "/code" + " && sh admin.sh init"
    data = public.execShell(cmd)
    return "shell:<br>" + data[0] + "<br>" + " error:<br>" + data[1]


def initData():
    cmd = "cd " + getServerDir() + "/code" + " && sh admin.sh migration"
    data = public.execShell(cmd)
    return "shell:<br>" + data[0] + "<br>" + " error:<br>" + data[1]
# rsyncdReceive
if __name__ == "__main__":
    func = sys.argv[1]
    if func == 'status':
        print status()
    elif func == 'start':
        print start()
    elif func == 'stop':
        print stop()
    elif func == 'restart':
        print restart()
    elif func == 'reload':
        print reload()
    elif func == 'initd_status':
        print initdStatus()
    elif func == 'initd_install':
        print initdInstall()
    elif func == 'initd_uninstall':
        print initdUinstall()
    elif func == 'run_log':
        print getLog()
    elif func == 'prod_conf':
        print prodConf()
    elif func == 'init_env':
        print initEnv()
    elif func == 'init_data':
        print initData()
    else:
        print 'error'
