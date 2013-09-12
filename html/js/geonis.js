function getPID() {
    var i, item;
    var searchStr = window.location.search;
    if (searchStr.length > 1) {
        searchStr = searchStr.substring(1);
    }
    else {
       return "";
    }
    searchItems = searchStr.split('&');
    for(i = 0; i < searchItems.length; i++) {
        item = searchItems[i].split('=');
        if (item[0] == "packageid") {
            return item[1];
        }
    }
    return "";
}

// Attempts to create links in a block of text which may or may not contain links...
function createLinks(errReport) {
    var regex;
    if (typeof errReport !== 'undefined') {
        regex = /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
        return errReport.replace(regex, "<a href='$1'>$1</a>");
    }
    else {
        return errReport;
    }
}

/**
 * Parse the raw error report which we fetched from the database using the
 * Search service, which has the following pipe-delimited structure:
 * error report | package-report or entity-report | ...
 *    ...JSON string containing various package + entity information
 */
function parseReport(rawReport) {
    var splitPipe = rawReport.split('|');
    report = "<ul><li>" + splitPipe[0].trim();
    report += "</li>";
    return {
        'report': report.replace(/\n/g, '<br />'),
        'reportType': splitPipe[1].trim(),
        'biography': JSON.parse(splitPipe[2].trim())
    };
}

/** 
 * Check the package and entity tables for error reports, and append them to the
 * active error report if found.
 */
function checkTables(biography, report, reportType) {
    var formatted, isPackage, spatialType, service;
    isPackage = (reportType === 'package-report');
    if (isPackage) {
        formatted = {
            'report': report,
            'subject': 'package',
            'service': null
        };
    }
    else {
        if (biography.israster) {
            spatialType = 'raster';
            service = biography.service;  // Not yet implemented!
        }
        else {
            spatialType = 'vector';
            service = biography.service;
        }
        formatted = {
            'report': checkEntity(biography, report, spatialType),
            'subject': spatialType,
            'service': biography.service
        };
    }
    return formatted;
}

/**
 * Check for report entries in the entity table, and append them to its error report.
 */
function checkEntity(biography, report, spatialType) {
    var entityname = (biography['entityname'] === 'None') ?
        'Untitled ' + spatialType + ' data set' : biography['entityname'];
    report = "<span class='entity-name'>" + entityname + "</span> " + report;
    return report;
}

/**
 * Replaces the default "Searching for package..." with a readable 
 * site ID: revision banner.
 */
function generateBanner(pid) {
    var splitPid = pid.split('.');
    var banner = lter[splitPid[0].split('-')[2]].name;
    if (splitPid[1] && splitPid[2]) {
         banner += " #" + splitPid[1] + ", version " + splitPid[2];
    }
    $('#pid').html(banner);
}

/**
 * Determines whether this package was retrieved from the staging
 * (pasta-s.lternet.edu) or live (pasta.lternet.edu) server.
 */
function getServerInfo(biography) {
    var serverInfo;
    if (biography.pasta.indexOf('pasta-s') !== -1) {
        serverInfo = {
            'server': 'staging',
            'baseURL': 'pasta-s.lternet.edu'
        };
    }
    else {
        serverInfo = {
            'server': 'live',
            'baseURL': 'pasta.lternet.edu'
        };
    }
    return serverInfo;
}

/**
 * Adds a sentence at the bottom of the page w/ server + download info
 * e.g., Package knb-lter-and.5030.1 was downloaded from the live server
 * on 2013-07-18 at 18:04:59 MDT.  (With download link.)
 */
function appendServerInfo(serverInfo, biography) {
    var packageLink = "<a href='https://" + serverInfo['baseURL'] + "/package/eml/" +
        biography['packageid'].split('.')[0] + "/" + biography['identifier'] +
        "/" + biography['revision'] + "'>" + biography['packageid'] + "</a>";
    $('#workflow-info').html(
        "Package " + packageLink + " was downloaded from the <a href='https://" +
        serverInfo.baseURL + "'>" + serverInfo.server +
        " server</a> on " + biography['downloaded'].split(' ')[0] + " at " +
        biography['downloaded'].split(' ')[1].split('.')[0] + " MDT."
    );
}

// Fetch a list of other packages from the same site containing spatial data
function fetchSitePackages(siteCode) {
    siteReportUrl = "http://maps3.lternet.edu/arcgis/rest/services/Test/" +
        "queryPackage/MapServer/1/query?where=scope+%3D+%27" +
        siteCode.split('-')[2] + "%27&returnGeometry=true&f=pjson";
    $.getJSON(siteReportUrl, function (response) {
        var i, sitePackages, packageTitleLink;
        var sitePackageArray = [];
        for (i = 0; i < response.features.length; i++) {
            sitePackageArray.push(response.features[i].attributes.packageid);
        }
        sitePackageArray = sitePackageArray.sortNumeric();
        packageTitleLink = $('<a />')
            .attr('href', '#')
            .text("Packages (" + sitePackageArray.length + ")");
        if (sitePackageArray.length) {
            packageTitleLink.click(function () {
                $('#site-report').slideToggle('fast');
            });
        }
        $('#site-report-title').prepend($('<p />').append(packageTitleLink));
        sitePackages = '';
        for (i = 0; i < sitePackageArray.length; i++) {
            sitePackages += '<li><a href="index.html?packageid=' + sitePackageArray[i] + '">' +
                sitePackageArray[i] + '</a></li>';
        }
        if (sitePackageArray.length) {
            $('#site-report').html('<ul>' + sitePackages + '</ul>');
        }
    });
}

