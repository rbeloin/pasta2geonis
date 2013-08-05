var GEONIS = (function () {
    $(document).ready(function () {
        var welcomeMessage, servicesUrl, entityUrl, reportUrl, siteReportUrl, siteCode, entities;
        pid = getPID();
        siteCode = pid.split('.')[0];
        site = siteCode.split('-')[2];
        $('#' + site).addClass('selected');
        $('.leftbar-menu').css('max-height', $(window).height() - $('.leftbar-grid').height() - 100);
        if (!pid) {
            $('#pid').html("Welcome to GeoNIS!");
            $('#welcome-message').show();
            return;
        }
        else if (!pid.split('.')[1] || !pid.split('.')[2]) {
            generateBanner(pid);
            $('#package-report').hide();
            $('#workflow-info').hide();
            $('.banner').css('border', 'none');
            $('#pid').css('border', '1px solid #ccc');

            servicesUrl = "http://maps3.lternet.edu/arcgis/rest/services/";
            window.mapInfo = {
                'site': site,
                'services': {'map': true, 'image': true},
                'mapUrl': servicesUrl + "Test/" + site + "_layers/MapServer",
                'imageUrl': servicesUrl + "ImageTest/" + site + "_mosaic/ImageServer"
            };
            loadMapBlock();
            window.layerData = {};
            entityUrl = servicesUrl + "Test/queryGeonisLayer/MapServer/1/query?" +
                "where=scope+%3D+%27" + site + "%27&returnGeometry=true&" +
                "outFields=*&f=pjson";
            $.getJSON(entityUrl, function (response) {
                $.each(response.features, function () {
                    window.layerData[this.attributes.layername] = {
                        'packageid': this.attributes.packageid,
                        'title': this.attributes.title,
                        'entityname': this.attributes.entityname,
                        'abstract': this.attributes.abstract,
                        'sourceloc': this.attributes.sourceloc,
                        'ESRI_OID': this.attributes.ESRI_OID
                    }
                    var packageid =
                        this.attributes.packageid.split('.').slice(1, 3).join('.');
                    var title = shorten(this.attributes.title);
                    var abstract = shorten(this.attributes.abstract);
                    var entityname = shorten(this.attributes.entityname);
                    var layerID = this.attributes.ESRI_OID;
                    var fullTitle = $('<li class="detail-title" />').text(this.attributes.title);
                    var fullSourceloc = $('<li class="detail-sourceloc" />').append($('<a />')
                        .attr('href', this.attributes.sourceloc)
                        .text(this.attributes.sourceloc)
                    );
                    var fullAbstract = $('<li />').append($('<p />').text(this.attributes.abstract));
                    var row = $('<tr />')
                        .attr('id', 'layer' + layerID)
                        .append($('<td />').text(this.attributes.layername))
                        .append($('<td />').text(packageid))
                        .append($('<td />').text(entityname))
                        .append($('<td />').text(title))
                        .click(function (event) {
                            var details = $('#layer-detail-row-' + layerID);
                            if (!details.length) {
                                $('.detail-box:visible').hide();
                                $(event.target).parent().after(
                                    $('<tr class="detail-box" />')
                                        .attr('id', 'layer-detail-row-' + layerID)
                                        .append($('<td />')
                                            .attr('colspan', 4)
                                            .append($('<div />')
                                                .attr('id', 'detailText' + layerID)
                                            )
                                        )
                                );
                                var detailText = $('<ul />').appendTo($('#detailText' + layerID));
                                detailText.append(fullTitle);
                                detailText.append(fullSourceloc);
                                detailText.append(fullAbstract);
                            }
                            else {
                                if ($('.detail-box:visible').length === 1 && details.is(':visible')) {
                                    details.hide();
                                }
                                else if ($('.detail-box:visible').length > 1 && details.is(':visible')) {
                                    $('.detail-box:visible').hide();
                                }
                                else if ($('.detail-box:visible').length === 1 && !details.is(':visible')) {
                                    $('.detail-box:visible').hide();
                                    details.show();
                                }
                                else {
                                    details.show();
                                }
                            }
                        })
                        .hover(
                            function () {
                                $(this).css('background-color', '#CEECF5');
                                $(this).css('cursor', 'pointer');
                            },
                            function () {
                                $(this).css('background-color', '#FFF');
                                $(this).css('cursor', 'default');
                            }
                        )
                        .addClass('hidden');
                    $('#active-layers tbody').append(row);
                    function shorten(data) {
                        return (data.length < 40) ? data : data.slice(0, 39) + '...';
                    }
                });
            });
        }
        else {
            generateBanner(pid);
            $('#site-report').show();
            entities = [];

            // Fetch report from database using the Search service, then parse
            // the report, extract information about the report from the
            // stringified-JSON structure, then write output to document.
            reportUrl = "http://maps3.lternet.edu/arcgis/rest/services/Test/" +
                "Search/MapServer/2/query?where=packageid+%3D+%27" + pid +
                "%27&returnGeometry=true&outFields=report&f=pjson&callback=?";
            $.getJSON(reportUrl, function (response) {
                var i, serverInfo, parsed, counter, reports;
                counter = {'package': 0, 'vector': 0, 'raster': 0};
                reports = {'package': '', 'vector': '', 'raster': ''};

                // The error report is pipe-delimited from other useful info stored in
                // the report field, in stringified-JSON format
                $.each(response.features, function () {

                    // Parse the raw report from the Search service
                    parsed = parseReport(this.attributes.report);
                    formatted = checkTables(
                        parsed.biography, parsed.report, parsed.reportType
                    );
                    counter[formatted.subject]++;
                    if (parsed.reportType === 'entity-report') {
                        entities.push(
                            (parsed.biography.entityname === 'None') ?
                            'Untitled ' + formatted.subject + ' data set' :
                            parsed.biography.entityname
                        );
                    }
                    if (!serverInfo) {
                        serverInfo = getServerInfo(parsed.biography);
                    }

                    // Append the report text onto the appropriate section
                    reports[formatted.subject] += '<p>' + formatted.report + '</p>';
                });

                // Insert report text into document, and create section headers
                writeReports(reports, counter);

                // Map and image buttons
                createServiceButtons(site, entities);

                // Append server information and download link to the bottom of the report
                if (parsed && parsed.biography) {
                    appendServerInfo(serverInfo, parsed.biography);
                }
            });
            if (pid.split('.')[1]) {
                $('#package-report').html(
                    "<p style='text-align: center; padding-top: 5px;'>Data set not found.</p>"
                );
            }
        }

        // Other data sets from the same site
        fetchSitePackages(siteCode);
    });
})();