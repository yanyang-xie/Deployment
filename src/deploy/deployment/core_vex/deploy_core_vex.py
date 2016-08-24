#!/usr/bin/python
# coding:utf-8
# author: yanyang.xie

import os
import string
import sys
import time

from fabric.context_managers import lcd, cd
from fabric.decorators import roles, task, parallel
from fabric.operations import run, local, put
from fabric.state import env
from fabric.tasks import execute

sys.path.append('../util')
import common_util
import constant
import fab_util
import log_util

# whether to run the script in local, default is running the script in remote
# is_local = False

here = os.path.dirname(os.path.abspath(__file__))
sys.path.append(here)

vex_snapshot_dir, golden_files, user, public_key, password = ('', '', '', '', '')
core_vex_server_list, memcached_server_list = ([], [])

download_sona_build = False
sona_user_name, sona_user_password = ('', '')
vex_project_name, vex_project_version, vex_project_extension_name = ('', '', '')
vex_local_file_dir, vex_local_file_name = ('', '')
http_proxy, https_proxy = None, None
download_command_prefix = None

@task
@parallel
@roles('core_vex_server')
def shutdown_core_vex_cluster(service_name=constant.TOMCAT_SERVICE):
    fab_util.fab_shutdown_service(service_name)
    
@task
@parallel
@roles('core_vex_server')
def start_core_vex_cluster(service_name=constant.TOMCAT_SERVICE, clean_log=False):
    _fab_start_server(service_name)

@task
@parallel
@roles('memcached_server')
def shutdown_memcached_cluster(service_name=constant.MEMCACHED_SERVICE):
    fab_util.fab_shutdown_service(service_name)

@task
@parallel
@roles('memcached_server')
def start_memcached_cluster(service_name=constant.MEMCACHED_SERVICE):
    _fab_start_server(service_name)

@task
def shutdown_core_vex_service():
    print '#' * 100
    print 'Shutdown core vex service'
    execute(shutdown_core_vex_cluster)
    execute(shutdown_memcached_cluster)

@task
def start_core_vex_service():
    print '#' * 100
    print 'Start up core vex service'
    execute(start_memcached_cluster)
    execute(start_core_vex_cluster)

@task
@parallel
@roles('core_vex_server')
def upload_vex_zip_file():
    with cd('/tmp'):
        run('rm -rf %s' % (constant.VEX_ZIP_FILE), pty=False)
        run('rm -rf %s' % (constant.VEX_AUTO_DEPLOY_DIR), pty=False)
        run('mkdir -p %s' % (constant.VEX_AUTO_DEPLOY_DIR), pty=False)
    
    with lcd(here):
        put(constant.VEX_ZIP_FILE, '/tmp')
    
    with cd('/tmp'):
        run('unzip -o %s -d %s' % (constant.VEX_ZIP_FILE, constant.VEX_AUTO_DEPLOY_DIR))

@task
@parallel
@roles('core_vex_server')
def do_golden_config():
    print '#' * 100
    print 'Use golden config to setup vex initialize environment'
    with cd(env.vex_snapshot_dir):
        run('chmod a+x setup.sh', pty=False)
        run('./setup.sh', pty=False)

@task
@parallel
@roles('core_vex_server')
def upload_vex_conf():
    print '#' * 100
    print 'Upload vex configuration file into tomcat/lib'
    
    # upload configured files to tomcat/lib
    put('%s/vex.properties' % (here), constant.TOMCAT_DIR + '/lib')
       
    if golden_files:
        for golden_file in golden_files.split(','):
            if os.path.exists('%s/%s' % (here, golden_file)):
                put('%s/%s' % (here, golden_file), constant.TOMCAT_DIR + '/lib')
            else:
                print 'Golden file %s is not exist in %s, not upload it.' % (golden_file, here)
    
    # change owner to tomcat
    # run('chown -R tomcat:tomcat ' + constant.TOMCAT_DIR, pty=False)
    
    print 'update netty cache miss host'
    with cd(constant.TOMCAT_DIR + '/lib'):
        run("sed '/cluster.host=/s/localhost/%s/g' vex.properties > vex-tmp.properties" % (env.host), pty=False)
        run('mv vex-tmp.properties vex.properties')
        run('chown -R tomcat:tomcat ' + constant.TOMCAT_DIR, pty=False)