Array.prototype.sortNumeric = function () {
    var tempArr = [], n;
    var i, j;
    for (i in this) {
        tempArr[i] = this[i].toString().match(/([^0-9]+)|([0-9]+)/g);
        for (j in tempArr[i]) {
            if (!isNaN(n = parseInt(tempArr[i][j]))){
                tempArr[i][j] = n;
            }
        }
    }
    tempArr.sort(function (x, y) {
        for (var i in x) {
            if (y.length < i || x[i] < y[i]) {
                return -1; // x is longer
            }
            if (x[i] > y[i]) {
                return 1;
            }
        }
        return 0;
    });
    for (i in tempArr) {
        this[i] = tempArr[i].join('');
    }
    return this;
};

Array.prototype.getUnique = function () {
    var u = {}, a = [];
    for(var i = 0, l = this.length; i < l; ++i){
        if(u.hasOwnProperty(this[i])) {
            continue;
        }
        a.push(this[i]);
        u[this[i]] = 1;
    }
    return a;
};

function pluralize(str, count) {
    plural = str + 's';
    return (count == 1 ? str : plural);
}

// Insert reports and section headers into the html document
function writeReports(reports, counter) {
    var packageOk;
    if (counter.package) {
        packageOk = "<p><ul><li>No errors found.</li></p>";
        if (reports.package === packageOk) {
            $('#package-report').html('');
        }
        else {
            $('#package-report').html(reports.package);
        }
    }
    if (counter.vector) {
        $('#vector-banner').show();
        $('#vector-report-header').html(
            '<h3>' + counter.vector + ' vector ' + pluralize('dataset', counter.vector) + '</h3>'
        ).show();
        $('#vector-report').html(reports.vector);
    }
    if (counter.raster) {
        $('#raster-banner').show();
        $('#raster-report-header').html(
            '<h3>' + counter.raster + ' raster ' + pluralize('dataset', counter.raster) + '</h3>'
        ).show();
        $('#raster-report').html(reports.raster);
    }
}

/**
 * Create the buttons linking to the map and image services, and to
 * the lightboxed map and images.
 */
function createServiceButtons(site) {
    var servicesUrl = "http://maps3.lternet.edu/arcgis/rest/services/";
    window.mapInfo.services.map = true;
    var linkToMapService = $("<a />")
        .attr("href", window.mapInfo.mapUrl)
        .append($('<p />')
            .text("Map service")
        );
    $('#map-service').append(linkToMapService).show();
    $.getJSON(window.mapInfo.imageUrl + "?f=pjson&callback=?", function (response) {
        if (!response.error) {
            window.mapInfo.services.image = true;
            /*var linkToImageLightbox = $("<a />")
                .attr("href", "#")
                .text("View image")
                .click(function () {
                    showLightbox(mapInfo, 'image');
                }
            );*/
            var linkToImageService = $("<a />")
                .attr("href", window.mapInfo.imageUrl)
                .text("Image service");
            //$('#view-image').html(linkToImageLightbox).show();
            $('#image-service').append($('<p />').append(linkToImageService)).show();
        }
        else {
            //$('#view-image').hide();
            $('#image-service').hide();
        }
        //$('#linkbar').show();
        $('#service-links').show();
    });
}

// Call the map creator function when user clicks on the "view map" button
function showLightbox(mapInfo, serviceType) {
    mapInfo.serviceType = serviceType;
    dojo.require("esri.map");
    dojo.require("esri.layers.FeatureLayer");
    $('#map-lightbox').lightbox_me({centered: true});
    dojo.addOnLoad(init(mapInfo));
}

// Load an embedded map in response to user clicking on the LTER site grid
function loadMapBlock() {
    var dojoConfig = {parseOnLoad: true};
    dojo.require("dojo.parser");
    dojo.require("dijit.layout.BorderContainer");
    dojo.require("dijit.layout.ContentPane");
    dojo.require("esri.map");
    dojo.require("esri.dijit.Scalebar");
    dojo.addOnLoad(embedInit);
}

/**
 * Fetch layers from the map service, which are grouped into
 * a "stack" of layers, and process the layers.
 * Initially, only the site boundary is shown (if present).
 * Other layers can be shown by clicking on their checkboxes.
 */
