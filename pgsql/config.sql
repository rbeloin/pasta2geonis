
--create table
create table if not exists workflow.wfconfig (
name varchar(50),
strvalue varchar(500) );
--reload table
delete from workflow.wfconfig;
--reset values for workflow production
/*
insert into workflow.wfconfig values
('pathtoenvsettings','C:\Users\ron\Documents\geonis_tests\savedEnv.xml'),
('geodatabase', 'C:\Users\ron\Documents\geonis_tests\geonis.gdb'),
('pathtostylesheets','Z:\docs\local\git\pasta2geonis_sg\stylesheets'),
('pathtorasterdata','C:\Users\ron\Documents\geonis_tests\raster_data'),
('pathtorastermosaicdatasets','C:\Users\ron\Documents\geonis_tests\raster_md.gdb'),
('pathtomapdoc','Z:\docs\local'),
('layerqueryuri','http://maps3.lternet.edu/arcgis/rest/services/Test/VectorData/MapServer/layers?f=json'),
('scratchws','C:\Users\ron\AppData\Local\Temp'),
('schema','workflow'),
('pubconnection',''),
('mapservinfo','VectorData;Test;GEONIS;Test services for vector data'),
('imageservinfo',''),
('datasetscopesuffix','_main'),
('pathtodownloadedpkgs',''),
('pathtoprocesspkgs','');
*/
--reset values for dev env (ron's machine)
insert into workflow.wfconfig values
('pathtoenvsettings','C:\Users\ron\Documents\geonis_tests\savedEnv.xml'),
('geodatabase', 'C:\Users\ron\Documents\geonis_tests\geonis.gdb'),
('pathtostylesheets','Z:\docs\local\git\pasta2geonis_sg\stylesheets'),
('pathtorasterdata','C:\Users\ron\Documents\geonis_tests\raster_data'),
('pathtorastermosaicdatasets','C:\Users\ron\Documents\geonis_tests\raster_md.gdb'),
('pathtomapdoc','Z:\docs\local'),
('layerqueryuri','http://maps3.lternet.edu/arcgis/rest/services/Test/VectorData/MapServer/layers?f=json'),
('scratchws','C:\Users\ron\AppData\Local\Temp'),
('schema','workflow'),
('pubconnection',''),
('mapservinfo','VectorData;Test;GEONIS;Test services for vector data'),
('imageservinfo',''),
('datasetscopesuffix','_main'),
('pathtodownloadedpkgs','Z:\docs\local\geonis_testdata\downloaded_pkgs'),
('pathtoprocesspkgs','Z:\docs\local\geonis_testdata\pkgs');
/*
create table if not exists workflow_d.wfconfig (LIKE workflow.wfconfig);
--reset values for workflow testing
insert into workflow_d.wfconfig values
('pathtoenvsettings','C:\Users\ron\Documents\geonis_tests\savedEnv.xml'),
('geodatabase', 'C:\Users\ron\Documents\geonis_tests\geonis.gdb'),
('pathtostylesheets','Z:\docs\local\git\pasta2geonis_sg\stylesheets'),
('pathtorasterdata','C:\Users\ron\Documents\geonis_tests\raster_data'),
('pathtorastermosaicdatasets','C:\Users\ron\Documents\geonis_tests\raster_md.gdb'),
('pathtomapdoc','Z:\docs\local'),
('layerqueryuri','http://maps3.lternet.edu/arcgis/rest/services/Test/VectorData/MapServer/layers?f=json'),
('scratchws','C:\Users\ron\AppData\Local\Temp'),
('schema','workflow_d'),
('pubconnection',''),
('mapservinfo','VectorData;Test;GEONIS;Test services for vector data'),
('imageservinfo',''),
('datasetscopesuffix','_main'),
('pathtodownloadedpkgs',''),
('pathtoprocesspkgs','');
*/
