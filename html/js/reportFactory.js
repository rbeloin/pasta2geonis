$(document).ready(function () {
    var reportUrl, requestObj, siteCode, otherReportUrl, otherRequestObj;
    var pid = getPID();
    if (pid !== "") {
        document.getElementById("pid").innerHTML = pid;
        // There are multiple entities w/ the same packageid!!
        reportUrl = "http://maps3.lternet.edu/arcgis/rest/services/Test/" +
            "Search/MapServer/2/query?where=packageid+%3D+%27" + pid +
            "%27&returnGeometry=true&outFields=report&f=pjson";
        requestObj = new XMLHttpRequest();
        requestObj.onreadystatechange = function() {
            var i, responseJson, response, replaceBanner, serverInfo, report, biography, packageLink;
            if (requestObj.readyState == 4 && (requestObj.status == 200 || requestObj.status == 304)) {
                responseJson = requestObj.responseText;
                response = JSON.parse(responseJson);

                // The error report is pipe-delimited from other useful info stored in
                // the report field, in stringified-JSON format
                replaceBanner = false;
                for (i = 0; i < response.features.length; i++) {

                    // First parse the raw report
                    parsedReport = parseReport(response.features[i].attributes.report);
                    report = parsedReport.report;
                    biography = parsedReport.biography;
                    report = checkTables(biography, report);

                    // Generate a banner with the site name, id, and revision, if we haven't
                    // done so already
                    if (!replaceBanner) {
                        serverInfo = generateBanner(biography);
                        replaceBanner = true;
                    }

                    // Insert the reports into the report div
                    insertReport('<p>' + report + '</p>', 'report', i === 0);
                }

                // Append server information and download link to the bottom of the report
                packageLink = "<a href='https://" + serverInfo['baseURL'] + "/package/eml/" +
                    biography['packageid'].split('.')[0] + "/" + biography['identifier'] +
                    "/" + biography['revision'] + "'>" + biography['packageid'] + "</a>";
                document.getElementById('workflow-info').innerHTML = "<hr />" +
                    "<em>Package " + packageLink + " was downloaded from the <a href='https://" +
                    serverInfo.baseURL + "'>" + serverInfo.server +
                    " server</a> on " + biography['downloaded'].split(' ')[0] + " at " +
                    biography['downloaded'].split(' ')[1].split('.')[0] + " MDT.</em>";
            }
        };
        document.getElementById("report").innerHTML = "<p style='text-align: center;'>Data set not found.</p>";
        requestObj.open("Get", reportUrl, true);
        requestObj.send();

        // Other data sets from the same site
        siteCode = pid.split('.')[0];
        otherReportUrl = "http://maps3.lternet.edu/arcgis/rest/services/Test/" +
            "Search/MapServer/2/query?where=packageid+like+%27" + siteCode +
            "%%27&returnGeometry=true&f=pjson";
        otherRequestObj = new XMLHttpRequest();
        otherRequestObj.onreadystatechange = function() {
            var i, responseJson, response, sitePackageArray, sitePackages;
            if (otherRequestObj.readyState == 4 && (otherRequestObj.status == 200 || otherRequestObj.status == 304)) {
                responseJson = otherRequestObj.responseText;
                response = JSON.parse(responseJson);
                sitePackageArray = [];
                for (i = 0; i < response.features.length; i++) {
                    sitePackageArray.push(response.features[i].attributes.packageid);
                }
                sitePackageArray = sitePackageArray.getUnique().sortNumeric();
                packagePlural = (sitePackageArray.length === 1) ? " package" : " packages";
                document.getElementById('site-report-title').innerHTML = "<p>" +
                    "<span class='entity-name'>" +
                    siteCode.split('-').slice(-1)[0].toUpperCase() +
                    " (" + sitePackageArray.length + packagePlural + ")" +
                    "</span></p>";
                sitePackages = '';
                for (i = 0; i < sitePackageArray.length; i++) {
                    sitePackages += '<li><a href="report.html?packageid=' + sitePackageArray[i] + '">' +
                        sitePackageArray[i] + '</a></li>';
                }
                document.getElementById('site-report').innerHTML = '<ul>' + sitePackages + '</ul>';
            }
        };
        otherRequestObj.open("Get", otherReportUrl, true);
        otherRequestObj.send();

        /*var allReportUrl = "http://maps3.lternet.edu/arcgis/rest/services/Test/Search/MapServer/2/query?where=packageid+like+%27knb-lter%%%27&returnGeometry=true&f=pjson"
        var allRequestObj = new XMLHttpRequest();
        allRequestObj.onreadystatechange = function() {
            if (allRequestObj.readyState == 4 && (allRequestObj.status == 200 || allRequestObj.status == 304)) {
                var responseJson = allRequestObj.responseText;
                var response = JSON.parse(responseJson);
                document.getElementById('all-report-title').innerHTML = "<p><span class='entity-name'>Found " + 
                    response.features.length + " other packages</span></p>";
                for (i = 0; i < response.features.length; i++) {
                    insertReport(
                        '<ul><li>' + response.features[i].attributes.packageid + '</li>', 
                        'all-report', 
                        i == 0
                    );
                }
            }
        }
        allRequestObj.open("Get", allReportUrl, true);
        allRequestObj.send();*/
    }
});