
--create table
create table if not exists workflow.wfconfig (
name varchar(50),
strvalue varchar(500) );
--reload table
delete from workflow.wfconfig;
--reset values for workflow production
/*
insert into workflow.wfconfig values
('pathtoenvsettings','C:\pasta2geonis\savedEnv.xml'),
('geodatabase', 'C:\pasta2geonis\geonisOnMaps3.sde'),
('pathtostylesheets','C:\pasta2geonis\stylesheets'),
('pathtorasterdata','C:\pasta2geonis\Gis_data\Raster_raw'),
('pathtorastermosaicdatasets','C:\pasta2geonis\Gis_data\Raster_md.gdb'),
('pathtomapdoc','C:\pasta2geonis'),
('layerqueryuri','http://maps3.lternet.edu/arcgis/rest/services/%s/%s/MapServer/layers?f=json'),
('scratchws','C:\Temp'),
('schema','workflow'),
('mapservinfo','placeholder;VectorData;GEONIS;GEONIS services for vector data'),
('mapservsuffix','_layers'),
('imageservinfo',''),
('datasetscopesuffix','_main'),
('pathtodownloadedpkgs','C:\Temp'),
('pathtoprocesspkgs','C:\Temp');
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
('mapservinfo','placeholder;Test;GEONIS;Test services for vector data'),
('mapservsuffix','_layers'),
('imageservinfo',''),
('datasetscopesuffix','_main'),
('pathtodownloadedpkgs','Z:\docs\local\geonis_testdata\downloaded_pkgs'),
('pathtoprocesspkgs','Z:\docs\local\geonis_testdata\pkgs');
/*
create table if not exists workflow_d.wfconfig (LIKE workflow.wfconfig);
--reset values for workflow testing
insert into workflow_d.wfconfig values
('pathtoenvsettings','C:\pasta2geonis\savedEnv.xml'),
('geodatabase', 'C:\pasta2geonis\geonisOnMaps3.sde'),
('pathtostylesheets','C:\pasta2geonis\stylesheets'),
('pathtorasterdata','C:\pasta2geonis\Gis_data\Raster_raw_test'),
('pathtorastermosaicdatasets','C:\pasta2geonis\Gis_data\Raster_md_test.gdb'),
('pathtomapdoc','C:\pasta2geonis\test_mxds'),
('layerqueryuri','http://maps3.lternet.edu/arcgis/rest/services/%s/%s/MapServer/layers?f=json'),
('scratchws','C:\Temp'),
('schema','workflow'),
('mapservinfo','placeholder;Test;Test;Test services for vector data'),
('mapservsuffix','_layers'),
('imageservinfo',''),
('datasetscopesuffix','_test'),
('pathtodownloadedpkgs','C:\Temp'),
('pathtoprocesspkgs','C:\Temp');
*/
