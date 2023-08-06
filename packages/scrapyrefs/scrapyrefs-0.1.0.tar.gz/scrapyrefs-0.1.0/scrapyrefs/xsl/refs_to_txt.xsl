<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="text"/>
    <xsl:strip-space elements="*"/>
    
    <xsl:template match="article">
            <xsl:apply-templates select="back/ref-list/ref"></xsl:apply-templates>
    </xsl:template>
    
    <xsl:template match="ref"><xsl:apply-templates select="* | node()" mode="strip"></xsl:apply-templates>LINEBREAK</xsl:template>

    <xsl:template match="* | node()" mode="strip"><xsl:value-of select="normalize-space()" /></xsl:template>

</xsl:stylesheet>