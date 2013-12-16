==============
Uploading data
==============

Presently, GeoNIS does not allow direct spatial data uploads.  Instead, all data must initially be uploaded through the `Provenance Aware Synthesis Tracking Architecture (PASTA) <https://portal.lternet.edu/nis/home.jsp>`_ website.  Once a data set has been accepted into PASTA, it will receive a revision number (an ID).  GeoNIS is programmed to automatically check PASTA for new data sets.  When GeoNIS finds a new data set, it will download it, then parse it for spatial data (by looking for ``<spatialVector>`` and ``<spatialRaster>`` tags in the metadata).

Please note that GeoNIS will only recognize spatial datasets if they are marked as such (using the spatial EML tags); if your metadata does not contain a ``<spatialVector>`` or ``<spatialRaster>`` tag, GeoNIS will *not* be able to process your data!

GeoNIS performs a variety of quality and error checks on data it downloads from PASTA.