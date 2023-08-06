<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="text"/>
    <xsl:strip-space elements="*"/>
    
    <xsl:template match="article">
            <xsl:apply-templates select="back/ref-list/ref"></xsl:apply-templates>
    </xsl:template>
    
    <xsl:template match="ref"><xsl:apply-templates select="mixed-citation" mode="meta" />METADATABREAK<xsl:apply-templates select="* | node()" mode="strip"></xsl:apply-templates>LINEBREAK</xsl:template>

    <xsl:template match="mixed-citation" mode="meta"><xsl:value-of select="string-name[1]/surname" />METADATAITEM<xsl:value-of select="string-name[1]/given-names" />METADATAITEM<xsl:value-of select="article-title[1]" />METADATAITEM<xsl:value-of select="source[1]" />METADATAITEM<xsl:value-of select="year[1]" /></xsl:template>

    <xsl:template match="* | node()" mode="strip"><xsl:value-of select="normalize-space()" /></xsl:template>

</xsl:stylesheet>