def _fab_start_server(server_name, command=None, is_local=False, warn_only=True):
    cmd = command or 'service %s start'
    command_line = cmd % (server_name)
    
    print 'Start %s server by command %s......' % (server_name, command_line)
    fab_util.fab_run_command(command_line, is_local, warn_only=warn_only, ex_abort=True)

'''
Check the status whether installation files are existed in local source folder
'''
def exist_vex_zip_file():
    if not os.path.exists(here + os.sep + constant.VEX_ZIP_FILE):
        print 'WARN:Core VEX release file(.zip) \'%s\' is not exist in folder %s, please check it first.' % (constant.VEX_ZIP_FILE, here)
        return False
    else:
        return True

def init_vex_deploy_log():
    log_dir = here + os.sep + 'logs/'
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    
    sys.stdout = log_util.Logger(log_dir, "deploy-core-vex.log.%s" % (time.strftime("%Y-%m-%d", time.localtime())))
    sys.stderr = sys.stdout

def init_vex_deploy_parameters():
    print '#' * 100
    print 'Initial vex deployment parameters from config.properties'
    vex_parameters = common_util.load_properties(here + os.sep + 'config.properties')
    
    global golden_files, user, public_key, password, core_vex_server_list, memcached_server_list
    golden_files = vex_parameters.get('golden.config.file.list')
    
    user = vex_parameters.get('user')
    public_key = vex_parameters.get('public.key') if vex_parameters.has_key('public.key') else ''
    password = vex_parameters.get('password') if vex_parameters.has_key('password') else ''
    core_vex_server_list = [user + '@' + core_ip for core_ip in vex_parameters.get('core.vex.server.list').split(',')]
    memcached_server_list = [user + '@' + m_ip for m_ip in vex_parameters.get('memcached.server.list').split(',')]
    
    print 'golden_files:%s' % (golden_files)
    print 'user:%s' % (user)
    print 'public_key:%s' % (public_key)
    print 'password:%s' % (password)
    print 'core_vex_server_list:%s' % (string.join(core_vex_server_list, ','))
    print 'memcached_server_list:%s' % (string.join(memcached_server_list, ','))
    print '#' * 100
    
    global download_sona_build, sona_user_name, sona_user_password, download_command_prefix
    global vex_project_name, vex_project_version, vex_project_extension_name, vex_local_file_name, vex_local_file_dir
    global http_proxy, https_proxy
    if vex_parameters.has_key('auto.download.sona.build') and string.strip(vex_parameters['auto.download.sona.build']) == 'True':
        download_sona_build = True
        sona_user_name = vex_parameters.get('sona.user.name')
        sona_user_password = vex_parameters.get('sona.user.passwd')
        vex_project_name = vex_parameters.get('vex.project.name')
        vex_project_version = vex_parameters.get('vex.project.version')
        vex_project_extension_name = vex_parameters.get('vex.project.extension.name')
        vex_local_file_name = vex_parameters.get('vex.local.file.name')
        vex_local_file_dir = vex_parameters.get('vex.local.file.dir') if vex_parameters.has_key('vex.local.file.dir') else here
        
        http_proxy = vex_parameters.get('http.proxy') if vex_parameters.has_key('http.proxy') else None
        https_proxy = vex_parameters.get('https.proxy') if vex_parameters.has_key('https.proxy') else None
        
        download_command_prefix = vex_parameters.get('download.command.prefix') if vex_parameters.has_key('download.command.prefix') else None
        
        print 'download_sona_build:%s' % (download_sona_build)
        print 'sona_user_name:%s' % (sona_user_name)
        print 'sona_user_password:%s' % ('***')
        print 'vex_project_name:%s' % (vex_project_name)
        print 'vex_project_version:%s' % (vex_project_version)
        print 'vex_project_extension_name:%s' % (vex_project_extension_name)
        print 'vex_local_file_dir:%s' % (vex_local_file_dir)
        print 'vex_local_file_name:%s' % (vex_local_file_name)
        print 'http_proxy:%s' % (http_proxy)
        print 'https_proxy:%s' % (https_proxy)
        print 'download_command_prefix:%s' % (download_command_prefix)
        print '#' * 100
    else:
        download_sona_build = False
        print 'download_sona_build:%s' % (download_sona_build)