function embedInit() {

    // Create the map, centered on the current LTER site
    window.embeddedMap = new esri.Map('map-block', {
        basemap: 'satellite',
        center: [lter[site].coords[1], lter[site].coords[0]],
        zoom: lter[site].zoom || 12,
        sliderStyle: 'small'
    });
    //ArcGIS basemaps: "streets" , "satellite" , "hybrid", "topo", "gray", "oceans", "national-geographic", "osm"

    // Create the layer stack and click handlers for the layer menu
    window.layerStack = new esri.layers.ArcGISDynamicMapServiceLayer(
        mapInfo.mapUrl,
        {id: 'layerStack'}
    );
    dojo.connect(layerStack, 'onLoad', function (layers) {
        var i, layerInfo, layerTitleLink, siteBoundary, layerChecks, checkbox, checkboxLink;
        layerInfo = layers.layerInfos;
        layerTitleLink = $('<a />')
            .attr('href', '#')
            .text("Layers (" + layerInfo.length + ")")
            .click(function () {
                $('#layer-checks').slideToggle('fast');
            });
        $('#layer-checks-title').prepend($('<p />').append(layerTitleLink));
        layerChecks = $('<ul />').appendTo('#layer-checks');
        for (i = 0; i < layerInfo.length; i++) {
            /*checkboxLink = $('<a />')
                .attr('href', '#')
                .click({'index': i}, function (event) {
                    event.preventDefault(event);
                    mapLayerToggle(event, true);
                });*/
            if (layerInfo[i].name === "LTER site boundary") {
                siteBoundary = i;
                checkbox = $('<label />').text('Boundary').addClass('drop-down-font');
                checkbox.prepend($('<input />')
                    .attr('type', 'checkbox')
                    .attr('name', 'checkbox' + i)
                    .attr('id', 'checkbox' + i)
                    .prop('checked', true)
                    .click({'index': i}, function (event) {
                        mapLayerToggle(event, true);
                    })
                );
                layerChecks.prepend($('<li />').append(checkbox));
            }
            else {
                var layerDesc = layerInfo[i].name.split(':');
                checkbox = $('<label />').text(layerDesc[0]).addClass('drop-down-font');
                checkbox.prepend($('<input />')
                    .attr('type', 'checkbox')
                    .attr('name', 'checkbox' + i)
                    .attr('id', 'checkbox' + i)
                    .click({'index': i}, function (event) {
                        mapLayerToggle(event, true);
                    })
                );
                var layerButton = $('<li />').append(checkbox);
                layerChecks.append(layerButton);
            }
        }
        layers.setVisibleLayers([siteBoundary]);
    });

    // Create the image stack and click handlers for the image menu
    $.getJSON(window.mapInfo.imageUrl + "?f=pjson&callback=?", function (response) {
        if (!response.error) {
            var imageParams = new esri.layers.ImageServiceParameters();
            imageParams.noData = 0;
            window.imageStack = new esri.layers.ArcGISImageServiceLayer(
                mapInfo.imageUrl, {
                    id: 'imageStack',
                    imageServiceParameters: imageParams,
                    opacity: 0.75
                }
            );
            window.imageLayer = false;
            dojo.connect(imageStack, 'onLoad', function (images) {
                var i, imageTitleLink, imageChecks;
                imageTitleLink = $('<a />')
                    .attr('href', '#')
                    .text("Images (" + Object.keys(imageData).length + ")")
                    .click(function () {
                        $('#image-checks').slideToggle('fast');
                    });
                $('#image-checks-title').prepend($('<p />').append(imageTitleLink));
                imageChecks = $('<ul />').appendTo('#image-checks');
                $.each(imageData, function () {
                    checkbox = $('<label />').text(this.layername).addClass('drop-down-font');
                    checkbox.prepend($('<input />')
                        .attr('type', 'checkbox')
                        .attr('name', 'checkbox-' + this.layername)
                        .attr('id', 'checkbox-' + this.layername)
                        .click({'layername': this.layername}, function (event) {
                            var visibleImage, mosaicRule;
                            if (embeddedMap.layerIds.indexOf('imageStack') !== -1) {
                                visibleImage =
                                    imageStack.mosaicRule.where.split('=')[1].split('\'')[1];
                            }
                            mosaicRule = new esri.layers.MosaicRule({
                                "method": esri.layers.MosaicRule.METHOD_LOCKRASTER,
                                "ascending": true,
                                "operation": esri.layers.MosaicRule.OPERATION_FIRST,
                                "where": "Name='" + event.data.layername + "'"
                            });
                            imageStack.setMosaicRule(mosaicRule);
                            $(event.target).parents().eq(2).find(':checked').prop('checked', false);
                            $(event.target).prop('checked', true);
                            if (embeddedMap.layerIds.indexOf('imageStack') === -1) {
                                embeddedMap.addLayer(imageStack);
                                window.imageLayer = true;
                            }
                            else if (visibleImage === event.data.layername) {
                                embeddedMap.removeLayer(
                                    embeddedMap.getLayer('imageStack')
                                );
                                $(event.target).parent().children().prop('checked', false);
                                window.imageLayer = false;
                            }
                            $('#active-layers').show();
                            $.each(window.imageData, function () {
                                $('#image' + this.layername).addClass('hidden');
                            });
                            $('#image' + event.data.layername).removeClass('hidden');
                            $('#image' + event.data.layername).trigger('click');
                            if (!window.imageLayer && layerStack.visibleLayers &&
                                layerStack.visibleLayers.length === 1 &&
                                (layerStack.layerInfos[layerStack.visibleLayers[0]].name ===
                                    'LTER site boundary')) {
                                $('#active-layers').hide();
                            }
                        })
                    );
                    imageChecks.append($('<li />').append(checkbox));
                });
            });
        }
        else {
            $('#image-checks-title').html('<a href="#">Images (0)</a>');
        }
    });

    // Once the map is loaded, add layers, resize, and scalebar
    dojo.connect(embeddedMap, 'onLoad', function (theMap) {
        var resizeTimer;
        theMap.addLayer(layerStack);
        var scalebar = new esri.dijit.Scalebar({
            map: theMap,
            srcNodeRef: '#scale',
            scalebarUnit: 'dual'
        });
        $('#scale').append(
            $('.esriScalebar')//.removeClass('scalebar_bottom-left')
        ).show();
        $('#basemap-gallery-container').show();
        require([
            "esri/map", "esri/dijit/BasemapGallery", "esri/arcgis/utils", "dojo/parser",
            "dijit/layout/BorderContainer", "dijit/layout/ContentPane", "dijit/TitlePane",
            "dojo/domReady!"
        ], function(Map, BasemapGallery, arcgisUtils, parser) {
            parser.parse();

            //add the basemap gallery, in this case we'll display maps from ArcGIS.com including bing maps
            var basemapGallery = new BasemapGallery({
                showArcGISBasemaps: true,
                map: embeddedMap
            }, "basemapGallery");
            basemapGallery.startup();

            basemapGallery.on("error", function(msg) {
              console.log("basemap gallery error:  ", msg);
            });
        });
        dojo.connect(dijit.byId('map-block'), 'resize', function () {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(function () {
                map.resize();
                map.reposition();
            }, 500);
        });
    });
}

