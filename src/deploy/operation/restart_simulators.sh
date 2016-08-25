#!/bin/sh

#ads
fab -f vex_operation.py stop_ads_simulator
fab -f vex_operation.py start_ads_simulator
#fab -f vex_operation.py setup_ads_simulator_response_template

#content router
fab -f vex_operation.py stop_content_router_simulator
fab -f vex_operation.py start_content_router_simulator
fab -f vex_operation.py setup_content_router_ad_redirect_rule

#cns
fab -f vex_operation.py stop_cns_simulator
fab -f vex_operation.py start_cns_simulator

#mock origin
fab -f vex_operation.py stop_content_router_simulator
fab -f vex_operation.py start_content_router_simulator

#origin proxy 
#fab -f vex_operation.py batch_stop_origin_proxy_simulator
#fab -f vex_operation.py batch_start_origin_proxy_simulator

#origin_simulator
#fab -f vex_operation.py stop_origin_simulator
#fab -f vex_operation.py start_origin_simulator

#cdvr simulator
#fab -f vex_operation.py stop_cdvr_simulator
#fab -f vex_operation.py start_cdvr_simulator
#fab -f vex_operation.py setup_cdvr_simulator_ad_insertion

#vod simulator
#fab -f vex_operation.py stop_vod_simulator
#fab -f vex_operation.py start_vod_simulator
#fab -f vex_operation.py setup_vod_simulator_ad_insertion
