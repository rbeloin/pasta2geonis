
/* package exists, we have not yet counted its spatial nodes 
CREATE VIEW workflow_d.vw_newpackage AS
SELECT packageid, scope, identifier, revision FROM workflow_d.package WHERE spatialcount = -1;
*/
/* package has spatial node(s), but hasn't been downloaded 
CREATE VIEW workflow_d.vw_newspatialpackage AS
SELECT packageid, scope, identifier, revision FROM workflow_d.package
 WHERE spatialcount > 0 AND downloaded is NULL;
*/

/* this view now not needed, needs to be modded where layerid is null, because layer recs made at mxd add 
CREATE VIEW workflow_d.vw_stalemapservices AS
SELECT DISTINCT ent.mxd from workflow_d.entity as ent LEFT OUTER JOIN workflow_d.geonis_layer AS lyr ON ent.id = lyr.id
WHERE (lyr.layerid = -1 or lyr.layerid is null) AND ent.status like 'Ready%' AND ent.isvector AND ent.mxd is not null;
*/

/* package has been downloaded, but no entities yet exist 
CREATE VIEW workflow_d.vw_processqueue AS
SELECT pack.scope, pack.packageid, pack.downloaded from workflow_d.package AS pack LEFT OUTER JOIN workflow_d.entity AS ent
ON pack.packageid = ent.packageid WHERE pack.downloaded is not null and ent.packageid is null
ORDER BY pack.scope; 
*/

/* entities that didn't complete process 
CREATE VIEW workflow_d.vw_incompleteentity AS
SELECT packageid, entityname, israster, isvector, status FROM workflow_d.entity
WHERE completed is null;
*/

/* this view works, but not needed. update mxd tool needs to create rec in layer table 
CREATE VIEW workflow_d.vw_newvectorlayer AS
SELECT  ent.id, ent.packageid, pack.scope, ent.entityname, ent.entitydescription, ent.layername
 FROM workflow_d.entity as ent JOIN workflow_d.package AS pack ON ent.packageid = pack.packageid
 LEFT OUTER JOIN workflow_d.geonis_layer AS lyr ON ent.id = lyr.id
 WHERE lyr.id is null AND ent.status = 'OK' AND ent.isvector AND ent.mxd is not null;
*/

/* this is easier, gets package id of all superseded revs without assembling it. Create this view, then join it in 
create view workflow.vw_maxrevs as select p2.scope, p2.identifier,  max(p2.revision) as maxrev from workflow.package as p2 group by p2.scope, p2.identifier;
*/