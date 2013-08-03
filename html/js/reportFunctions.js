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
        "Search/MapServer/2/query?where=packageid+like+%27" + siteCode +
        "%%27&returnGeometry=true&f=pjson&callback=?";
    $.getJSON(siteReportUrl, function (response) {
        var i, sitePackages, packageTitleLink;
        var sitePackageArray = [];
        for (i = 0; i < response.features.length; i++) {
            sitePackageArray.push(response.features[i].attributes.packageid);
        }
        sitePackageArray = sitePackageArray.getUnique().sortNumeric();
        //var packagePlural = (sitePackageArray.length === 1) ? "Package " : "Packages ";
        packageTitleLink = $('<a />')
            .attr('href', '#')
            .text("Packages (" + sitePackageArray.length + ")")
        if (sitePackageArray.length) {
            packageTitleLink.click(function () {
                $('#site-report').slideToggle('fast');
            });
        }
        $('#site-report-title').append($('<p />').append(packageTitleLink));
        sitePackages = '';
        for (i = 0; i < sitePackageArray.length; i++) {
            sitePackages += '<li><a href="report.html?packageid=' + sitePackageArray[i] + '">' +
                sitePackageArray[i] + '</a></li>';
        }
        if (sitePackageArray.length) {
            $('#site-report').html('<ul>' + sitePackages + '</ul>');
        }
    });
}

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
function createServiceButtons(site, entities) {

    // Check if map and/or image services exist for this site
    var servicesUrl = "http://maps3.lternet.edu/arcgis/rest/services/";
    var mapInfo = {
        'site': site,
        'services': {'map': true, 'image': true},
        'mapUrl': servicesUrl + "Test/" + site + "_layers/MapServer",
        'imageUrl': servicesUrl + "ImageTest/" + site + "_mosaic/ImageServer",
        'entities': entities
    };
    $.getJSON(mapInfo.mapUrl + "?f=pjson", function (response) {
        if (!response.error) {
            mapInfo.services.map = true;
            var linkToMapLightbox = $("<a />")
                .attr("href", "#")
                .text("View map")
                .click(function () {
                    showLightbox(mapInfo, 'map');
                }
            );
            var linkToMapService = $("<a />")
                .attr("href", mapInfo.mapUrl)
                .text("Map service");
            $('#view-map').html(linkToMapLightbox).show();
            $('#map-service').html(linkToMapService).show();
        }
        else {
            $('#view-map').hide();
            $('#map-service').hide();
        }
    });
    $.getJSON(mapInfo.imageUrl + "?f=pjson", function (response) {
        if (!response.error) {
            mapInfo.services.image = true;
            var linkToImageLightbox = $("<a />")
                .attr("href", "#")
                .text("View image")
                .click(function () {
                    showLightbox(mapInfo, 'image');
                }
            );
            var linkToImageService = $("<a />")
                .attr("href", mapInfo.imageUrl)
                .text("Image service");
            $('#view-image').html(linkToImageLightbox).show();
            $('#image-service').html(linkToImageService).show();
        }
        else {
            $('#view-image').hide();
            $('#image-service').hide();
        }
        $('#linkbar').show();
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
    window.embeddedMap = new esri.Map('map-block', {
        basemap: 'satellite',
        center: [lter[site].coords[1], lter[site].coords[0]],
        zoom: lter[site].zoom || 12,
        sliderStyle: 'small'
    });
    window.layerStack = new esri.layers.ArcGISDynamicMapServiceLayer(
        window.mapInfo.mapUrl,
        {id: 'layerStack'}
    );
    dojo.connect(window.layerStack, 'onLoad', function (layers) {
        var i, layerInfo, layerTitleLink, siteBoundary, layerChecks, checklist, checkbox;
        layerInfo = layers.layerInfos;
        layerTitleLink = $('<a />')
            .attr('href', '#')
            .text("Layers (" + layerInfo.length + ")")
            .click(function () {
                $('#layer-checks').slideToggle('fast');
            });
        $('#layer-checks-title').append($('<p />').append(layerTitleLink));
        layerChecks = $('<ul />').appendTo('#layer-checks');
        for (i = 0; i < layerInfo.length; i++) {
            checkbox = $('<a />')
                .attr('href', '#')
                .click({'index': i}, function (event) {
                    event.preventDefault(event);
                    mapLayerToggle(event, true);
                });
            if (layerInfo[i].name === "LTER site boundary") {
                siteBoundary = i;
                checkbox.text('Boundary');
                layerChecks.prepend($('<li class="show-layer" />').append(checkbox));
            }
            else {
                checkbox.text(layerInfo[i].name);
                layerChecks.append($('<li />').append(checkbox));
            }
        }
        layers.setVisibleLayers([siteBoundary]);
    });

    // Once the map is loaded, add layers, resize, and scalebar
    dojo.connect(window.embeddedMap, 'onLoad', function (theMap) {
        var resizeTimer;
        theMap.addLayer(window.layerStack);
        var scalebar = new esri.dijit.Scalebar({
            map: theMap,
            srcNodeRef: '#scale',
            scalebarUnit: 'dual'
        });
        $('#scale').append(
            $('.esriScalebar').removeClass('scalebar_bottom-left')
        );
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
    layerName = $(event.target).text();
    if (window.layerData[layerName]) {
        layerDetail = window.layerData[layerName].ESRI_OID;
    }
    substack = (isVector) ? window.layerStack : window.imageStack;
    showLayers = substack.visibleLayers;
    layerIndex = showLayers.indexOf(layer);
    if (!showLayers.length) {
        window.layerStack.show();
    }
    if (layerIndex === -1) {
        showLayers.push(layer);
        listItem.addClass('show-layer');
        if (layerDetail) {
            $('#active-layers').show();
            $('#layer' + layerDetail).removeClass('hidden');
        }
    }
    else {
        showLayers.splice(layerIndex, 1);
        listItem.removeClass('show-layer');
        if (layerDetail) {
            $('#layer' + layerDetail).addClass('hidden');
        }
    }
    substack.setVisibleLayers(showLayers);
    if (!substack.visibleLayers.length) {
        substack.hide();
        $('#active-layers').hide();
    }
    if (substack.visibleLayers.length) {
        isBoundary = (layerStack.layerInfos[substack.visibleLayers[0]].name ===
            'LTER site boundary');
        if (substack.visibleLayers.length === 1 && isBoundary) {
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
