//
// Copyright 2016 AppFormix Inc.
//

// This script creates users in MongoDB directly through the Mongo shell.
// USERNAME and PASSWORD are variables whose value must be set before executing
// this script.
//
// For example:
//   mongo credentials.js add_mongo_users.js
// OR
//   mongo --eval 'USERNAME="<username>"; PASSWORD="<pw>"' add_mongo_users.js

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
            conn = new Mongo();
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
    db = conn.getDB(adminDb);
    db.auth(USERNAME, PASSWORD);
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
