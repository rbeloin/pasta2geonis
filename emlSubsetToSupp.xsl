<?xml version="1.0"?>
<!-- Copies nodes from EMLSubset file into a metadata supplement file that will be used to supplement metadata
	Output nodes are compatible with Arcgis metadata, and are sometimes copied as is into metadata file. -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:eml="eml://ecoinformatics.org/eml-2.1.0"  xmlns:xs="http://www.w3.org/2001/XMLSchema" >	

	<xsl:output method="xml" indent="no" version="1.0" encoding="UTF-8" omit-xml-declaration="no"/>
	<!-- reduce these to single text node by removing empty text nodes -->
	<xsl:strip-space elements="title abstract purpose" />

	<xsl:template match="/">
		<xsl:apply-templates select="node()"/>
	</xsl:template>
	
	<xsl:template match="/emlSubset">
		<xsl:element name="dataIdInfo">
			<xsl:apply-templates select="node()"/>
		</xsl:element>
	</xsl:template>
	
	<!-- match link to data, write the aggrInfo node -->
	<xsl:template match="*/physical/distribution/online/url">
		<xsl:element name="aggrInfo">
			<xsl:element name="aggrDSName">
				<xsl:element name="citId">
					<xsl:element name="identCode">
						<xsl:value-of select="/emlSubset/@packageId" />
					</xsl:element>
				</xsl:element>
				<xsl:element name="citOnlineRes">
					<xsl:element name="linkage">
						<xsl:copy-of select="./text()" />
					</xsl:element>
				</xsl:element>
			</xsl:element>
		</xsl:element>
	</xsl:template>

	<!-- title -->
	<xsl:template match="title">
		<xsl:element name="idCitation">
			<xsl:element name="resTitle">
				<xsl:copy-of select="normalize-space(descendant::text())" />
			</xsl:element>
		</xsl:element>
	</xsl:template>

	<!-- abstract (text only, skip <para> ) -->
	<xsl:template match="abstract">
		<xsl:element name="idAbs">
			<xsl:value-of select="normalize-space(descendant::text())" />
		</xsl:element>
	</xsl:template>

	<!-- purpose  (text only, skip <para> ) -->
	<xsl:template match="purpose">
		<xsl:element name="idPurp">
			<xsl:value-of select="normalize-space(descendant::text())" />
		</xsl:element>
	</xsl:template>

	
	<!-- match first keywordSet, then pick up keywords from any other keywordSets -->
	<xsl:template match="keywordSet[1]">
		<xsl:element name="searchKeys">
			<xsl:for-each select="child::keyword">
				<xsl:element name="keyword">
					<xsl:value-of select="text()" />
				</xsl:element>
			</xsl:for-each>
			<xsl:for-each select="following-sibling::keywordSet/keyword">
				<xsl:element name="keyword">
					<xsl:value-of select="text()" />
				</xsl:element>
			</xsl:for-each>
		</xsl:element>
	</xsl:template>
	
	<!-- suppress default behavior to copy text -->
	<xsl:template match="text()">
	</xsl:template>
	
</xsl:stylesheet>