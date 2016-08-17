# -*- coding=utf-8 -*-
# author: yanyang.xie@gmail.com

import base64
from contextlib import closing
import os
import requests

class ProgressBar(object):
    '''
    Downloading status bar, format is as follow:
    [title] running_status current/1024 KB total/1024 KB
    [vex-2.0.0-20140610.062448-284-release.zip] downloading 1024.00 KB / 32710.29 KB
    '''
    def __init__(self, title, current=0.0, running_status=None, finished_status=None, total=1000.0, sep='/'):
        super(ProgressBar, self).__init__()
        self.status_format = "[%s] %s %.2f %s %s %.2f %s %.2f%%"
        self.title = title
        self.total = total
        self.current = current
        self.status = running_status or ""
        self.finished_status = finished_status or " " * len(self.statue)
        self.unit = 'KB'
        self.chunk_size = 1024.0
        self.seq = sep

    def get_status(self):
        return self.status_format % (self.title, self.status, self.current / self.chunk_size, self.unit, self.seq, self.total / self.chunk_size, self.unit, 100 * self.current / self.total)

    def refresh(self, current=1, status=None):
        self.current += current
        # if status is not None:
        self.status = status or self.status
        end_str = "\r"
        if self.current >= self.total:
            end_str = '\n'
            self.status = status or self.finished_status
        print (self.get_status() + end_str)

class RequestsDownload(object):
    '''
    Using Python requests lib to download file from remote
    @param url: download url
    @param local_file_name: local file name, if not set, using the downloading file name as local file name
    @param headers: request headers. format is {'Authorization':auth_token, }
    @param proxies: request proxies, format is {"http": "http://10.10.1.10:3128","https": "http://10.10.1.10:1080",}
    @param params: request parameters
    @param stream: whether to use streaming download
    @param chunk_size: max download bytes in each downloading reading
    '''
    # chunk_size 单次请求最大值
    def __init__(self, url, local_file_name=None, headers={}, params=None, proxies=None, stream=True, chunk_size=512 * 1024.0,):
        self.url = url
        self.headers = headers
        self.stream = True
        self.chunk_size = chunk_size
        self.local_file_name = local_file_name
        self.proxies = proxies
        self.params = params
    
    def download_sona_build(self):
        if self.local_file_name is None:
            self.local_file_name = url.split('/')[-1]
        
        try:
            if os.path.exists(self.local_file_name):
                os.remove(self.local_file_name)
        except Exception, e:
            print e
            return
        
        if self.stream is True:
            with closing(requests.get(self.url, stream=self.stream, headers=self.headers, proxies=self.proxies, params=self.params)) as response:
                content_size = int(response.headers['content-length'])  # 内容体总大小
                progress = ProgressBar(self.local_file_name, total=content_size, running_status="Downloading", finished_status="Finished.")
                
                with open(self.local_file_name, "wb") as f:
                    for data in response.iter_content(chunk_size=int(self.chunk_size)):
                        f.write(data)
                        progress.refresh(current=len(data))
        else:
            with closing(requests.get(self.url, self.stream, headers=self.headers)) as response:
                with open(self.local_file_name, "wb") as f:
                    for data in response.iter_content(chunk_size=int(self.chunk_size)):
                        f.write(data)

def download_sona_build(url, user_name, sona_password, local_file_name=None, stream=True, chunk_size=512 * 1024.0, unit='KB', proxies={}):
    base64string = base64.encodestring('%s:%s' % (user_name, sona_password)).replace('\n', '')
    auth_token = 'Basic %s' % (base64string)
    headers = {'Authorization':auth_token, 'Referer':'https://nexus.eng.thistech.com/nexus/index.html'}
    rd = RequestsDownload(url, local_file_name, headers=headers, proxies=proxies, stream=stream, chunk_size=chunk_size)
    rd.download_sona_build()

if __name__ == '__main__':
    user = 'yanyang.xie' 
    sona_passwd = 'Vicky****'
    url = 'https://nexus.eng.thistech.com/nexus/service/local/repositories/thistech-snapshots/content/com/thistech/vex/2.0.0-SNAPSHOT/vex-2.0.0-20140610.062448-284-release.zip'
    download_sona_build(url, user, sona_passwd, stream=True, chunk_size=256 * 1024.0)
