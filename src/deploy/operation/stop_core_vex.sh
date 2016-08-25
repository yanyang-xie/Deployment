#!/bin/sh

python vex_operation.py stop_vex_fe_cluster
python vex_operation.py stop_core_vex_cluster
python vex_operation.py stop_vex_director_cluster
python vex_operation.py stop_vex_origin_manager_cluster
python vex_operation.py stop_memcached_cluster
