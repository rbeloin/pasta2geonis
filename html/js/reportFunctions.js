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
    return "<span class='entity-name'></span>" + report;
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
 * Replaces the default "Searching for package..." with a readable site ID: revision
 * banner, and determines whether this package was retrieved from the staging
 * (pasta-s.lternet.edu) or live (pasta.lternet.edu) server.
 */
function generateBanner(biography) {
    var serverInfo;
    if (biography['scope'] !== 'undefined') {
        $('#pid').html(
            biography['scope'].toUpperCase() + " " + biography['identifier'] +
            ", revision " + biography['revision']
        );
    }
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

// Creates initial HTML or appends HTML to a div, as appropriate...
function insertReport(report, reportDiv, isFirstReport) {
    var nextReport;
    if (isFirstReport) {
        $('#' + reportDiv).html(report);
    }
    else {
        nextReport = document.createElement('div');
        nextReport.innerHTML = report;
        while (nextReport.firstChild) {
            document.getElementById(reportDiv).appendChild(nextReport.firstChild);
        }
    }
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

// Create and display the ArcGIS map inside a lightbox
function init(site, service) {
    var map, layer, layerURL, serviceLink;
    $('#' + service + '-lightbox').show();
    $('#' + service).show();
    if (service === "map") {
        layerURL = "http://maps3.lternet.edu/arcgis/rest/services/Test/" +
            site + "_layers/MapServer";
        serviceLink = $("<a />")
            .attr("href", layerURL)
            .text("Click here to go to the " + site.toUpperCase() + " map service.");
        $('#map-service-link').html(serviceLink);
        layer = new esri.layers.ArcGISDynamicMapServiceLayer(layerURL);
    }
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

// Call the map creator function when user clicks on the "view map" button
function showLightbox(siteCode, service) {
    dojo.require("esri.map");
    $('#' + service + '-lightbox').lightbox_me({centered: true});
    dojo.ready(init(siteCode, service));
    return false;
}

