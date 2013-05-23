<?xml version="1.0"?>
<!-- Copies nodes from EML that will be used to supplement metadata, find packageId, data type, data source, and run other data checks -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:eml="eml://ecoinformatics.org/eml-2.1.0"  xmlns:xs="http://www.w3.org/2001/XMLSchema" >	

	<xsl:output method="xml" indent="no" version="1.0" encoding="UTF-8" omit-xml-declaration="no"/>

	<xsl:template match="/">
		<xsl:apply-templates select="node()"/>
	</xsl:template>
	
	<xsl:template match="/eml:eml">
		<xsl:element name="emlSubset">
			<xsl:attribute name="packageId">
				<xsl:value-of select="@packageId" />
			</xsl:attribute>
			<xsl:apply-templates select="node()"/>
			<xsl:element name="workingData">
			<!-- a node to store various data by and for tools during workflow -->
			</xsl:element>
		</xsl:element>
	</xsl:template>
	
	<!-- copy these nodes -->
	<xsl:template match="dataset/spatialVector |
						 dataset/spatialRaster |
						 dataset/title         |
						 dataset/abstract      |
						 dataset/purpose       |
						 dataset/keywordSet    |
                         dataset/contact/electronicMailAddress">
		<xsl:copy-of select="." />
	</xsl:template>
	
	<!-- suppress default behavior to copy text -->
	<xsl:template match="text()">
	</xsl:template>
	
</xsl:stylesheet>