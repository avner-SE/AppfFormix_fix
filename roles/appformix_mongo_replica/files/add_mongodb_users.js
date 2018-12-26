//
// Copyright 2016 AppFormix Inc.
//

// This script creates users in MongoDB directly through
// the Mongo shell.
// USERNAME and PASSWORD are expected to be
// specified as environment variables.
// To run:
// mongo add_mongo_users.js --eval "PORT=<port>; USERNAME=\"<username>\"; PASSWORD=\"<pw>\""

var adminDb = "admin";
var controllerConfigDb = "controller_config";
var eventsDb = "events_db";
var conn;
var adminAuth;
var controllerConfigAuth;
var eventsDbAuth;

function connect() {
    while(!conn) {
        try {
            conn = new Mongo("localhost:" + PORT);
        } catch(error) {
            sleep(3000); // 3 seconds
        }
    }
}

function checkUsersExist() {
    db = conn.getDB(adminDb);
    adminAuth = db.auth(USERNAME, PASSWORD);
    db = conn.getDB(controllerConfigDb);
    controllerConfigAuth = db.auth(USERNAME, PASSWORD);
    db = conn.getDB(eventsDb);
    eventsDbAuth = db.auth(USERNAME, PASSWORD);
    return adminAuth && controllerConfigAuth && eventsDbAuth;
}

function createUsers() {
    if (!adminAuth) {
        db = conn.getDB(adminDb);
        db.createUser({user: USERNAME, pwd: PASSWORD, roles: ['root']});
    }
    if (!controllerConfigAuth) {
        db = conn.getDB(controllerConfigDb);
        db.createUser({user: USERNAME, pwd: PASSWORD, roles: ['dbOwner']});
    }
    if (!eventsDbAuth) {
        db = conn.getDB(eventsDb);
        db.createUser({user: USERNAME, pwd: PASSWORD, roles: ['dbOwner']});
    }
}

connect();
if (!checkUsersExist()) {
    createUsers();
}
