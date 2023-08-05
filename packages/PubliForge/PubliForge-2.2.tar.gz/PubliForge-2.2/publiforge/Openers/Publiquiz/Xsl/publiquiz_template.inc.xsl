<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!--
      *************************************************************************
                                   CALLABLE TEMPLATES
      *************************************************************************
  -->
  <!--
      =========================================================================
      Template quiz_engine
      =========================================================================
  -->
  <xsl:template name="quiz_engine">
    <xsl:param name="node" select="."/>
    <xsl:choose>
      <xsl:when test="$node/choices-radio">choices-radio</xsl:when>
      <xsl:when test="$node/choices-check">choices-check</xsl:when>
      <xsl:when test="$node/blanks-fill">blanks-fill</xsl:when>
      <xsl:when test="$node/blanks-select">blanks-select</xsl:when>
      <xsl:when test="$node/blanks-media">blanks-media</xsl:when>
      <xsl:when test="$node/blanks-choices">blanks-choices</xsl:when>
      <xsl:when test="$node/correct-line">correct-line</xsl:when>
      <xsl:when test="$node/pointing">pointing</xsl:when>
      <xsl:when test="$node/pointing-categories">pointing-categories</xsl:when>
      <xsl:when test="$node/matching">matching</xsl:when>
      <xsl:when test="$node/sort">sort</xsl:when>
      <xsl:when test="$node/categories">categories</xsl:when>
      <xsl:when test="$node/production">production</xsl:when>
      <xsl:when test="$node/wordsearch">wordsearch</xsl:when>
      <xsl:when test="$node/flashcard">flashcard</xsl:when>
      <xsl:when test="$node/coloring">coloring</xsl:when>
      <xsl:when test="$node/memory">memory</xsl:when>
      <xsl:when test="$node/composite">composite</xsl:when>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
