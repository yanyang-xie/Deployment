# -*- coding=utf-8 -*-
# author: yanyang.xie@gmail.com

import getopt
import os
import re
import string
import sys

sys.path.append("../util")

from requests.auth import HTTPBasicAuth
import requests_util

sona_build_url = 'https://nexus.eng.thistech.com/nexus/service/local/repositories/%s/content/com/thistech/%s/%s/'
sona_user_name, sona_passwd = ('', '')
sona_build_regular = r'<text>(.*%s)</text>'
project_name, project_version, project_build_file_ext_name = ('', '', '')
http_proxy, https_proxy = None, None
local_file_dir, local_file_name = (os.path.dirname(os.path.abspath(__file__)), '')

def get_sona_build_version_xml(url, user_name, sona_password):
    headers = {'Referer':'https://nexus.eng.thistech.com/nexus/index.html'}
    auth = HTTPBasicAuth(user_name, sona_password)
    
    rd = requests_util.RequestsUtility()
    return rd.get_response(url, headers=headers, auth=auth)

def download_sona_build(url, user_name, sona_password, local_file_name=None, proxies=None, params=None, stream=True, chunk_size=512 * 1024.0):
    # base64string = base64.encodestring('%s:%s' % (user_name, sona_password)).replace('\n', '')
    # auth_token = 'Basic %s' % (base64string)
    # headers = {'Authorization':auth_token, 'Referer':'https://nexus.eng.thistech.com/nexus/index.html'}
    
    headers = {'Referer':'https://nexus.eng.thistech.com/nexus/index.html'}
    auth = HTTPBasicAuth(user_name, sona_password)
    
    rd = requests_util.RequestsUtility()
    rd.download_file(url, local_file_name=local_file_name, auth=auth, headers=headers, params=params, proxies=proxies, stream=stream, chunk_size=chunk_size)

def get_latest_build_file_name(build_manifest, sona_build_regular):
    t_info = re.findall(sona_build_regular, build_manifest)
    t_info.sort()
    return t_info[-1] if len(t_info) > 0 else []

def generate_local_file_path(local_dir, local_file_name):
    local_file = local_dir + os.sep + local_file_name if local_dir[-1] != os.sep else local_dir + local_file_name
    return local_file

def read_opts(short_param_list=[], long_param_list=[]):
    short_params = 'h'
    for param in short_param_list:
        short_params += param.replace('-', '').strip() + ':'
    
    long_params = ["help"]
    for param in long_param_list:
        long_params.append(param.replace('-', '').strip() + '=')
        
    opts, args = getopt.getopt(sys.argv[1:], short_params, long_params)
    
    opt_dict = {}
    for opt, value in opts:
        opt_dict[opt] = value
    
    return opt_dict, args

def usage():
    print '*' * 100
    print 'Usage:'
    print '-h: help message.'
    print '-u: user name of SONA.'
    print '-p, password of SONA.'
    print '-n, project name in SONA, such as \'vex\''
    print '-v, project version in SONA, such as \'1.1.0-SNAPSHOT\' | \'1.1.0-RC1\' | \'1.1.0-ER1\' | \'1.1.0-GA\''
    print '-e, extension name of SONA build, *.war or *.zip, such as release.zip or release.war'
    print '-d, local file dir to store downloaded SONA build, default is current directory %s' % (local_file_dir)
    print '-f, local file name of downloaded SONA build, default is the same as SONA build name'
    print '-y, http proxy to download sona build, default is not proxy. Format is 54.251.191.164:1080'
    print '-Y, https proxy to download sona build, default is not proxy. Format is 54.251.191.164:1080'
    print 'Example: python download_sona_build.py -u yanyang.xie -p *** -n vex -v 1.1.0-SNAPSHOT -e release.zip'
    print '*' * 100

