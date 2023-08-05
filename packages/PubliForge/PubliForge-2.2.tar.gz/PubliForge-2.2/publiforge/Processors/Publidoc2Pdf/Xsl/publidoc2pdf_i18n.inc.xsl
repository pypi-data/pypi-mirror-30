<?xml version='1.0' encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:variable name="i18n_bibliography">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Bibliographie</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Bibliografía</xsl:when>
      <xsl:otherwise>Bibliography</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
</xsl:stylesheet>
