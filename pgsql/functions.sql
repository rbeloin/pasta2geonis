
CREATE OR REPLACE FUNCTION workflow.movesuperseded() RETURNS integer AS $$
/* This function will move any packages where there exists a higher numbered revision into similar tables
   for later processing. It returns the number of packages found to be superseded.
   Function uses unqualified table names, therefore you must set search_path to select between
   workflow_d and workflow.
   It relies on the existence of LIKE tables package_superseded, entity_superseded, geonis_layer_superseded, and also the view
   create view vw_maxrevs as select p2.scope, p2.identifier,  max(p2.revision) as maxrev from package as p2 group by p2.scope, p2.identifier;
*/
DECLARE packagenum integer;
BEGIN
drop table if exists superseded;
create temporary table superseded as select packageid from package as p join vw_maxrevs as m on p.scope = m.scope and p.identifier = m.identifier where p.revision < m.maxrev;
select count(*) into packagenum from superseded;
if packagenum > 0 then
/* package_superseded table; clear, insert */
delete from package_superseded where packageid in (select packageid from superseded);
insert into package_superseded select * from package where packageid in (select packageid from superseded);
/* entity_superseded table; clear, insert */
delete from entity_superseded where packageid in (select packageid from superseded);
insert into entity_superseded select * from entity where packageid in (select packageid from superseded);
/* geonis_layer_superseded table; clear, insert */
delete from geonis_layer_superseded where packageid in (select packageid from superseded);
insert into geonis_layer_superseded select * from geonis_layer where packageid in (select packageid from superseded);
/* now delete from active tables, bottom up because of constraints */
delete from geonis_layer where packageid in (select packageid from superseded);
delete from entity where packageid in (select packageid from superseded);
delete from package where packageid in (select packageid from superseded);
end if;
drop table if exists superseded;
return packagenum;
END; $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION workflow.addpackageerrorreport(pkgid varchar(50), contact varchar(150), rep text) RETURNS void AS $$
BEGIN
update package set report = rep where packageid = pkgid;
insert into errornotify values (pkgid, contact);
END; $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION workflow.addentityerrorreport(pkgid varchar(50), name varchar(50), contact varchar(150), rep text) RETURNS void AS $$
BEGIN
update entity set report = rep where packageid = pkgid and entityname = name;
insert into errornotify values (pkgid, contact);
END; $$ LANGUAGE plpgsql;