// Show/hide layers in response to user clicks
function mapLayerToggle(event, isVector) {
    var layer, listItem, layerName, layerDetail, substack;
    var showLayers, layerIndex, isBoundary;
    layer = event.data['index'];
    listItem = $(event.target).parent();
    layerName = listItem.text(); //.split(':')[0];
    if (layerData[layerName]) {
        layerDetail = layerData[layerName].ESRI_OID;
    }
    substack = (isVector) ? layerStack : imageStack;
    showLayers = substack.visibleLayers;
    layerIndex = showLayers.indexOf(layer);
    if (!showLayers.length) {
        layerStack.show();
    }
    if (layerIndex === -1) {
        showLayers.push(layer);
        $(event.target).prop('checked', true);
        $('#active-layers').show();
        $('#layer' + layerDetail).removeClass('hidden');
        $('#layer' + layerDetail).trigger('click');
    }
    else {
        showLayers.splice(layerIndex, 1);
        $(event.target).prop('checked', false);
        $('#layer' + layerDetail).addClass('hidden');
    }
    substack.setVisibleLayers(showLayers);
    if (!substack.visibleLayers.length) {
        substack.hide();
        $('#active-layers').hide();
    }
    if (substack.visibleLayers.length) {
        isBoundary = (layerStack.layerInfos[substack.visibleLayers[0]].name ===
            'LTER site boundary');
        if (substack.visibleLayers.length === 1 && isBoundary &&
            (typeof imageLayer === 'undefined' || !imageLayer)) {
            $('.detail-box').hide();
            $('#active-layers').hide();
        }
    }
}

// Create and display the ArcGIS map inside a lightbox
function init(mapInfo) {
    var mapDiv, layer, serviceLink, imageParams, mapLayer, imageLayer;
    mapDiv = "map";

    // Add onclick handler to the map lightbox close button
    $('#close-map-lightbox').click(function (event) {
        event.preventDefault(event);
        $('#map-lightbox').trigger('close');
        $('#map').empty();
    });

    $('#map-lightbox').show();
    $('#map').show();
    if (mapInfo.serviceType === "map") {
        serviceLink = $("<a />")
            .attr("href", mapInfo.mapUrl)
            .text("Click here to go to the " + mapInfo.site.toUpperCase() + " map service.");
        $('#service-link').html(serviceLink);
        layer = new esri.layers.ArcGISDynamicMapServiceLayer(mapInfo.mapUrl);
    }
    else {
        serviceLink = $("<a />")
            .attr("href", mapInfo.imageUrl)
            .text("Click here to go to the " + mapInfo.site.toUpperCase() + " image service.");
        $('#service-link').html(serviceLink);
        imageParams = new esri.layers.ImageServiceParameters();
        imageParams.noData = 0;
        layer = new esri.layers.ArcGISImageServiceLayer(mapInfo.imageUrl, {
            imageServiceParameters: imageParams,
            opacity: 0.75
        });
    }
    window.map = new esri.Map(mapDiv, {
        basemap: 'satellite',
        center: [lter[site].coords[1], lter[site].coords[0]], // longitude, latitude
        zoom: lter[site].zoom || 12,
        sliderStyle: 'small'
    });
    window.map.addLayer(layer);

    // Now get the other layers for this site
    if (mapInfo.services.map) {
        mapLayer = new esri.layers.ArcGISDynamicMapServiceLayer(mapInfo.mapUrl);
    }
    if (mapInfo.services.image) {
        imageParams = new esri.layers.ImageServiceParameters();
        imageParams.noData = 0;
        imageLayer = new esri.layers.ArcGISImageServiceLayer(mapInfo.imageUrl, {
            imageServiceParameters: imageParams,
            opacity: 0.75
        });
    }
}

