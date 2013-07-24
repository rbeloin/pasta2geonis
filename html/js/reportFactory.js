$(document).ready(function () {
    var reportUrl, siteReportUrl, siteCode;
    var pid = getPID();
    siteCode = pid.split('.')[0];
    if (pid !== "") {
        $('#pid').html(pid);

        // There are multiple entities w/ the same packageid...
        reportUrl = "http://maps3.lternet.edu/arcgis/rest/services/Test/" +
            "Search/MapServer/2/query?where=packageid+%3D+%27" + pid +
            "%27&returnGeometry=true&outFields=report&f=pjson&callback=?";
        $.getJSON(reportUrl, function (response) {
            var i, replaceBanner, serverInfo, parsed, counter, services, reports;

            // The error report is pipe-delimited from other useful info stored in
            // the report field, in stringified-JSON format
            replaceBanner = false;
            counter = {'package': 0, 'vector': 0, 'raster': 0};
            services = {'image': false, 'map': false};
            reports = {'package': '', 'vector': '', 'raster': ''};
            for (i = 0; i < response.features.length; i++) {

                // First parse the raw report
                parsed = parseReport(response.features[i].attributes.report);
                formatted = checkTables(parsed.biography, parsed.report, parsed.reportType);
                counter[formatted.subject]++;

                // Generate a banner with the site name, id, and revision, if we haven't
                // done so already
                if (!replaceBanner) {
                    serverInfo = generateBanner(parsed.biography);
                    replaceBanner = true;
                }

                if (formatted.service !== null) {
                    if (!services.image && formatted.subject === 'raster') {
                        services.image = formatted.service;
                    }
                    else if (!services.map && formatted.subject === 'vector') {
                        services.map = formatted.service;
                    }
                }

                // Insert the reports into the report div
                //insertReport('<p>' + formatted.report + '</p>', 'report', i === 0);
                reports[formatted.subject] += '<p>' + formatted.report + '</p>';
            }

            if (counter.package) {
                $('#linkbar').show();
                if (reports.package === "<p><span class='entity-name'></span><ul><li>No errors found.</li></p>") {
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

            // Map and image server info
            //"<a href='" + services.map.split('/').slice(0, -1).join('/') + "'>" +
            //"Map service</a>"
            //"<a href='http://maps3.lternet.edu/arcgis/rest/services/Test/" +
            //pid.split('.')[0].split('-')[2] + "_layers/MapServer'>Map service</a>"
            // $(\'#intro\').lightbox_me({centered: true}); return false;
            var linkToMapLightbox = $("<a />").attr("href", "#").text("View map").click(function () {
                showMapLightbox(siteCode.split('-')[2]);
            });
            $('#view-map').html(linkToMapLightbox);
            $('#map-service').html(
                "<a href='http://maps3.lternet.edu/arcgis/rest/services/Test/" +
                pid.split('.')[0].split('-')[2] + "_layers/MapServer'>Map service</a>"
            );
            $('#image-service').html(
                "<a href='http://maps3.lternet.edu/arcgis/rest/services/ImageTest/" +
                pid.split('.')[0].split('-')[2] + "_mosaic/ImageServer'>Image service</a>"
            );

            // Append server information and download link to the bottom of the report
            appendServerInfo(serverInfo, parsed.biography);
        });
        $('#package-report').html("<p style='text-align: center; padding-top: 20px;'>Data set not found.</p>");

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