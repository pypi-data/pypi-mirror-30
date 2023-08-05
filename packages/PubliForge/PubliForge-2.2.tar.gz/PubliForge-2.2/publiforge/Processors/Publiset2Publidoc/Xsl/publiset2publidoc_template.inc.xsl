<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!--
      =========================================================================
      Template image_extension
      =========================================================================
  -->
  <xsl:template name="image_extension">
    <xsl:choose>
      <xsl:when test="processing-instruction('tune-html-img-format')">
        <xsl:text>.</xsl:text>
        <xsl:value-of
            select="normalize-space(processing-instruction('tune-html-img-format'))"/>
      </xsl:when>
      <xsl:when test="ancestor::cover">
        <xsl:value-of select="$img_ext_cover"/>
      </xsl:when>
      <xsl:when test="@type='animation'">.gif</xsl:when>
      <xsl:when test="ancestor::hotspot">.png</xsl:when>
      <xsl:when test="ancestor::dropzone">.png</xsl:when>
      <xsl:when test="@type='icon' or not(ancestor::media)">
        <xsl:value-of select="$img_ext_icon"/>
      </xsl:when>
      <xsl:when test="contains($img_ext, '+')">
        <xsl:value-of select="substring-before($img_ext, '+')"/>
      </xsl:when>
      <xsl:otherwise><xsl:value-of select="$img_ext"/></xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      Template image_size
      =========================================================================
  -->
  <xsl:template name="image_size">
    <xsl:choose>
      <xsl:when test="processing-instruction('tune-html-img-size')">
        <xsl:value-of
            select="normalize-space(processing-instruction('tune-html-img-size'))"/>
      </xsl:when>
      <xsl:when test="@type='thumbnail' or ancestor::match
                      or ancestor::right or ancestor::wrong
                      or (ancestor::item and not(ancestor::list))">
        <xsl:value-of select="$img_size_thumbnail"/>
      </xsl:when>
      <xsl:when test="@type='cover' or ancestor::cover">
        <xsl:value-of select="$img_size_cover"/>
      </xsl:when>
      <xsl:when test="ancestor::header or ancestor::footer">
        <xsl:value-of select="$img_size_header"/>
      </xsl:when>
      <xsl:when test="ancestor::blanks-media and not(ancestor::dropzone)">
        <xsl:value-of select="$img_size"/>
      </xsl:when>
      <xsl:when test="ancestor::blanks-media">
        <xsl:value-of select="$img_size_thumbnail"/>
      </xsl:when>
      <xsl:when test="@type='icon' or not(ancestor::media)">
        <xsl:value-of select="$img_size_icon"/>
      </xsl:when>
      <xsl:otherwise><xsl:value-of select="$img_size"/></xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