def read_parameters():
    global sona_user_name, sona_passwd, sona_passwd
    global project_name, project_version, project_build_file_ext_name
    global local_file_dir, local_file_name
    global http_proxy, https_proxy
    
    opt_dict = read_opts(['-h', '-u', '-p', '-n', '-v', '-e', '-d', '-f', '-y', '-Y'])[0]
    if opt_dict.has_key('-h'):
        usage()
    else:
        if opt_dict.has_key('-u'):
            sona_user_name = string.strip(opt_dict['-u'])
    
        if opt_dict.has_key('-p'):
            sona_passwd = string.strip(opt_dict['-p'])
        
        if opt_dict.has_key('-n'):
            project_name = string.strip(opt_dict['-n'])
        
        if opt_dict.has_key('-v'):
            project_version = string.strip(opt_dict['-v'])
            
        if opt_dict.has_key('-e'):
            project_build_file_ext_name = string.strip(opt_dict['-e'])
            
        if opt_dict.has_key('-d'):
            local_file_dir = string.strip(opt_dict['-d'])
            
        if opt_dict.has_key('-f'):
            local_file_name = string.strip(opt_dict['-f'])
        
        if opt_dict.has_key('-y'):
            http_proxy = string.strip(opt_dict['-y'])
        
        if opt_dict.has_key('-Y'):
            https_proxy = string.strip(opt_dict['-Y'])
         
        return True

def check_parameters():
    if sona_user_name is None or sona_user_name == '':
        print 'SONA user name must not be empty. \n-h: help message'
        return False
    
    if sona_passwd is None or sona_passwd == '':
        print 'SONA password must not be empty. \n-h: help message'
        return False
    
    if project_name is None or project_name == '':
        print 'SONA project name must not be empty. \n-h: help message'
        return False
    
    if project_version is None or project_version == '':
        print 'SONA project version must not be empty. \n-h: help message'
        return False
    
    if project_build_file_ext_name is None or project_build_file_ext_name == '':
        print 'Extension name of SONA build must not be empty. \n-h: help message'
        return False
    
    return True

def main():
    if not read_parameters():
        sys.exit(0)
    
    if not check_parameters():
        usage()
        sys.exit(0)
    
    print local_file_name
    
    '''
    sona_user_name, sona_passwd = ('yanyang.xie', '****')
    project_name, project_version, project_build_file_ext_name = ('vex', '2.8.0-SNAPSHOT', 'release.zip')
    local_file_name = 'vex.zip'
    print sona_user_name, '***', project_name, project_version, project_build_file_ext_name, local_file_dir, local_file_name
    '''

    repositories_name = 'thistech-snapshots' if project_version.find('SNAPSHOT') > 0 else 'thistech'
    project_basic_url = sona_build_url % (repositories_name, project_name, project_version)
    project_build_regular = sona_build_regular % (project_build_file_ext_name)
    
    print 'Get project %s-%s manifest using following url:\n\t%s' % (project_name, project_version, project_basic_url)
    response_data = get_sona_build_version_xml(project_basic_url, sona_user_name, sona_passwd).text
    project_latest_build_name = get_latest_build_file_name(response_data, project_build_regular)
    print 'Latest build file name in %s-%s manifest:\t%s' % (project_name, project_version, project_latest_build_name)
    
    build_download_url = project_basic_url + project_latest_build_name
    print 'Start to download sona build %s to %s using following url:\n\t%s' % (project_latest_build_name, generate_local_file_path(local_file_dir, local_file_name), build_download_url)
    
    proxies = {}
    if http_proxy: proxies["http"] = http_proxy
    if https_proxy: proxies["https"] = https_proxy
    
    file_name = project_latest_build_name if local_file_name == '' else local_file_name
    downloaded_file_name = generate_local_file_path(local_file_dir, file_name)
    download_sona_build(build_download_url, sona_user_name, sona_passwd, downloaded_file_name, proxies=proxies)
    print 'Finish to download sona build %s to %s.' % (project_latest_build_name, downloaded_file_name)


if __name__ == '__main__':
    main()
    # python download_sona_build.py -u yanyang.xie -p ***** -n vex -v 2.0.0-SNAPSHOT -e release.zip -f vex.zip
    # 
    # if you are running in virtualenv, please active your env first
    # source /Users/xieyanyang/py27/bin/activate && python download_sona_build.py -u yanyang.xie -p ***** -n vex -v 2.0.0-SNAPSHOT -e release.zip -f vex.zip
