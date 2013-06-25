--workflow_d

CREATE TABLE workflow_d.package (
packageid varchar(50) PRIMARY KEY,
doi varchar(100),
scope     varchar(50),
identifier integer,
revision integer,
spatialcount smallint NOT NULL DEFAULT -1,
downloaded timestamp,
report text );
CREATE TABLE workflow_d.entity (
id serial PRIMARY KEY,
packageid varchar(50) REFERENCES workflow_d.package(packageid),
entityname varchar(200),
israster boolean NOT NULL DEFAULT FALSE,
isvector boolean NOT NULL DEFAULT FALSE,
entitydescription varchar(1000),
completed timestamp,
storage varchar(200),
mxd varchar(200),
layername varchar(100),
status varchar(500),
report text,
UNIQUE ( packageid, entityname ) );
CREATE TABLE workflow_d.geonis_layer (
id integer PRIMARY KEY REFERENCES workflow_d.entity(id),
packageid varchar(50),
scope     varchar(50),
entityname varchar(200),
entitydescription varchar(2000),
title varchar(1000),
abstract varchar(1000),
purpose varchar(2000),
keywords varchar(1000),
sourceloc varchar(2000),
layername varchar(100),
arcloc varchar(100),
layerid integer);
CREATE TABLE workflow_d.errornotify (packageid varchar(50), contact varchar(200));
CREATE TABLE workflow_d.limit_identifier (identifier varchar(50));

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
report text );
CREATE TABLE workflow.entity (
id serial PRIMARY KEY,
packageid varchar(50) REFERENCES workflow.package(packageid),
entityname varchar(200),
israster boolean NOT NULL DEFAULT FALSE,
isvector boolean NOT NULL DEFAULT FALSE,
entitydescription varchar(1000),
completed timestamp,
storage varchar(200),
mxd varchar(200),
layername varchar(100),
status varchar(500),
report text,
UNIQUE ( packageid, entityname ) );
CREATE TABLE workflow.geonis_layer (
id integer PRIMARY KEY REFERENCES workflow.entity(id),
packageid varchar(50),
scope     varchar(50),
entityname varchar(200),
entitydescription varchar(2000),
title varchar(1000),
abstract varchar(1000),
purpose varchar(2000),
keywords varchar(1000),
sourceloc varchar(2000),
layername varchar(100),
arcloc varchar(100),
layerid integer);
CREATE TABLE workflow.errornotify (packageid varchar(50), contact varchar(200));
CREATE TABLE workflow.limit_identifier (identifier varchar(50));
--dupe tables without defaults, constraints
CREATE TABLE workflow.package_superseded (LIKE workflow.package );
CREATE TABLE workflow.entity_superseded (LIKE workflow.entity );
CREATE TABLE workflow.geonis_layer_superseded (LIKE workflow.geonis_layer );

--for geodb files only (?)
ALTER TABLE geonis_layer ALTER COLUMN abstract TYPE TEXT;