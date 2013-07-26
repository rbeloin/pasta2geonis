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
            'report': checkPackage(biography, report),
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
function checkPackage(biography, report) {
    return report;
}

/**
 * Check for report entries in the entity table, and append them to its error report.
 */
function checkEntity(biography, report, spatialType) {
    entityname = (biography['entityname'] === 'None') ?
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
    $('#pid').html(
        splitPid[0].split('-')[2].toUpperCase() + " " + splitPid[1] +
        ", revision " + splitPid[2]
    );
}

/**
 * Determines whether this package was retrieved from the staging
 * (pasta-s.lternet.edu) or live (pasta.lternet.edu) server.
 */
function getServerInfo(biography) {
    var serverInfo;
    if (biography['pasta'].indexOf('pasta-s') !== -1) {
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
    var services = {'map': true, 'image': true};
    var mapUrl = "http://maps3.lternet.edu/arcgis/rest/services/Test/" +
        site + "_layers/MapServer";
    var imageUrl = "http://maps3.lternet.edu/arcgis/rest/services/ImageTest/" +
        site + "_mosaic/ImageServer";
    $.getJSON(mapUrl + "?f=pjson", function (response) {
        if (!response.error) {
            services.map = true;
            var linkToMapLightbox = $("<a />")
                .attr("href", "#")
                .text("View map")
                .click(function () {
                    showLightbox(site, 'map', entities);
                }
            );
            var linkToMapService = $("<a />")
                .attr("href", mapUrl)
                .text("Map service");
            $('#view-map').html(linkToMapLightbox).show();
            $('#map-service').html(linkToMapService).show();
        }
        else {
            $('#view-map').hide();
            $('#map-service').hide();
        }
    });
    $.getJSON(imageUrl + "?f=pjson", function (response) {
        if (!response.error) {
            services.image = true;
            var linkToImageLightbox = $("<a />")
                .attr("href", "#")
                .text("View image")
                .click(function () {
                    showLightbox(site, 'image', entities);
                }
            );
            var linkToImageService = $("<a />")
                .attr("href", imageUrl)
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
function showLightbox(siteCode, service, entities) {
    dojo.require("esri.map");
    $('#' + service + '-lightbox').lightbox_me({centered: true});
    dojo.ready(init(siteCode, service, entities));
    return false;
}

// Create and display the ArcGIS map inside a lightbox
function init(site, service, entities) {

    // Do we need separate view map/view image buttons??
    // Idea: just have one button, and allow the user to switch layers on/off
    // as needed...
    var map, layer, layerURL, serviceLink;
    $('#' + service + '-lightbox').show();
    $('#' + service).show();

    // If this is a map service
    if (service === "map") {
        layerURL = "http://maps3.lternet.edu/arcgis/rest/services/Test/" +
            site + "_layers/MapServer";
        serviceLink = $("<a />")
            .attr("href", layerURL)
            .text("Click here to go to the " + site.toUpperCase() + " map service.");
        $('#map-service-link').html(serviceLink);
        layer = new esri.layers.ArcGISDynamicMapServiceLayer(layerURL);
    }

    // If this is an image service
    else {
        layerURL = "http://maps3.lternet.edu/arcgis/rest/services/ImageTest/" +
            site + "_mosaic/ImageServer";
        //layerURL = "http://maps3.lternet.edu/arcgis/rest/services/ImageTest/and_gi01001/ImageServer";
        serviceLink = $("<a />")
            .attr("href", layerURL)
            .text("Click here to go to the " + site.toUpperCase() + " image service.");
        $('#image-service-link').html(serviceLink);

        var params = new esri.layers.ImageServiceParameters();
        params.noData = 0;
        layer = new esri.layers.ArcGISImageServiceLayer(layerURL, {
            imageServiceParameters: params,
            opacity: 0.75
        });
        //layer = new esri.layers.ArcGISImageServiceLayer(layerURL);
    }
    map = new esri.Map(service, {
        basemap: 'satellite',
        center: [lter[site].coords[1], lter[site].coords[0]], // longitude, latitude
        zoom: (lter[site].zoom) ? lter[site].zoom : 12,
        sliderStyle: "small"
    });
    map.addLayer(layer);

    /*layerURL = "http://maps3.lternet.edu/arcgis/rest/services/ImageTest/and_gi01007/ImageServer";
    layer = new esri.layers.ArcGISImageServiceLayer(layerURL);
    map.addLayer(layer);*/
}