def init_vex_deploy_environment():
    print 'Setup fabric environment'
    if public_key != '':
        fab_util.setKeyFile(public_key)
        
    if password != '':
        fab_util.setPassword(password)
    
    fab_util.setRoles('core_vex_server', core_vex_server_list)
    fab_util.setRoles('memcached_server', memcached_server_list)

def init_vex_deploy_dir():
    print 'Initial vex deployment temp directory %s' % (constant.VEX_AUTO_DEPLOY_DIR)
    local('rm -rf ' + constant.VEX_AUTO_DEPLOY_DIR)
    local('mkdir -p ' + constant.VEX_AUTO_DEPLOY_DIR)

def clean_up_log(log_dir=constant.TOMCAT_DIR + '/logs'):
    print 'Clean tomcat logs %s' % (log_dir)
    run('rm -rf %s/*' % (log_dir), pty=False)

def merge_vex_golden_config():
    print '#' * 100
    print 'Merge vex changes file %s with vex golden config %s' % ('vex-changes.properties', 'vex-golden.properties')
    
    with lcd(here):
        local('rm -rf %s/vex.properties' % (here))
        local('rm -rf %s/vex-golden.properties' % (here))
        local('unzip -o %s -d %s' % (constant.VEX_ZIP_FILE, constant.VEX_AUTO_DEPLOY_DIR))
        
        time.sleep(2)
        snapshot_folder = os.listdir(constant.VEX_AUTO_DEPLOY_DIR)[0]
        vex_snapshot_dir = constant.VEX_AUTO_DEPLOY_DIR + os.sep + snapshot_folder + os.sep
        env.vex_snapshot_dir = vex_snapshot_dir
    
    with lcd(env.vex_snapshot_dir + 'conf'):
        local('cp vex-golden.properties vex.properties')
        common_util.merge_properties(vex_snapshot_dir + 'conf' + os.sep + 'vex.properties', here + os.sep + 'vex-changes.properties')
     
        local('cp vex.properties %s/vex.properties' % (here))
        local('cp vex-golden.properties %s/vex-golden.properties' % (here))

def download_build():
    # print 'python %s/download_sona_build.py -u %s -p %s -n %s -v %s -e %s -d %s -f %s' %(here,sona_user_name,sona_user_password,vex_project_name,vex_project_version,vex_project_extension_name,vex_local_file_dir, vex_local_file_name)
    # local('python %s/download_sona_build.py -u %s -p %s -n %s -v %s -e %s -d %s -f %s' %(here,sona_user_name,sona_user_password,vex_project_name,vex_project_version,vex_project_extension_name,vex_local_file_dir, vex_local_file_name))

    command = 'python %s/download_sona_build.py -u %s -p %s -n %s -v %s -e %s -d %s -f %s' % (here, sona_user_name, sona_user_password, vex_project_name, vex_project_version, vex_project_extension_name, vex_local_file_dir, vex_local_file_name)
    command = command + ' -y %s ' % (http_proxy) if http_proxy is not None else command
    command = command + ' -Y %s ' % (https_proxy) if https_proxy is not None else command
    if download_command_prefix is not None:
        command = 'source %s && %s' % (download_command_prefix, command)
    print '#' * 100
    print 'Start to download %s build from sona' % (vex_project_name)
    local(command)
    print '#' * 100
    

if __name__ == '__main__':
    # prepare
    init_vex_deploy_log()
    init_vex_deploy_parameters()
    init_vex_deploy_environment()
    init_vex_deploy_dir()

    if download_sona_build:
        execute(download_build)
    
    if exist_vex_zip_file():
        merge_vex_golden_config()
        execute(shutdown_core_vex_service)
        execute(upload_vex_zip_file)
        execute(do_golden_config)
        execute(upload_vex_conf)
        execute(start_core_vex_service)
