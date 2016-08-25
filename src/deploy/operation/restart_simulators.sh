#!/bin/sh

#ads
python vex_operation.py stop_ads_simulator
python vex_operation.py start_ads_simulator
#python vex_operation.py setup_ads_simulator_response_template

#content router
python vex_operation.py stop_content_router_simulator
python vex_operation.py start_content_router_simulator
python vex_operation.py setup_content_router_ad_redirect_rule

#cns
python vex_operation.py stop_cns_simulator
python vex_operation.py start_cns_simulator

#mock origin
python vex_operation.py stop_content_router_simulator
python vex_operation.py start_content_router_simulator

#origin proxy 
#python vex_operation.py batch_stop_origin_proxy_simulator
#python vex_operation.py batch_start_origin_proxy_simulator

#origin_simulator
#python vex_operation.py stop_origin_simulator
#python vex_operation.py start_origin_simulator

#cdvr simulator
#python vex_operation.py stop_cdvr_simulator
#python vex_operation.py start_cdvr_simulator
#python vex_operation.py setup_cdvr_simulator_ad_insertion

#vod simulator
#python vex_operation.py stop_vod_simulator
#python vex_operation.py start_vod_simulator
#python vex_operation.py setup_vod_simulator_ad_insertion
