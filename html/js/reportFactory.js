$(document).ready(function () {
    var reportUrl, requestObj, siteCode, otherReportUrl, otherRequestObj;
    var pid = getPID();
    if (pid !== "") {
        $('#pid').html(pid);
        // There are multiple entities w/ the same packageid...
        reportUrl = "http://maps3.lternet.edu/arcgis/rest/services/Test/" +
            "Search/MapServer/2/query?where=packageid+%3D+%27" + pid +
            "%27&returnGeometry=true&outFields=report&f=pjson&callback=?";
        $.getJSON(reportUrl, function (response) {
            var i, replaceBanner, serverInfo, report, biography, packageLink;

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
            $('#workflow-info').html(
                "<hr />" +
                "<em>Package " + packageLink + " was downloaded from the <a href='https://" +
                serverInfo.baseURL + "'>" + serverInfo.server +
                " server</a> on " + biography['downloaded'].split(' ')[0] + " at " +
                biography['downloaded'].split(' ')[1].split('.')[0] + " MDT.</em>"
            );
        });
        $('#report').html("<p style='text-align: center;'>Data set not found.</p>");

        // Other data sets from the same site
        siteCode = pid.split('.')[0];
        otherReportUrl = "http://maps3.lternet.edu/arcgis/rest/services/Test/" +
            "Search/MapServer/2/query?where=packageid+like+%27" + siteCode +
            "%%27&returnGeometry=true&f=pjson&callback=?";
        $.getJSON(otherReportUrl, function (response) {
            var i, sitePackages;
            var sitePackageArray = [];
            for (i = 0; i < response.features.length; i++) {
                sitePackageArray.push(response.features[i].attributes.packageid);
            }
            sitePackageArray = sitePackageArray.getUnique().sortNumeric();
            packagePlural = (sitePackageArray.length === 1) ? " package" : " packages";
            $('#site-report-title').html(
                "<p>" +
                "<span class='entity-name'>" +
                siteCode.split('-').slice(-1)[0].toUpperCase() +
                " (" + sitePackageArray.length + packagePlural + ")" +
                "</span></p>"
            );
            sitePackages = '';
            for (i = 0; i < sitePackageArray.length; i++) {
                sitePackages += '<li><a href="report.html?packageid=' + sitePackageArray[i] + '">' +
                    sitePackageArray[i] + '</a></li>';
            }
            $('#site-report').html('<ul>' + sitePackages + '</ul>');
        });
    }
});