<?xml version="1.0"?>
<!-- Converts nodes from EMLSubset file into python object -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" >
	<xsl:output method="text"/>

	<xsl:template name="translateDoubleQuotes">
		<xsl:param name="string" select="''" />

		<xsl:choose>
			<xsl:when test="contains($string, '&quot;')">
				<xsl:text /><xsl:value-of select="substring-before($string, '&quot;')" />\"<xsl:call-template name="translateDoubleQuotes"><xsl:with-param name="string" select="substring-after($string, '&quot;')" /></xsl:call-template><xsl:text />
			</xsl:when>
			<xsl:otherwise>
				<xsl:text /><xsl:value-of select="$string" /><xsl:text />
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	
	<xsl:template match="/"><xsl:apply-templates select="node()"/></xsl:template>
	<!-- bracket the dictionary items -->
	<xsl:template match="emlSubset">{<xsl:apply-templates select="node()"/>}</xsl:template>

	<!-- title -->
	<xsl:template match="title">"title":"<xsl:call-template name="translateDoubleQuotes"><xsl:with-param name="string"><xsl:copy-of select="normalize-space(descendant::text())" /></xsl:with-param></xsl:call-template>",</xsl:template>

	<!-- abstract (text only, skip <para> <literalLayout> ) -->
	<xsl:template match="abstract">"abstract":"<xsl:for-each select="descendant::text()[string-length(normalize-space(.)) > 0]"><xsl:call-template name="translateDoubleQuotes"><xsl:with-param name="string"><xsl:value-of select="normalize-space(.)" /></xsl:with-param></xsl:call-template></xsl:for-each>",</xsl:template>

	<!-- purpose  -->
	<xsl:template match="purpose">"purpose":"<xsl:for-each select="descendant::text()[string-length(normalize-space(.)) > 0]"><xsl:call-template name="translateDoubleQuotes"><xsl:with-param name="string"><xsl:value-of select="normalize-space(.)" /></xsl:for-each></xsl:with-param></xsl:call-template>",</xsl:template>

	<!-- match first keywordSet, then pick up keywords from any other keywordSets -->
	<xsl:template match="keywordSet[1]">"keywords":"<xsl:for-each select="child::keyword"><xsl:value-of select="text()" />;</xsl:for-each>
			<xsl:for-each select="following-sibling::keywordSet/keyword"><xsl:value-of select="text()" />;</xsl:for-each>",</xsl:template>
			
	<!-- source url -->
	<xsl:template match="*/physical/distribution/online/url">"source":"<xsl:value-of select = "normalize-space(.)" />",</xsl:template>

	<!-- description  -->
	<xsl:template match="workingData/item[@name='entityDesc']/text()">"desc":"<xsl:call-template name="translateDoubleQuotes"><xsl:with-param name="string"><xsl:value-of select = "normalize-space(.)" /></xsl:with-param></xsl:call-template>",</xsl:template>
	
	<!-- layer name  -->
	<xsl:template match="workingData/item[@name='layerName']/text()">"layer":"<xsl:value-of select = "normalize-space(.)" />",</xsl:template>


	<!-- suppress default behavior to copy text -->
	<xsl:template match="text()" />
</xsl:stylesheet>
