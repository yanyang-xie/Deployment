# -*- coding=utf-8 -*-
# author: yanyang.xie@gmail.com

from fabric.operations import run, local, put, get, execute
from fabric.api import *
from fabric.state import env

# host and role lists will be merge to one list of deduped hosts while execute task
def setRoles(role_name, host_list, roledefs_dict=None):
    # env.roledefs = { 'testserver': ['user1@host1:port1',], 'realserver': ['user2@host2:port2', ] }
    env.roledefs.update({role_name:host_list})
    if roledefs_dict and type(roledefs_dict) is dict:
        env.roledefs.update(roledefs_dict)

def set_hosts(hosts):
    # env.hosts = ['user@host1:port', 'host2']
    env.hosts = hosts

def setKeyFile(key_filename):
    if key_filename is None or key_filename == '':
        return
    env.key_filename = key_filename

def set_user(user):
    if user is None or user == '':
        return
    env.user = user
    
def set_password(password):
    if password is None or password == '':
        return
    env.password = password

def set_host_password_matching(host_past_word_dict):
    if type(host_past_word_dict) is not dict:
        return
    
    '''
        env.passwords = {
            'host1': "pwdofhost1",
            'host2': "pwdofhost2",
            'host3': "pwdofhost3",
        }
    '''
    env.passwords.update(host_past_word_dict)

# update env setttings
def update_env_settings(env_settings_dict={}):
    if type(env_settings_dict) is not dict:
        return
    '''
        env = _AttributeDict({
            'all_hosts': [],
            'colorize_errors': False,
            'command': None,
            'command_prefixes': [],
            'cwd': '',  # Must be empty string, not None, for concatenation purposes
            'dedupe_hosts': True,
            'default_port': default_port,
            'eagerly_disconnect': False,
            'echo_stdin': True,
            'exclude_hosts': [],
            'gateway': None,
            'host': None,
            'host_string': None,
            'lcwd': '',  # Must be empty string, not None, for concatenation purposes
            'local_user': _get_system_username(),
            'output_prefix': True,
            'passwords': {},
            'path': '',
            'path_behavior': 'append',
            'port': default_port,
            'real_fabfile': None,
            'remote_interrupt': None,
            'roles': [],
            'roledefs': {},
            'shell_env': {},
            'skip_bad_hosts': False,
            'ssh_config_path': default_ssh_config_path,
            'ok_ret_codes': [0],     # a list of return codes that indicate success
            # -S so sudo accepts passwd via stdin, -p with our known-value prompt for
            # later detection (thus %s -- gets filled with env.sudo_prompt at runtime)
            'sudo_prefix': "sudo -S -p '%(sudo_prompt)s' ",
            'sudo_prompt': 'sudo password:',
            'sudo_user': None,
            'tasks': [],
            'use_exceptions_for': {'network': False},
            'use_shell': True,
            'use_ssh_config': False,
            'user': None,
            'version': get_version('short')
        })
    '''
    env.update(env_settings_dict)

def fab_run_command(command, is_local=False, command_path=None, command_prefix=None, pty=False, warn_only=True):
    fab_method = local if is_local else run
    command_path_method = lcd if is_local else cd
    '''
     with cd('/path/to/app'), prefix('workon myvenv'):
         ./manage.py syncdb
                相当于 cd /path/to/app && workon myvenv && ./manage.py syncdb
    '''
    if command_path is not None:
        with command_path_method(command_path):
            if command_prefix is not None:
                with prefix(command_prefix):
                   fab_method(command, pty=pty, warn_only=warn_only)
            else:
                fab_method(command, pty=pty, warn_only=warn_only) 
    else:
        if command_prefix is not None:
            with prefix(command_prefix):
               fab_method(command, pty=pty, warn_only=warn_only)
        else:
            fab_method(command, pty=pty, warn_only=warn_only) 

def fab_shutdown_service(service_tag, service_shutdown_command=None, is_local=False):
    fab_method = local if is_local else run
    
    if service_shutdown_command:
        try:
            fab_method(service_shutdown_command, pty=False)
            
            import time
            time.sleep(1)
        except:
            print 'Stop service %s failed by command [%s]' % (service_tag, service_shutdown_command)

    pid = fab_method("ps gaux | grep %s | grep -v grep | awk '{print $2}'" % (service_tag), pty=False)
    if pid == '':
        return

    pids = str(pid).splitlines()
    if pids is None or len(pids) == 0:
        print 'Service \'%s\' is not running till now.' % (service_tag)
    else:
        print 'Service \'%s\' is running, kill.' % (service_tag)
        for p_id in pids:
            fab_method('kill -9 %s' % (p_id), pty=False)

def upload_file_or_dir_to_remote(local_path, remote_path):
    '''
        Upload one or more files to a remote host. 
        @param local_path: may be a relative or absolute local file or directory path
        @param remote_path: absolute local directory path
    '''
    if not os.path.exist(local_path):
        exit()
    
    # make the directory in remote machine
    with cd('/tmp'):
        run('mkdir -p %s' % (remote_path))
        put(local_path, remote_path)

def download_file_or_dir_to_local(local_path, remote_path):
    '''
        Download one or more files from a remote host. 
        @param local_path: may be a relative or absolute directory path
        @param remote_path: absolute remote directory path
    '''
    
    if not os.path.exist(local_path):
        os.makedirs(local_path)

    get(remote_path, local_path)
    
