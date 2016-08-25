#!/usr/bin/python
# coding:utf-8

'''
Created on 2014-1-3

@author: yanyang
'''

from functools import wraps
import os
import string
import sys
import time

from fabric.colors import red
from fabric.context_managers import cd
from fabric.decorators import roles, task, parallel
from fabric.tasks import execute

import common_util
import constant
import fab_util

here = os.path.dirname(os.path.abspath(__file__))

config_sub_folder = sys.argv[1] + os.sep if len(sys.argv) > 1 else ''  # such as perf
config_file = here + os.sep + config_sub_folder + 'config.properties'
configs = common_util.load_properties(config_file)

user = common_util.get_config_value_by_key(configs, 'user')
pub_key = common_util.get_config_value_by_key(configs, 'public.key')
password = common_util.get_config_value_by_key(configs, 'password')
port = common_util.get_config_value_by_key(configs, 'port', 22)

core_vex_servers = common_util.get_config_value_by_key(configs, 'core.vex.server.list')
vex_fe_servers = common_util.get_config_value_by_key(configs, 'vex.fe.server.list')
vex_director_server = common_util.get_config_value_by_key(configs, 'vex.director.server.list')
vex_origin_manager_server = common_util.get_config_value_by_key(configs, 'vex.origin.manager.server.list')
memcached_servers = common_util.get_config_value_by_key(configs, 'memcached.server.list')
zookeeper_servers = common_util.get_config_value_by_key(configs, 'zookeeper.server.list')
origin_server = common_util.get_config_value_by_key(configs, 'origin.server.host')
acs_server = common_util.get_config_value_by_key(configs, 'acs.server.host')
ads_simulator_server = common_util.get_config_value_by_key(configs, 'ads.simulator.host')
content_router_simulator_server = common_util.get_config_value_by_key(configs, 'content.router.simulator.host')
cns_server = common_util.get_config_value_by_key(configs, 'cns.simulator.host')
origin_proxy_server = common_util.get_config_value_by_key(configs, 'origin.proxy.simulator.host')
origin_simulator = common_util.get_config_value_by_key(configs, 'origin.simulator.host')
cdvr_simulator = common_util.get_config_value_by_key(configs, 'cdvr.simulator.host')
vod_simulator = common_util.get_config_value_by_key(configs, 'vod.simulator.host')
ecc_spark_server_host = common_util.get_config_value_by_key(configs, 'ecc.spark.server.host')

clean_tomcat_log = True if common_util.get_config_value_by_key(configs, 'tomcat.log.clean', 'False') == 'True' else False
zookeeper_server_eth1_map = common_util.get_config_value_by_key(configs, 'zookeeper.server.eth1.map')
ads_simulator_dir = common_util.get_config_value_by_key(configs, 'ads.simlator.dir')
content_router_simulator_dir = common_util.get_config_value_by_key(configs, 'content.router.simulator.dir')
cns_simulator_dir = common_util.get_config_value_by_key(configs, 'cns.simulator.dir')
origin_proxy_dir = common_util.get_config_value_by_key(configs, 'origin.proxy.dir')
origin_proxy_batch_dir = common_util.get_config_value_by_key(configs, 'origin.proxy.batch.operation.dir')
origin_simulator_dir = common_util.get_config_value_by_key(configs, 'origin.simulator.dir')
vod_simulator_dir = common_util.get_config_value_by_key(configs, 'vod.simulator.dir')
cdvr_simulator_dir = common_util.get_config_value_by_key(configs, 'cdvr.simulator.dir')

mongo_server_host = common_util.get_config_value_by_key(configs, 'mongo.server.host')
mongo_script = common_util.get_config_value_by_key(configs, 'mongo.script')

def clear_log(clean=True, log_dir=constant.TOMCAT_DIR + '/logs', is_local=False):
    "Decorator that logs any exceptions."
    def clear_log(f):
        @wraps(f)
        def clean_log_file(*args, **kwargs):
            if clean:
                fab_util.fab_run_command('rm -rf %s/*' % (log_dir), is_local, pty=False, warn_only=True)
            return f(*args, **kwargs)
        return clean_log_file  # true decorator
    return clear_log

@task
@parallel
@roles('core_vex_server')
def stop_core_vex_cluster(service_name=constant.TOMCAT_SERVICE):
    fab_util.fab_shutdown_service(service_name)

@task
@parallel
@roles('core_vex_server')
@clear_log(clean=clean_tomcat_log)
def start_core_vex_cluster(service_name=constant.TOMCAT_SERVICE):
    _fab_start_server(service_name)

@task
@parallel
@roles('vex_fe_server')
def stop_vex_fe_cluster(service_name=constant.TOMCAT_SERVICE):
    fab_util.fab_shutdown_service(service_name)
    
