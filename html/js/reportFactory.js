var GEONIS = (function () {
    $(document).ready(function () {
        var welcomeMessage, servicesUrl, reportUrl, siteReportUrl, siteCode, entities;
        pid = getPID();
        siteCode = pid.split('.')[0];
        site = siteCode.split('-')[2];
        $('#' + site).addClass('selected');
        $('.leftbar-menu').css(
            'max-height',
            $(window).height() - $('.leftbar-grid').height() - 100
        );
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
                'imageUrl': servicesUrl + "ImageTest/" + site + "_mosaic/ImageServer",
                'entityUrl': servicesUrl + "Test/queryGeonisLayer/MapServer/1/query?" +
                    "where=scope+%3D+%27" + site + "%27&returnGeometry=true&" +
                    "outFields=*&f=pjson",
                'rasterEntityUrl': servicesUrl + "ImageTest/queryRaster/MapServer/1/query?" +
                    "where=packageid+like+%27knb-lter-" + site + "%%%27&returnGeometry=true" +
                    "&outFields=*&f=pjson"
            };
            window.imageData = {};
            $.getJSON(mapInfo.rasterEntityUrl, function (response) {
                $.each(response.features, function () {
                    imageData[this.attributes.id] = {
                        'packageid': this.attributes.packageid,
                        'entityname': this.attributes.entityname,
                        'layername': this.attributes.lyrname
                    };
                });
            });
            loadMapBlock();
            window.layerData = {};
            $.getJSON(mapInfo.entityUrl, function (response) {
                $.each(response.features, function () {
                    layerData[this.attributes.layername] = {
                        'packageid': this.attributes.packageid,
                        'title': this.attributes.title,
                        'entityname': this.attributes.entityname,
                        'abstract': this.attributes.abstract,
                        'sourceloc': this.attributes.sourceloc,
                        'ESRI_OID': this.attributes.ESRI_OID
                    };
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
            /*$.getJSON(mapInfo.rasterEntityUrl, function (response) {
                $.each(response.features, function () {
                    window.imageData[this.attributes.entityname] = {
                        'packageid': this.attributes.packageid,
                        'ESRI_OID': this.attributes.ESRI_OID
                    };
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
            });*/
        }
        else {
            generateBanner(pid);
            $('#site-report').show();
            //entities = [];
            window.packageReports = [];
            window.vectorReports = {};
            window.rasterReports = {};

            // Fetch detailed reports from viewreport using viewreport query layer
            var viewReportUrl = "http://maps3.lternet.edu/arcgis/rest/services/Test/" +
                "viewreport/MapServer/1/query?where=packageid+%3D+%27" + pid +
                "%27&returnGeometry=true&outFields=*&f=pjson&callback=?";
            $.getJSON(viewReportUrl, function (response) {
                $.each(response.features, function() {
                    if (this.attributes.entityid === null) {
                        packageReports.push(this.attributes);
                    }
                    else if (this.attributes.isvector) {
                        if (vectorReports[this.attributes.entityid]) {
                            vectorReports[this.attributes.entityid].push(this.attributes);
                        }
                        else {
                            vectorReports[this.attributes.entityid] = [this.attributes];
                        }
                    }
                    else if (this.attributes.israster) {
                        if (rasterReports[this.attributes.entityid]) {
                            rasterReports[this.attributes.entityid].push(this.attributes);
                        }
                        else {
                            rasterReports[this.attributes.entityid] = [this.attributes];
                        }

                    }
                });
                if (packageReports.length) {
                    $('#package-report').append($('<table />')
                        .attr('id', 'package-report-table')
                        .attr('class', 'report-table')
                        .append($('<tr />')
                            .append($('<th />').text("Task description"))
                            .append($('<th />').text("Report"))
                            .append($('<th />').text("Status"))
                        )
                    );
                    $.each(packageReports, function () {
                        var reportText = this.report || '';
                        var statusText = (this.status) ? 'Complete' : 'Error';
                        $('#package-report-table').append($('<tr />')
                            .append($('<td />').text(this.taskdescription))
                            .append($('<td />').text(reportText))
                            .append($('<td />').text(statusText))
                        );
                    });
                }
                if (!$.isEmptyObject(vectorReports)) {
                    var numVectors = Object.keys(vectorReports).length;
                    $('#vector-banner').show();
                    $('#vector-report-header').append($('<h3 />')
                        .text(numVectors + ' vector ' + pluralize('dataset', numVectors))
                    ).show();
                    $('#vector-report').append($('<ul />').attr('id', 'vector-entities'));
                    $.each(vectorReports, function () {
                        $('#vector-entities').prepend($('<li />')
                            .addClass('entity-name')
                            .attr('id', 'entity-' + this[0].entityid)
                            .text(this[0].entityname)
                            .css('cursor', 'pointer')
                            .click(function (event) {
                                var isSelected = $(event.target).hasClass('selected');
                                $('.report-wrapper').hide();
                                $(event.target).parent().children().removeClass('selected');
                                if (!isSelected) {
                                    $('#report-wrapper-' + this.id.split('-')[1]).slideDown('fast');
                                    $(event.target).addClass('selected');
                                }
                            })
                        );
                        $('#vector-entities').append($('<li />')
                            .append($('<div />')
                                .hide()
                                .addClass('report-wrapper')
                                .attr('id', 'report-wrapper-' + this[0].entityid)
                                .append($('<table />')
                                    .attr('id', 'report-' + this[0].entityid)
                                    .attr('class', 'report-table')
                                    .append($('<tr />')
                                        .append($('<th />').text("Task description"))
                                        .append($('<th />').text("Report"))
                                        .append($('<th />').text("Status"))
                                    )
                                )
                            )
                        );
                        $.each(this, function () {
                            var reportText = this.report || '';
                            var statusText = (this.status) ? 'Complete' : 'Error';
                            $('#report-' + this.entityid).append($('<tr />')
                                .append($('<td />').text(this.taskdescription))
                                .append($('<td />').text(reportText))
                                .append($('<td />').text(statusText))
                            );
                        });
                    });
                }
                if (!$.isEmptyObject(rasterReports)) {
                    var numRasters = Object.keys(rasterReports).length;
                    $('#raster-banner').show();
                    $('#raster-report-header').append($('<h3 />')
                        .text(numRasters + ' raster ' + pluralize('dataset', numRasters))
                    ).show();
                    $('#raster-report').append($('<ul />').attr('id', 'raster-entities'));
                    $.each(rasterReports, function () {
                        $('#raster-entities').prepend($('<li />')
                            .addClass('entity-name')
                            .attr('id', 'entity-' + this[0].entityid)
                            .text(this[0].entityname)
                            .css('cursor', 'pointer')
                            .click(function (event) {
                                var isSelected = $(event.target).hasClass('selected');
                                $('.report-wrapper').hide();
                                $(event.target).parent().children().removeClass('selected');
                                if (!isSelected) {
                                    $('#report-wrapper-' + this.id.split('-')[1]).slideDown('fast');
                                    $(event.target).addClass('selected');
                                }
                            })
                        );
                        $('#raster-entities').append($('<li />')
                            .append($('<div />')
                                .hide()
                                .addClass('report-wrapper')
                                .attr('id', 'report-wrapper-' + this[0].entityid)
                                .append($('<table />')
                                    .attr('id', 'report-' + this[0].entityid)
                                    .attr('class', 'report-table')
                                    .append($('<tr />')
                                        .append($('<th />').text("Task description"))
                                        .append($('<th />').text("Report"))
                                        .append($('<th />').text("Status"))
                                    )
                                )
                            )
                        );
                        $.each(this, function () {
                            var reportText = this.report || '';
                            var statusText = (this.status) ? 'Complete' : 'Error';
                            $('#report-' + this.entityid).append($('<tr />')
                                .append($('<td />').text(this.taskdescription))
                                .append($('<td />').text(reportText))
                                .append($('<td />').text(statusText))
                            );
                        });
                    });
                }
            });

            // Fetch report from database using the Search service, then parse
            // the report, extract information about the report from the
            // stringified-JSON structure, then write output to document.
            /*reportUrl = "http://maps3.lternet.edu/arcgis/rest/services/Test/" +
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
            }*/
        }

        // Other data sets from the same site
        fetchSitePackages(siteCode);
    });
})();