function fetchVectors() {
    $.getJSON(mapInfo.entityUrl, function (response) {
        $.each(response.features, function () {
            layerData[this.attributes.layername] = {
                'packageid': this.attributes.packageid,
                'title': this.attributes.title,
                'entityname': this.attributes.entityname,
                'abstract': this.attributes.abstract,
                'sourceloc': this.attributes.sourceloc,
                'ESRI_OID': this.attributes.ESRI_OID,
                'entitydescription': this.attributes.entitydescription
            };
            var packageid =
                this.attributes.packageid.split('.').slice(1, 3).join('.');
            var title = shorten(this.attributes.entitydescription);
            var abstract = shorten(this.attributes.abstract);
            var entityname = shorten(this.attributes.entityname);
            var layerID = this.attributes.ESRI_OID;
            var fullTitle = $('<li class="detail-title" />').text(this.attributes.title);
            var fullSourceloc = $('<li class="detail-sourceloc" />').append($('<a />')
                .attr('href', this.attributes.sourceloc)
                .text('Download')
            );
            var fullAbstract = $('<li />').append(
                $('<p />').text(this.attributes.abstract)
            );
            var fullEntityname = $('<li />').append(
                'Entity name: ' + this.attributes.entityname
            );
            var fullLayername = $('<li />').append(
                'Layer/object name: ' + this.attributes.layername
            );
            var fullEntitydescription = $('<li />').append(
                $('<p />').text(this.attributes.entitydescription)
            );
            var row = $('<tr />')
                .attr('id', 'layer' + layerID)
                .append($('<td />').text(this.attributes.layername))
                .append($('<td />').text(packageid))
                .append($('<td />').text(entityname))
                .append($('<td />').text(title))
                .click(function (event) {
                    var details = $('#layer-detail-row-' + layerID);
                    if (!details.length) {
                        $('.detail-box:visible').hide();
                        $(event.target).parent().after(
                            $('<tr class="detail-box" />')
                                .attr('id', 'layer-detail-row-' + layerID)
                                .append($('<td />')
                                    .attr('colspan', 4)
                                    .append($('<div />')
                                        .attr('id', 'detailText' + layerID)
                                        .append($('<img />')
                                            .attr('src', 'images/close-button.png')
                                            .attr('alt', 'Close')
                                            .attr('title', 'Close')
                                            .click(function () {
                                                $('#layer' + layerID).trigger('click');
                                            })
                                        )
                                    )
                                )
                        );
                        var detailText = $('<ul />').appendTo($('#detailText' + layerID));
                        detailText.append(fullTitle);
                        detailText.append(fullEntityname);
                        detailText.append(fullLayername);
                        detailText.append(fullSourceloc);
                        detailText.append(fullEntitydescription);
                        //detailText.append(fullAbstract);
                    }
                    else {
                        if ($('.detail-box:visible').length === 1 && details.is(':visible')) {
                            details.hide();
                        }
                        else if ($('.detail-box:visible').length > 1 && details.is(':visible')) {
                            $('.detail-box:visible').hide();
                        }
                        else if ($('.detail-box:visible').length === 1 && !details.is(':visible')) {
                            $('.detail-box:visible').hide();
                            details.show();
                        }
                        else {
                            details.show();
                        }
                    }
                })
                .hover(
                    function () {
                        $(this).css('background-color', '#CEECF5');
                        $(this).css('cursor', 'pointer');
                    },
                    function () {
                        $(this).css('background-color', '#FFF');
                        $(this).css('cursor', 'default');
                    }
                )
                .addClass('hidden');
            $('#active-layers tbody').append(row);
            function shorten(data) {
                return (data.length < 65) ? data : data.slice(0, 64) + '...';
            }
        });
    });
}

function fetchRasters() {
    $.getJSON(mapInfo.rasterEntityUrl, function (response) {
        $.each(response.features, function () {
            window.imageData[this.attributes.lyrname] = {
                'packageid': this.attributes.packageid,
                'ESRI_OID': this.attributes.id,
                'entityname': this.attributes.entityname,
                'layername': this.attributes.lyrname
            };
            var packageid =
                this.attributes.packageid.split('.').slice(1, 3).join('.');
            var title = shorten(this.attributes.title);
            var abstract = shorten(this.attributes.abstract);
            var entityname = shorten(this.attributes.entityname);
            var layerID = this.attributes.lyrname;
            var fullTitle = $('<li class="detail-title" />').text(this.attributes.title);
            var fullSourceloc = $('<li class="detail-sourceloc" />').append($('<a />')
                .attr('href', this.attributes.sourceloc)
                .text('Download')
            );
            var fullAbstract = $('<li />').append(
                $('<p />').text(this.attributes.abstract)
            );
            var fullEntityname = $('<li />').append(
                'Entity name: ' + this.attributes.entityname
            );
            var fullLayername = $('<li />').append(
                'Layer/object name: ' + this.attributes.lyrname
            );
            var fullEntitydescription = $('<li />').append(
                $('<p />').text(this.attributes.entitydescription)
            );
            var row = $('<tr />')
                .attr('id', 'image' + layerID)
                .append($('<td />').text(this.attributes.lyrname))
                .append($('<td />').text(packageid))
                .append($('<td />').text(entityname))
                .append($('<td />').text(title))
                .click(function (event) {
                    var details = $('#image-detail-row-' + layerID);
                    if (!details.length) {
                        $('.detail-box:visible').hide();
                        $(event.target).parent().after(
                            $('<tr class="detail-box" />')
                                .attr('id', 'image-detail-row-' + layerID)
                                .append($('<td />')
                                    .attr('colspan', 4)
                                    .append($('<div />')
                                        .attr('id', 'detailText' + layerID)
                                        .append($('<img />')
                                            .attr('src', 'images/close-button.png')
                                            .attr('alt', 'Close')
                                            .attr('title', 'Close')
                                            .click(function () {
                                                $('#image' + layerID).trigger('click');
                                            })
                                        )
                                    )
                                )
                        );
                        var detailText = $('<ul />').appendTo($('#detailText' + layerID));
                        detailText.append(fullTitle);
                        detailText.append(fullEntityname);
                        detailText.append(fullLayername);
                        detailText.append(fullSourceloc);
                        detailText.append(fullEntitydescription);
                    }
                    else {
                        if ($('.detail-box:visible').length === 1 && details.is(':visible')) {
                            details.hide();
                        }
                        else if ($('.detail-box:visible').length > 1 && details.is(':visible')) {
                            $('.detail-box:visible').hide();
                        }
                        else if ($('.detail-box:visible').length === 1 && !details.is(':visible')) {
                            $('.detail-box:visible').hide();
                            details.show();
                        }
                        else {
                            details.show();
                        }
                    }
                })
                .hover(
                    function () {
                        $(this).css('background-color', '#CEECF5');
                        $(this).css('cursor', 'pointer');
                    },
                    function () {
                        $(this).css('background-color', '#FFF');
                        $(this).css('cursor', 'default');
                    }
                )
                .addClass('hidden');
            $('#active-layers tbody').append(row);
            function shorten(data) {
                return (data.length < 65) ? data : data.slice(0, 64) + '...';
            }
        });
    });
}

