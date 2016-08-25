#!/bin/sh

fab -f  vex_operation.py stop_layer7_gateway
fab -f  vex_operation.py start_layer7_gateway

fab -f vex_operation.py stop_sportlink_core
fab -f vex_operation.py start_sportlink_core
