# -*- coding=utf-8 -*-
# author: yanyang.xie@gmail.com

from contextlib import closing
import json
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

class RequestsUtility(object):
    
    def get_response(self, url, timeout=2, params=None, **kwargs):
        response = requests.get(url, params=params, timeout=timeout, **kwargs)
        return response
    
    def post(self, url, data=None):
        response = requests.post("http://httpbin.org/post", data=data)
        return response
    
    def post_json(self, url, data):
        response = requests.post(url, data=json.dumps(data))
        return response
    
    def post_files(self, url, file_list):
        files = {}
        for f in file_list:
            file_name = f.split('.')[-1]
            file[file_name] = open(f, 'rb')

        response = requests.post(url, files=files)
        return response
    
    def download_file(self, url, local_file_name=None, headers=None, params=None, proxies=None, stream=True, chunk_size=512 * 1024.0,):
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
        
        if local_file_name is None:
            local_file_name = url.split('/')[-1]
        
        try:
            if os.path.exists(local_file_name):
                os.remove(local_file_name)
        except Exception, e:
            print e
            return
        
        if stream is True:
            with closing(requests.get(url, stream=stream, headers=headers, proxies=proxies, params=params)) as response:
                content_size = int(response.headers['content-length'])  # 内容体总大小
                progress = ProgressBar(local_file_name, total=content_size, running_status="Downloading", finished_status="Finished.")
                
                with open(local_file_name, "wb") as f:
                    for data in response.iter_content(chunk_size=int(chunk_size)):
                        f.write(data)
                        progress.refresh(current=len(data))
        else:
            with closing(requests.get(url, stream, headers=headers)) as response:
                with open(local_file_name, "wb") as f:
                    for data in response.iter_content(chunk_size=int(chunk_size)):
                        f.write(data)
