#!/bin/bash

set -ex

CONTAINER_IMAGE="$1"
FILES_DIR="$2"
PLATFORM_IP="$3"
PLATFORM_USER="$4"
PLATFORM_PASS="$5"
LXC_CONF="$6"
VNF_CONF="$7"
LXC_SETUP_SCRIPT="$8"

PUBLIC_DIR="/var/public"
PLATFORM_LXC_DIR="$PUBLIC_DIR/appformix"

JDM="sshpass -p $PLATFORM_PASS ssh -o StrictHostKeyChecking=no -t $PLATFORM_USER@$PLATFORM_IP"
JDM_HYPERVISOR="$JDM vhclient -t /bin/bash"

# Stop lxc container
docker run --rm -v $FILES_DIR:$FILES_DIR ${CONTAINER_IMAGE} \
    "/usr/bin/python" \
    "$FILES_DIR/$LXC_SETUP_SCRIPT" \
    "$VNF_CONF" \
    "$PLATFORM_IP" \
    "$PLATFORM_USER" \
    "$PLATFORM_PASS"

# Remove the lxc conf file
$JDM rm -rf $PUBLIC_DIR/$LXC_CONF

# Clean the the lxc container directory
$JDM_HYPERVISOR rm -rf $PLATFORM_LXC_DIR
