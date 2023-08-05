<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!--
      =========================================================================
      Template image_extra
      =========================================================================
  -->
  <xsl:template name="image_extra">
    <xsl:if test="$extract_cover_size and name(..)='cover'">
      <xsl:call-template name="image_ini">
        <xsl:with-param name="size" select="$extract_cover_size"/>
        <xsl:with-param name="ext" select="$extract_cover_ext"/>
        <xsl:with-param name="idx" select="1"/>
        <xsl:with-param name="target"
                        select="concat($output, $fid, $extract_cover_ext)"/>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>