var lter = {
    "and": {
        "coords": [44.24, -122.18],
        "name": "Andrews Forest LTER",
        "zoom": 12
    },
    "arc": {
        "coords": [68.5, -149.1],
        "name": "Arctic LTER",
        "zoom": 9
    },
    "bes": {
        "coords": [39.36, -76.82],
        "name": "Baltimore Ecosystem Study",
        "zoom": 11
    },
    "bnz": {
        "coords": [64.86, -147.85],
        "name": "Bonanza Creek LTER",
        "zoom": 8
    },
    "cce": {
        "coords": [32.87, -122.28],
        "name": "California Current Ecosystem LTER",
        "zoom": 6
    },
    "cdr": {
        "coords": [45.4, -93.2],
        "name": "Cedar Creek LTER"
    },
    "cap": {
        "coords": [33.43, -111.93],
        "name": "Central Arizona - Phoenix LTER",
        "zoom": 8
    },
    "cwt": {
        "coords": [35.07, -83.5],
        "name": "Coweeta LTER"
    },
    "fce": {
        "coords": [25.47, -80.85],
        "name": "Florida Coastal Everglades LTER",
        "zoom": 8
    },
    "gce": {
        "coords": [31.43, -81.37],
        "name": "Georgia Coastal Ecosystems LTER",
        "zoom": 9
    },
    "hfr": {
        "coords": [42.53, -72.19],
        "name": "Harvard Forest LTER",
        "zoom": 11
    },
    "hbr": {
        "coords": [43.94, -71.75],
        "name": "Hubbard Brook LTER"
    },
    "jrn": {
        "coords": [32.62, -106.74],
        "name": "Jornada Basin LTER",
        "zoom": 10
    },
    "kbs": {
        "coords": [42.4, -85.4],
        "name": "Kellogg Biological Station LTER",
        "zoom": 13
    },
    "knz": {
        "coords": [39.09, -96.58],
        "name": "Konza Prairie LTER"
    },
    "lno": {
        "coords": [35.08, -106.62],
        "name": "LTER Network Office"
    },
    "luq": {
        "coords": [18.3, -65.8],
        "name": "Luquillo LTER"
    },
    "mcm": {
        "coords": [-77.51, 162.52],
        "name": "McMurdo Dry Valleys LTER",
        "zoom": 7
    },
    "mcr": {
        "coords": [-17.49, -149.83],
        "name": "Moorea Coral Reef LTER",
        "zoom": 11
    },
    "nwt": {
        "coords": [40.04, -105.59],
        "name": "Niwot Ridge LTER"
    },
    "ntl": {
        "coords": [46.01, -89.67],
        "name": "North Temperate Lakes LTER",
        "zoom": 9
    },
    "pal": {
        "coords": [-64.77, -64.05],
        "name": "Palmer Antarctica LTER",
        "zoom": 4
    },
    "pie": {
        "coords": [42.76, -70.89],
        "name": "Plum Island Ecosystem LTER",
        "zoom": 9
    },
    "sbc": {
        "coords": [34.41, -119.84],
        "name": "Santa Barbara Coastal LTER",
        "zoom": 8
    },
    "sev": {
        "coords": [34.35, -106.88],
        "name": "Sevilleta LTER",
        "zoom": 10
    },
    "sgs": {
        "coords": [40.83, -104.72],
        "name": "Shortgrass Steppe",
        "zoom": 12
    },
    "vcr": {
        "coords": [37.28, -75.91],
        "name": "Virginia Coast Reserve LTER",
        "zoom": 8
    }
};

