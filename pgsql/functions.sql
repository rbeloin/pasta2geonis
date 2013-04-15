
CREATE OR REPLACE FUNCTION movesuperseded() RETURNS integer AS $$
/* This function will move any packages where there exists a higher numbered revision into similar tables
   for later processing. It returns the number of packages found to be superseded.
   It relies on the existence of LIKE tables package_superseded, entity_superseded, geonis_layer_superseded, and also the view
   create view workflow.vw_maxrevs as select p2.scope, p2.identifier,  max(p2.revision) as maxrev from workflow.package as p2 group by p2.scope, p2.identifier;
*/
DECLARE packagenum integer;
BEGIN
drop table if exists superseded;
create temporary table superseded as select packageid from workflow.package as p join workflow.vw_maxrevs as m on p.scope = m.scope and p.identifier = m.identifier where p.revision < m.maxrev;
select count(*) into packagenum from superseded;
if packagenum > 0 then
/* package_superseded table; clear, insert */
delete from workflow.package_superseded where packageid in (select packageid from superseded);
insert into workflow.package_superseded select * from workflow.package where packageid in (select packageid from superseded);
/* entity_superseded table; clear, insert */
delete from workflow.entity_superseded where packageid in (select packageid from superseded);
insert into workflow.entity_superseded select * from workflow.entity where packageid in (select packageid from superseded);
/* geonis_layer_superseded table; clear, insert */
delete from workflow.geonis_layer_superseded where packageid in (select packageid from superseded);
insert into workflow.geonis_layer_superseded select * from workflow.geonis_layer where packageid in (select packageid from superseded);
/* now delete from active tables, bottom up because of constraints */
delete from workflow.geonis_layer where packageid in (select packageid from superseded);
delete from workflow.entity where packageid in (select packageid from superseded);
delete from workflow.package where packageid in (select packageid from superseded);
end if;
drop table if exists superseded;
return packagenum;
END; $$ LANGUAGE plpgsql;