@task
@parallel
@roles('vex_fe_server')
@clear_log(clean=clean_tomcat_log)
def start_vex_fe_cluster(service_name=constant.TOMCAT_SERVICE):
    _fab_start_server(service_name)

@task
@parallel
@roles('vex_director_server')
def stop_vex_director_cluster(service_name=constant.TOMCAT_SERVICE):
    fab_util.fab_shutdown_service(service_name)
    
@task
@parallel
@roles('vex_director_server')
@clear_log(clean=clean_tomcat_log)
def start_vex_director_cluster(service_name=constant.TOMCAT_SERVICE):
    _fab_start_server(service_name)

@task
@parallel
@roles('vex_origin_manager_server')
def stop_vex_origin_manager_cluster(service_name=constant.TOMCAT_SERVICE):
    fab_util.fab_shutdown_service(service_name)
    
@task
@parallel
@roles('vex_origin_manager_server')
@clear_log(clean=clean_tomcat_log)
def start_vex_origin_manager_cluster(service_name=constant.TOMCAT_SERVICE):
    _fab_start_server(service_name)

@task
@parallel
@roles('zookeeper_server')
def stop_zookeeper_cluster(service_name=constant.ZOOKEEPER_SERVICE):
    fab_util.fab_shutdown_service(service_name)

@task
@parallel
@roles('zookeeper_server')
def start_zookeeper_cluster(service_name=constant.ZOOKEEPER_SERVICE):
    _fab_start_server(service_name)

@task
@parallel
@roles('memcached_server')
def stop_memcached_cluster(service_name=constant.MEMCACHED_SERVICE):
    fab_util.fab_shutdown_service(service_name)

@task
@parallel
@roles('memcached_server')
def start_memcached_cluster(service_name=constant.MEMCACHED_SERVICE):
    _fab_start_server(service_name)

@task
@parallel
@roles('origin_server')
def stop_origin_server(service_name=constant.TOMCAT_SERVICE):
    fab_util.fab_shutdown_service(service_name)

@task
@parallel
@roles('origin_server')
@clear_log(clean=clean_tomcat_log)
def start_origin_server(service_name=constant.TOMCAT_SERVICE):
    _fab_start_server(service_name)
    
@task
@roles('acs_server')
def stop_acs_server(service_name=constant.TOMCAT_SERVICE):
    fab_util.fab_shutdown_service(service_name)

@task
@roles('acs_server')
@clear_log(clean=clean_tomcat_log)
def start_acs_server(service_name=constant.TOMCAT_SERVICE):
    _fab_start_server(service_name)

@task
@parallel
@roles('ads_simulator')
def stop_ads_simulator():
    with cd(ads_simulator_dir):
        try:
            fab_util.fab_run_command("java -version")
            fab_util.fab_run_command("./shutdown.sh")
        except:
            print red('stop ads simulator failed. %s' % (ads_simulator_dir))

@task
@parallel
@roles('ads_simulator')
def start_ads_simulator():
    with cd(ads_simulator_dir):
        try:
            fab_util.fab_run_command("java -version")
            fab_util.fab_run_command("nohup ./run.sh &")
        except Exception, e:
            print e
            print red('start ads simulator failed. %s' % (ads_simulator_dir))
        else:
            time.sleep(2)
            fab_util.fab_run_command("netstat -an | grep 8088", warn_only=False)

@task
@parallel
@roles('ads_simulator')
def setup_ads_simulator_response_template():
    with cd(ads_simulator_dir + os.sep + 'script'):
        try:
            fab_util.fab_run_command('./setup_vod_ad_response_template.sh')
        except:
            print red('setup vod response failed. %s' % (ads_simulator_dir + os.sep + 'script'))

@task
@parallel
@roles('content_router_simulator')
def stop_content_router_simulator():
    with cd(content_router_simulator_dir):
        try:
            fab_util.fab_run_command("java -version")
            fab_util.fab_run_command("./shutdown.sh")
        except Exception, e:
            print red('stop content router simulator failed. %s.%s' % (content_router_simulator_dir, str(e)))

@task
@parallel
@roles('content_router_simulator')
def start_content_router_simulator():
    with cd(content_router_simulator_dir):
        try:
            fab_util.fab_run_command("java -version")
            fab_util.fab_run_command("nohup ./run.sh &")
        except Exception, e:
            print e
            print red('start content router simulator failed. %s' % (content_router_simulator_dir))
        else:
            time.sleep(2)
            fab_util.fab_run_command("netstat -an | grep 80", warn_only=False)
        
@task
@parallel
@roles('content_router_simulator')
def setup_content_router_ad_redirect_rule():
    with cd(content_router_simulator_dir + os.sep + 'script'):
        try:
            fab_util.fab_run_command('./setup_ad_redirect_rule.sh', warn_only=False)
        except:
            print red('setup ad redirect rule failed. %s' % (content_router_simulator_dir + os.sep + 'script'))
            
