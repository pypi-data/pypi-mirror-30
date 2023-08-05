<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:import href="publiset_render_base.inc.xsl"/>

  <!-- PubliForge parameters -->
  <xsl:param name="fid"/>         <!-- XML File name without extension -->
  <xsl:param name="route"/>       <!-- Route to the opener public directory -->
  <xsl:param name="main_route"/>  <!-- Route to the main public directory -->

  <!-- Overview parameters -->
  <xsl:param name="mode"/>

  <!-- Variables -->
  <xsl:variable name="img_dir"
                select="concat($main_route, 'Images/notfound.jpg#')"/>


  <xsl:output method="xml" encoding="utf-8" indent="yes"
              omit-xml-declaration="yes"/>

  <!--
      =========================================================================
      publiset
      =========================================================================
  -->
  <xsl:template match="publiset">
    <xsl:apply-templates select="composition|selection"/>
  </xsl:template>

  <!--
      =========================================================================
      composition, selection
      =========================================================================
  -->
  <xsl:template match="composition|selection">
    <xsl:choose>
      <xsl:when test="$mode='title'">
        <xsl:if test="division/head/title">
          <xsl:apply-templates
              select="division[head/title][1]/head/title" mode="text"/>
        </xsl:if>
      </xsl:when>
      <xsl:otherwise>
        <xsl:if test="division/head/title">
          <div><strong>
            <xsl:apply-templates select="division[head/title][1]/head/title"/>
          </strong></div>
          <xsl:if test="division[head/title][1]/head/subtitle">
            <div><em>
              <xsl:apply-templates
                  select="division[head/title][1]/head/subtitle"/>
            </em></div>
          </xsl:if>
        </xsl:if>
        <xsl:if test="division/head/cover">
          <div>
            <img src="{$img_dir}{division[head/cover][1]/head/cover/image/@id}"
                 height="48" alt="{$fid}"/>
          </div>
        </xsl:if>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
