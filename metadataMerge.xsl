<?xml version="1.0"?>
<!-- Adds Geonis metadata to existing Arcgis metadata. Use with XSLTransform tool in Conversion-Metadata toolset -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:esri="http://www.esri.com/metadata/">	
	<xsl:output method="xml" indent="no" version="1.0" encoding="UTF-8" omit-xml-declaration="no"/>
	<!-- param should be xml file that supplies supplemental values -->
	<xsl:param name="gpparam"/>
	<!-- this title will replace the one that is there, because arcgis always supplies a title -->
	<xsl:variable name="title" select="document($gpparam)//resTitle" />
	<!-- abstract, purpose, keywords copied only if they are not present -->
	<xsl:variable name="abstract" select="document($gpparam)//idAbs" />
	<xsl:variable name="purpose" select="document($gpparam)//idPurp" />
	<xsl:variable name="keywords" select="document($gpparam)//searchKeys" />
	<!--for these, we point to the text node, as all we need is the value  -->
	<xsl:variable name="dataURL" select="document($gpparam)//aggrInfo/aggrDSName/citOnlineRes/linkage/text()" />
	<xsl:variable name="packageId" select="document($gpparam)//aggrInfo/aggrDSName/citId/identCode/text()" />
	<xsl:variable name="loadDate" select="document($gpparam)//aggrInfo/aggrDSName/date/pubDate/text()" />
		
	
	<xsl:template match="/">
		<xsl:apply-templates select="node()|@*"/>
	</xsl:template>

	<!-- remove white space while we're at it -->
	<xsl:template match="text()">
		<xsl:value-of select="normalize-space(.)" />
	</xsl:template>
	
	<!-- match and copy everything (that doesn't fall into another template) -->
	<xsl:template match="node()|@*" name="identity" priority="0">
		<xsl:copy>
			 <xsl:apply-templates select="node()|@*"/>
		</xsl:copy>
	</xsl:template>
		
	<!-- match dataIdInfo if it doesn't have one of the nodes we have. -->
	<xsl:template match="//dataIdInfo[not(idAbs) or not(idPurp) or not(searchKeys)]" priority="1">
		<xsl:copy>
			<xsl:apply-templates select="node()|@*"/>
			<xsl:if test="not(./idAbs)" >
				<xsl:copy-of select="$abstract" />
			</xsl:if>
			<xsl:if test="not(./searchKeys)" >
				<xsl:copy-of select="$keywords" />	
			</xsl:if>
			<xsl:if test="not(./idPurp)" >
				<xsl:copy-of select="$purpose" />	
			</xsl:if>
			<xsl:call-template name="makeAggrInfo" />
		</xsl:copy>
	</xsl:template>
	
	<!-- match dataIdInfo for cases where it didn't match above -->
	<xsl:template match="//dataIdInfo" priority="1">
		<xsl:copy>
			<xsl:apply-templates select="node()|@*"/>
			<xsl:call-template name="makeAggrInfo" />
		</xsl:copy>
	</xsl:template>
	
	<xsl:template name="makeAggrInfo">
		<xsl:element name="aggrInfo">
			<xsl:element name="assocType">
				<xsl:element name="AscTypeCd"><xsl:attribute name="value">004</xsl:attribute></xsl:element>
			</xsl:element>
			<xsl:element name="aggrDSName">
				<xsl:element name="resTitle">
					<xsl:value-of select="$title/text()" />
				</xsl:element>
				<xsl:element name="date">
					<xsl:element name="pubDate">
						<xsl:value-of select="$loadDate" />
					</xsl:element>
				</xsl:element>
				<xsl:element name="citOnlineRes">
					<xsl:element name="linkage">
						<xsl:value-of select="$dataURL" />
					</xsl:element>
					<xsl:element name="orDesc"><xsl:text>Data online resource</xsl:text>
					</xsl:element>
					<xsl:element name="orFunct">
						<xsl:element name="OnFunctCd" ><xsl:attribute name="value">001</xsl:attribute></xsl:element>
					</xsl:element>
				</xsl:element>
				<xsl:element name="citId">
					<xsl:element name="identCode">
						<xsl:value-of select="$packageId" />
					</xsl:element>
				</xsl:element>				
			</xsl:element>									
		</xsl:element>
	</xsl:template>

		
	<!-- special case for the resTitle - always put in supplemental one, overwriting old one. -->
	<xsl:template match="//dataIdInfo/idCitation/resTitle" priority="2">
		<xsl:copy-of select="$title" />
	</xsl:template>

</xsl:stylesheet>