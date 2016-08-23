# -*- coding=utf-8 -*-
# author: yanyang.xie@gmail.com

import os
import string


def get_config_value_by_key(config_dict, key, default_value=None):
    '''
    Get configured value by key from configuration value
    
    @param config_dict: configurations dict
    @param key: key in configurations dict
    @param default_value: default value if not found the key in configurations dict
    @return: string
    '''
    value = string.strip(config_dict[key]) if config_dict.has_key(key) else None
    if value is None and default_value is not None:
        value = default_value
    return value

def load_properties(config_file, ignore_line_by_start_tag='#'):
    '''
    Load configurations from configuration file
    
    @param config_file: configuration file in absolute path
    @return: configuration dict
    '''
    infos = {}
    if not os.path.exists(config_file):
        return {}
    
    with open(config_file, 'rU') as pf:
        for line in pf:
            if string.strip(line) == '' or string.strip(line) == '\n' or string.find(line, ignore_line_by_start_tag) == 0:
                continue
            line = string.replace(line, '\n', '')
            tmp = line.split("=", 1)
            values = tmp[1].split("#", 1)
            infos[string.strip(tmp[0])] = string.strip(values[0])
    return infos