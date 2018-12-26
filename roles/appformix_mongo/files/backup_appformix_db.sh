#
# Copyright 2016 AppFormix Inc.
#

# This scripts backs up the AppFormix Databases
usage () {
    echo "Usage: backup_appformix_db.sh <mongo_username> <mongo_password>"`
         `"<local_mongo_backup_dir> <docker_mongo_backup_dir>"
    exit 1
}

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ]; then
    usage
fi

MONGO_USERNAME=$1
MONGO_PASSWORD=$2

# LOCAL_MONGO_BACKUP_DIR is mounted on DOCKER_MONGO_BACKUP_DIR
LOCAL_MONGO_BACKUP_DIR=$3
DOCKER_MONGO_BACKUP_DIR=$4
MONGO_BACKUP_FILE=$LOCAL_MONGO_BACKUP_DIR/mongo_backup.tar.gz

docker exec appformix-mongo mongodump -u $MONGO_USERNAME -p $MONGO_PASSWORD \
    -d controller_config -o $DOCKER_MONGO_BACKUP_DIR \
    > $LOCAL_MONGO_BACKUP_DIR/backup_controller_config.log 2>&1
docker exec appformix-mongo mongodump -u $MONGO_USERNAME -p $MONGO_PASSWORD \
    -d events_db -o $DOCKER_MONGO_BACKUP_DIR \
    > $LOCAL_MONGO_BACKUP_DIR/backup_events_db.log 2>&1

# Compress backup and logs into a tar file
tar -C $LOCAL_MONGO_BACKUP_DIR -czvf ${MONGO_BACKUP_FILE}.new controller_config \
    events_db \
    backup_controller_config.log \
    backup_events_db.log

mv ${MONGO_BACKUP_FILE}.new ${MONGO_BACKUP_FILE}

rm -rf $LOCAL_MONGO_BACKUP_DIR/controller_config \
    $LOCAL_MONGO_BACKUP_DIR/events_db \
    $LOCAL_MONGO_BACKUP_DIR/backup_controller_config.log \
    $LOCAL_MONGO_BACKUP_DIR/backup_events_db.log
