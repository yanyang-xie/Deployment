#!/usr/bin/python
# coding:utf-8
# author: yanyang.xie

TOMCAT_SERVICE = 'tomcat'
MEMCACHED_SERVICE = 'memcached'
ZOOKEEPER_SERVICE = 'zookeeper'

TOMCAT_DIR = '/usr/local/thistech/tomcat'

LAYER7_WAY_COMMAND_START = 'su gateway -c "/opt/SecureSpan/Gateway/runtime/bin/gateway.sh start"'
LAYER7_WAY_COMMAND_STOP = 'su gateway -c "/opt/SecureSpan/Gateway/runtime/bin/gateway.sh stop"'

SPARK_COMMAND_START = 'su spark -c "sh /usr/local/spark/sbin/start-thistech.sh"'
SPARK_COMMAND_STOP = 'su spark -c "sh /usr/local/spark/sbin/stop-all.sh"'


