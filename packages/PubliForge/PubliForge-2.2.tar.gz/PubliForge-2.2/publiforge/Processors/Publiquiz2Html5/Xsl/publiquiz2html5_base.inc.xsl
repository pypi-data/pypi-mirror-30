<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml">

  <!--
      *************************************************************************
                                   COMPONENT LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      document mode onefiletoc
      =========================================================================
  -->
  <xsl:template match="document" mode="onefiletoc">
    <xsl:if test="$toc">
      <h2><xsl:value-of select="$i18n_toc"/></h2>
      <div class="pdocOneFile pdocToc">
        <ul>
          <xsl:apply-templates select="division|topic|quiz" mode="onefiletoc"/>
        </ul>
      </div>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      quiz mode meta
      =========================================================================
  -->
  <xsl:template match="quiz" mode="meta">
    <xsl:if
        test="@id or ../@id or @type or ../@type or @xml:lang or ../@xml:lang
              or head/title or head/shorttitle or head/subtitle
              or head/identifier or head/copyright or head/collection
              or head/contributors or head/date or head/place or head/source
              or head/keywordset or head/subjectset or head/abstract
              or head/cover or head/annotation">
      <table class="pdocMeta">
        <xsl:apply-templates
            select="@id|../@id|@type|../@type|@xml:lang|../@xml:lang
                    |head/title|head/shorttitle|head/subtitle|head/identifier
                    |head/copyright|head/collection|head/contributors
                    |head/date|head/place|head/source|head/keywordset
                    |head/subjectset|head/abstract|head/cover|head/annotation"
            mode="meta_item"/>
        <xsl:if test="choices-radio|choices-check
                      |blanks-fill|blanks-select|blanks-media|correct-line
                      |pointing|pointing-categories|matching|sort|categories
                      |wordsearch|coloring|memory|production|composite">
          <xsl:for-each select="choices-radio/@*|choices-check/@*
                                |blanks-fill/@*|blanks-select/@*|blanks-media/@*|correct-line/@*
                                |pointing/@*|pointing-categories/@*|matching/@*|sort/@*
                                |wordsearch/@*|categories/@*|coloring/@*|memory/@*
                                |production/@*|composite/@*">
            <tr class="pquizAttribute">
              <th>
                <xsl:value-of select="name()"/>
              </th>
              <td>
                <xsl:value-of select="."/>
              </td>
            </tr>
          </xsl:for-each>
        </xsl:if>
      </table>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      quiz mode onefiletoc
      =========================================================================
  -->
  <xsl:template match="quiz" mode="onefiletoc">
    <xsl:if test="$toc and ancestor::document and head/title">
      <li>
        <a>
          <xsl:attribute name="href">
            <xsl:text>#</xsl:text>
            <xsl:choose>
              <xsl:when test="@xml:id"><xsl:value-of select="@xml:id"/></xsl:when>
              <xsl:when test="@id"><xsl:value-of select="@id"/></xsl:when>
              <xsl:otherwise>
                <xsl:value-of select="concat('quz', count(preceding::quiz)+1)"/>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:attribute>
          <xsl:call-template name="quiz_toc_title"/>
        </a>
      </li>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      quiz mode onefile
      =========================================================================
  -->
  <xsl:template match="quiz" mode="onefile">
    <xsl:choose>
      <xsl:when test="memory"/>
      <xsl:otherwise>
        <div>
          <xsl:attribute name="id">
            <xsl:choose>
              <xsl:when test="@xml:id"><xsl:value-of select="@xml:id"/></xsl:when>
              <xsl:when test="@id"><xsl:value-of select="@id"/></xsl:when>
              <xsl:otherwise>
                <xsl:value-of select="concat('quz', count(preceding::quiz)+1)"/>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:attribute>
          <xsl:attribute name="class">
            <xsl:text>pquizQuiz pquizQuizOneFile</xsl:text>
            <xsl:if test="@type"> pquizQuiz-<xsl:value-of select="@type"/></xsl:if>
            <xsl:if test="ancestor::division">
              <xsl:value-of select="concat(' depth', count(ancestor::division)+1)"/>
            </xsl:if>
          </xsl:attribute>
          <xsl:if test="head/title">
            <xsl:choose>
              <xsl:when test="count(ancestor::division)=0">
            <h2><xsl:apply-templates select="head/title"/></h2>
              </xsl:when>
              <xsl:when test="count(ancestor::division)=1">
                <h3><xsl:apply-templates select="head/title"/></h3>
              </xsl:when>
              <xsl:otherwise>
                <h4><xsl:apply-templates select="head/title"/></h4>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:if>
          <xsl:if test="head/subtitle">
            <xsl:choose>
              <xsl:when test="count(ancestor::division)=0">
                <h3><xsl:call-template name="subtitle"/></h3>
              </xsl:when>
              <xsl:when test="count(ancestor::division)=1">
                <h4><xsl:call-template name="subtitle"/></h4>
              </xsl:when>
              <xsl:otherwise>
                <h5><xsl:call-template name="subtitle"/></h5>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:if>
          <xsl:apply-templates select="." mode="corpus"/>
          <div class="clear"><xsl:text> </xsl:text></div>
        </div>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      quiz mode toc
      =========================================================================
  -->
  <xsl:template match="quiz" mode="toc">
    <xsl:if test="head/title">
      <li id="quz{count(preceding::quiz)+1}">
        <a href="{$fid}-quz-{format-number(count(preceding::quiz)+1, '0000')}{$html_ext}">
          <xsl:call-template name="quiz_toc_title"/>
        </a>
      </li>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      quiz mode file
      =========================================================================
  -->
  <xsl:template match="quiz" mode="file">
    <xsl:call-template name="html_file">
      <xsl:with-param name="name"
                      select="concat($fid, '-quz-',
                              format-number(count(preceding::quiz)+1, '0000'))"/>

      <xsl:with-param name="title">
        <xsl:if test="/*/*/head/title">
          <xsl:apply-templates select="/*/*/head/title" mode="text"/>
        </xsl:if>
        <xsl:if test="head/title">
          <xsl:if test="/*/*/head/title"><xsl:value-of select="$str_sep"/></xsl:if>
          <xsl:apply-templates select="head/title" mode="text"/>
        </xsl:if>
        <xsl:if test="not(/*/*/head/title) and not (head/title)">
          <xsl:value-of select="$fid"/>
        </xsl:if>
      </xsl:with-param>

      <xsl:with-param name="body">
        <body>
          <xsl:attribute name="class">
            <xsl:text>pquizQuiz</xsl:text>
            <xsl:if test="@type"> pquizQuiz-<xsl:value-of select="@type"/></xsl:if>
            <xsl:if test="ancestor::division">
              <xsl:value-of select="concat(' depth', count(ancestor::division)+1)"/>
              <xsl:for-each select="ancestor::division">
                <xsl:if test="@type"> pdocDivision-<xsl:value-of select="@type"/></xsl:if>
              </xsl:for-each>
            </xsl:if>
          </xsl:attribute>
          <xsl:call-template name="navigation"/>
          <xsl:call-template name="lead"/>
          <xsl:call-template name="anchor_levels"/>

          <xsl:if test="head/title">
            <h1>
              <span class="pdocTitle">
                <xsl:apply-templates select="head/title"/>
              </span>
            </h1>
          </xsl:if>
          <xsl:if test="head/subtitle">
            <h2><xsl:call-template name="subtitle"/></h2>
          </xsl:if>
          <form action="#" method="post">
            <xsl:apply-templates select="." mode="corpus"/>
            <xsl:call-template name="quiz_action"/>
          </form>

          <xsl:call-template name="navigation">
            <xsl:with-param name="bottom" select="1"/>
          </xsl:call-template>
        </body>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:template>

  <!--
      =========================================================================
      quiz mode corpus
      =========================================================================
  -->
  <xsl:template match="quiz" mode="corpus">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>
    <xsl:variable name="engine">
      <xsl:call-template name="quiz_engine"/>
    </xsl:variable>
    <xsl:variable name="engine_options">
      <xsl:call-template name="quiz_engine_options"/>
    </xsl:variable>

    <div data-quiz-id="{$quiz_id}" data-engine="{$engine}"
         data-context-key="{$context_key}" data-context-ttl="{$context_ttl}">
      <xsl:attribute name="class">
        <xsl:value-of select="@id"/>
        <xsl:if test="not(memory)"> publiquiz</xsl:if>
        <xsl:if test="memory"> pquizMemory</xsl:if>
        <xsl:if test="*/@nomark='true' or coloring[not(areas)]"> pquizNoMark</xsl:if>
      </xsl:attribute>
      <xsl:if test="$engine_options!=''">
        <xsl:attribute name="data-engine-options">
          <xsl:value-of select="normalize-space($engine_options)"/>
        </xsl:attribute>
      </xsl:if>
      <xsl:if test="*/@display">
        <xsl:attribute name="data-engine-display">
          <xsl:value-of select="*/@display"/>
        </xsl:attribute>
      </xsl:if>
      <xsl:apply-templates select="instructions"/>
      <xsl:apply-templates
          select="choices-radio|choices-check|blanks-fill|blanks-select
                  |blanks-media|correct-line|blanks-choices
                  |pointing|pointing-categories|matching|sort|categories
                  |wordsearch|flashcard|coloring|memory|production|composite"/>
      <xsl:apply-templates select="help|answer"/>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      subquiz
      =========================================================================
  -->
  <xsl:template match="subquiz">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>
    <xsl:variable name="engine">
      <xsl:call-template name="quiz_engine"/>
    </xsl:variable>
    <xsl:variable name="engine_options">
      <xsl:call-template name="quiz_engine_options"/>
    </xsl:variable>

    <li class="pquizElement" data-quiz-id="{$quiz_id}" data-engine="{$engine}">
      <xsl:if test="$engine_options!=''">
        <xsl:attribute name="data-engine-options">
          <xsl:value-of select="normalize-space($engine_options)"/>
        </xsl:attribute>
      </xsl:if>
      <xsl:if test="ancestor::composite[@multipage='true']">
        <p class="pdocP pquizNumbering"><xsl:text> </xsl:text></p>
      </xsl:if>
      <xsl:apply-templates select="instructions"/>
      <xsl:apply-templates
          select="choices-radio|choices-check|blanks-fill|blanks-select
                  |blanks-media|correct-line|blanks-choices
                  |pointing|pointing-categories|matching|sort|categories
                  |production"/>
      <xsl:apply-templates select="help|answer"/>
    </li>
  </xsl:template>


  <!--
      *************************************************************************
                                   SECTION LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      instructions
      =========================================================================
  -->
  <xsl:template match="instructions">
    <div class="pquizInstructions">
      <xsl:if test="head/title">
        <div class="pquizInstructionsTitle">
          <xsl:apply-templates select="head/title"/>
        </div>
      </xsl:if>
      <xsl:if test="head/subtitle">
        <div class="pquizInstructionsSubtitle">
          <xsl:call-template name="subtitle"/>
        </div>
      </xsl:if>
      <xsl:apply-templates
          select="section|p|speech|list|blockquote|table|media"/>
      <xsl:apply-templates select="head/audio" mode="header"/>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      choices-radio & choices-check
      =========================================================================
  -->
  <xsl:template match="choices-radio|choices-check">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <div id="{$quiz_id}_engine" class="pquizEngine">
      <div id="{$quiz_id}_correct" class="hidden">
        <xsl:for-each select="right">
          <xsl:value-of select="format-number(count(preceding-sibling::right
                                |preceding-sibling::wrong)+1, '000')"/>
          <xsl:text>x</xsl:text>
          <xsl:if test="count(following-sibling::right)">::</xsl:if>
        </xsl:for-each>
        <xsl:if test="not(right)"><xsl:text> </xsl:text></xsl:if>
      </div>

      <xsl:choose>
        <xsl:when test="$mode_choices_check='radio'">
          <xsl:call-template name="choices_check_mode_radio">
            <xsl:with-param name="quiz_id" select="$quiz_id"/>
          </xsl:call-template>
        </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name="choices_basic">
            <xsl:with-param name="quiz_id" select="$quiz_id"/>
          </xsl:call-template>
        </xsl:otherwise>
      </xsl:choose>
    </div>
  </xsl:template>

  <xsl:template name="choices_basic">
    <xsl:param name="quiz_id"/>
    <ul class="pquizChoices">
      <xsl:for-each select="right|wrong">
        <li id="{concat($quiz_id, '_', format-number(
                count(preceding-sibling::right|preceding-sibling::wrong)+1, '000'))}">
          <xsl:attribute name="class">
            <xsl:text>pquizChoice</xsl:text>
            <xsl:if test="ancestor::choices-radio">
              <xsl:text> pquizChoiceRadio</xsl:text>
            </xsl:if>
            <xsl:if test="ancestor::choices-check">
              <xsl:text> pquizChoiceCheckbox</xsl:text>
            </xsl:if>
          </xsl:attribute>
          <input>
            <xsl:choose>
              <xsl:when test="name(..)='choices-radio'">
                <xsl:attribute name="name"><xsl:value-of select="$quiz_id"/></xsl:attribute>
                <xsl:attribute name="type">radio</xsl:attribute>
              </xsl:when>
              <xsl:when test="name(..)='choices-check'">
                <xsl:attribute name="type">checkbox</xsl:attribute>
              </xsl:when>
            </xsl:choose>
          </input>
          <xsl:text> </xsl:text>
          <xsl:choose>
            <xsl:when test="p">
              <xsl:apply-templates select="p/node()"/>
            </xsl:when>
            <xsl:otherwise>
              <xsl:apply-templates/>
            </xsl:otherwise>
          </xsl:choose>
        </li>
      </xsl:for-each>
    </ul>
  </xsl:template>

  <xsl:template name="choices_check_mode_radio">
    <xsl:param name="quiz_id"/>
    <table>
      <tr>
        <th> </th>
        <th><xsl:value-of select="$i18n_true"/></th>
        <th><xsl:value-of select="$i18n_false"/></th>
      </tr>
      <xsl:for-each select="right|wrong">
        <tr>
          <td><xsl:apply-templates/></td>
          <td class="pquizChoice pquizChoiceRadio"
              data-group="{format-number(count(preceding-sibling::*)+1, '000')}"
              data-name="true">
            <input type="radio">
              <xsl:attribute name="name">
                <xsl:value-of select="concat($quiz_id, '-', count(preceding-sibling::*))"/>
              </xsl:attribute>
            </input>
          </td>
          <td class="pquizChoice pquizChoiceRadio"
              data-group="{format-number(count(preceding-sibling::*)+1, '000')}"
              data-name="false">
            <input type="radio">
              <xsl:attribute name="name">
                <xsl:value-of select="concat($quiz_id, '-', count(preceding-sibling::*))"/>
              </xsl:attribute>
            </input>
          </td>
        </tr>
      </xsl:for-each>
    </table>
  </xsl:template>

  <!--
      =========================================================================
      blanks-fill
      =========================================================================
  -->
  <xsl:template match="blanks-fill">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <div id="{$quiz_id}_engine" class="pquizEngine">
      <div id="{$quiz_id}_correct" class="hidden">
        <xsl:for-each select=".//blank">
          <xsl:call-template name="blank_num"/>
          <xsl:choose>
            <xsl:when test="s">
              <xsl:for-each select="s">
                <xsl:value-of select="normalize-space()"/>
                <xsl:if test="count(following-sibling::s)">|</xsl:if>
              </xsl:for-each>
            </xsl:when>
            <xsl:otherwise>
              <xsl:value-of select="normalize-space()"/>
            </xsl:otherwise>
          </xsl:choose>
          <xsl:call-template name="blank_separator"/>
        </xsl:for-each>
        <xsl:if test="not(normalize-space(.//blank))">
          <xsl:text> </xsl:text>
        </xsl:if>
      </div>

      <div class="pquizText">
        <xsl:apply-templates
            select="section|p|speech|list|blockquote|table|media"/>
      </div>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      blanks-select
      =========================================================================
  -->
  <xsl:template match="blanks-select">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <div id="{$quiz_id}_engine" class="pquizEngine">
      <div id="{$quiz_id}_correct" class="hidden">
        <xsl:for-each select=".//blank[not(ancestor::intruders)]">
          <xsl:call-template name="blank_num"/>
          <xsl:choose>
            <xsl:when test="s">
              <xsl:for-each select="s">
                <xsl:call-template name="make_id">
                  <xsl:with-param name="item" select="."/>
                </xsl:call-template>
                <xsl:if test="count(following-sibling::s)">|</xsl:if>
              </xsl:for-each>
            </xsl:when>
            <xsl:otherwise>
              <xsl:call-template name="make_id">
                <xsl:with-param name="item" select="."/>
              </xsl:call-template>
            </xsl:otherwise>
          </xsl:choose>
          <xsl:call-template name="blank_separator"/>
        </xsl:for-each>
        <xsl:if test="not(normalize-space(.//blank[not(ancestor::intruders)]))">
          <xsl:text> </xsl:text>
        </xsl:if>
      </div>

      <xsl:choose>
        <!-- mode combobox -->
        <xsl:when
            test="(((not(ancestor::composite) and not(ancestor::quiz/processing-instruction('argument')))
                  or (ancestor::composite and not(contains(ancestor::quiz/processing-instruction('argument'), 'blanks-select:'))))
                  and $mode_blanks_select='combobox')
                  or (not(ancestor::composite) and ancestor::quiz/processing-instruction('argument')='combobox')
                  or contains(ancestor::quiz/processing-instruction('argument'), 'blanks-select:combobox')">
          <xsl:call-template name="blanks_select_combobox">
            <xsl:with-param name="quiz_id" select="$quiz_id"/>
          </xsl:call-template>
        </xsl:when>
        <!-- mode dragndrop -->
        <xsl:otherwise>
          <xsl:call-template name="blanks_select_dragndrop">
            <xsl:with-param name="quiz_id" select="$quiz_id"/>
          </xsl:call-template>
        </xsl:otherwise>
      </xsl:choose>
    </div>
  </xsl:template>

  <!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
  <xsl:template name="blanks_select_dragndrop">
    <xsl:param name="quiz_id"/>
    <xsl:if test="not(@orientation='east' or @orientation='south')">
      <xsl:call-template name="blanks_select_items">
        <xsl:with-param name="quiz_id" select="$quiz_id"/>
      </xsl:call-template>
    </xsl:if>
    <xsl:if test="not(@orientation)">
      <div class="clear"><xsl:text> </xsl:text></div>
    </xsl:if>
    <div>
      <xsl:attribute name="class">
        <xsl:text>pquizText</xsl:text>
        <xsl:if test="@orientation='east' or @orientation='west'">
          <xsl:text> pquizDropFloat</xsl:text>
        </xsl:if>
      </xsl:attribute>
      <xsl:apply-templates
          select="section|p|speech|list|blockquote|table|media"/>
    </div>
    <xsl:if test="@orientation='south'">
      <div class="clear"><xsl:text> </xsl:text></div>
    </xsl:if>
    <xsl:choose>
      <xsl:when test="@orientation='east' or @orientation='south'">
        <xsl:call-template name="blanks_select_items">
          <xsl:with-param name="quiz_id" select="$quiz_id"/>
        </xsl:call-template>
        <div class="clear"><xsl:text> </xsl:text></div>
      </xsl:when>
      <xsl:otherwise>
        <div class="clear"><xsl:text> </xsl:text></div>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="blanks_select_items">
    <xsl:param name="quiz_id"/>
    <div id="{$quiz_id}_items">
      <xsl:attribute name="class">
        <xsl:text>pquizItems</xsl:text>
        <xsl:if test="@orientation='east' or @orientation='west'">
          <xsl:text> pquizPickFloat</xsl:text>
        </xsl:if>
      </xsl:attribute>
      <xsl:text> </xsl:text>
      <xsl:choose>
        <xsl:when test="@no-shuffle='alpha'">
          <xsl:for-each select=".//blank[not(*)]|.//blank/s|intruders/blank">
            <xsl:sort/>
            <xsl:call-template name="blanks_select_item">
              <xsl:with-param name="quiz_id" select="$quiz_id"/>
            </xsl:call-template>
          </xsl:for-each>
        </xsl:when>
        <xsl:otherwise>
          <xsl:for-each select=".//blank[not(*)]|.//blank/s|intruders/blank">
            <xsl:call-template name="blanks_select_item">
              <xsl:with-param name="quiz_id" select="$quiz_id"/>
            </xsl:call-template>
          </xsl:for-each>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:if test="not(.//blank)"><xsl:text> </xsl:text></xsl:if>
    </div>
  </xsl:template>

  <!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
  <xsl:template name="blanks_select_combobox">
    <xsl:param name="quiz_id"/>

    <div class="pquizText">
      <xsl:apply-templates
          select="section|p|speech|list|blockquote|table|media"/>
    </div>
  </xsl:template>

  <!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
  <xsl:template name="blanks_select_item">
    <xsl:param name="quiz_id"/>
    <xsl:if test="not(ancestor::blanks-select[@multiple='true']|ancestor::blanks-select[@multiple='strict']) or
                  count((preceding::blank[not(*)]|preceding::blank/s)[normalize-space()=normalize-space(current())])
                  -count((ancestor::blanks-select/preceding::blank[not(*)]
                  |ancestor::blanks-select/preceding::blank/s)[normalize-space()=normalize-space(current())])=0">
      <span>
        <xsl:attribute name="class">
          <xsl:text>pquizItem </xsl:text>
          <xsl:if test="@type">
            <xsl:value-of select="@type"/>
          </xsl:if>
        </xsl:attribute>
        <xsl:attribute name="id">
          <xsl:value-of
              select="concat($quiz_id, '_item', format-number(position(), '000'))"/>
        </xsl:attribute>
        <xsl:attribute name="data-item-value">
          <xsl:call-template name="make_id"><xsl:with-param name="item" select="."/></xsl:call-template>
          <xsl:if test="not(normalize-space())">
            <xsl:text> </xsl:text>
          </xsl:if>
        </xsl:attribute>
        <xsl:if test="ancestor::blanks-select[@multiple='strict']">
          <xsl:attribute name="data-item-count">
            <xsl:value-of select="count((preceding::blank[not(*)]|preceding::blank/s)[normalize-space()=normalize-space(current())]
                                  |(following::blank[not(*)]|following::blank/s)[normalize-space()=normalize-space(current())])
                                  -count((ancestor::blanks-select/preceding::blank[not(*)]
                                  |ancestor::blanks-select/preceding::blank/s)[normalize-space()=normalize-space(current())]
                                  |(ancestor::blanks-select/following::blank[not(*)]
                                  |ancestor::blanks-select/following::blank/s)[normalize-space()=normalize-space(current())])+1"/>
          </xsl:attribute>
        </xsl:if>
        <xsl:value-of select="normalize-space()"/>
        <xsl:if test="not(normalize-space())"><xsl:text> </xsl:text></xsl:if>
      </span>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      blanks-media
      =========================================================================
  -->
  <xsl:template match="blanks-media">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <div id="{$quiz_id}_engine" class="pquizEngine">
      <div id="{$quiz_id}_correct" class="hidden">
        <xsl:for-each select=".//blank[not(ancestor::intruders)]">
          <xsl:if test="*">
            <xsl:call-template name="blank_num"/>
            <xsl:choose>
              <xsl:when test="s">
                <xsl:for-each select="s">
                  <xsl:call-template name="make_id">
                    <xsl:with-param name="item" select="."/>
                  </xsl:call-template>
                  <xsl:if test="count(following-sibling::s)">|</xsl:if>
                </xsl:for-each>
              </xsl:when>
              <xsl:otherwise>
                <xsl:call-template name="make_id">
                  <xsl:with-param name="item" select="."/>
                </xsl:call-template>
              </xsl:otherwise>
            </xsl:choose>
            <xsl:call-template name="blank_separator"/>
          </xsl:if>
        </xsl:for-each>
        <xsl:if test="not(normalize-space(.//blank[not(ancestor::intruders)]))">
          <xsl:text> </xsl:text>
        </xsl:if>
      </div>

      <xsl:if test="not(@orientation='east' or @orientation='south')">
        <xsl:call-template name="bsm_items">
          <xsl:with-param name="quiz_id" select="$quiz_id"/>
        </xsl:call-template>
      </xsl:if>
      <xsl:if test="not(@orientation)">
        <div class="clear"><xsl:text> </xsl:text></div>
      </xsl:if>
      <div>
        <xsl:attribute name="class">
          <xsl:text>pquizText</xsl:text>
          <xsl:if test="@orientation='east' or @orientation='west'">
            <xsl:text> pquizDropFloat</xsl:text>
          </xsl:if>
        </xsl:attribute>
        <xsl:apply-templates
            select="section|p|speech|list|blockquote|table|media"/>
      </div>
      <xsl:if test="@orientation='south'">
        <div class="clear"><xsl:text> </xsl:text></div>
      </xsl:if>
      <xsl:choose>
        <xsl:when test="@orientation='east' or @orientation='south'">
          <xsl:call-template name="bsm_items">
            <xsl:with-param name="quiz_id" select="$quiz_id"/>
          </xsl:call-template>
          <div class="clear"><xsl:text> </xsl:text></div>
        </xsl:when>
        <xsl:otherwise>
          <div class="clear"><xsl:text> </xsl:text></div>
        </xsl:otherwise>
      </xsl:choose>
    </div>
  </xsl:template>

  <!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
  <xsl:template name="bsm_items">
    <xsl:param name="quiz_id"/>
    <div id="{$quiz_id}_items">
      <xsl:attribute name="class">
        <xsl:text>pquizItems</xsl:text>
        <xsl:if test="@orientation='east' or @orientation='west'">
          <xsl:text> pquizPickFloat</xsl:text>
        </xsl:if>
      </xsl:attribute>
      <xsl:text> </xsl:text>
      <xsl:choose>
        <xsl:when test="@no-shuffle='alpha'">
          <xsl:for-each select=".//blank[p]|.//blank[image]|.//blank[math]|.//blank[audio]
                                |.//blank/s|intruders/blank">
            <xsl:sort/>
            <xsl:call-template name="bsm_item">
              <xsl:with-param name="quiz_id" select="$quiz_id"/>
            </xsl:call-template>
          </xsl:for-each>
        </xsl:when>
        <xsl:otherwise>
          <xsl:for-each select=".//blank[p]|.//blank[image]|.//blank[math]|.//blank[audio]
                                |.//blank/s|intruders/blank">
            <xsl:call-template name="bsm_item">
              <xsl:with-param name="quiz_id" select="$quiz_id"/>
            </xsl:call-template>
          </xsl:for-each>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:if test="not(.//blank)"><xsl:text> </xsl:text></xsl:if>
    </div>
  </xsl:template>

  <!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
  <xsl:template name="bsm_item">
    <xsl:param name="quiz_id"/>
    <xsl:if test="not(ancestor::blanks-media[@multiple='true']|ancestor::blanks-media[@multiple='strict']) or
                  count(preceding::blank[p and normalize-space()=normalize-space(current())]
                  |preceding::blank[image and image/@id=current()/image/@id]
                  |preceding::blank[audio and audio/@id=current()/audio/@id]
                  |preceding::blank[math and math/latex=current()/math/latex]
                  |preceding::blank/s[p and normalize-space()=normalize-space(current())]
                  |preceding::blank/s[image and image/@id=current()/image/@id]
                  |preceding::blank/s[audio and audio/@id=current()/audio/@id]
                  |preceding::blank/s[math and math/latex=current()/math/latex])
                  -count(ancestor::blanks-media/preceding::blank[p and normalize-space()=normalize-space(current())]
                  |ancestor::blanks-media/preceding::blank[image and image/@id=current()/image/@id]
                  |ancestor::blanks-media/preceding::blank[audio and audio/@id=current()/audio/@id]
                  |ancestor::blanks-media/preceding::blank[math and math/latex=current()/math/latex]
                  |ancestor::blanks-media/preceding::blank/s[p and normalize-space()=normalize-space(current())]
                  |ancestor::blanks-media/preceding::blank/s[image and image/@id=current()/image/@id]
                  |ancestor::blanks-media/preceding::blank/s[audio and audio/@id=current()/audio/@id]
                  |ancestor::blanks-media/preceding::blank/s[math and math/latex=current()/math/latex])=0">
      <span>
        <xsl:attribute name="class">
          <xsl:text>pquizItem</xsl:text>
          <xsl:if test="image">
            <xsl:text> pquizItemImage</xsl:text>
          </xsl:if>
          <xsl:if test="audio">
            <xsl:text> pquizItemAudio</xsl:text>
          </xsl:if>
          <xsl:if test="@type">
            <xsl:text> </xsl:text><xsl:value-of select="@type"/>
          </xsl:if>
        </xsl:attribute>
        <xsl:attribute name="id">
          <xsl:value-of
              select="concat($quiz_id, '_item', format-number(position(), '000'))"/>
        </xsl:attribute>
        <xsl:attribute name="data-item-value">
          <xsl:call-template name="make_id"><xsl:with-param name="item" select="."/></xsl:call-template>
          <xsl:if test="not(p or image or audio or video or normalize-space())">
            <xsl:text> </xsl:text>
          </xsl:if>
        </xsl:attribute>
        <xsl:choose>
          <xsl:when test="math">
            <xsl:apply-templates select="math"/>
          </xsl:when>
          <xsl:when test="p">
            <xsl:apply-templates select="." mode="blank"/>
            <xsl:if test="not(normalize-space())"><xsl:text> </xsl:text></xsl:if>
          </xsl:when>
          <xsl:otherwise>
            <xsl:apply-templates/>
          </xsl:otherwise>
        </xsl:choose>
      </span>
    </xsl:if>
  </xsl:template>

  <!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
  <xsl:template match="p" mode="blank">
    <xsl:apply-templates/>
  </xsl:template>

  <!--
      =========================================================================
      blanks-choices
      =========================================================================
  -->
  <xsl:template match="blanks-choices">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <div id="{$quiz_id}_engine" class="pquizEngine">
      <div id="{$quiz_id}_correct" class="hidden">
        <xsl:for-each select=".//blank">
          <xsl:call-template name="blank_num"/>
          <xsl:choose>
            <xsl:when test="right &gt; 1">
              <xsl:for-each select="right">
                <xsl:value-of select="translate(normalize-space(), ' :', '__')"/>
                <xsl:if test="count(following-sibling::right)">|</xsl:if>
              </xsl:for-each>
            </xsl:when>
            <xsl:otherwise>
              <xsl:value-of select="translate(normalize-space(right), ' :', '__')"/>
            </xsl:otherwise>
          </xsl:choose>
          <xsl:call-template name="blank_separator"/>
        </xsl:for-each>
        <xsl:if test="not(normalize-space(.//blank/right))">
          <xsl:text> </xsl:text>
        </xsl:if>
      </div>

      <div class="pquizText">
        <xsl:apply-templates
            select="section|p|speech|list|blockquote|table|media"/>
      </div>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      correct-line
      =========================================================================
  -->
  <xsl:template match="correct-line">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <div id="{$quiz_id}_engine" class="pquizEngine">
      <div id="{$quiz_id}_correct" class="hidden">
        <xsl:for-each select=".//p">
          <xsl:value-of select="format-number(position(), '000')"/>
          <xsl:value-of select="."/>
          <xsl:if test="count(following::p)-count(ancestor::quiz/following::p)">::</xsl:if>
        </xsl:for-each>
      </div>
      <div id="correct-line-1_items" class="pquizItems">
        <xsl:if test="../correct-line[@remove-space='true']">
          <span class="{$quiz_id} pquizItemLetter" data-item-value="space"><xsl:text> </xsl:text></span>
        </xsl:if>
        <xsl:if test=".//char|intruders/char">
          <xsl:for-each select=".//char|intruders/char">
            <xsl:if test="count(preceding::char[normalize-space()=normalize-space(current())])
                          -count(ancestor::correct-line/preceding::char[normalize-space()=normalize-space(current())])=0">
              <xsl:choose>
                <xsl:when test="@function='uppercase'"/>
                <xsl:otherwise>
                  <span class="{$quiz_id} pquizItemLetter">
                    <xsl:attribute name="data-item-value">
                      <xsl:value-of select="."/>
                    </xsl:attribute>
                    <xsl:if test="@function">
                      <xsl:attribute name="data-item-function">
                        <xsl:value-of select="@function"/>
                      </xsl:attribute>
                    </xsl:if>
                    <xsl:value-of select="."/>
                  </span>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:if>
          </xsl:for-each>
        </xsl:if>
        <xsl:if test=".//char[@function='uppercase']">
          <span class="{$quiz_id} pquizItemLetter" data-item-value="upper" data-item-function="uppercase">
            <xsl:text>aA</xsl:text>
          </span>
          <span class="{$quiz_id} pquizItemLetter" data-item-value="lower" data-item-function="lowercase">
            <xsl:text>Aa</xsl:text>
          </span>
        </xsl:if>
        <span class="correct-line-1 pquizItemLetter" data-item-value="delete" data-item-function="delete">←</span>
      </div>
      <div class="clear"><xsl:text> </xsl:text></div>

      <div class="pquizText">
        <xsl:for-each select=".//p">
          <div class="pquizSentence" id="{$quiz_id}_{format-number(position(), '000')}"><xsl:apply-templates/></div>
        </xsl:for-each>
      </div>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      pointing
      =========================================================================
  -->
  <xsl:template match="pointing">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <div id="{$quiz_id}_engine" class="pquizEngine">
      <div id="{$quiz_id}_correct" class="hidden">
        <xsl:for-each select=".//point[@ref]">
          <xsl:call-template name="point_num"/>
          <xsl:text>x</xsl:text>
          <xsl:call-template name="point_separator"/>
        </xsl:for-each>
        <xsl:if test="not(.//point[@ref])"><xsl:text> </xsl:text></xsl:if>
      </div>

      <div class="pquizText">
        <xsl:apply-templates/>
      </div>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      pointing-categories
      =========================================================================
  -->
  <xsl:template match="pointing-categories">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>
    <xsl:variable name="preceding_point" select="count(preceding::point)"/>

    <div id="{$quiz_id}_engine" class="pquizEngine">
      <div id="{$quiz_id}_correct" class="hidden">
        <xsl:for-each select=".//point[@ref]">
          <xsl:value-of select="format-number(substring(@ref, 4), '000')"/>
          <xsl:value-of
              select="format-number(count(preceding::point)-$preceding_point+1,
                      '000')"/>
          <xsl:if test="count(following::point)
                        &gt; count(ancestor::pointing-categories/following::point)"
                  >::</xsl:if>
        </xsl:for-each>
        <xsl:if test="not(.//point)"><xsl:text> </xsl:text></xsl:if>
      </div>

      <div id="{$quiz_id}_categories" class="pquizCategories">
        <xsl:for-each select="categories/category">
          <span class="pquizCategory"
                data-category-id="{format-number(@id, '000')}">
            <xsl:apply-templates/>
            <span class="pquizCategoryColor pquizBgColor{@id}"> </span>
          </span>
        </xsl:for-each>
      </div>
      <div class="clear"><xsl:text> </xsl:text></div>

      <div class="pquizText">
        <xsl:apply-templates
            select="section|p|speech|list|blockquote|table|media"/>
      </div>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      matching
      =========================================================================
  -->
  <xsl:template match="matching">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <div id="{$quiz_id}_engine" class="pquizEngine">
      <div id="{$quiz_id}_correct" class="hidden">
        <xsl:for-each select="match">
          <xsl:sort select="normalize-space(item[2])"/>
          <xsl:value-of select="format-number(count(preceding-sibling::match)+1, '000')"/>
          <xsl:call-template name="make_id">
            <xsl:with-param name="item" select="item[2]"/>
          </xsl:call-template>
          <xsl:if test="not(position()=last())">::</xsl:if>
        </xsl:for-each>
      </div>

      <xsl:choose>
        <!-- mode link -->
        <xsl:when test="(((not(ancestor::composite) and not(ancestor::quiz/processing-instruction('argument')))
                        or (ancestor::composite and not(contains(ancestor::quiz/processing-instruction('argument'), 'matching:'))))
                        and $mode_matching='link')
                        or (not(ancestor::composite) and ancestor::quiz/processing-instruction('argument')='link')
                        or contains(ancestor::quiz/processing-instruction('argument'), 'matching:link')">
          <xsl:call-template name="matching_link">
            <xsl:with-param name="quiz_id" select="$quiz_id"/>
          </xsl:call-template>
        </xsl:when>
        <!-- mode dragndrop -->
        <xsl:otherwise>
          <xsl:call-template name="matching_dragndrop">
            <xsl:with-param name="quiz_id" select="$quiz_id"/>
          </xsl:call-template>
        </xsl:otherwise>
      </xsl:choose>
    </div>
  </xsl:template>

  <!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
  <xsl:template name="matching_dragndrop">
    <xsl:param name="quiz_id"/>

    <xsl:if test="not(@orientation='east' or @orientation='south')">
      <xsl:call-template name="matching_items">
        <xsl:with-param name="quiz_id" select="$quiz_id"/>
      </xsl:call-template>
    </xsl:if>
    <xsl:if test="not(@orientation)">
      <div class="clear"><xsl:text> </xsl:text></div>
    </xsl:if>

    <table>
      <xsl:attribute name="class">
        <xsl:text>pquizMatching</xsl:text>
        <xsl:if test="@orientation='east' or @orientation='west'">
          <xsl:text> pquizDropFloat</xsl:text>
        </xsl:if>
      </xsl:attribute>
      <xsl:choose>
        <xsl:when test="count(match) &gt; 10">
          <xsl:for-each select="match">
            <xsl:if test="position() mod 2=1">
              <tr>
                <td><xsl:apply-templates select="item[1]/node()"/></td>
                <td>  </td>
                <td id="{concat($quiz_id, '_',
                        format-number(count(preceding-sibling::match)+1, '000'))}"
                    class="pquizDrop pquizDots"><xsl:text> </xsl:text></td>
                <td>    </td>
                <td>
                  <xsl:if test="following-sibling::match">
                    <xsl:apply-templates select="following-sibling::match[1]/item[1]/node()"/>
                  </xsl:if>
                </td>
                <td>  </td>
                <td id="{concat($quiz_id, '_',
                        format-number(count(preceding-sibling::match)+2, '000'))}">
                  <xsl:if test="following-sibling::match">
                    <xsl:attribute name="class">pquizDrop pquizDots</xsl:attribute>
                    <xsl:text> </xsl:text>
                  </xsl:if>
                </td>
              </tr>
            </xsl:if>
          </xsl:for-each>
        </xsl:when>
        <xsl:otherwise>
          <xsl:for-each select="match">
            <tr>
              <td><xsl:apply-templates select="item[1]/node()"/></td>
              <td>  </td>
              <td id="{concat($quiz_id, '_',
                      format-number(count(preceding-sibling::match)+1, '000'))}"
                  class="pquizDrop pquizDots"><xsl:text> </xsl:text></td>
            </tr>
          </xsl:for-each>
        </xsl:otherwise>
      </xsl:choose>
    </table>
    <xsl:if test="@orientation='south'">
      <div class="clear"><xsl:text> </xsl:text></div>
    </xsl:if>
    <xsl:choose>
      <xsl:when test="@orientation='east' or @orientation='south'">
        <xsl:call-template name="matching_items">
          <xsl:with-param name="quiz_id" select="$quiz_id"/>
        </xsl:call-template>
        <div class="clear"><xsl:text> </xsl:text></div>
      </xsl:when>
      <xsl:otherwise>
        <div class="clear"><xsl:text> </xsl:text></div>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="matching_items">
    <xsl:param name="quiz_id"/>
    <div id="{$quiz_id}_items">
      <xsl:attribute name="class">
        <xsl:text>pquizItems</xsl:text>
        <xsl:if test="@orientation='east' or @orientation='west'">
          <xsl:text> pquizPickFloat</xsl:text>
        </xsl:if>
      </xsl:attribute>
      <xsl:text> </xsl:text>
      <xsl:choose>
        <xsl:when test="@no-shuffle='alpha'">
          <xsl:for-each select="intruders/item|match/item[2]">
            <xsl:sort select="normalize-space()"/>
            <xsl:call-template name="matching_item">
              <xsl:with-param name="quiz_id" select="$quiz_id"/>
            </xsl:call-template>
          </xsl:for-each>
        </xsl:when>
        <xsl:otherwise>
          <xsl:for-each select="intruders/item|match/item[2]">
            <xsl:call-template name="matching_item">
              <xsl:with-param name="quiz_id" select="$quiz_id"/>
            </xsl:call-template>
          </xsl:for-each>
        </xsl:otherwise>
      </xsl:choose>
    </div>
  </xsl:template>

  <xsl:template name="matching_item">
    <xsl:param name="quiz_id"/>
    <xsl:if test="not(ancestor::matching[@multiple='true']|ancestor::matching[@multiple='strict']) or
                  count(preceding::item[not(image) and normalize-space()=normalize-space(current())]
                  |preceding::item[image and image/@id=current()/image/@id])
                  -count(ancestor::matching/preceding::item[not(image) and normalize-space()=normalize-space(current())]
                  |ancestor::matching/preceding::item[image and image/@id=current()/image/@id])=0">
      <span>
        <xsl:attribute name="class">
          <xsl:text>pquizItem</xsl:text>
          <xsl:if test="image">
            <xsl:text> pquizItemImage</xsl:text>
          </xsl:if>
          <xsl:if test="audio">
            <xsl:text> pquizItemAudio</xsl:text>
          </xsl:if>
        </xsl:attribute>
        <xsl:attribute name="id">
          <xsl:value-of
              select="concat($quiz_id, '_item', format-number(position(), '000'))"/>
        </xsl:attribute>
        <xsl:attribute name="data-item-value">
          <xsl:call-template name="make_id">
            <xsl:with-param name="item" select="."/>
          </xsl:call-template>
          <xsl:if test="not(image or audio or video or normalize-space())">
            <xsl:text> </xsl:text>
          </xsl:if>
        </xsl:attribute>
        <xsl:if test="ancestor::matching[@multiple='strict']">
          <xsl:attribute name="data-item-count">
            <xsl:value-of select="count(preceding::item[not(image) and normalize-space()=normalize-space(current())]
                                  |preceding::item[image and image/@id=current()/image/@id]
                                  |following::item[not(image) and normalize-space()=normalize-space(current())]
                                  |following::item[image and image/@id=current()/image/@id])
                                  -count(ancestor::matching/preceding::item[not(image) and normalize-space()=normalize-space(current())]
                                  |ancestor::matching/preceding::item[image and image/@id=current()/image/@id]
                                  |ancestor::matching/following::item[not(image) and normalize-space()=normalize-space(current())]
                                  |ancestor::matching/following::item[image and image/@id=current()/image/@id])+1"/>
          </xsl:attribute>
        </xsl:if>
        <xsl:choose>
          <xsl:when test="not(image or audio or video)">
            <xsl:value-of select="normalize-space()"/>
            <xsl:if test="not(normalize-space())"><xsl:text> </xsl:text></xsl:if>
          </xsl:when>
          <xsl:otherwise>
            <xsl:apply-templates/>
          </xsl:otherwise>
        </xsl:choose>
      </span>
    </xsl:if>
  </xsl:template>

  <!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
  <xsl:template name="matching_link">
    <xsl:param name="quiz_id"/>

    <div id="{$quiz_id}_items_left" class="pquizMatchingLinkItems pquizMatchingLinkItemsLeft">
      <xsl:for-each select="match">
        <span id="{concat($quiz_id, '_',
                  format-number(count(preceding-sibling::match)+1, '000'))}"
              class="pquizMatchingLinkItem">
          <xsl:apply-templates select="item[1]/node()"/>
        </span>
      </xsl:for-each>
    </div>

    <canvas id="{$quiz_id}_canvas" width="300">
      <xsl:value-of select="$i18n_nocanvas"/>
    </canvas>

    <div id="{$quiz_id}_items_right" class="pquizMatchingLinkItems pquizMatchingLinkItemsRight">
      <xsl:for-each select="intruders/item|match/item[2]">
        <xsl:sort select="normalize-space()"/>
        <span class="pquizMatchingLinkItem">
          <xsl:attribute name="data-item-value">
            <xsl:call-template name="make_id">
              <xsl:with-param name="item" select="."/>
            </xsl:call-template>
          </xsl:attribute>
          <xsl:choose>
            <xsl:when test="not(image or audio or video)">
              <xsl:value-of select="normalize-space()"/>
            </xsl:when>
            <xsl:otherwise>
              <xsl:apply-templates/>
            </xsl:otherwise>
          </xsl:choose>
        </span>
      </xsl:for-each>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      sort
      =========================================================================
  -->
  <xsl:template match="sort">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <div id="{$quiz_id}_engine" class="pquizEngine">
      <div id="{$quiz_id}_correct" class="hidden">
        <xsl:for-each select="item">
          <xsl:value-of select="format-number(count(preceding-sibling::item)+1, '000')"/>
          <xsl:call-template name="make_id"><xsl:with-param name="item" select="."/></xsl:call-template>
          <xsl:if test="count(following-sibling::item)">::</xsl:if>
        </xsl:for-each>
      </div>

      <xsl:if test="not(@orientation='east' or @orientation='south')">
        <xsl:call-template name="sort_items">
          <xsl:with-param name="quiz_id" select="$quiz_id"/>
        </xsl:call-template>
      </xsl:if>
      <xsl:if test="not(@orientation)">
        <div class="clear"><xsl:text> </xsl:text></div>
      </xsl:if>

      <div>
        <xsl:attribute name="class">
          <xsl:text>pquizText</xsl:text>
          <xsl:if test="@orientation='east' or @orientation='west'">
            <xsl:text> pquizDropFloat</xsl:text>
          </xsl:if>
        </xsl:attribute>
        <xsl:for-each select="item">
          <span
              id="{concat($quiz_id, '_',
                  format-number(count(preceding-sibling::item)+1, '000'))}"
              class="pquizDrop pquizDots"><xsl:text> </xsl:text></span>
          <xsl:if test="../comparison and count(following-sibling::item)">
            <xsl:text> </xsl:text>
            <xsl:apply-templates select="../comparison"/>
          </xsl:if>
          <xsl:text> </xsl:text>
        </xsl:for-each>
      </div>
      <xsl:if test="@orientation='south'">
        <div class="clear"><xsl:text> </xsl:text></div>
      </xsl:if>
      <xsl:choose>
        <xsl:when test="@orientation='east' or @orientation='south'">
          <xsl:call-template name="sort_items">
            <xsl:with-param name="quiz_id" select="$quiz_id"/>
          </xsl:call-template>
          <div class="clear"><xsl:text> </xsl:text></div>
        </xsl:when>
        <xsl:otherwise>
          <div class="clear"><xsl:text> </xsl:text></div>
        </xsl:otherwise>
      </xsl:choose>
    </div>
  </xsl:template>

  <xsl:template name="sort_items">
    <xsl:param name="quiz_id"/>
    <div id="{$quiz_id}_items">
      <xsl:attribute name="class">
        <xsl:text>pquizItems</xsl:text>
        <xsl:if test="@orientation='east' or @orientation='west'">
          <xsl:text> pquizPickFloat</xsl:text>
        </xsl:if>
      </xsl:attribute>
      <xsl:text> </xsl:text>
      <xsl:for-each select="item">
        <xsl:sort select="@shuffle"/>
        <span>
          <xsl:attribute name="class">
            <xsl:text>pquizItem</xsl:text>
            <xsl:if test="image">
              <xsl:text> pquizItemImage</xsl:text>
            </xsl:if>
            <xsl:if test="audio">
              <xsl:text> pquizItemAudio</xsl:text>
            </xsl:if>
          </xsl:attribute>
          <xsl:attribute name="id">
            <xsl:value-of
                select="concat($quiz_id, '_item', format-number(position(), '000'))"/>
          </xsl:attribute>
          <xsl:attribute name="data-item-value">
            <xsl:call-template name="make_id">
              <xsl:with-param name="item" select="."/>
            </xsl:call-template>
            <xsl:if test="not(image or audio or video or normalize-space())">
              <xsl:text> </xsl:text>
            </xsl:if>
          </xsl:attribute>
          <xsl:choose>
            <xsl:when test="not(image or audio or video)">
              <xsl:value-of select="normalize-space()"/>
              <xsl:if test="not(normalize-space())"><xsl:text> </xsl:text></xsl:if>
            </xsl:when>
            <xsl:otherwise>
              <xsl:apply-templates/>
            </xsl:otherwise>
          </xsl:choose>
        </span>
      </xsl:for-each>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      categories
      =========================================================================
  -->
  <xsl:template match="categories">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <div id="{$quiz_id}_engine" class="pquizEngine">
      <div id="{$quiz_id}_correct" class="hidden">
        <xsl:for-each select="category/item">
          <xsl:value-of
              select="format-number(count(ancestor::category/preceding-sibling::category)+1, '000')"/>
          <xsl:call-template name="make_id">
            <xsl:with-param name="item" select="."/>
          </xsl:call-template>
          <xsl:if test="count(following-sibling::item|ancestor::category/following-sibling::category)"
                  >::</xsl:if>
        </xsl:for-each>
      </div>

      <xsl:choose>
        <!-- mode float -->
        <xsl:when test="(((not(ancestor::composite) and not(ancestor::quiz/processing-instruction('argument')))
                        or (ancestor::composite and not(contains(ancestor::quiz/processing-instruction('argument'), 'categories:'))))
                        and $mode_categories='float')
                        or (not(ancestor::composite) and ancestor::quiz/processing-instruction('argument')='float')
                        or contains(ancestor::quiz/processing-instruction('argument'), 'categories:float')">
          <xsl:call-template name="categories_float">
            <xsl:with-param name="quiz_id" select="$quiz_id"/>
          </xsl:call-template>
        </xsl:when>
        <!-- mode color -->
        <xsl:when test="(((not(ancestor::composite) and not(ancestor::quiz/processing-instruction('argument')))
                        or (ancestor::composite and not(contains(ancestor::quiz/processing-instruction('argument'), 'categories:'))))
                        and $mode_categories='color')
                        or (not(ancestor::composite) and ancestor::quiz/processing-instruction('argument')='color')
                        or contains(ancestor::quiz/processing-instruction('argument'), 'categories:color')">
          <xsl:call-template name="categories_color">
            <xsl:with-param name="quiz_id" select="$quiz_id"/>
          </xsl:call-template>
        </xsl:when>
        <!-- mode grid -->
        <xsl:when test="(((not(ancestor::composite) and not(ancestor::quiz/processing-instruction('argument')))
                        or (ancestor::composite and not(contains(ancestor::quiz/processing-instruction('argument'), 'categories:'))))
                        and $mode_categories='grid')
                        or (not(ancestor::composite) and ancestor::quiz/processing-instruction('argument')='grid')
                        or contains(ancestor::quiz/processing-instruction('argument'), 'categories:grid')">
          <xsl:call-template name="categories_grid">
            <xsl:with-param name="quiz_id" select="$quiz_id"/>
          </xsl:call-template>
        </xsl:when>
        <!-- mode basket -->
        <xsl:otherwise>
          <xsl:call-template name="categories_basket">
            <xsl:with-param name="quiz_id" select="$quiz_id"/>
          </xsl:call-template>
        </xsl:otherwise>
      </xsl:choose>
    </div>
  </xsl:template>

  <!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
  <xsl:template name="categories_flottant">
    <xsl:param name="quiz_id"/>
    <div class="pquizCategoriesFullItems">
      <xsl:call-template name="category_items">
        <xsl:with-param name="quiz_id" select="$quiz_id"/>
      </xsl:call-template>
      <div class="clear"><xsl:text> </xsl:text></div>
      <div id="{$quiz_id}_legend_items" class="pquizCategoriesLegendItems">
        <xsl:for-each select="category/head/title">
          <span class="pquizCategoryLegendItem">
            <xsl:attribute name="id">
              <xsl:value-of
                  select="concat($quiz_id, '_legend_item', format-number(position(), '000'))"/>
            </xsl:attribute>
            <xsl:attribute name="data-item-value">
              <xsl:call-template name="make_id"><xsl:with-param name="item" select="."/></xsl:call-template>
              <xsl:if test="not(image or audio or video or normalize-space())">
                <xsl:text> </xsl:text>
              </xsl:if>
            </xsl:attribute>
            <xsl:apply-templates/>
          </span>
        </xsl:for-each>
      </div>
    </div>
    <div class="clear"><xsl:text> </xsl:text></div>
    <div class="pquizCategoriesDrops">
      <xsl:for-each select="category">
        <xsl:if test="item">
          <div class="pquizCategoriesBasket">
            <div id="{$quiz_id}_{format-number(count(preceding-sibling::category)*2+1, '000')}" class="legend pquizCategoryLegendDrop pquizDots"><xsl:text> </xsl:text></div>
            <div id="{$quiz_id}_{format-number(count(preceding-sibling::category)*2+2, '000')}" class="pquizCategoryDrop"><xsl:text> </xsl:text></div>
          </div>
        </xsl:if>
      </xsl:for-each>
    </div>
    <div class="clear"><xsl:text> </xsl:text></div>
  </xsl:template>

  <!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
  <xsl:template name="categories_color">
    <xsl:param name="quiz_id"/>

    <div id="{$quiz_id}_categories" class="pquizCategories">
      <xsl:for-each select="category">
        <span class="pquizCategory"
              data-category-id="{format-number(count(preceding-sibling::category)+1, '000')}">
          <xsl:apply-templates select="head/title"/>
          <span class="pquizCategoryColor pquizBgColor{count(preceding-sibling::category)+1}"> </span>
        </span>
      </xsl:for-each>
    </div>
    <div class="clear"><xsl:text> </xsl:text></div>
    <ul class="pquizCategoriesChoices">
      <xsl:for-each select="category/item">
        <xsl:sort/>
        <xsl:if test="not(ancestor::categories[@multiple='true']|ancestor::categories[@multiple='strict']) or
                      count(preceding::item[normalize-space()=normalize-space(current())])
                      -count(ancestor::categories/preceding::item[normalize-space()=normalize-space(current())])=0">
          <li class="pquizChoice">
            <xsl:attribute name="data-choice-value">
              <xsl:call-template name="make_id"><xsl:with-param name="item" select="."/></xsl:call-template>
            </xsl:attribute>
            <xsl:apply-templates/>
          </li>
        </xsl:if>
      </xsl:for-each>
    </ul>
  </xsl:template>

  <!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
  <xsl:template name="categories_basket">
    <xsl:param name="quiz_id"/>
    <xsl:if test="not(@orientation='east' or @orientation='south')">
      <xsl:call-template name="category_items">
        <xsl:with-param name="quiz_id" select="$quiz_id"/>
      </xsl:call-template>
    </xsl:if>
    <xsl:if test="not(@orientation)">
      <div class="clear"><xsl:text> </xsl:text></div>
    </xsl:if>
    <div>
      <xsl:attribute name="class">
        <xsl:text>pquizCategoriesDrops</xsl:text>
        <xsl:if test="@orientation='east' or @orientation='west'">
          <xsl:text> pquizDropFloat</xsl:text>
        </xsl:if>
      </xsl:attribute>
      <xsl:for-each select="category">
        <div class="pquizCategoriesBasket">
          <div class="legend"><xsl:apply-templates select="head/title"/></div>
          <div id="{$quiz_id}_{format-number(count(preceding-sibling::category)+1, '000')}"
               class="pquizCategoryDrop">
            <xsl:text> </xsl:text>
          </div>
        </div>
      </xsl:for-each>
    </div>
    <xsl:if test="@orientation='south'">
      <div class="clear"><xsl:text> </xsl:text></div>
    </xsl:if>
    <xsl:choose>
      <xsl:when test="@orientation='east' or @orientation='south'">
        <xsl:call-template name="category_items">
          <xsl:with-param name="quiz_id" select="$quiz_id"/>
        </xsl:call-template>
        <div class="clear"><xsl:text> </xsl:text></div>
      </xsl:when>
      <xsl:otherwise>
        <div class="clear"><xsl:text> </xsl:text></div>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="category_items">
    <xsl:param name="quiz_id"/>
    <div id="{$quiz_id}_items">
      <xsl:attribute name="class">
        <xsl:text>pquizCategoriesItems</xsl:text>
        <xsl:if test="@orientation='east' or @orientation='west'">
          <xsl:text> pquizPickFloat</xsl:text>
        </xsl:if>
      </xsl:attribute>
      <xsl:text> </xsl:text>
      <xsl:choose>
        <xsl:when test="@no-shuffle='alpha'">
          <xsl:for-each select="intruders/item|category/item">
            <xsl:sort select="normalize-space()"/>
            <xsl:call-template name="category_item">
              <xsl:with-param name="quiz_id" select="$quiz_id"/>
            </xsl:call-template>
          </xsl:for-each>
        </xsl:when>
        <xsl:otherwise>
          <xsl:for-each select="intruders/item|category/item">
            <xsl:call-template name="category_item">
              <xsl:with-param name="quiz_id" select="$quiz_id"/>
            </xsl:call-template>
          </xsl:for-each>
        </xsl:otherwise>
      </xsl:choose>
    </div>
  </xsl:template>

  <xsl:template name="category_item">
    <xsl:param name="quiz_id"/>
    <xsl:if test="not(ancestor::categories[@multiple='true']|ancestor::categories[@multiple='strict']) or
                  count(preceding::item[not(image) and normalize-space()=normalize-space(current())]
                  |preceding::item[image and image/@id=current()/image/@id])
                  -count(ancestor::categories/preceding::item[not(image) and normalize-space()=normalize-space(current())]
                  |ancestor::categories/preceding::item[image and image/@id=current()/image/@id])=0">
      <div>
        <xsl:attribute name="class">
          <xsl:text>pquizCategoryItem</xsl:text>
          <xsl:if test="image">
            <xsl:text> pquizItemImage</xsl:text>
          </xsl:if>
          <xsl:if test="audio">
            <xsl:text> pquizItemAudio</xsl:text>
          </xsl:if>
        </xsl:attribute>
        <xsl:attribute name="id">
          <xsl:value-of
              select="concat($quiz_id, '_item', format-number(position(), '000'))"/>
        </xsl:attribute>
        <xsl:attribute name="data-item-value">
          <xsl:call-template name="make_id"><xsl:with-param name="item" select="."/></xsl:call-template>
          <xsl:if test="not(image or audio or video or normalize-space())">
            <xsl:text> </xsl:text>
          </xsl:if>
        </xsl:attribute>
        <xsl:if test="ancestor::categories[@multiple='strict']">
          <xsl:attribute name="data-item-count">
            <xsl:value-of select="count(preceding::item[not(image) and normalize-space()=normalize-space(current())]
                                  |preceding::item[image and image/@id=current()/image/@id]
                                  |following::item[not(image) and normalize-space()=normalize-space(current())]
                                  |following::item[image and image/@id=current()/image/@id])
                                  -count(ancestor::categories/preceding::item[not(image) and normalize-space()=normalize-space(current())]
                                  |ancestor::categories/preceding::item[image and image/@id=current()/image/@id]
                                  |ancestor::categories/following::item[not(image) and normalize-space()=normalize-space(current())]
                                  |ancestor::categories/following::item[image and image/@id=current()/image/@id])+1"/>
          </xsl:attribute>
        </xsl:if>
        <xsl:apply-templates/>
      </div>
    </xsl:if>
  </xsl:template>

  <!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
  <xsl:template name="categories_grid">
    <xsl:param name="quiz_id"/>
    <div class="pdocTable pquizTableCategories">
      <table>
        <thead>
          <tr>
            <th> </th>
            <xsl:for-each select="category/head/title">
              <th>
                <xsl:if test="not(image or audio or video or normalize-space())">
                  <xsl:text> </xsl:text>
                </xsl:if>
                <xsl:apply-templates/>
              </th>
            </xsl:for-each>
          </tr>
        </thead>
        <tbody>
          <xsl:choose>
            <xsl:when test="@no-shuffle='alpha'">
              <xsl:for-each select="intruders/item|category/item">
                <xsl:sort/>
                <xsl:call-template name="category_grid_item">
                  <xsl:with-param name="quiz_id" select="$quiz_id"/>
                </xsl:call-template>
              </xsl:for-each>
            </xsl:when>
            <xsl:otherwise>
              <xsl:for-each select="intruders/item|category/item">
                <xsl:call-template name="category_grid_item">
                  <xsl:with-param name="quiz_id" select="$quiz_id"/>
                </xsl:call-template>
              </xsl:for-each>
            </xsl:otherwise>
          </xsl:choose>
        </tbody>
      </table>
    </div>
  </xsl:template>


  <xsl:template name="category_grid_item">
    <xsl:param name="quiz_id"/>
    <xsl:if test="not(ancestor::categories[@multiple='true']|ancestor::categories[@multiple='strict']) or
                  count(preceding::item[not(image) and normalize-space()=normalize-space(current())]
                  |preceding::item[image and image/@id=current()/image/@id])
                  -count(ancestor::categories/preceding::item[not(image) and normalize-space()=normalize-space(current())]
                  |ancestor::categories/preceding::item[image and image/@id=current()/image/@id])=0">
      <tr>
        <th>
          <span id="{$quiz_id}_item{format-number(position(), '000')}">
            <xsl:attribute name="data-item-value">
              <xsl:choose>
                <xsl:when test="image or audio or video">
                  <xsl:value-of select="(image|audio|video)/@id"/>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="translate(normalize-space(), ' :', '__')"/>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:attribute>
            <xsl:apply-templates/>
          </span>
        </th>
        <xsl:call-template name="category_grid">
          <xsl:with-param name="data-group">
            <xsl:value-of select="format-number(position(), '000')"/>
          </xsl:with-param>
          <xsl:with-param name="name">
            <xsl:value-of
                select="concat($quiz_id, '-', format-number(position(), '0'))"/>
          </xsl:with-param>
        </xsl:call-template>
      </tr>
    </xsl:if>
  </xsl:template>

  <!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
  <xsl:template name="category_grid">
    <xsl:param name="data-group"/>
    <xsl:param name="name"/>

    <xsl:for-each select="ancestor::categories/category">
      <td data-category-id="{format-number(count(preceding-sibling::category)+1, '000')}"
          data-group="{$data-group}">
        <xsl:attribute name="class">
          <xsl:text>pquizCategoryChoice</xsl:text>
          <xsl:choose>
            <xsl:when test="ancestor::categories[@multiple='true']
                            |ancestor::categories[@multiple='strict']">
              <xsl:text> pquizChoiceCheckbox</xsl:text>
            </xsl:when>
            <xsl:otherwise>
              <xsl:text> pquizChoiceRadio</xsl:text>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:attribute>
        <input name="{$name}">
          <xsl:attribute name="type">
            <xsl:choose>
              <xsl:when test="ancestor::categories[@multiple='true']
                              |ancestor::categories[@multiple='strict']">
                <xsl:text>checkbox</xsl:text>
              </xsl:when>
              <xsl:otherwise>
                <xsl:text>radio</xsl:text>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:attribute>
        </input>
      </td>
    </xsl:for-each>
  </xsl:template>

  <!--
      =========================================================================
      wordsearch
      =========================================================================
  -->
  <xsl:template match="wordsearch">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <div id="{$quiz_id}_engine" class="pquizEngine">
      <div id="{$quiz_id}_correct" class="hidden">
        <xsl:for-each select="words/item">
          <xsl:value-of
              select="format-number(count(preceding-sibling::item)+1, '000')"/>
          <xsl:value-of
              select="concat(@startx, ';', @starty, '-', @endx, ';', @endy)"/>
          <xsl:if test="following-sibling::item"
                  >::</xsl:if>
        </xsl:for-each>
      </div>
      <div id="{$quiz_id}_wordsearch" class="pquizWordsearch">
        <xsl:call-template name="WordsearchTools"/>
        <xsl:if test="@wordlist='left'">
          <div class="pdocList pquizWordList pquizDropFloat">
            <ul>
              <xsl:for-each select="words/item">
                <li data-item-id="{format-number(count(preceding-sibling::item)+1, '000')}">
                  <xsl:apply-templates/>
                </li>
              </xsl:for-each>
            </ul>
          </div>
        </xsl:if>
        <div class="pquizGrid pquizGridWordsearch">
          <xsl:apply-templates select="grid"/>
          <div class="pquizWordsearchOverlay"><xsl:text> </xsl:text></div>
        </div>
        <xsl:if test="@wordlist='right' or not(@wordlist)">
          <div class="pdocList pquizWordList">
            <ul>
              <xsl:for-each select="words/item">
                <li data-item-id="{format-number(count(preceding-sibling::item)+1, '000')}">
                  <xsl:apply-templates/>
                </li>
              </xsl:for-each>
            </ul>
          </div>
        </xsl:if>
      </div>
    </div>
  </xsl:template>

  <xsl:template name="WordsearchTools">
    <div class="pquizWordsearchTools">
      <div class="pquizWordsearchHighlighter"><img alt="highlighter" src="{concat($img_dir, 'highlighter.png')}"/></div>
      <div class="pquizWordsearchEraser"><img alt="eraser" src="{concat($img_dir, 'eraser.png')}"/></div>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      flashcard
      =========================================================================
  -->
  <xsl:template match="flashcard">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <div class="pquizFlashcard">
      <xsl:apply-templates select="side1"/>
      <xsl:apply-templates select="side2"/>
    </div>
    <div class="pquizFlashcardTurnOver">
      <a class="pquizButton"><xsl:value-of select="$i18n_turnover"/></a>
    </div>
  </xsl:template>

  <xsl:template match="side1">
    <div class="pquizFlashcardSide side1">
      <div><xsl:apply-templates/></div>
    </div>
  </xsl:template>

  <xsl:template match="side2">
    <div class="pquizFlashcardSide side2">
      <div>
        <xsl:apply-templates select="instructions"/>
        <xsl:apply-templates
            select="choices-radio|choices-check|blanks-fill|blanks-select
                    |blanks-media|correct-line|blanks-choices
                    |pointing|pointing-categories|matching|sort|categories
                    |production"/>
        <xsl:apply-templates select="help|answer"/>
      </div>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      coloring
      =========================================================================
  -->
  <xsl:template match="coloring">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <xsl:if test="$img">
      <xsl:apply-templates select="canvas|areas" mode="ini"/>
    </xsl:if>
    <div id="{$quiz_id}_engine" class="pquizEngine">
      <div id="{$quiz_id}_correct" class="hidden">
        <xsl:call-template name="coloring_correct"/>
      </div>
      <div class="pquizColoringPalette">
        <xsl:call-template name="coloring_palette"/>
      </div>
      <canvas class="pquizColoringCanvas" id="{$quiz_id}">
        <xsl:attribute name="width">
          <xsl:value-of select="substring-before($img_size, 'x')"/>
        </xsl:attribute>
        <xsl:attribute name="height">
          <xsl:value-of select="substring-after($img_size, 'x')"/>
        </xsl:attribute>
        <xsl:attribute name="data-coloring-outline">
          <xsl:value-of select="concat($img_dir, canvas/@id, $img_ext)"/>
        </xsl:attribute>
        <xsl:if test="areas">
          <xsl:attribute name="data-coloring-mask">
            <xsl:value-of select="concat($img_dir, areas/@id, $img_ext)"/>
          </xsl:attribute>
        </xsl:if>
        <xsl:text>Your browser doesn't support canvas.</xsl:text>
      </canvas>
    </div>
  </xsl:template>

  <xsl:template match="color">
    <xsl:variable name="lowerhex">abcdef</xsl:variable>
    <xsl:variable name="upperhex">ABCDEF</xsl:variable>
    <xsl:variable name="code" select="translate(@code, $upperhex, $lowerhex)"/>

    <div data-drawing-color="{$code}">
      <xsl:attribute name="class">
        <xsl:text>pquizColoringColor</xsl:text>
        <xsl:if test="not(preceding-sibling::color)">
          <xsl:text> selected</xsl:text>
        </xsl:if>
      </xsl:attribute>
      <div class="pquizColoringSample" style="background-color: {$code};">
        <xsl:text> </xsl:text>
      </div>
    </div>
  </xsl:template>

  <xsl:template match="canvas" mode="ini">
    <xsl:call-template name="image_ini">
      <xsl:with-param name="idx">
        <xsl:value-of select="concat(count(ancestor::quiz/preceding-sibling::quiz/coloring)+1,
                              '-', count(ancestor::subquiz/preceding-sibling::subquiz/coloring)+1,
                              '_canvas')"/>
      </xsl:with-param>
      <xsl:with-param name="size">100%%</xsl:with-param>
      <xsl:with-param name="ext">
        <xsl:call-template name="image_extension"/>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="areas" mode="ini">
    <xsl:call-template name="image_ini">
      <xsl:with-param name="idx">
        <xsl:value-of select="concat(count(ancestor::quiz/preceding-sibling::quiz/coloring)+1,
                              '-', count(ancestor::subquiz/preceding-sibling::subquiz/coloring)+1,
                              '_areas')"/>
      </xsl:with-param>
      <xsl:with-param name="size">100%%</xsl:with-param>
      <xsl:with-param name="ext">
        <xsl:call-template name="image_extension"/>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:template>

  <!--
      ========================================================================
      memory
      ========================================================================
  -->
  <xsl:template match="memory">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <div class="pquizMemoryItems hidden">
      <xsl:apply-templates select="match" mode="memory"/>
    </div>
    <div class="pquizMemoryBoard">
      <xsl:attribute name="data-number-display">
        <xsl:choose>
          <xsl:when test="@display">
            <xsl:value-of select="@display"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="count(match)"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:attribute>
      <xsl:attribute name="data-memory-delay">
        <xsl:choose>
          <xsl:when test="@delay">
            <xsl:value-of select="@delay * 1000"/>
          </xsl:when>
          <xsl:otherwise><xsl:text>500</xsl:text></xsl:otherwise>
        </xsl:choose>
      </xsl:attribute>
      <div class="pquizMemoryPick"><xsl:text> </xsl:text></div>
      <div class="pquizMemoryCorrectAnswer hidden"><xsl:text> </xsl:text></div>
    </div>
    <div class="pquizMemoryAnswerBox abs hidden">
      <div class="container"><xsl:text> </xsl:text></div>
    </div>
  </xsl:template>

  <xsl:template match="match" mode="memory">
    <xsl:variable name="match_num"
                  select="format-number(count(preceding-sibling::match)+1, '000')"/>
    <xsl:comment>
      <xsl:value-of select="concat('Item ', $match_num)"/>
    </xsl:comment>
    <div class="pquizMemoryItem" data-item-value="item{$match_num}"
         data-item-order="001">
      <div class="front abs">
        <xsl:apply-templates select="item[1]/image"/>
      </div>
      <xsl:call-template name="memory_backcard"/>
      <xsl:if test="item[1]/audio">
        <div class="hidden">
          <xsl:call-template name="audio">
            <xsl:with-param name="id" select="item[1]/audio/@id"/>
            <xsl:with-param name="controls" select="0"/>
            <xsl:with-param name="preload" select="1"/>
          </xsl:call-template>
        </div>
      </xsl:if>
    </div>

    <div class="pquizMemoryItem" data-item-value="item{$match_num}"
         data-item-order="002">
      <div class="front abs">
        <xsl:apply-templates select="item[2]/image"/>
      </div>
      <xsl:call-template name="memory_backcard"/>
      <xsl:if test="item[2]/audio">
        <div class="hidden">
          <xsl:call-template name="audio">
            <xsl:with-param name="id" select="item[2]/audio/@id"/>
            <xsl:with-param name="controls" select="0"/>
            <xsl:with-param name="preload" select="1"/>
          </xsl:call-template>
        </div>
      </xsl:if>
    </div>
  </xsl:template>

  <xsl:template name="memory_audios">
    <div class="pquizMemoryAudios hidden">
      <span class="right">
        <audio>
          <source src="{$aud_dir}right.ogg" type="audio/ogg" />
          <source src="{$aud_dir}right.mp3" type="audio/mpeg" />
          <span><xsl:value-of select="$i18n_noaudio"/></span>
        </audio>
      </span>
      <span class="wrong">
        <audio>
          <source src="{$aud_dir}wrong.ogg" type="audio/ogg" />
          <source src="{$aud_dir}wrong.mp3" type="audio/mpeg" />
          <span><xsl:value-of select="$i18n_noaudio"/></span>
        </audio>
      </span>
    </div>
  </xsl:template>

  <xsl:template name="memory_backcard">
    <div class="back abs">
      <img src="{$img_dir}back_card{$img_ext}" alt="back_card"/>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      production
      =========================================================================
  -->
  <xsl:template match="production">
    <div class="pquizEngine">
      <textarea cols="50" rows="5" class="pquizProduction">
        <xsl:value-of select="."/><xsl:text> </xsl:text>
      </textarea>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      composite
      =========================================================================
  -->
  <xsl:template match="composite">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <ol id="{$quiz_id}_engine" class="pquizElements">
      <xsl:apply-templates select="subquiz"/>
    </ol>
    <xsl:if test="@multipage='true'">
      <div>
        <a class="pquizButton pquizCompositePrevious">Précédent</a>
        <a class="pquizButton pquizCompositeNext">Suivant</a>
      </div>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      help
      =========================================================================
  -->
  <xsl:template match="help">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <div class="pquizHelpButton">
      <a href='#{$quiz_id}_help-slot' id="{$quiz_id}_help-link">
        <xsl:attribute name="class">
          <xsl:text>pquizButton</xsl:text>
          <xsl:apply-templates select="link" mode="class"/>
        </xsl:attribute>
        <xsl:value-of select="$i18n_help"/>
      </a>
    </div>
    <div id="{$quiz_id}_help-slot" class="pquizHelpPopUp hidden abs">
      <div class="helpContainer">
        <div class="helpClose"><xsl:text> </xsl:text></div>
        <h3 class="helplegend"><xsl:value-of select="$i18n_help"/></h3>
        <xsl:apply-templates
            select="section|p|speech|list|blockquote|table|media"/>
      </div>
    </div>
  </xsl:template>

  <xsl:template match="link" mode="include">
    <xsl:if test="@uri">
      <xsl:if test="//topic[@id=current()/@uri]/head/title">
        <h1><xsl:apply-templates select="//topic[@id=current()/@uri]/head/title"/></h1>
      </xsl:if>
      <xsl:apply-templates select="//topic[@id=current()/@uri]" mode="corpus"/>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      answer
      =========================================================================
  -->
  <xsl:template match="answer">
    <xsl:if test="not(ancestor::right|ancestor::wrong)">
      <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>
      <fieldset id="{$quiz_id}_answer-slot" class="pquizAnswerText">
        <legend> <xsl:value-of select="$i18n_answer"/> </legend>
        <xsl:apply-templates
            select="section|p|speech|list|blockquote|table|media"/>
      </fieldset>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      grid, line, cell
      =========================================================================
  -->
  <xsl:template match="grid">
    <table>
      <xsl:apply-templates select="line"/>
    </table>
  </xsl:template>

  <xsl:template match="line">
    <tr>
      <xsl:apply-templates select="cell"/>
    </tr>
  </xsl:template>

  <xsl:template match="cell">
    <td>
      <xsl:apply-templates/>
    </td>
  </xsl:template>


  <!--
      *************************************************************************
                                   INLINE LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      Template note_file
      =========================================================================
  -->
  <xsl:template name="note_file">
    <xsl:call-template name="html_file">
      <xsl:with-param name="name">
        <xsl:value-of
            select="concat($fid, '-not-', format-number(count(preceding::note)+1, '0000'))"/>
      </xsl:with-param>
      <xsl:with-param name="title">
        <xsl:apply-templates select="." mode="title"/>
      </xsl:with-param>
      <xsl:with-param name="nojs" select="1"/>
      <xsl:with-param name="body">
        <body class="pdocNote">
          <h1><xsl:apply-templates select="." mode="title"/></h1>
          <div class="pdocNoteText">
            <xsl:apply-templates select="*[name()!='w']|text()"/>
          </div>
          <div class="pdocNoteBack">
            <xsl:choose>
              <xsl:when test="$toc_division_depth&gt;count(ancestor::division)-1
                              and (ancestor::front or name(../../..)='division')">
                <a href="{$fid}-div-{format-number(count(preceding::division
                         |ancestor::division), '0000')}{$html_ext}#n{count(preceding::note)+1}">
                  <xsl:value-of select="concat('— ', $i18n_back, ' —')"/>
                </a>
              </xsl:when>
              <xsl:when test="(name(//*/*)='topic' or name(//*/*)='quiz')
                              and not(contains($path, 'Container~/'))">
                <a href="{$home}{$html_ext}#n{count(preceding::note)+1}">
                  <xsl:value-of select="concat('— ', $i18n_back, ' —')"/>
                </a>
              </xsl:when>
              <xsl:when test="ancestor::quiz">
                <a href="{$fid}-quz-{format-number(count(preceding::quiz)+1, '0000')}{$html_ext}#n{count(preceding::note)+1}">
                  <xsl:value-of select="concat('— ', $i18n_back, ' —')"/>
                </a>
              </xsl:when>
              <xsl:otherwise>
                <a href="{$fid}-tpc-{format-number(count(preceding::topic)+1, '0000')}{$html_ext}#n{count(preceding::note)+1}">
                  <xsl:value-of select="concat('— ', $i18n_back, ' —')"/>
                </a>
              </xsl:otherwise>
            </xsl:choose>
          </div>
        </body>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:template>

  <!--
      =========================================================================
      blank
      =========================================================================
  -->
  <xsl:template match="blank">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <xsl:choose>
      <xsl:when test="ancestor::blanks-fill">
        <xsl:choose>
          <xsl:when test="@area='true'">
            <textarea class="pquizChoice" cols="50" rows="3">
              <xsl:attribute name="id">
                <xsl:value-of select="concat($quiz_id, '_')"/>
                <xsl:call-template name="blank_num"/>
              </xsl:attribute>
              <xsl:text> </xsl:text>
            </textarea>
          </xsl:when>
          <xsl:otherwise>
            <input type="text">
              <xsl:attribute name="class">
                <xsl:text>pquizChoice </xsl:text>
                <xsl:if test="@type">
                  <xsl:value-of select="@type"/>
                </xsl:if>
              </xsl:attribute>
              <xsl:attribute name="id">
                <xsl:value-of select="concat($quiz_id, '_')"/>
                <xsl:call-template name="blank_num"/>
              </xsl:attribute>
              <xsl:if test="ancestor::blanks-fill/@long or @long">
                <xsl:attribute name="style">
                  <xsl:text>width: </xsl:text>
                  <xsl:choose>
                    <xsl:when test="@long"><xsl:value-of select="@long"/></xsl:when>
                    <xsl:otherwise>
                      <xsl:value-of select="ancestor::blanks-fill/@long"/>
                    </xsl:otherwise>
                  </xsl:choose>
                  <xsl:text>em;</xsl:text>
                </xsl:attribute>
              </xsl:if>
            </input>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>

      <xsl:when test="ancestor::blanks-select">
        <xsl:choose>
          <xsl:when
              test="(((not(ancestor::composite) and not(ancestor::quiz/processing-instruction('argument')))
                    or (ancestor::composite and not(contains(ancestor::quiz/processing-instruction('argument'), 'blanks-select:'))))
                    and $mode_blanks_select='combobox')
                    or (not(ancestor::composite) and ancestor::quiz/processing-instruction('argument')='combobox')
                    or contains(ancestor::quiz/processing-instruction('argument'), 'blanks-select:combobox')">
            <xsl:choose>
              <xsl:when test="ancestor::dropzone">
                <div class="pquizDropzone pquizDrop">
                  <xsl:attribute name="style">
                    <xsl:value-of
                        select="concat('position: absolute; left:', ancestor::dropzone/@x, '; top:',
                                ancestor::dropzone/@y, ';')"/>
                    <xsl:choose>
                      <xsl:when test="ancestor::dropzone/@h">
                        <xsl:value-of select="concat(' height:', ancestor::dropzone/@h, ';')"/>
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:text> height:5%;</xsl:text>
                      </xsl:otherwise>
                    </xsl:choose>
                    <xsl:choose>
                      <xsl:when test="ancestor::dropzone/@w">
                        <xsl:value-of select="concat(' width:', ancestor::dropzone/@w, ';')"/>
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:text> width:15%;</xsl:text>
                      </xsl:otherwise>
                    </xsl:choose>
                  </xsl:attribute>
                  <xsl:call-template name="select_item"/>
                </div>
              </xsl:when>
              <xsl:otherwise>
                <xsl:call-template name="select_item"/>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:when>
          <xsl:otherwise>
            <xsl:choose>
              <xsl:when test="ancestor::dropzone">
                <div class="pquizDropzone pquizDropzone-visible pquizDrop">
                  <xsl:attribute name="style">
                    <xsl:value-of
                        select="concat('position: absolute; left:', ancestor::dropzone/@x, '; top:',
                                ancestor::dropzone/@y, ';')"/>
                    <xsl:choose>
                      <xsl:when test="ancestor::dropzone/@h">
                        <xsl:value-of select="concat(' height:', ancestor::dropzone/@h, ';')"/>
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:text> height:5%;</xsl:text>
                      </xsl:otherwise>
                    </xsl:choose>
                    <xsl:choose>
                      <xsl:when test="ancestor::dropzone/@w">
                        <xsl:value-of select="concat(' width:', ancestor::dropzone/@w, ';')"/>
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:text> width:15%;</xsl:text>
                      </xsl:otherwise>
                    </xsl:choose>
                  </xsl:attribute>
                  <xsl:attribute name="id">
                    <xsl:value-of select="concat($quiz_id, '_')"/>
                    <xsl:call-template name="blank_num"/>
                  </xsl:attribute>
                  <xsl:text> </xsl:text>
                </div>
              </xsl:when>
              <xsl:otherwise>
                <span class="pquizDrop pquizDots">
                  <xsl:attribute name="id">
                    <xsl:value-of select="concat($quiz_id, '_')"/>
                    <xsl:call-template name="blank_num"/>
                  </xsl:attribute>
                  <xsl:text> </xsl:text>
                </span>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>

      <xsl:when test="ancestor::blanks-media">
        <xsl:choose>
          <xsl:when test="ancestor::dropzone">
            <div class="pquizDropzone pquizDropzone-visible pquizDrop">
              <xsl:attribute name="style">
                <xsl:value-of
                    select="concat('position: absolute; left:', ancestor::dropzone/@x, '; top:',
                            ancestor::dropzone/@y, '; height:', ancestor::dropzone/@h, '; width:',
                            ancestor::dropzone/@w, ';')"/>
              </xsl:attribute>
              <xsl:attribute name="id">
                <xsl:value-of select="concat($quiz_id, '_')"/>
                <xsl:call-template name="blank_num"/>
              </xsl:attribute>
              <xsl:text> </xsl:text>
            </div>
          </xsl:when>
          <xsl:otherwise>
            <span class="pquizDrop pquizDots">
              <xsl:attribute name="id">
                <xsl:value-of select="concat($quiz_id, '_')"/>
                <xsl:call-template name="blank_num"/>
              </xsl:attribute>
              <xsl:text> </xsl:text>
            </span>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>

      <xsl:when test="ancestor::blanks-choices">
        <xsl:choose>
          <xsl:when
              test="(((not(ancestor::composite) and not(ancestor::quiz/processing-instruction('argument')))
                    or (ancestor::composite and not(contains(ancestor::quiz/processing-instruction('argument'), 'blanks-choices:'))))
                    and $mode_blanks_choices='pointing')
                    or (not(ancestor::composite) and ancestor::quiz/processing-instruction('argument')='pointing')
                    or contains(ancestor::quiz/processing-instruction('argument'), 'blanks-choices:pointing')">

            <span class="pquizPointChoices">
              <xsl:attribute name="id">
                <xsl:value-of select="concat($quiz_id, '_')"/>
                <xsl:call-template name="blank_num"/>
              </xsl:attribute>
              <xsl:for-each select="right|wrong">
                <xsl:if test="preceding-sibling::right or preceding-sibling::wrong">
                  <xsl:text> / </xsl:text>
                </xsl:if>
                <span class="pquizPoint">
                  <xsl:attribute name="data-choice-value">
                    <xsl:value-of select="translate(normalize-space(), ' :', '__')"/>
                  </xsl:attribute>
                  <xsl:apply-templates/>
                </span>
              </xsl:for-each>
            </span>
          </xsl:when>
          <xsl:otherwise>
            <xsl:choose>
              <xsl:when test="ancestor::dropzone">
                <div class="pquizDropzone pquizDrop">
                  <xsl:attribute name="style">
                    <xsl:value-of
                        select="concat('position: absolute; left:', ancestor::dropzone/@x, '; top:',
                                ancestor::dropzone/@y, ';')"/>
                    <xsl:choose>
                      <xsl:when test="ancestor::dropzone/@h">
                        <xsl:value-of select="concat(' height:', ancestor::dropzone/@h, ';')"/>
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:text> height:5%;</xsl:text>
                      </xsl:otherwise>
                    </xsl:choose>
                    <xsl:choose>
                      <xsl:when test="ancestor::dropzone/@w">
                        <xsl:value-of select="concat(' width:', ancestor::dropzone/@w, ';')"/>
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:text> width:15%;</xsl:text>
                      </xsl:otherwise>
                    </xsl:choose>
                  </xsl:attribute>
                  <xsl:call-template name="bc_select_item"/>
                </div>
              </xsl:when>
              <xsl:otherwise>
                <xsl:call-template name="bc_select_item"/>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="select_item">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>
    <select class="pquizSelectItem">
      <xsl:attribute name="id">
        <xsl:value-of select="concat($quiz_id, '_')"/>
        <xsl:call-template name="blank_num"/>
      </xsl:attribute>
      <option value=""> </option>
      <xsl:for-each select="ancestor::blanks-select//blank[not(s)]|ancestor::blanks-select//blank/s">
        <option>
          <xsl:attribute name="value">
            <xsl:value-of select="translate(normalize-space(), ' :', '__')"/>
          </xsl:attribute>
          <xsl:value-of select="normalize-space()"/>
        </option>
      </xsl:for-each>
    </select>
  </xsl:template>

  <xsl:template name="bc_select_item">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>
    <select class="pquizSelectChoices">
      <xsl:attribute name="id">
        <xsl:value-of select="concat($quiz_id, '_')"/>
        <xsl:call-template name="blank_num"/>
      </xsl:attribute>
      <option value=""> </option>
      <xsl:for-each select="right|wrong">
        <option>
          <xsl:attribute name="value">
            <xsl:value-of select="translate(normalize-space(), ' :', '__')"/>
          </xsl:attribute>
          <xsl:value-of select="normalize-space()"/>
        </option>
      </xsl:for-each>
    </select>
  </xsl:template>

  <!--
      =========================================================================
      char
      =========================================================================
  -->
  <xsl:template match="char">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <span class="pquizLetter">
      <xsl:if test="@function">
        <xsl:attribute name="data-function">
          <xsl:value-of select="@function"/>
        </xsl:attribute>
      </xsl:if>
      <xsl:value-of select="."/>
    </span>
  </xsl:template>

  <!--
      =========================================================================
      point
      =========================================================================
  -->
  <xsl:template match="point">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <span>
      <xsl:attribute name="class">
        <xsl:text>pquizPoint</xsl:text>
        <xsl:if test="image or audio or video"> pquizPointMedia</xsl:if>
      </xsl:attribute>
      <xsl:choose>
        <xsl:when test="ancestor::pointing-categories">
          <xsl:attribute name="data-choice-id">
            <xsl:value-of
                select="format-number(count(preceding::point)
                        -count(ancestor::pointing-categories/preceding::point)+1,
                        '000')"/>
          </xsl:attribute>
        </xsl:when>
        <xsl:otherwise>
          <xsl:attribute name="id">
            <xsl:value-of select="concat($quiz_id, '_')"/>
            <xsl:call-template name="point_num"/>
          </xsl:attribute>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:apply-templates/>
    </span>
  </xsl:template>

</xsl:stylesheet>
