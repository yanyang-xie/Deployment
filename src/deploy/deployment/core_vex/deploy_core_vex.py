# -*- coding=utf-8 -*-
# author: yanyang.xie@gmail.com

import os
import string
import sys
import time

from fabric.colors import red, yellow, green
from fabric.context_managers import lcd, cd, settings
from fabric.decorators import roles, task, parallel
from fabric.operations import run, local, put
from fabric.state import env
from fabric.tasks import execute
from fabric.utils import abort

sys.path.append('../util')
import common_util
import constant
import encrypt_util
import fab_util
import log_util

here = os.path.dirname(os.path.abspath(__file__))
sys.path.append(here)

config_file, changes_file = ('', '')
config_parameters = {}

snapshot_deploy_dir, golden_files, user, public_key, password = ('', '', '', '', '')
core_vex_server_list, memcached_server_list = ([], [])
project_name, project_version, project_extension_name = ('', '', '')

auto_download_build = False
sona_user_name, sona_user_password = ('', '')

download_build_file_dir, downloaded_build_file_name = ('', '')
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
    with settings(skip_bad_hosts=True):
        fab_util.fab_shutdown_service(service_name)

@task
@parallel
@roles('memcached_server')
def start_memcached_cluster(service_name=constant.MEMCACHED_SERVICE):
    with settings(skip_bad_hosts=True):
        _fab_start_server(service_name)

@task
def shutdown_service():
    print '#' * 100
    print 'Shutdown core vex service'
    execute(shutdown_core_vex_cluster)
    execute(shutdown_memcached_cluster)

@task
def start_service():
    print '#' * 100
    print 'Start up core vex service'
    execute(start_memcached_cluster)
    execute(start_core_vex_cluster)

@task
@parallel
@roles('core_vex_server')
def upload_build_zip_file():
    with cd('/tmp'):
        run('rm -rf %s' % (constant.ZIP_FILE_NAME), pty=False)
        run('rm -rf %s' % (constant.AUTO_DEPLOY_DIR), pty=False)
        run('mkdir -p %s' % (constant.AUTO_DEPLOY_DIR), pty=False)
    
    with lcd(here):
        put(constant.ZIP_FILE_NAME, '/tmp')
    
    with cd('/tmp'):
        run('unzip -o %s -d %s' % (constant.ZIP_FILE_NAME, constant.AUTO_DEPLOY_DIR))

@task
@parallel
@roles('core_vex_server')
def do_golden_config():
    print '#' * 100
    print 'Use golden config to setup environment'
    with cd(env.snapshot_deploy_dir):
        run('chmod a+x setup.sh', pty=False)
        run('./setup.sh', pty=False)

@task
@parallel
@roles('core_vex_server')
def update_conf():
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

    print 'update cluster.host to internal IP %s' % (env.host)
    with cd(constant.TOMCAT_DIR + '/lib'):
        run("sed '/cluster.host=/s/localhost/%s/g' vex.properties > vex-tmp.properties" % (env.host), pty=False)
        run('mv vex-tmp.properties vex.properties')
        run('chown -R tomcat:tomcat ' + constant.TOMCAT_DIR, pty=False)

'''
Check the status whether installation files are existed in local source folder
'''
def exist_zip_file(file_name):
    if not os.path.exists(file_name):
        print 'WARN: release file(.zip) \'%s\' is not exist, please check it first.' % (file_name)
        return False
    else:
        return True

def init_config_and_change_file():
    config_file_name = 'config.properties'
    config_sub_folder = sys.argv[1] + os.sep if len(sys.argv) > 1 else ''  # such as perf/
    
    global config_file, changes_file
    config_file = here + os.sep + config_sub_folder + config_file_name
    if not os.path.exists(config_file):
        abort('Not found the configuration file %s, please check' % (config_file))
    
    config_parameters = common_util.load_properties(config_file)
    changes_file_name = common_util.get_config_value_by_key(config_parameters, 'changes.file.name')
    changes_file = here + os.sep + config_sub_folder + changes_file_name
    
    print 'config_file: %s' % (config_file)
    print 'change_file:%s' % (changes_file)