var GEONIS = (function () {
    $(window).load(function () {
        var welcomeMessage, servicesUrl, reportUrl, siteReportUrl, siteCode, entities;
        var headerHeight = $('#header').height();
        var leftbarWidth = $('#leftbar-wrapper').width();
        var lterlinksWidth = $('.sidebar').width();
        $(window).on('resize', function () {
            $('#map-block')
                .css('height', $(window).height() - headerHeight)
                .css('width', $(window).width() - lterlinksWidth - leftbarWidth);
            $('#active-layers')
                .css('width', $(window).width() - lterlinksWidth - leftbarWidth);
            $('.leftbar-menu').css(
                'height',
                $(window).height() - headerHeight - 60
            );
            midWidth = $(window).width() - lterlinksWidth - leftbarWidth - 30;
            $('#report-wrapper')
                .css('width', midWidth)
                .css('max-height', $(window).height() - headerHeight - 30);
            $('.banner').each(function() {
                $(this).css('width', midWidth);
            });
            $('#welcome-message').css('width', $(window).width() - lterlinksWidth - 40);
        });
        $('#map-block')
            .css('height', $(window).height() - headerHeight)
            .css('width', $(window).width() - lterlinksWidth - leftbarWidth);
        pid = getPID();
        siteCode = pid.split('.')[0];
        site = siteCode.split('-')[2];
        $('#' + site).addClass('selected');
        $('.leftbar-menu').css(
            'height',
            $(window).height() - headerHeight - 60
        );
        servicesUrl = "http://maps3.lternet.edu/arcgis/rest/services/";
        window.mapInfo = {
            'site': site,
            'services': {'map': true, 'image': true},
            'mapUrl': servicesUrl + "Test/" + site + "_layers/MapServer",
            'imageUrl': servicesUrl + "ImageTest/" + site + "_mosaic/ImageServer",
            'entityUrl': servicesUrl + "Test/queryGeonisLayer/MapServer/1/query?" +
                "where=scope+%3D+%27" + site + "%27&returnGeometry=true&" +
                "outFields=*&f=pjson&callback=?",
            'rasterEntityUrl': servicesUrl + "ImageTest/queryRaster/MapServer/1/query?" +
                "where=packageid+like+%27knb-lter-" + site + "%%%27&returnGeometry=true" +
                "&outFields=*&f=pjson&callback=?"
        };
        if (!pid) {
            $('#map-block').hide();
            $('#pid').html("Welcome to GeoNIS!");
            $('#leftbar-wrapper').hide();
            $('#welcome-message').show().css('width', $(window).width() - lterlinksWidth - 40);
            return;
        }
        else if (!pid.split('.')[1] || !pid.split('.')[2]) {
            generateBanner(pid);
            $('#geonis').fadeIn('slow');
            $('#active-layers')
                .css('width', $(window).width() - lterlinksWidth - leftbarWidth)
                .css('left', leftbarWidth);
            $('#package-report').hide();
            $('#workflow-info').hide();
            $('.banner').css('border', 'none');
            createServiceButtons(site);
            loadMapBlock();
            window.layerData = {};
            window.imageData = {};
            fetchVectors();
            fetchRasters();
        }
        else {
            generateBanner(pid);
            $('#geonis').fadeIn('slow');
            $('#pid').css('font-size', '125%');
            leftbarWidth = $('#leftbar-wrapper').width();
            lterlinksWidth = $('.sidebar').width();
            $('#site-report').show();
            $('#map-block').hide();
            midWidth = $(window).width() - lterlinksWidth - leftbarWidth - 30;  // -2 for borders, -15 for scrollbar
            //console.log($(window).width() + ' ' + lterlinksWidth + ' ' + leftbarWidth + ' ' + $(document).width());
            $('#report-wrapper')
                .show()
                .css('width', midWidth)
                .css('max-height', $(window).height() - headerHeight - 30);
            $('.banner').each(function() {
                $(this).css('width', midWidth);
            });
            $('#layer-checks-title').hide();
            $('#image-checks-title').hide();
            createServiceButtons(site);
            window.packageReports = [];
            window.vectorReports = {};
            window.rasterReports = {};

            var packageUrl = "http://maps3.lternet.edu/arcgis/rest/services/Test/" +
                "queryPackageDetails/MapServer/1/query?where=packageid+%3D+%27" +
                pid + "%27&outFields=*&returnGeometry=true&f=pjson";
            $.getJSON(packageUrl, function (response) {
                $.each(response.features, function () {
                    var purpose = (!this.attributes.purpose) ? '' : this.attributes.purpose;
                    var keywords = (!this.attributes.keywords) ?  '' : this.attributes.keywords;
                    var abstract = (!this.attributes.abstract) ? '' : this.attributes.abstract;
                    var packageHeaders = $('<ul />').prependTo($('#package-report'));
                    packageHeaders.append($('<li />')
                        .addClass('package-title')
                        .text(this.attributes.packageid + ': ' + this.attributes.title));
                    packageHeaders.append($('<li />')
                        .append($('<a />')
                            .attr('href', this.attributes.sourceloc)
                            .text('Download package')
                        )
                    );
                    packageHeaders.append($('<li />').text('Purpose: ' + purpose));
                    packageHeaders.append($('<li />').text('Keywords: ' + keywords));
                    packageHeaders.append($('<li />').text('Abstract: ' + abstract));
                    //packageHeaders.append($('<li />').text(this.attributes.downloaded));
                    //packageHeaders.append($('<li />').addClass('package-title').text('GeoNIS reports:'));
                    var summaryReport = this.attributes.report.split(' | ')[0];
                    packageHeaders.append($('<hr />'));
                    packageHeaders.append($('<li />').addClass('package-title').text('GeoNIS package report summary: ' + summaryReport));
                });
            });

            // Fetch detailed reports from viewreport using viewreport query layer
            var viewReportUrl = "http://maps3.lternet.edu/arcgis/rest/services/Test/" +
                "viewreport/MapServer/1/query?where=packageid+%3D+%27" + pid +
                "%27&returnGeometry=true&outFields=*&f=pjson";
            $.getJSON(viewReportUrl, function (response) {
                $.each(response.features, function() {
                    if (this.attributes.entityid === null) {
                        packageReports.push(this.attributes);
                    }
                    else if (this.attributes.isvector) {
                        if (vectorReports[this.attributes.entityid]) {
                            vectorReports[this.attributes.entityid].push(this.attributes);
                        }
                        else {
                            vectorReports[this.attributes.entityid] = [this.attributes];
                        }
                    }
                    else if (this.attributes.israster) {
                        if (rasterReports[this.attributes.entityid]) {
                            rasterReports[this.attributes.entityid].push(this.attributes);
                        }
                        else {
                            rasterReports[this.attributes.entityid] = [this.attributes];
                        }

                    }
                });
                if (packageReports.length) {
                    $('#package-report').append($('<table />')
                        .attr('id', 'package-report-table')
                        .attr('class', 'report-table')
                        .append($('<tr />')
                            .append($('<th />').text("Task description"))
                            .append($('<th />').text("Report"))
                            .append($('<th />').text("Status"))
                        )
                    );
                    $.each(packageReports, function () {
                        var reportText = this.report || '';
                        var statusText = (this.status) ? 'Complete' : 'Error';
                        $('#package-report-table').append($('<tr />')
                            .append($('<td />').text(this.taskdescription))
                            .append($('<td />').text(reportText))
                            .append($('<td />').text(statusText))
                        );
                    });
                }
                if (!$.isEmptyObject(vectorReports)) {
                    var numVectors = Object.keys(vectorReports).length;
                    $('#vector-banner').show();
                    $('#vector-report-header').append($('<h3 />')
                        .text(numVectors + ' vector ' + pluralize('dataset', numVectors))
                    ).show();
                    $('#vector-report').append($('<ul />').attr('id', 'vector-entities'));
                    $.each(vectorReports, function () {
                        $('#vector-entities').prepend($('<li />')
                            .addClass('entity-name')
                            .attr('id', 'entity-' + this[0].entityid)
                            .text(this[0].entityname)
                            .css('cursor', 'pointer')
                            .click(function (event) {
                                var isSelected = $(event.target).hasClass('selected');
                                $('.report-wrapper').hide();
                                $(event.target).parent().children().removeClass('selected');
                                if (!isSelected) {
                                    $('#report-wrapper-' + this.id.split('-')[1]).fadeIn('fast');
                                    $(event.target).addClass('selected');
                                }
                            })
                        );
                        var entityReportSummary = (!this[0].jsonreport) ? '' : this[0].jsonreport.split(' | ')[0];
                        $('#vector-entities').append($('<li />')
                            .append($('<div />')
                                .hide()
                                .addClass('report-wrapper')
                                .attr('id', 'report-wrapper-' + this[0].entityid)
                                .append($('<ul />')
                                    .append($('<li />')
                                        .addClass('report-table-header')
                                        .text('Entity name: ' + this[0].entityname)
                                    )
                                    .append($('<li />')
                                        .text(this[0].entitydescription)
                                    )
                                    .append($('<hr />'))
                                    .append($('<li />')
                                        .addClass('report-table-header')
                                        .text('GeoNIS entity report summary: ' + entityReportSummary)
                                    )
                                )
                                .append($('<table />')
                                    .attr('id', 'report-' + this[0].entityid)
                                    .attr('class', 'report-table')
                                    .append($('<tr />')
                                        .append($('<th />').text("Task description"))
                                        .append($('<th />').text("Report"))
                                        .append($('<th />').text("Status"))
                                    )
                                )
                            )
                        );
                        $.each(this, function () {
                            var reportText = this.report || '';
                            var statusText = (this.status) ? 'Complete' : 'Error';
                            $('#report-' + this.entityid).append($('<tr />')
                                .append($('<td />').text(this.taskdescription))
                                .append($('<td />').text(reportText))
                                .append($('<td />').text(statusText))
                            );
                        });
                    });
                }
                if (!$.isEmptyObject(rasterReports)) {
                    var numRasters = Object.keys(rasterReports).length;
                    $('#raster-banner').show();
                    $('#raster-report-header').append($('<h3 />')
                        .text(numRasters + ' raster ' + pluralize('dataset', numRasters))
                    ).show();
                    $('#raster-report').append($('<ul />').attr('id', 'raster-entities'));
                    $.each(rasterReports, function () {
                        $('#raster-entities').prepend($('<li />')
                            .addClass('entity-name')
                            .attr('id', 'entity-' + this[0].entityid)
                            .css('cursor', 'pointer')
                            .text(this[0].entityname)
                            .click(function (event) {
                                var isSelected = $(event.target).hasClass('selected');
                                $('.report-wrapper').hide();
                                $(event.target).parent().children().removeClass('selected');
                                if (!isSelected) {
                                    $('#report-wrapper-' + this.id.split('-')[1]).fadeIn('fast');
                                    $(event.target).addClass('selected');
                                }
                            })
                        );
                        var entityReportSummary = (!this[0].jsonreport) ? '' : this[0].jsonreport.split(' | ')[0];
                        $('#raster-entities').append($('<li />')
                            .append($('<div />')
                                .hide()
                                .addClass('report-wrapper')
                                .attr('id', 'report-wrapper-' + this[0].entityid)
                                .append($('<ul />')
                                    .append($('<li />')
                                        .addClass('report-table-header')
                                        .text('Entity name: ' + this[0].entityname)
                                    )
                                    .append($('<li />')
                                        .text(this[0].entitydescription)
                                    )
                                    .append($('<hr />'))
                                    .append($('<li />')
                                        .addClass('report-table-header')
                                        .text('GeoNIS entity report summary: ' + entityReportSummary)
                                    )
                                )
                                .append($('<table />')
                                    .attr('id', 'report-' + this[0].entityid)
                                    .attr('class', 'report-table')
                                    .append($('<tr />')
                                        .append($('<th />').text("Task description"))
                                        .append($('<th />').text("Report"))
                                        .append($('<th />').text("Status"))
                                    )
                                )
                            )
                        );
                        $.each(this, function () {
                            var reportText = this.report || '';
                            var statusText = (this.status) ? 'Complete' : 'Error';
                            $('#report-' + this.entityid).append($('<tr />')
                                .append($('<td />').text(this.taskdescription))
                                .append($('<td />').text(reportText))
                                .append($('<td />').text(statusText))
                            );
                        });
                    });
                }
            });
        }

        // Other data sets from the same site
        fetchSitePackages(siteCode);
    });
})();