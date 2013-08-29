--create table
create table if not exists workflow.wfconfig (
name varchar(50),
strvalue varchar(500) );
--reload table
delete from workflow.wfconfig;
--reset values for workflow production
insert into workflow.wfconfig values
('pathtoenvsettings','C:\pasta2geonis\savedEnv.xml'),
#('geodatabase', 'C:\pasta2geonis\geonisOnMaps3.sde'),
('geodatabase', 'Database Connections\Connection to Maps3.sde'),
('pathtostylesheets','C:\pasta2geonis\stylesheets'),
('pathtorasterdata','C:\pasta2geonis\Gis_data\Raster_raw'),
('pathtorastermosaicdatasets','C:\pasta2geonis\Gis_data\Raster_md.gdb'),
('pathtomapdoc','C:\pasta2geonis\Arcmap_mxd'),
('layerqueryuri','http://maps3.lternet.edu/arcgis/rest/services/%s/%s/MapServer/layers?f=json'),
('scratchws','C:\Temp'),
('schema','workflow'),
('mapservinfo','placeholder;VectorData;GEONIS;GEONIS services for vector data'),
('mapservsuffix','_layers'),
('imageservinfo',''),
('datasetscopesuffix','_main'),
('pathtodownloadedpkgs','C:\Temp\pasta_pkg'),
('pathtoprocesspkgs','C:\Temp\valid_pkg'),
('emailgroup','rbeloin@me.com;rmbeloin@gmail.com'),
('errorquery','http://maps3.lternet.edu/arcgis/rest/services/VectorData/Search/MapServer/2/query?where=packageid=''%s''&outFields=report&f=html'),
('pastaurl','https://pasta.lternet.edu');
/*
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
('pathtoprocesspkgs','Z:\docs\local\geonis_testdata\pkgs'),
('emailgroup','rbeloin@me.com;rmbeloin@gmail.com');
*/
create table if not exists workflow_d.wfconfig (LIKE workflow.wfconfig);
--reset values for workflow testing
delete from workflow_d.wfconfig;
insert into workflow_d.wfconfig values
('pathtoenvsettings','C:\pasta2geonis\savedEnv.xml'),
#('geodatabase', 'C:\pasta2geonis\geonisOnMaps3.sde'),
('geodatabase', 'Database Connections\Connection to Maps3.sde'),
('pathtostylesheets','C:\pasta2geonis\stylesheets'),
('pathtorasterdata','C:\pasta2geonis\Gis_data\Raster_raw_test'),
('pathtorastermosaicdatasets','C:\pasta2geonis\Gis_data\Raster_md_test.gdb'),
('pathtomapdoc','C:\pasta2geonis\Arcmap_mxd_test'),
('layerqueryuri','http://maps3.lternet.edu/arcgis/rest/services/%s/%s/MapServer/layers?f=json'),
('scratchws','C:\Temp'),
('schema','workflow_d'),
('mapservinfo','placeholder;Test;Test;Test services for vector data'),
('mapservsuffix','_layers'),
('imageservinfo',''),
('datasetscopesuffix','_test'),
('pathtodownloadedpkgs','C:\Temp\pasta_pkg_test'),
('pathtoprocesspkgs','C:\Temp\valid_pkg_test'),
('emailgroup','rbeloin@me.com;rmbeloin@gmail.com'),
('errorquery','http://maps3.lternet.edu/arcgis/rest/services/Test/Search/MapServer/2/query?where=packageid=''%s''&outFields=report&f=html'),
('pastaurl','https://pasta.lternet.edu');
