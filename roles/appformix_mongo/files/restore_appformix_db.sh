#
# Copyright 2016 AppFormix Inc.
#

# This script restores the AppFormix Databases

usage () {
    echo "Usage: restore_appformix_db.sh <mongo_username> <mongo_password>"`
         `"<mongo_backup_file> <local_mongo_backup_dir> <docker_mongo_backup_dir>"
    exit 1
}

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ] || [ -z "$5" ]; then
    usage
fi

MONGO_USERNAME=$1
MONGO_PASSWORD=$2

MONGO_BACKUP_FILE=$3

# LOCAL_MONGO_BACKUP_DIR is mounted on DOCKER_MONGO_BACKUP_DIR
LOCAL_MONGO_BACKUP_DIR=$4
DOCKER_MONGO_BACKUP_DIR=$5
LOCAL_MONGO_RESTORE_DIR="${LOCAL_MONGO_BACKUP_DIR}/mongo_restore_dir"
DOCKER_MONGO_RESTORE_DIR="${DOCKER_MONGO_BACKUP_DIR}/mongo_restore_dir"
mkdir -p $LOCAL_MONGO_RESTORE_DIR
# Cleanup any old files inside the directory
rm -rf ${LOCAL_MONGO_RESTORE_DIR}/*
RESTORE_LOGS_FILE=$LOCAL_MONGO_RESTORE_DIR/restore_logs.tar.gz

tar -xzf $MONGO_BACKUP_FILE -C $LOCAL_MONGO_RESTORE_DIR

docker exec appformix-mongo mongorestore -u $MONGO_USERNAME -p $MONGO_PASSWORD \
    -d controller_config $DOCKER_MONGO_RESTORE_DIR/controller_config \
    2>&1 > $LOCAL_MONGO_RESTORE_DIR/restore_controller_config.log
docker exec appformix-mongo mongorestore -u $MONGO_USERNAME -p $MONGO_PASSWORD \
    -d events_db $DOCKER_MONGO_RESTORE_DIR/events_db \
    2>&1 > $LOCAL_MONGO_RESTORE_DIR/restore_events_db.log

# Compress logs into a tar file

tar -C $LOCAL_MONGO_RESTORE_DIR -czf ${RESTORE_LOGS_FILE}.new \
    restore_controller_config.log \
    restore_events_db.log

mv ${RESTORE_LOGS_FILE}.new ${RESTORE_LOGS_FILE}

# Remove the extracted contents of tar file after restore
rm -rf $LOCAL_MONGO_RESTORE_DIR/controller_config \
    $LOCAL_MONGO_RESTORE_DIR/events_db \
    $LOCAL_MONGO_RESTORE_DIR/backup_controller_config.log \
    $LOCAL_MONGO_RESTORE_DIR/backup_events_db.log \
    $LOCAL_MONGO_RESTORE_DIR/restore_controller_config.log \
    $LOCAL_MONGO_RESTORE_DIR/restore_events_db.log