def init_deploy_log(log_file_name):
    log_dir = here + os.sep + 'logs/'
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    
    sys.stdout = log_util.Logger(log_dir, "%s.%s" % (log_file_name, time.strftime("%Y-%m-%d", time.localtime())))
    sys.stderr = sys.stdout

def init_deploy_parameters(config_file):
    print '#' * 100
    print 'Initial deployment config_parameters from %s' % (config_file)
    global config_parameters
    config_parameters = common_util.load_properties(config_file)
    
    global user, public_key, password, core_vex_server_list, memcached_server_list, golden_files
    user = common_util.get_config_value_by_key(config_parameters, 'user')
    public_key = common_util.get_config_value_by_key(config_parameters, 'public.key')
    password = common_util.get_config_value_by_key(config_parameters, 'password')
    golden_files = common_util.get_config_value_by_key(config_parameters, 'golden.config.file.list')
    
    print 'golden_files:%s' % (golden_files)
    print 'user:%s' % (user)
    print 'public_key:%s' % (public_key)
    print 'password:%s' % (password)
    print '#' * 100
    
    global auto_download_build, sona_user_name, sona_user_password, download_command_prefix
    global project_name, project_version, project_extension_name, downloaded_build_file_name, download_build_file_dir
    global http_proxy, https_proxy
    
    auto_download_build = common_util.get_config_value_by_key(config_parameters, 'auto.download.sona.build')
    if auto_download_build and string.lower(auto_download_build) == 'true':
        auto_download_build = True
        sona_user_name = common_util.get_config_value_by_key(config_parameters, 'sona.user.name')
        sona_user_password = encrypt_util.decrypt('Thistech', common_util.get_config_value_by_key(config_parameters, 'sona.user.passwd'))
        
        project_name = common_util.get_config_value_by_key(config_parameters, 'project.name')
        project_version = common_util.get_config_value_by_key(config_parameters, 'project.version')
        project_extension_name = common_util.get_config_value_by_key(config_parameters, 'project.extension.name')
        downloaded_build_file_name = common_util.get_config_value_by_key(config_parameters, 'build.local.file.name')
        download_build_file_dir = common_util.get_config_value_by_key(config_parameters, 'build.local.file.dir', here)
        http_proxy = common_util.get_config_value_by_key(config_parameters, 'http.proxy')
        https_proxy = common_util.get_config_value_by_key(config_parameters, 'https.proxy')
        download_command_prefix = common_util.get_config_value_by_key(config_parameters, 'download.command.prefix')
        
        print 'auto_download_build:%s' % (auto_download_build)
        print 'sona_user_name:%s' % (sona_user_name)
        print 'sona_user_password:%s' % ('***')
        print 'project_name:%s' % (project_name)
        print 'project_version:%s' % (project_version)
        print 'project_extension_name:%s' % (project_extension_name)
        print 'download_build_file_dir:%s' % (download_build_file_dir)
        print 'downloaded_build_file_name:%s' % (downloaded_build_file_name)
        print 'http_proxy:%s' % (http_proxy)
        print 'https_proxy:%s' % (https_proxy)
        print 'download_command_prefix:%s' % (download_command_prefix)
        print '#' * 100
    else:
        auto_download_build = False
        print 'auto_download_build:%s' % (auto_download_build)
    
def init_fab_ssh_env():
    print 'Setup fabric ssh environment'
    if public_key != '':
        fab_util.setKeyFile(public_key)

    if password != '':
        fab_util.set_password(password)

