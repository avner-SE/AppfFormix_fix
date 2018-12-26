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
LXC_STATE_SCRIPT="$9"
PUBLIC_DIR="/var/public"
PLATFORM_LXC_DIR="$PUBLIC_DIR/appformix"

APPFORMIX_LXC_IMAGE="appformix-lxc-images*.tar.gz"
APPFORMIX_MANAGER_PACKAGE_FILE="appformix-manager*_all.deb"
APPFORMIX_MANAGER_DIR="/opt/appformix/manager"
PLATFORM_APPFORMIX_MANAGER_DIR=$PLATFORM_LXC_DIR$APPFORMIX_MANAGER_DIR
PLATFORM_APPFORMIX_MANAGER_PACKAGE_DIR="$PLATFORM_APPFORMIX_MANAGER_DIR/bin"

COPY="sshpass -p $PLATFORM_PASS scp -o StrictHostKeyChecking=no"
JDM="sshpass -p $PLATFORM_PASS ssh -o StrictHostKeyChecking=no -t $PLATFORM_USER@$PLATFORM_IP"
JDM_HYPERVISOR="$JDM vhclient -t /bin/bash"

LXC_INSTALLED_OK="appformix lxc installed"

LXC_INSTALLED=$(docker run --rm -v $FILES_DIR:$FILES_DIR ${CONTAINER_IMAGE} \
    "/usr/bin/python" \
    "$FILES_DIR/$LXC_STATE_SCRIPT" \
    "$PLATFORM_IP" \
    "$PLATFORM_USER" \
    "$PLATFORM_PASS" \
    | grep "$LXC_INSTALLED_OK" || true)

if [ "$LXC_INSTALLED_OK" == "$LXC_INSTALLED" ]; then
  exit 0
fi

# COPY LXC Conf and Image
$COPY $FILES_DIR/$LXC_CONF $PLATFORM_USER@$PLATFORM_IP:$PUBLIC_DIR
$COPY $FILES_DIR/$APPFORMIX_LXC_IMAGE $PLATFORM_USER@$PLATFORM_IP:$PUBLIC_DIR/

# Create Appformix LXC Directory and UnTar Image
$JDM mkdir -p $PLATFORM_LXC_DIR
$JDM_HYPERVISOR tar -xzf $PUBLIC_DIR/$APPFORMIX_LXC_IMAGE -C $PLATFORM_LXC_DIR
$JDM rm -rf $PUBLIC_DIR/$APPFORMIX_LXC_IMAGE

# Copy LXC hosts, interfaces and dns files
$COPY $FILES_DIR/interfaces_$PLATFORM_IP $PLATFORM_USER@$PLATFORM_IP:$PLATFORM_LXC_DIR/etc/network/interfaces
$COPY $FILES_DIR/hosts $PLATFORM_USER@$PLATFORM_IP:$PLATFORM_LXC_DIR/etc/hosts
$JDM cp /etc/resolv.conf $PLATFORM_LXC_DIR/etc/resolv.conf

# Copy Appformix Manager Package and Hypervisor IP File for Appformix Manager Installer
$JDM mkdir -p $PLATFORM_APPFORMIX_MANAGER_PACKAGE_DIR
$COPY $FILES_DIR/hypervisor_ip $PLATFORM_USER@$PLATFORM_IP:$PLATFORM_APPFORMIX_MANAGER_DIR
$COPY $FILES_DIR/$APPFORMIX_MANAGER_PACKAGE_FILE $PLATFORM_USER@$PLATFORM_IP:$PLATFORM_APPFORMIX_MANAGER_PACKAGE_DIR

# Setup password less ssh key access
$JDM_HYPERVISOR mkdir -p /root/.ssh
$JDM_HYPERVISOR cp $PLATFORM_LXC_DIR/root/.ssh/id_rsa.pub /root/.ssh/authorized_keys

# Load Conf and Launch LXC Container
docker run --rm -v $FILES_DIR:$FILES_DIR ${CONTAINER_IMAGE} \
    "/usr/bin/python" \
    "$FILES_DIR/$LXC_SETUP_SCRIPT" \
    "$FILES_DIR/$VNF_CONF" \
    "$PLATFORM_IP" \
    "$PLATFORM_USER" \
    "$PLATFORM_PASS"
