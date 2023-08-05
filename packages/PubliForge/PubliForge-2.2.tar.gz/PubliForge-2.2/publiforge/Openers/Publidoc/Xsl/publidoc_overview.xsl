<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:import href="publidoc2xhtml_template.inc.xsl"/>
  <xsl:import href="publidoc2xhtml_base.inc.xsl"/>

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
      publidoc
      =========================================================================
  -->
  <xsl:template match="publidoc">
    <xsl:apply-templates select="document|topic|glossary"/>
  </xsl:template>

  <!--
      =========================================================================
      document, topic
      =========================================================================
  -->
  <xsl:template match="document|topic">
    <xsl:choose>
      <xsl:when test="$mode='title'">
        <xsl:call-template name="title_text"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:call-template name="overview"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      glossary
      =========================================================================
  -->
  <xsl:template match="glossary">
    <xsl:if test="not($mode)">
      <div>
        <xsl:apply-templates select="entry[1]/mainterm" mode="text"/>
        <xsl:if test="count(entry) &gt; 1">
          <xsl:value-of select="concat('… + ', count(entry)-1)"/>
        </xsl:if>
      </div>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>
