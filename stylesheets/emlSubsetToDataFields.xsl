<?xml version="1.0"?>
<!-- Converts nodes from EMLSubset file into python object -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" >
	<xsl:output method="text"/>
	
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

	<!-- escape double quotes -->
	<xsl:strip-space elements="*"/>

	<xsl:param name="pPattern">"</xsl:param>
	<xsl:param name="pReplacement">\"</xsl:param>

	<xsl:template match="node()|@*">
	    <xsl:copy>
		    <xsl:apply-templates select="node()|@*"/>
	    </xsl:copy>
	</xsl:template>

	<xsl:template match="statement1/text()" name="replace">
		<xsl:param name="pText" select="."/>
		<xsl:param name="pPat" select="$pPattern"/>
		<xsl:param name="pRep" select="$pReplacement"/>

		 <xsl:choose>
	  <xsl:when test="not(contains($pText, $pPat))">
	   <xsl:copy-of select="$pText"/>
	  </xsl:when>
	  <xsl:otherwise>
	   <xsl:copy-of select="substring-before($pText, $pPat)"/>
	   <xsl:copy-of select="$pRep"/>
	   <xsl:call-template name="replace">
	    <xsl:with-param name="pText" select=
	         "substring-after($pText, $pPat)"/>
	    <xsl:with-param name="pPat" select="$pPat"/>
	    <xsl:with-param name="pRep" select="$pRep"/>
	   </xsl:call-template>
	  </xsl:otherwise>
	 </xsl:choose>
	 </xsl:template>


	<!-- suppress default behavior to copy text -->
	<xsl:template match="text()" />
</xsl:stylesheet>
