-- WORKFLOW_D --
--package exists, we have not yet counted its spatial nodes 
/*
CREATE OR REPLACE VIEW workflow_d.vw_newpackage AS
 SELECT packageid, scope, identifier, revision FROM package WHERE spatialcount = -1;
--
--package has spatial node(s), but hasn't been downloaded 
CREATE OR REPLACE VIEW workflow_d.vw_newspatialpackage AS
 SELECT packageid, scope, identifier, revision FROM package WHERE spatialcount > 0 AND downloaded is NULL;
--
--this view now not needed, needs to be modded where layerid is null, because layer recs made at mxd add 
CREATE OR REPLACE VIEW workflow_d.vw_stalemapservices AS
 SELECT DISTINCT ent.mxd from entity as ent LEFT OUTER JOIN geonis_layer AS lyr ON ent.id = lyr.id
 WHERE (lyr.layerid = -1 or lyr.layerid is null) AND ent.status like 'Ready%' AND ent.isvector AND ent.mxd is not null;
--
--package has been downloaded, but no entities yet exist 
CREATE OR REPLACE VIEW workflow_d.vw_processqueue AS
 SELECT pack.scope, pack.packageid, pack.downloaded from package AS pack LEFT OUTER JOIN entity AS ent
 ON pack.packageid = ent.packageid WHERE pack.downloaded is not null and ent.packageid is null
 ORDER BY pack.scope; 
--
--entities that didn't complete process 
CREATE OR REPLACE VIEW workflow_d.vw_incompleteentity AS
 SELECT packageid, entityname, israster, isvector, status FROM entity WHERE completed is null;
--get package id of all superseded revs without assembling it. Create this view, then join it in query for superseded
CREATE OR REPLACE VIEW workflow_d.vw_maxrevs as select scope, identifier,  max(revision) as maxrev from package group by scope, identifier;
--
-- view for query layer
CREATE OR REPLACE VIEW workflow_d.vw_publist AS
 SELECT geonis_layer.packageid AS package, geonis_layer.scope AS site_code, geonis_layer.entityname AS entity, geonis_layer.entitydescription AS description, geonis_layer.title, geonis_layer.abstract, geonis_layer.purpose, geonis_layer.keywords, geonis_layer.sourceloc AS source, geonis_layer.layername AS lyrname, geonis_layer.arcloc AS service, geonis_layer.layerid AS lyrid FROM geonis_layer WHERE geonis_layer.layerid <> (-1);
 */
-- WORKFLOW --
--package exists, we have not yet counted its spatial nodes 
CREATE OR REPLACE VIEW workflow.vw_newpackage AS
 SELECT packageid, scope, identifier, revision FROM package WHERE spatialcount = -1;
--
--package has spatial node(s), but hasn't been downloaded 
CREATE OR REPLACE VIEW workflow.vw_newspatialpackage AS
 SELECT packageid, scope, identifier, revision FROM package WHERE spatialcount > 0 AND downloaded is NULL;
--
--this view now not needed, needs to be modded where layerid is null, because layer recs made at mxd add 
CREATE OR REPLACE VIEW workflow.vw_stalemapservices AS 
 SELECT DISTINCT ent.mxd from entity as ent LEFT OUTER JOIN geonis_layer AS lyr ON ent.id = lyr.id WHERE (lyr.layerid = -1 or lyr.layerid is null) AND ent.status like 'Ready%' AND ent.isvector AND ent.mxd is not null;
--
--package has been downloaded, but no entities yet exist 
CREATE OR REPLACE VIEW workflow.vw_processqueue AS 
 SELECT pack.scope, pack.packageid, pack.downloaded from package AS pack LEFT OUTER JOIN entity AS ent ON pack.packageid = ent.packageid WHERE pack.downloaded is not null and ent.packageid is null ORDER BY pack.scope; 
--
--entities that didn't complete process 
CREATE OR REPLACE VIEW workflow.vw_incompleteentity AS
 SELECT packageid, entityname, israster, isvector, status FROM entity WHERE completed is null;
--get package id of all superseded revs without assembling it. Create this view, then join it in query for superseded
CREATE OR REPLACE VIEW workflow.vw_maxrevs as select scope, identifier,  max(revision) as maxrev from package group by scope, identifier;
--
-- view for query layer
CREATE OR REPLACE VIEW workflow.vw_publist AS
 SELECT geonis_layer.packageid AS package, geonis_layer.scope AS site_code, geonis_layer.entityname AS entity, geonis_layer.entitydescription AS description, geonis_layer.title, geonis_layer.abstract, geonis_layer.purpose, geonis_layer.keywords, geonis_layer.sourceloc AS source, geonis_layer.layername AS lyrname, geonis_layer.arcloc AS service, geonis_layer.layerid AS lyrid FROM geonis_layer WHERE geonis_layer.layerid <> (-1);



/* this view works, but not needed. update mxd tool needs to create rec in layer table 
CREATE OR REPLACE VIEW workflow_d.vw_newvectorlayer AS
SELECT  ent.id, ent.packageid, pack.scope, ent.entityname, ent.entitydescription, ent.layername
 FROM workflow_d.entity as ent JOIN workflow_d.package AS pack ON ent.packageid = pack.packageid
 LEFT OUTER JOIN workflow_d.geonis_layer AS lyr ON ent.id = lyr.id
 WHERE lyr.id is null AND ent.status = 'OK' AND ent.isvector AND ent.mxd is not null;
*/


