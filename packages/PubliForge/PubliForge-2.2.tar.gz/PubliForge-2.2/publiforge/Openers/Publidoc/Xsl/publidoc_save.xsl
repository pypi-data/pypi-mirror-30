<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:import href="publidoc_save_base.inc.xsl"/>

  <!-- PubliForge parameters -->
  <xsl:param name="fid"/>         <!-- XML File name without extension -->
  <xsl:param name="variables"/>   <!-- Full path to variable file -->

  <!-- Variables -->
  <xsl:variable name="variables_doc" select="document($variables)"/>


  <xsl:output method="xml" encoding="utf-8" indent="yes"/>
  <xsl:strip-space elements="*"/>


  <!--
      =========================================================================
      document
      =========================================================================
  -->
  <xsl:template match="document">
    <xsl:variable name="num" select="0"/>

    <xsl:copy>
      <xsl:apply-templates select="$variables_doc/*/*/group[@name='head']"
                           mode="head">
        <xsl:with-param name="num" select="$num"/>
        <xsl:with-param name="node" select="."/>
      </xsl:apply-templates>
      <xsl:apply-templates select="$variables_doc/*/*/group[@name='document']"
                           mode="corpus">
        <xsl:with-param name="num" select="$num"/>
        <xsl:with-param name="node" select="."/>
      </xsl:apply-templates>
    </xsl:copy>
  </xsl:template>

  <!--
      =========================================================================
      topic
      =========================================================================
  -->
  <xsl:template match="topic">
    <xsl:variable name="num" select="count(preceding::topic)"/>

    <xsl:copy>
      <xsl:apply-templates select="$variables_doc/*/*/group[@name='head']"
                           mode="head">
        <xsl:with-param name="num" select="$num"/>
        <xsl:with-param name="node" select="."/>
      </xsl:apply-templates>
      <xsl:apply-templates select="$variables_doc/*/*/group[@name='topic']"
                           mode="corpus">
        <xsl:with-param name="num" select="$num"/>
        <xsl:with-param name="node" select="."/>
      </xsl:apply-templates>
    </xsl:copy>
  </xsl:template>

  <!--
      =========================================================================
      glossary
      =========================================================================
  -->
  <xsl:template match="glossary">
    <xsl:variable name="num" select="count(preceding::glossary)"/>

    <xsl:copy>
      <xsl:apply-templates
          select="$variables_doc/*/*/group[@name='head_glossary']"
          mode="head">
        <xsl:with-param name="num" select="$num"/>
        <xsl:with-param name="node" select="."/>
      </xsl:apply-templates>
      <xsl:apply-templates select="$variables_doc/*/*/group[@name='glossary']"
                           mode="corpus">
        <xsl:with-param name="num" select="$num"/>
        <xsl:with-param name="node" select="."/>
      </xsl:apply-templates>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