@task
@parallel
@roles('content_router_simulator')
def setup_content_router_playlist_redirect_rule():
    with cd(content_router_simulator_dir + os.sep + 'script'):
        try:
            fab_util.fab_run_command('./setup_playlist_redirect_rule.sh', warn_only=False)
        except:
            print red('setup playlist redirect rule failed. %s' % (content_router_simulator_dir + os.sep + 'script'))

@task
@parallel
@roles('cns')
def stop_cns_simulator():
    with cd(cns_simulator_dir):
        try:
            fab_util.fab_run_command("java -version")
            fab_util.fab_run_command("./shutdown.sh")
        except:
            print red('stop cns simulator failed. %s' % (cns_simulator_dir))

@task
@parallel
@roles('cns')
def start_cns_simulator():
    with cd(cns_simulator_dir):
        try:
            fab_util.fab_run_command("java -version")
            fab_util.fab_run_command("nohup ./run.sh &")
        except:
            print red('start cns simulator failed. %s' % (cns_simulator_dir))
        else:
            time.sleep(2)
            fab_util.fab_run_command("netstat -an | grep 80", warn_only=False)
        
@task
@parallel
@roles('origin_proxy')
def stop_origin_proxy_simulator():
    with cd(origin_proxy_dir):
        try:
            fab_util.fab_run_command("java -version", warn_only=False)
            fab_util.fab_run_command("./shutdown.sh")
        except:
            print red('stop origin proxy simulator failed. %s' % (origin_proxy_dir))

@task
@parallel
@roles('origin_proxy')
def start_origin_proxy_simulator():
    with cd(origin_proxy_dir):
        try:
            fab_util.fab_run_command("java -version", warn_only=True)
            fab_util.fab_run_command("nohup ./run.sh &", timeout=20)
        except:
            print red('start origin proxy simulator failed. %s' % (origin_proxy_dir))
        else:
            time.sleep(2)
            fab_util.fab_run_command("netstat -an | grep 80", warn_only=False)

@task
@parallel
@roles('origin_proxy')
def batch_stop_origin_proxy_simulator():
    with cd(origin_proxy_batch_dir):
        try:
            fab_util.fab_run_command("java -version", warn_only=True)
            fab_util.fab_run_command("./shutdown_origin_proxys.sh", timeout=20)
        except:
            print red('batch stop origin proxy simulator failed. %s' % (origin_proxy_batch_dir))

@task
@parallel
@roles('origin_proxy')
def batch_start_origin_proxy_simulator():
    with cd(origin_proxy_batch_dir):
        try:
            fab_util.fab_run_command("java -version", warn_only=False)
            fab_util.fab_run_command("./start_up_origin_proxys.sh", timeout=20, warn_only=False)
        except:
            print red('batch start origin proxy simulator failed. %s' % (origin_proxy_batch_dir))
        else:
            time.sleep(2)
            fab_util.fab_run_command("netstat -an | grep 81", warn_only=False)

@task
@parallel
@roles('origin_simulator')
def stop_origin_simulator():
    with cd(origin_simulator_dir):
        try:
            fab_util.fab_run_command("java -version")
            fab_util.fab_run_command("./shutdown.sh")
        except:
            print red('stop origin simulator failed. %s' % (origin_simulator_dir))

@task
@parallel
@roles('origin_simulator')
def start_origin_simulator():
    with cd(origin_simulator_dir):
        try:
            fab_util.fab_run_command("java -version", warn_only=False)
            fab_util.fab_run_command("nohup ./run.sh &")
        except:
            print red('start origin simulator failed. %s' % (origin_simulator_dir))
        else:
            time.sleep(2)
            fab_util.fab_run_command("netstat -an | grep 8089", warn_only=False)

@task
@parallel
@roles('cdvr_simulator')
def stop_cdvr_simulator():
    with cd(cdvr_simulator_dir):
        try:
            fab_util.fab_run_command("java -version", warn_only=False)
            fab_util.fab_run_command("./shutdown.sh")
        except:
            print red('stop cdvr simulator failed. %s' % (cdvr_simulator_dir))

@task
@parallel
@roles('cdvr_simulator')
def start_cdvr_simulator():
    with cd(cdvr_simulator_dir):
        try:
            fab_util.fab_run_command("java -version", warn_only=False)
            fab_util.fab_run_command("nohup ./run.sh &")
        except:
            print red('start cdvr simulator failed. %s' % (cdvr_simulator_dir))
        else:
            time.sleep(2)
            fab_util.fab_run_command("netstat -an | grep 8082", warn_only=False)

