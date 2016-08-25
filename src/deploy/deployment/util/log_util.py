# -*- coding=utf-8 -*-
# author: yanyang.xie@gmail.com

'''
@author: yanyang.xie@thistech.com
@version: 0.1
@since: 10/23/2013
'''

import os.path
import sys

class Logger(object):  
    def __init__(self, path='/tmp/logs/', filename="default.log"):
        if not os.path.exists(path):
            os.makedirs(path)
            
        self.terminal = sys.stdout  
        self.log = open(path + filename, "a")  
  
    def write(self, message):  
        self.terminal.write(message)  
        self.log.write(message)  
  
    def flush(self):  
        self.terminal.flush()  
        self.log.flush()  
  
    def close(self):  
        self.terminal.close()  
        self.log.close()  
  
    def isatty(self):  
        return False 