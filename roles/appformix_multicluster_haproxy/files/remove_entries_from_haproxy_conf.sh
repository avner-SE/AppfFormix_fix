#!/bin/bash

cluster_id="$1"
appformix_haproxy_host_config_dir="$2"
appformix_haproxy_conf_file="$3"

haproxy_conf_file="$appformix_haproxy_host_config_dir/$appformix_haproxy_conf_file"

sed -i "/$cluster_id/d" $haproxy_conf_file