@task
@parallel
@roles('cdvr_simulator')
def setup_cdvr_simulator_ad_insertion():
    with cd(cdvr_simulator_dir + os.sep + 'script'):
        try:
            fab_util.fab_run_command('./setupAdSegments.sh', warn_only=False)
            time.sleep(4)
            fab_util.fab_run_command('./getHotRecording.sh', warn_only=False)
        except:
            print red('setup cdvr simulator ad insertion failed. %s' % (cdvr_simulator_dir + os.sep + 'script'))

@task
@parallel
@roles('vod_simulator')
def stop_vod_simulator():
    with cd(vod_simulator_dir):
        try:
            fab_util.fab_run_command("java -version", warn_only=False)
            fab_util.fab_run_command("./shutdown.sh")
        except:
            print red('stop vod simulator failed. %s' % (vod_simulator_dir))

@task
@parallel
@roles('vod_simulator')
def start_vod_simulator():
    with cd(vod_simulator_dir):
        try:
            fab_util.fab_run_command("java -version", warn_only=False)
            fab_util.fab_run_command("nohup ./run.sh &")
        except:
            print red('start vod simulator failed. %s' % (vod_simulator_dir))
        else:
            time.sleep(2)
            fab_util.fab_run_command("netstat -an | grep 8081", warn_only=False)

@task
@parallel
@roles('vod_simulator')
def setup_vod_simulator_ad_insertion():
    with cd(vod_simulator_dir + os.sep + 'script'):
        try:
            fab_util.fab_run_command('./setupVODAds.sh', warn_only=False)
        except:
            print red('setup vod simulator ad insertion failed. %s' % (vod_simulator_dir + os.sep + 'script'))

@task
@roles('ecc_spark_server_host')
def start_ecc_spark():
    try:
        fab_util.fab_run_command(constant.SPARK_COMMAND_START, warn_only=True, timeout=20)
        time.sleep(4)
        fab_util.fab_run_command('su - spark -c "ps -ef | grep java" ', warn_only=False)
    except Exception, e:
        print red('start spark failed ,%s' % (str(e)))

@task
@roles('ecc_spark_server_host')
def stop_ecc_spark():
    try:
        fab_util.fab_run_command(constant.SPARK_COMMAND_STOP, warn_only=True)
    except Exception, e:
        print red('start spark failed ,%s' % (str(e)))

@task
@roles('mongo_host')
def run_mongo_script():
    try:
        fab_util.fab_run_command('mongo %s' % (mongo_script), warn_only=False)
    except Exception, e:
        print red('run mongo script failed ,%s' % (str(e)))
    
def _fab_start_server(server_name, command=None, is_local=False, warn_only=True):
    cmd = command or 'service %s start'
    command_line = cmd % (server_name)
    
    print 'Start %s server by command %s......' % (server_name, command_line)
    fab_util.fab_run_command(command_line, is_local, warn_only=warn_only, ex_abort=True)

def _setup_facric_roles(role, host_string, user='root', port=22, host_sep=','):
    if role is None:
        return
    
    if host_string is not None and len(host_string) > 0:
        host_list = string.split(host_string, host_sep)
        fab_util.setRoles(role, host_list, user, port)

def _setup_fab_env():
    # setup fabric parameters
    fab_util.setKeyFile(pub_key)
    fab_util.set_password(password)
    
    _setup_facric_roles('core_vex_server', core_vex_servers, user, port)
    _setup_facric_roles('vex_fe_server', vex_fe_servers, user, port)
    _setup_facric_roles('vex_director_server', vex_director_server , user, port)
    _setup_facric_roles('vex_origin_manager_server', vex_origin_manager_server , user, port)
    _setup_facric_roles('zookeeper_server', zookeeper_servers , user, port)
    _setup_facric_roles('memcached_server', memcached_servers , user, port)
    _setup_facric_roles('origin_server', origin_server , user, port)
    _setup_facric_roles('acs_server', acs_server , user, port)
    _setup_facric_roles('ads_simulator', ads_simulator_server , user, port)
    _setup_facric_roles('content_router_simulator', content_router_simulator_server , user, port)
    _setup_facric_roles('cns', cns_server, user, port)
    _setup_facric_roles('origin_proxy', origin_proxy_server, user, port)
    _setup_facric_roles('origin_simulator', origin_simulator, user, port)
    _setup_facric_roles('vod_simulator', vod_simulator, user, port)
    _setup_facric_roles('cdvr_simulator', cdvr_simulator, user, port)
    _setup_facric_roles('ecc_spark_server_host', ecc_spark_server_host, user, port)
    _setup_facric_roles('mongo_host', mongo_server_host, user, port)

_setup_fab_env()

if __name__ == '__main__':
    # fab_command = 'fab -f %s %s' % (os.path.abspath(__file__), 'stop_layer7_gateway')
    # os.popen(fab_command)
    
    execute(stop_core_vex_cluster)
    execute(start_core_vex_cluster)
