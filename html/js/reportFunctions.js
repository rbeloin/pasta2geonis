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
    report = "<ul><li>" + splitPipe[0];
    report += "</li>";
    return {
        'report': report.replace(/\n/g, '<br />'),
        'reportType': splitPipe[1],
        'biography': JSON.parse(splitPipe[2])
    };
}

/** 
 * Check the package and entity tables for error reports, and append them to the
 * active error report if found.
 */
function checkTables(biography, report) {
    return (biography['entityname'] === null) ?
        checkPackage(biography, report) : checkEntity(biography, report);
}

/**
 * Check for report entries in the entity table, and append them to its error report.
 */
function checkPackage(biography, report) {
    return "<span class='entity-name'>Package report</span>" + report;
}

/**
 * Check for report entries in the entity table, and append them to its error report.
 */
function checkEntity(biography, report) {
    var imageService, mapService, spatialType;
    mapService = (biography['mxd'] === null) ?
        biography['entityname'] + " is not available as a map service due to errors." :
        "<a href='" + biography['service'].split('/').slice(0, -1).join('/') + "'>" +
            biography['entityname'] + " is available as a map service.</a>";
    spatialType = (biography['israster']) ? "raster" : "vector";
    report = "<span class='entity-name'>" + biography['entityname'] + "</span> " +
        "(" + spatialType + ")" + report;
    if (spatialType === 'vector') {
        report += "<li>" + mapService + "</li>";
    }
    else {
        imageService = "<a href='#'>A link to the image service will go here.</a>";
        report += "<li>" + imageService + "</li>";
    }
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
        "<hr />" +
        "<em>Package " + packageLink + " was downloaded from the <a href='https://" +
        serverInfo.baseURL + "'>" + serverInfo.server +
        " server</a> on " + biography['downloaded'].split(' ')[0] + " at " +
        biography['downloaded'].split(' ')[1].split('.')[0] + " MDT.</em>"
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

