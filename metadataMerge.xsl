<?xml version="1.0"?>
<!-- Adds Geonis metadata to existing Arcgis metadata. Use with XSLTransform tool in Conversion-Metadata toolset -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:esri="http://www.esri.com/metadata/">	
	<xsl:output method="xml" indent="yes" version="1.0" encoding="UTF-8" omit-xml-declaration="no"/>
	<!-- param should be xml file that supplies supplemental values -->
	<xsl:param name="gpparam"/>
	<!-- this title will replace the one that is there, because arcgis always supplies a title -->
	<xsl:variable name="title" select="document($gpparam)//resTitle" />
	<!-- abstract and keywords copied only if no idAbs or searchKeys, respectively, exists -->
	<xsl:variable name="abstract" select="document($gpparam)//idAbs" />
	<xsl:variable name="keywords" select="document($gpparam)//searchKeys" />
	<!-- any text in idCitation/otherCitDet is saved and combined with new text -->
	<xsl:variable name="otherDetails" select="document($gpparam)//otherCitDet/text()" />

	<!-- capture any otherCitDet text -->
	<xsl:variable name="existingCitDet">
		<xsl:choose>
			<xsl:when test="//dataIdInfo/idCitation/otherCitDet" >
				<xsl:value-of select="//dataIdInfo/idCitation/otherCitDet/text()" />
			</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="''" />
			</xsl:otherwise>
		</xsl:choose>
	</xsl:variable>
	
	
	<xsl:template match="/">
		<xsl:apply-templates select="node()|@*"/>
	</xsl:template>

	<xsl:template match="node()|@*" name="identity" priority="0">
		<xsl:copy>
			 <xsl:apply-templates select="node()|@*"/>
		</xsl:copy>
	</xsl:template>
	
	<!-- suppress the copy of otherCitDet, it is a special case -->
	<xsl:template match="//dataIdInfo/idCitation/otherCitDet" priority="3">
	</xsl:template>
	
	<!-- match dataIdInfo if it doesn't have abstract. This will also add searchKeys. -->
	<xsl:template match="//dataIdInfo[not(idAbs)]" priority="1">
		<xsl:copy>
			<xsl:apply-templates select="node()|@*"/>
			<xsl:copy-of select="$abstract" />
			<xsl:if test="not(./searchKeys)" >
				<xsl:copy-of select="$keywords" />	
			</xsl:if>
		</xsl:copy>
	</xsl:template>
	
	<!-- match dataIdInfo if it doesn't have searchKeys. This will also add abstract -->
	<xsl:template match="//dataIdInfo[not(searchKeys)]" priority="1">
		<xsl:copy>
			<xsl:apply-templates select="node()|@*"/>
			<xsl:copy-of select="$keywords" />
			<xsl:if test="not(./idAbs)" >
				<xsl:copy-of select="$abstract" />	
			</xsl:if>
		</xsl:copy>
	</xsl:template>

	<!-- match idCitation node, which I think is always going to be there with data loaded into dataset.
		 Copy the node, process childred, then create the otherCitDet node and merge the text.  -->
	<xsl:template match="//dataIdInfo/idCitation" priority="2">
		<xsl:copy>
			<xsl:apply-templates select="node()|@*"/>
			<xsl:element name="otherCitDet">
				<xsl:value-of select="$existingCitDet" />
				<xsl:copy-of select="$otherDetails" />
			</xsl:element>
		</xsl:copy>
	</xsl:template>
	
	<!-- special case for the resTitle - always put in supplemental one, overwriting old one. -->
	<xsl:template match="//dataIdInfo/idCitation/resTitle" priority="2">
		<xsl:copy-of select="$title" />
	</xsl:template>

</xsl:stylesheet>