#!/bin/bash
# TODO: need to check and remove other containers such as appformix-vcenter-adapter
interface=$1
containers=("appformix-dashboard" "appformix-datamanager" "appformix-controller" "appformix-openstack-adapter" "appformix-mongo" "appformix-redis")
for container in ${containers[@]};
do
    ipv6_address=$(docker inspect --format '{{range .NetworkSettings.Networks}}{{.GlobalIPv6Address}}{{end}}' $container)
    echo $ipv6_address, $container
    ip -6 neigh add proxy $ipv6_address dev $interface
done
