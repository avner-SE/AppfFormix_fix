#!/bin/bash

appformix_vip_url="{{ appformix_vip_url }}"
appformix_haproxy_sock_file="{{ appformix_haproxy_socket_stat_file }}"
haproxy_log_file="/haproxy/haproxy_action.log"
openstack_enabled="{{ openstack_platform_enabled }}"
aws_enabled="{{ aws_platform_enabled }}"
vcenter_enabled="{{ vcenter_platform_enabled }}"
network_device_enabled="{{ network_device_discovery_enabled }}"

send_master_update_to_controller() {
    # Enable master
    curl --insecure -H "Content-Type: application/json" -X POST \
        -d '{"EnableMaster": true}' \
        ${appformix_vip_url}/appformix/v1.0/enable_master
}

do_controller_health_check() {
    controller_file="/haproxy/controller_servers"
    temp_controller_file="/temp_controller_servers"
    echo "show stat" | socat "$appformix_haproxy_sock_file" stdio | \
        awk 'BEGIN {FS=","} {if ($0~/appformix-controller/) \
        {print $2, $18}}' > "$temp_controller_file"
    send_master_update_to_controller

    mv "$temp_controller_file" "$controller_file"
}

send_master_update_to_adapter() {
    # Enable master
    adapter_type=$1
    curl --insecure -H "Content-Type: application/json" -X POST \
        -d '{"EnableMaster": true}' \
        ${appformix_vip_url}/appformix/v1.0/${adapter_type}_adapter/enable_master
}

do_adapter_health_check() {
    adapter_type=$1
    adapter_file="/haproxy/adapter_servers"
    temp_adapter_file="/temp_adapter_servers"
    echo "show stat" | socat "$appformix_haproxy_sock_file" stdio | \
        awk 'BEGIN {FS=","} {if ($0~/appformix-${adapter_type}_adapter/) \
        {print $2, $18}}' > "$temp_adapter_file"

    send_master_update_to_adapter $adapter_type


    mv "$temp_adapter_file" "$adapter_file"
}

send_master_update_to_datamanager() {
    # Enable master
    curl --insecure -H "Content-Type: application/json" -X POST \
        ${appformix_vip_url}/version/2.0/data_manager_writer
}

do_datamanager_health_check() {
    datamanager_file="/haproxy/datamanager_servers"
    echo "show stat" | socat "$appformix_haproxy_sock_file" stdio | \
        awk 'BEGIN {FS=","} {if ($0~/appformix-datamanager_version/) \
        {print $2, $18}}' > "$datamanager_file"

    current_writer_id=`curl --insecure -H "Content-Type: application/json" -X GET \
        ${appformix_vip_url}/version/2.0/data_manager_writer | \
        awk 'BEGIN{FS="\""} {for(i=1;i<NF;i++) {if ($i=="DataManagerId") {print $(i+2)}}}'`

    status=`grep "$current_writer_id" "$datamanager_file" | awk '{print $2}'`

    if [ "$current_writer_id" == "" ] || [ "$status" != "UP" ]; then
        echo " =========== datamanager ========== " >> ${haproxy_log_file}
        cat ${datamanager_file} >> ${haproxy_log_file}
        echo "current_writer ""$current_writer_id" >> ${haproxy_log_file}
        send_master_update_to_datamanager
    fi
}

while true
do
    do_controller_health_check
    if [ "$openstack_enabled" == "true" ] || [ "$openstack_enabled" == "True" ]; then
        do_adapter_health_check "openstack"
    fi
    if [ "$aws_enabled" == "true" ] || [ "$aws_enabled" == "True" ]; then
        do_adapter_health_check "aws"
    fi
    if [ "$vcenter_enabled" == "true" ] || [ "$vcenter_enabled" == "True" ]; then
        do_adapter_health_check "vcenter"
    fi
    if [ "$network_device_enabled" == "true" ] || [ "$network_device_enabled" == "True" ]; then
        do_adapter_health_check "network_device"
    fi
    do_datamanager_health_check
    sleep 10
done
