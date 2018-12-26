#!/bin/bash

cluster_id="$1"
multicluster_haproxy_port="$2"
appformix_haproxy_host_config_dir="$3"
appformix_haproxy_conf_file="$4"
cluster_controller_host="$5"
cluster_controller_port="$6"

haproxy_conf_file="$appformix_haproxy_host_config_dir/$appformix_haproxy_conf_file"

line1="    acl ${cluster_id}_URI path_beg -i /cluster/$cluster_id"
line2="    use_backend $cluster_id if ${cluster_id}_URI"
line3="backend $cluster_id"
line4="    reqrep ^([^\\ :]*)\\ /cluster/$cluster_id(.*)     \\1\\ \\2"
line5="    server $cluster_id $cluster_controller_host:$cluster_controller_port"
add_after_line="bind 0.0.0.0:$multicluster_haproxy_port"
sed -i "/$add_after_line/a\\\n$line1\n$line2" $haproxy_conf_file
echo -e "\n$line3\n$line4\n$line5" >> $haproxy_conf_file
