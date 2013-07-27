(function () {
    $(document).ready(function () {
        var reportUrl, siteReportUrl, siteCode, entities;

        // Add onclick handlers to the map and image lightbox close buttons
        $('#close-map-lightbox').click(function (event) {
            event.preventDefault(event);
            $('#map-lightbox').trigger('close');
            $('#map').close();
        });

        // Set up the LTER link bar
        //var lterLinks = '';
        $.each(lter, function (i, site) {
            var linkId = 'link-' + i;
            var tooltip = linkId + '-tooltip';
            $('#' + linkId).mouseenter(function () {
                $('#' + tooltip)
                    .text(site.name)
                    .css({
                        position: 'absolute',
                        display: 'none',
                        border: '1px solid #ccc',
                        padding: '0 10px',
                        background: '#fff',
                        color: '#000',
                        top: $(this).position().top,
                        left: $(this).position().left
                    })
                    .fadeIn('fast');
                })
                .mouseleave(function () {
                    $('#' + tooltip).fadeOut('fast');
                });
        });
        //$('#lter-links').html(lterLinks);

        pid = getPID();
        siteCode = pid.split('.')[0];
        site = siteCode.split('-')[2];
        if (pid !== "") {
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
            $('#package-report').html(
                "<p style='text-align: center; padding-top: 20px;'>Data set not found.</p>"
            );

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
                $('#site-report').html('<ul>' + sitePackages + '</ul>');
            });
        }
    });
})();