<?xml version="1.0"?>
<!-- Converts nodes from EMLSubset file into python object -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" >
	<xsl:output method="text"/>

	<!-- Escape single quotes -->
	<xsl:template name="escape-single-quotes">
		<xsl:param name="text" />
		
		<xsl:variable name="apos">'</xsl:variable>
		<xsl:variable name="bapos">\'</xsl:variable>		
		<xsl:value-of select="str:replace($text, $apos, $bapos)" />
	</xsl:template>
	
	<!-- Escape double quotes -->
	<xsl:template name="escape-double-quotes">
		<xsl:param name="text" />
		
		<xsl:variable name="apos">"</xsl:variable>
		<xsl:variable name="bapos">\"</xsl:variable>		
		<xsl:value-of select="str:replace($text, $apos, $bapos)" />
	</xsl:template>	


	<xsl:call-template name="escape-single-quotes">
		<xsl:with-param name="text" select="/" />
	</xsl:call-template>
	
	<xsl:call-template name="escape-double-quotes">
		<xsl:with-param name="text" select="/" />
	</xsl:call-template>

	
	<xsl:template match="/"><xsl:apply-templates select="node()"/></xsl:template>
	<!-- bracket the dictionary items -->
	<xsl:template match="emlSubset">{<xsl:apply-templates select="node()"/>}</xsl:template>

	<!-- title -->
	<xsl:template match="title">"title":"<xsl:copy-of select="normalize-space(descendant::text())" />",</xsl:template>

	<!-- abstract (text only, skip <para> <literalLayout> ) -->
	<xsl:template match="abstract">"abstract":"<xsl:for-each select="descendant::text()[string-length(normalize-space(.)) > 0]"><xsl:value-of select="normalize-space(.)" /></xsl:for-each>",</xsl:template>

	<!-- purpose  -->
	<xsl:template match="purpose">"purpose":"<xsl:for-each select="descendant::text()[string-length(normalize-space(.)) > 0]"><xsl:value-of select="normalize-space(.)" /></xsl:for-each>",</xsl:template>

	<!-- match first keywordSet, then pick up keywords from any other keywordSets -->
	<xsl:template match="keywordSet[1]">"keywords":"<xsl:for-each select="child::keyword"><xsl:value-of select="text()" />;</xsl:for-each>
			<xsl:for-each select="following-sibling::keywordSet/keyword"><xsl:value-of select="text()" />;</xsl:for-each>",</xsl:template>
			
	<!-- source url -->
	<xsl:template match="*/physical/distribution/online/url">"source":"<xsl:value-of select = "normalize-space(.)" />",</xsl:template>

	<!-- description  -->
	<xsl:template match="workingData/item[@name='entityDesc']/text()">"desc":"<xsl:value-of select = "normalize-space(.)" />",</xsl:template>
	
	<!-- layer name  -->
	<xsl:template match="workingData/item[@name='layerName']/text()">"layer":"<xsl:value-of select = "normalize-space(.)" />",</xsl:template>


	<!-- suppress default behavior to copy text -->
	<xsl:template match="text()" />
</xsl:stylesheet>
