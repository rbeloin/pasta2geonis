<?xml version="1.0"?>
<!-- Adds Geonis metadata to existing Arcgis metadata. Use with XSLTransform tool in Conversion-Metadata toolset -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:esri="http://www.esri.com/metadata/">	
	<xsl:output method="xml" indent="yes" version="1.0" encoding="UTF-8" omit-xml-declaration="no"/>
	<xsl:param name="gpparam" />
	<xsl:variable name="suppNodes" select="document($gpparam,/geonis/*)" />

	<xsl:template match="/">
		<xsl:apply-templates select="node()|@*"/>
	</xsl:template>

	<xsl:template match="node()|@*" name="identity" priority="0">
		<xsl:copy>
			 <xsl:apply-templates select="node()|@*"/>
		</xsl:copy>
	</xsl:template>

	<xsl:template match="path/to/put/supp/data" priority="1" >
		<xsl:call-template name="identity" />
		<xsl:for-each select="$suppNodes">
			<xsl:copy-of select="." />
		</xsl:for-each>
	</xsl:template>
</xsl:stylesheet>