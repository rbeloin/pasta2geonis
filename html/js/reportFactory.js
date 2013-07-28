(function () {
    $(document).ready(function () {
        var welcomeMessage, reportUrl, siteReportUrl, siteCode, entities;

        // Add onclick handlers to the map and image lightbox close buttons
        $('#close-map-lightbox').click(function (event) {
            event.preventDefault(event);
            $('#map-lightbox').trigger('close');
            $('#map').close();
        });

        pid = getPID();
        siteCode = pid.split('.')[0];
        site = siteCode.split('-')[2];
        $('#' + site).addClass('selected');
        if (!pid) {
            $('#pid').html("Welcome to GeoNIS!");
            $('#welcome-message').show();
        }
        else {
            generateBanner(pid);
            entities = [];

            // Fetch report from database using the Search service, then parse
            // the report, extract information about the report from the
            // stringified-JSON structure, then write output to document.
            reportUrl = "http://maps3.lternet.edu/arcgis/rest/services/Test/" +
                "Search/MapServer/2/query?where=packageid+%3D+%27" + pid +
                "%27&returnGeometry=true&outFields=report&f=pjson&callback=?";
            $.getJSON(reportUrl, function (response) {
                var i, serverInfo, parsed, counter, reports;

                // The error report is pipe-delimited from other useful info stored in
                // the report field, in stringified-JSON format
                counter = {'package': 0, 'vector': 0, 'raster': 0};
                reports = {'package': '', 'vector': '', 'raster': ''};
                for (i = 0; i < response.features.length; i++) {

                    // Parse the raw report from the Search service
                    parsed = parseReport(response.features[i].attributes.report);
                    formatted = checkTables(parsed.biography, parsed.report, parsed.reportType);
                    counter[formatted.subject]++;
                    entities.push(
                        (parsed.biography.entityname === 'None') ?
                        'Untitled ' + formatted.subject + ' data set' :
                        parsed.biography.entityname
                    );
                    if (!serverInfo) {
                        serverInfo = getServerInfo(parsed.biography);
                    }

                    // Append the report text onto the appropriate section
                    reports[formatted.subject] += '<p>' + formatted.report + '</p>';
                }

                // Insert report text into document, and create section headers
                writeReports(reports, counter);

                // Map and image buttons
                createServiceButtons(site, entities);

                // Append server information and download link to the bottom of the report
                appendServerInfo(serverInfo, parsed.biography);
            });
            if (pid.split('.')[1]) {
                $('#package-report').html(
                    "<p style='text-align: center; padding-top: 20px;'>Data set not found.</p>"
                );
            }

            // Other data sets from the same site
            siteReportUrl = "http://maps3.lternet.edu/arcgis/rest/services/Test/" +
                "Search/MapServer/2/query?where=packageid+like+%27" + siteCode +
                "%%27&returnGeometry=true&f=pjson&callback=?";
            $.getJSON(siteReportUrl, function (response) {
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
                if (sitePackageArray.length) {
                    $('#site-report').html('<ul>' + sitePackages + '</ul>');
                }
            });
        }
    });
})();