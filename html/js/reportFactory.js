$(document).ready(function () {
    var reportUrl, siteReportUrl, siteCode, entities;

    // Add onclick handlers to the map and image lightbox close buttons
    $('#close-map-lightbox').click(function (event) {
        event.preventDefault(event);
        $('#map-lightbox').trigger('close');
        $('#map').close();
    });
    $('#close-image-lightbox').click(function (event) {
        event.preventDefault(event);
        $('#image-lightbox').trigger('close');
        $('#image').close();
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
    if (pid !== "") {
        $('#pid').html(pid);
        entities = [];
        reportUrl = "http://maps3.lternet.edu/arcgis/rest/services/Test/" +
            "Search/MapServer/2/query?where=packageid+%3D+%27" + pid +
            "%27&returnGeometry=true&outFields=report&f=pjson&callback=?";
        $.getJSON(reportUrl, function (response) {
            var i, foundServerInfo, serverInfo, parsed, counter, services, reports;

            // The error report is pipe-delimited from other useful info stored in
            // the report field, in stringified-JSON format
            foundServerInfo = false;
            counter = {'package': 0, 'vector': 0, 'raster': 0};
            reports = {'package': '', 'vector': '', 'raster': ''};
            generateBanner(pid);
            for (i = 0; i < response.features.length; i++) {

                // First parse the raw report
                parsed = parseReport(response.features[i].attributes.report);
                formatted = checkTables(parsed.biography, parsed.report, parsed.reportType);
                counter[formatted.subject]++;

                //alert(JSON.stringify(parsed.biography));
                entities.push(
                    (parsed.biography.entityname === 'None') ?
                    'Untitled ' + formatted.subject + ' data set' :
                    parsed.biography.entityname
                );

                // Generate a banner with the site name, id, and revision, if we haven't
                // done so already
                if (!foundServerInfo) {
                    serverInfo = getServerInfo(parsed.biography);
                    foundServerInfo = true;
                }

                // Append the report text onto the appropriate section
                reports[formatted.subject] += '<p>' + formatted.report + '</p>';
            }

            // Insert report text into document, and create section headers
            writeReports(reports, counter);

            // Map and image buttons
            createServiceButtons(siteCode.split('-')[2], entities);

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