--workflow_d

CREATE TABLE workflow_d.package (
packageid varchar(50) PRIMARY KEY,
doi varchar(100),
scope     varchar(50),
identifier integer,
revision integer,
spatialcount smallint NOT NULL DEFAULT -1,
downloaded timestamp,
title TEXT,
report text );
CREATE TABLE workflow_d.entity (
id serial PRIMARY KEY,
packageid varchar(50) REFERENCES workflow_d.package(packageid),
entityname varchar(2000),
israster boolean NOT NULL DEFAULT FALSE,
isvector boolean NOT NULL DEFAULT FALSE,
entitydescription TEXT,
completed timestamp,
storage varchar(200),
mxd varchar(200),
layername varchar(2000),
status varchar(500),
sourceloc varchar(2000),
report text,
UNIQUE ( packageid, entityname ) );
CREATE TABLE workflow_d.geonis_layer (
id integer PRIMARY KEY REFERENCES workflow_d.entity(id),
packageid varchar(50),
scope     varchar(50),
entityname VARCHAR(2000),
entitydescription TEXT,
title TEXT,
abstract TEXT,
purpose TEXT,
keywords varchar(1000),
sourceloc varchar(2000),
layername varchar(2000),
arcloc varchar(100),
layerid integer);
CREATE TABLE workflow_d.errornotify (packageid varchar(50), contact varchar(200));
CREATE TABLE workflow_d.limit_identifier (identifier varchar(50));
CREATE TABLE workflow_d.report (
    reportid SERIAL PRIMARY KEY,
    packageid VARCHAR(50) REFERENCES workflow_d.package(packageid),
    entityid INTEGER REFERENCES workflow_d.entity(id),
    entityname TEXT
);
CREATE TABLE workflow_d.taskreport (
    taskreportid SERIAL PRIMARY KEY,
    reportid INTEGER REFERENCES workflow_d.report(reportid),
    taskname VARCHAR(200),
    description TEXT,
    report TEXT,
    status BOOLEAN,
    UNIQUE(reportid, taskname)
);
-- this is a denormalized table which will be accessed via query layer
CREATE TABLE workflow_d.viewreport (
    taskreportid INTEGER PRIMARY KEY,
    reportid INTEGER,
    packageid VARCHAR(50),
    entityid INTEGER,
    entityname VARCHAR(2000),
    entitydescription TEXT,
    taskname VARCHAR(200),
    taskdescription TEXT,
    report TEXT,
    status BOOLEAN,
    israster BOOLEAN,
    isvector BOOLEAN,
    sourceloc VARCHAR(2000),
    UNIQUE(reportid, taskname)
);

--dupe tables without defaults, constraints
CREATE TABLE workflow_d.package_superseded (LIKE workflow_d.package );
CREATE TABLE workflow_d.entity_superseded (LIKE workflow_d.entity );
CREATE TABLE workflow_d.geonis_layer_superseded (LIKE workflow_d.geonis_layer );

--workflow
CREATE TABLE workflow.package (
packageid varchar(50) PRIMARY KEY,
doi varchar(100),
scope     varchar(50),
identifier integer,
revision integer,
spatialcount smallint NOT NULL DEFAULT -1,
downloaded timestamp,
title TEXT,
report text );
CREATE TABLE workflow.entity (
id serial PRIMARY KEY,
packageid varchar(50) REFERENCES workflow.package(packageid),
entityname varchar(2000),
israster boolean NOT NULL DEFAULT FALSE,
isvector boolean NOT NULL DEFAULT FALSE,
entitydescription TEXT,
title TEXT,
completed timestamp,
storage varchar(200),
mxd varchar(200),
layername varchar(2000),
status varchar(500),
sourceloc varchar(2000),
report text,
UNIQUE ( packageid, entityname ) );
CREATE TABLE workflow.geonis_layer (
id integer PRIMARY KEY REFERENCES workflow.entity(id),
packageid varchar(50),
scope     varchar(50),
entityname VARCHAR(2000),
entitydescription TEXT,
abstract TEXT,
purpose TEXT,
title TEXT,
keywords varchar(1000),
sourceloc varchar(2000),
layername varchar(2000),
arcloc varchar(100),
layerid integer);
CREATE TABLE workflow.errornotify (packageid varchar(50), contact varchar(200));
CREATE TABLE workflow.limit_identifier (identifier varchar(50));
--dupe tables without defaults, constraints
CREATE TABLE workflow.package_superseded (LIKE workflow.package );
CREATE TABLE workflow.entity_superseded (LIKE workflow.entity );
CREATE TABLE workflow.geonis_layer_superseded (LIKE workflow.geonis_layer );

CREATE TABLE workflow.report (
    reportid SERIAL PRIMARY KEY,
    packageid VARCHAR(50) REFERENCES workflow.package(packageid),
    entityid INTEGER REFERENCES workflow.entity(id),
    entityname TEXT
);
CREATE TABLE workflow.taskreport (
    taskreportid SERIAL PRIMARY KEY,
    reportid INTEGER REFERENCES workflow.report(reportid),
    taskname VARCHAR(200),
    description TEXT,
    report TEXT,
    status BOOLEAN,
    UNIQUE(reportid, taskname)
);
CREATE TABLE workflow.viewreport (
    taskreportid INTEGER PRIMARY KEY,
    reportid INTEGER,
    packageid VARCHAR(50),
    entityid INTEGER,
    entityname VARCHAR(2000),
    entitydescription TEXT,
    taskname VARCHAR(200),
    taskdescription TEXT,
    report TEXT,
    status BOOLEAN,
    israster BOOLEAN,
    isvector BOOLEAN,
    sourceloc VARCHAR(2000),
    UNIQUE(reportid, taskname)
);