def init_fab_roles():
    print 'Setup fabric roles'
    vex_servers = common_util.get_config_value_by_key(config_parameters, 'core.vex.server.list', '')
    memcached_servers = common_util.get_config_value_by_key(config_parameters, 'memcached.server.list', '')
    core_vex_server_list = [user + '@' + core_ip for core_ip in vex_servers.split(',')]
    memcached_server_list = [user + '@' + core_ip for core_ip in memcached_servers.split(',')]
    print 'core_vex_server_list:%s' % (string.join(core_vex_server_list, ','))
    print 'memcached_server_list:%s' % (string.join(memcached_server_list, ','))
    
    fab_util.setRoles('core_vex_server', core_vex_server_list)
    fab_util.setRoles('memcached_server', memcached_server_list)

def init_deploy_dir(f_dir):
    print 'Initial temp deployment directory %s' % (f_dir)
    local('rm -rf ' + f_dir)
    local('mkdir -p ' + f_dir)

def merge_golden_config():
    print '#' * 100
    print 'Merge changes file %s with golden config %s' % (changes_file, 'vex-golden.properties')
    
    with lcd(here):
        local('rm -rf %s/vex.properties' % (here))
        local('rm -rf %s/vex-golden.properties' % (here))
        local('unzip -o %s -d %s' % (constant.ZIP_FILE_NAME, constant.AUTO_DEPLOY_DIR))
        
        time.sleep(2)
        snapshot_folder = os.listdir(constant.AUTO_DEPLOY_DIR)[0]
        snapshot_deploy_dir = constant.AUTO_DEPLOY_DIR + os.sep + snapshot_folder + os.sep
        env.snapshot_deploy_dir = snapshot_deploy_dir
    
    with lcd(env.snapshot_deploy_dir + 'conf'):
        local('cp vex-golden.properties vex.properties')
        common_util.merge_properties(snapshot_deploy_dir + 'conf' + os.sep + 'vex.properties', changes_file)
     
        local('cp vex.properties %s/vex.properties' % (here))
        local('cp vex-golden.properties %s/vex-golden.properties' % (here))

def download_build():
    import download_sona_build as downbuild
    download_script = downbuild.__file__
    command = 'python %s -u %s -p %s -n %s -v %s -e %s -d %s -f %s' % (download_script, sona_user_name, sona_user_password, project_name, project_version, project_extension_name, download_build_file_dir, downloaded_build_file_name)
    command = command + ' -y %s ' % (http_proxy) if http_proxy is not None else command
    command = command + ' -Y %s ' % (https_proxy) if https_proxy is not None else command
    if download_command_prefix is not None:
        command = 'source %s && %s' % (download_command_prefix, command)
    print '#' * 100
    print 'Start to download %s build from sona' % (project_name)
    local(command)
    print '#' * 100

def _fab_start_server(server_name, command=None, is_local=False, warn_only=True):
    cmd = command or 'service %s start'
    command_line = cmd % (server_name)
    
    print 'Start %s server by command %s......' % (server_name, command_line)
    fab_util.fab_run_command(command_line, is_local, warn_only=warn_only, ex_abort=False)  

if __name__ == '__main__':
    try:
        # prepare
        init_config_and_change_file()
        init_deploy_log(constant.DEPLOY_LOG_FILE_NAME)
        init_deploy_parameters(config_file)
        init_deploy_dir(constant.AUTO_DEPLOY_DIR)
        init_fab_ssh_env()
        init_fab_roles()
    
        if auto_download_build:
            execute(download_build)
        
        if exist_zip_file(here + os.sep + constant.ZIP_FILE_NAME):
            merge_golden_config()
            execute(shutdown_service)
            execute(upload_build_zip_file)
            execute(do_golden_config)
            execute(update_conf)
            execute(start_service)
            print green('Finished to do %s-%s deployment.' % (project_name, project_version))
        else:
            print yellow('Not found the zip file %(s), not to do deployment any more' % (here + os.sep + constant.ZIP_FILE_NAME))
            abort(2)
    except Exception, e:
        print '#' * 100
        print red('Failed to do deployment. Line:%s, Reason: %s' % (sys.exc_info()[2].tb_lineno, str(e)))
        abort(1)
