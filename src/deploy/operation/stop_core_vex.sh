#!/bin/sh

fab -f vex_operation.py stop_vex_fe_cluster
fab -f vex_operation.py stop_core_vex_cluster
fab -f vex_operation.py stop_vex_director_cluster
fab -f vex_operation.py stop_vex_origin_manager_cluster
fab -f vex_operation.py stop_memcached_cluster
