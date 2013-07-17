var pid = getPID();
if (pid != "") {
    document.getElementById("pid").innerHTML = pid;
    var reportUrl = "http://maps3.lternet.edu/arcgis/rest/services/Test/Search/MapServer/2/query?where=packageid+%3D+%27" + pid + "%27&returnGeometry=true&outFields=report&f=pjson";
    var requestObj = new XMLHttpRequest();
    requestObj.onreadystatechange = function() {
        if (requestObj.readyState == 4 && (requestObj.status == 200 || requestObj.status == 304)) {
            var responseJson = requestObj.responseText;
            var response = JSON.parse(responseJson);

            // The error report is pipe-delimited from other useful info stored in
            // the report field, in stringified-JSON format
            var replaceBanner = false;
            for (var i = 0; i < response.features.length; i++) {

                // First parse the raw report
                parsedReport = parseReport(response.features[i].attributes.report);
                var report = parsedReport.report;
                var biography = parsedReport.biography;
                report = checkTables(biography, report);
                
                // Generate a banner with the site name, id, and revision, if we haven't
                // done so already
                if (!replaceBanner) {
                    var serverInfo = generateBanner(biography);
                    replaceBanner = true;
                }

                // Insert the reports into the report div
                insertReport('<p>' + report + '</p>', 'report', i == 0);
            }
            
            // Append server information and download link to the bottom of the report
            var packageLink = "<a href='https://" + serverInfo['baseURL'] + "/package/eml/" +
                biography['packageid'].split('.')[0] + "/" + biography['identifier'] +
                "/" + biography['revision'] + "'>" + biography['packageid'] + "</a>";
            document.getElementById('workflow-info').innerHTML = "<hr />\
                <em>Package " + packageLink + " was downloaded from the <a href='https://" + 
                serverInfo.baseURL + "'>" + serverInfo.server + 
                " server</a> on " + biography['downloaded'].split(' ')[0] + " at " + 
                biography['downloaded'].split(' ')[1].split('.')[0] + " MDT.</em>";
        }
    }
    document.getElementById("report").innerHTML = "<p style='text-align: center;'>Data set not found.</p>"
    requestObj.open("Get", reportUrl, true);
    requestObj.send();

    // Other data sets from the same site
    siteCode = pid.split('.')[0];
    var otherReportUrl = "http://maps3.lternet.edu/arcgis/rest/services/Test/Search/MapServer/2/query?where=packageid+like+%27" + siteCode + "%%27&returnGeometry=true&f=pjson"
    var otherRequestObj = new XMLHttpRequest();
    otherRequestObj.onreadystatechange = function() {
        if (otherRequestObj.readyState == 4 && (otherRequestObj.status == 200 || otherRequestObj.status == 304)) {
            var responseJson = otherRequestObj.responseText;
            var response = JSON.parse(responseJson);
            sitePackageArray = [];
            for (var i = 0; i < response.features.length; i++) {
                sitePackageArray.push(response.features[i].attributes.packageid);
            }
            sitePackageArray = sitePackageArray.getUnique().sortNumeric();
            document.getElementById('site-report-title').innerHTML = "<p><span class='entity-name'>" + 
                siteCode.split('-').slice(-1)[0].toUpperCase() + " (" + sitePackageArray.length + 
                " packages)</span></p>";
            var sitePackages = '';
            for (var i = 0; i < sitePackageArray.length; i++) {
                sitePackages += '<li><a href="report.html?packageid=' + sitePackageArray[i] + '">' + 
                    sitePackageArray[i] + '</a></li>';
            }
            document.getElementById('site-report').innerHTML = '<ul>' + sitePackages + '</ul>';
        }
    }
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
            for (var i = 0; i < response.features.length; i++) {
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