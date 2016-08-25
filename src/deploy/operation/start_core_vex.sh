#!/bin/sh

fab -f vex_operation.py start_vex_fe_cluster
fab -f vex_operation.py start_core_vex_cluster
fab -f vex_operation.py start_vex_director_cluster
fab -f vex_operation.py start_vex_origin_manager_cluster
fab -f vex_operation.py start_memcached_cluster
