<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml">

  <xsl:import href="publidoc2xhtml_template.inc.xsl"/>
  <xsl:import href="publidoc2xhtml_i18n.inc.xsl"/>
  <xsl:import href="publidoc2xhtml_base.inc.xsl"/>
  <xsl:import href="publidoc2xhtml_media.inc.xsl"/>
  <xsl:import href="publidoc2html5_template.inc.xsl"/>
  <xsl:import href="publidoc2html5_media.inc.xsl"/>
  <xsl:import href="publiquiz2html5_template.inc.xsl"/>
  <xsl:import href="publiquiz2html5_i18n.inc.xsl"/>
  <xsl:import href="publiquiz2html5_base.inc.xsl"/>

  <!-- PubliForge parameters -->
  <xsl:param name="fid"/>         <!-- XML File name without extension -->
  <xsl:param name="route"/>       <!-- Route to the opener public directory -->
  <xsl:param name="main_route"/>  <!-- Route to the main public directory -->

  <!-- Processor image variables -->
  <xsl:variable name="img" select="1"/>
  <xsl:variable name="img_ext"></xsl:variable>
  <xsl:variable name="img_ext_cover"></xsl:variable>
  <xsl:variable name="img_ext_icon"></xsl:variable>
  <xsl:variable name="img_size">1280x1280&gt;</xsl:variable>
  <!-- Processor audio variables -->
  <xsl:variable name="aud" select="1"/>
  <xsl:variable name="aud_ext1"></xsl:variable>
  <xsl:variable name="aud_ext2"></xsl:variable>
  <xsl:variable name="aud_custom" select="1"/>
  <!-- Processor video variables -->
  <xsl:variable name="vid" select="1"/>
  <xsl:variable name="vid_ext1"></xsl:variable>
  <xsl:variable name="vid_ext2"></xsl:variable>
  <xsl:variable name="vid_width">300</xsl:variable>
  <!-- Processor string parameters -->
  <xsl:variable name="str_sep"> – </xsl:variable>
  <xsl:variable name="str_notecall_open">(</xsl:variable>
  <xsl:variable name="str_notecall_close">)</xsl:variable>
  <!-- Processor quiz variables -->
  <xsl:variable name="max_retry" select="0"/>
  <xsl:variable name="base_score" select="0"/>
  <xsl:variable name="success_threshold" select="1.0"/>
  <xsl:variable name="mode_validation" select="0"/>
  <xsl:variable name="matching_link" select="1"/>
  <xsl:variable name="correct_line" select="1"/>
  <xsl:variable name="wordsearch" select="1"/>
  <xsl:variable name="flashcard" select="1"/>
  <xsl:variable name="coloring" select="1"/>
  <xsl:variable name="memory" select="1"/>
  <xsl:variable name="mode_choices_check">check</xsl:variable>
  <xsl:variable name="mode_blanks_choices">combobox</xsl:variable>
  <xsl:variable name="mode_blanks_select">dragndrop</xsl:variable>
  <xsl:variable name="mode_categories">basket</xsl:variable>
  <xsl:variable name="mode_matching">dragndrop</xsl:variable>
  <xsl:variable name="context_ttl" select="-1"/>
  <xsl:variable name="context_key"></xsl:variable>
  <!-- Processor HTML variables -->
  <xsl:variable name="toc" select="1"/>
  <xsl:variable name="toc_division_depth" select="5"/>
  <xsl:variable name="toc_section_depth" select="1"/>
  <xsl:variable name="toc_with_abstract" select="1"/>
  <xsl:variable name="subtoc" select="0"/>
  <xsl:variable name="index" select="1"/>
  <!-- Processor HTML 5 variables -->
  <xsl:variable name="onefile" select="1"/>
  <xsl:variable name="js" select="1"/>

  <!-- Variables -->
  <xsl:variable name="img_dir"
                select="concat($main_route, 'Images/notfound.jpg#')"/>
  <xsl:variable name="aud_dir">/media/audios/</xsl:variable>
  <xsl:variable name="vid_dir">/media/videos/</xsl:variable>
  <xsl:variable name="lang">
    <xsl:choose>
      <xsl:when test="/*/*/@xml:lang">
        <xsl:value-of select="/*/*/@xml:lang"/>
      </xsl:when>
      <xsl:otherwise>en</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>


  <xsl:output method="xml" encoding="utf-8" indent="yes"
              omit-xml-declaration="yes"/>

  <!--
      =========================================================================
      publiquiz
      =========================================================================
  -->
  <xsl:template match="publiquiz">
    <xsl:apply-templates select="document|topic|quiz"/>
  </xsl:template>

  <!--
      =========================================================================
      document
      =========================================================================
  -->
  <xsl:template match="document">
    <div class="pdocDocument">
      <xsl:apply-templates select="." mode="meta"/>
      <xsl:if test="head/title">
        <div class="h1">
          <xsl:apply-templates select="head/title"/>
          <xsl:if test="head/subtitle">
            <div><xsl:call-template name="subtitle"/></div>
          </xsl:if>
        </div>
      </xsl:if>
      <xsl:apply-templates select="head" mode="cover"/>
      <xsl:apply-templates select="." mode="onefiletoc"/>

      <xsl:apply-templates select="division|topic|quiz" mode="onefile"/>
      <xsl:call-template name="quiz_action"/>

      <xsl:if test=".//note">
        <div class="pdocNoteFooter">
          <xsl:apply-templates select=".//note" mode="footer"/>
        </div>
      </xsl:if>
      <xsl:call-template name="warnings"/>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      topic
      =========================================================================
  -->
  <xsl:template match="topic">
    <div>
      <xsl:attribute name="class">
        <xsl:text>pdocTopic</xsl:text>
        <xsl:if test="@type"> pdocTopic-<xsl:value-of select="@type"/></xsl:if>
      </xsl:attribute>
      <xsl:apply-templates select="." mode="meta"/>
      <xsl:apply-templates select="header"/>
      <xsl:if test="head/title">
        <h1><xsl:apply-templates select="head/title"/></h1>
      </xsl:if>
      <xsl:if test="head/subtitle">
        <h2><xsl:call-template name="subtitle"/></h2>
      </xsl:if>
      <xsl:apply-templates select="." mode="onefiletoc"/>
      <xsl:apply-templates select="." mode="corpus"/>
      <xsl:apply-templates select="footer"/>
      <xsl:if test=".//note">
        <div class="pdocNoteFooter">
          <xsl:apply-templates select=".//note" mode="footer"/>
        </div>
      </xsl:if>
      <xsl:call-template name="warnings"/>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      quiz
      =========================================================================
  -->
  <xsl:template match="quiz">
    <div class="pquizQuiz">
      <xsl:apply-templates select="." mode="meta"/>
      <xsl:if test="head/title">
        <h1><xsl:apply-templates select="head/title"/></h1>
      </xsl:if>
      <xsl:if test="head/subtitle">
        <h2><xsl:apply-templates select="head/subtitle"/></h2>
      </xsl:if>
      <xsl:apply-templates select="." mode="onefiletoc"/>

      <xsl:apply-templates select="." mode="corpus"/>
      <xsl:call-template name="quiz_action"/>
      <xsl:if test=".//note">
        <div class="pdocNoteFooter">
          <xsl:apply-templates select=".//note" mode="footer"/>
        </div>
      </xsl:if>
      <xsl:call-template name="warnings"/>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      warning
      =========================================================================
  -->
  <xsl:template match="warning">
    <xsl:variable name="count" select="count(preceding::warning)+1"/>
    <a href="#wc{$count}" id="w{$count}"
       class="pdocWarning"><xsl:apply-templates/></a>
  </xsl:template>

  <xsl:template match="warning" mode="call">
    <xsl:variable name="count" select="count(preceding::warning)+1"/>
    <a href="#w{$count}" id="wc{$count}">
      <span>(<xsl:value-of select="$count"/>) </span>
      <xsl:apply-templates/>
    </a>
    <xsl:if test="following::warning">
      <span> | </span>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      Template warnings
      =========================================================================
  -->
  <xsl:template name="warnings">
    <xsl:if test=".//warning">
      <div class="pdocWarnings">
        <label><xsl:value-of select="count(.//warning)"/> warning(s)</label>
        <xsl:apply-templates select=".//warning" mode="call"/>
      </div>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      Template pulse_gif
      =========================================================================
  -->
  <xsl:template name="pulse_gif">
    <xsl:value-of select="concat($route, 'Images/pulse.gif')"/>
  </xsl:template>

  <!--
      =========================================================================
      Template image_extension
      =========================================================================
  -->
  <xsl:template name="image_extension"/>

  <!--
      =========================================================================
      Template WordsearchTools
      =========================================================================
  -->
  <xsl:template name="WordsearchTools">
    <div class="pquizWordsearchTools">
      <div class="pquizWordsearchHighlighter"><img alt="highlighter" src="{$route}Images/highlighter.png"/></div>
      <div class="pquizWordsearchEraser"><img alt="eraser" src="{$route}Images/eraser.png"/></div>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      coloring
      =========================================================================
  -->
  <xsl:template match="coloring">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>

    <div id="{$quiz_id}_engine" class="pquizEngine">
      <div id="{$quiz_id}_correct" class="hidden">
        <xsl:call-template name="coloring_correct"/>
      </div>
      <div class="pquizColoringPalette">
        <xsl:call-template name="coloring_palette"/>
      </div>
      <img class="pquizColoringOutline hidden">
        <xsl:attribute name="src">
          <xsl:value-of select="concat($img_dir, canvas/@id, $img_ext)"/>
        </xsl:attribute>
      </img>
      <img class="pquizColoringMask hidden">
        <xsl:attribute name="src">
          <xsl:value-of select="concat($img_dir, areas/@id, $img_ext)"/>
        </xsl:attribute>
      </img>
      <canvas class="pquizColoringCanvas" id="{$quiz_id}">
        <xsl:attribute name="width">
          <xsl:value-of select="substring-before($img_size, 'x')"/>
        </xsl:attribute>
        <xsl:attribute name="height">
          <xsl:value-of select="substring-after($img_size, 'x')"/>
        </xsl:attribute>
        <xsl:text>Your browser doesn't support canvas.</xsl:text>
      </canvas>
    </div>
  </xsl:template>

  <xsl:template name="coloring_palette">
    <xsl:choose>
      <xsl:when test="@nomark='true'">
        <div class="pquizColoringToolSize">
          <div><xsl:value-of select="$i18n_thickness"/></div>
          <div class="pquizColoringToolSizeButtons">
            <span class="pquizColoringToolSizeMinus">-</span>
            <span class="pquizColoringToolSizeValue">05</span>
            <span class="pquizColoringToolSizePlus">+</span>
          </div>
        </div>
        <div class="pquizColoringTool selected" data-drawing-tool="brush">
          <div class="pquizColoringSample">
            <img class="pquizColoringBrush" src="{$route}/Images/brush.png" alt="paint_brush"/>
          </div>
        </div>
        <xsl:if test="areas">
          <div class="pquizColoringTool" data-drawing-tool="bucket">
            <div class="pquizColoringSample">
              <img class="pquizColoringBucket" src="{$route}/Images/bucket.png" alt="paint_bucket"/>
            </div>
          </div>
        </xsl:if>
        <div class="pquizColoringTool" data-drawing-tool="eraser">
          <div class="pquizColoringSample">
            <img class="pquizColoringEraser" src="{$route}/Images/eraser.png" alt="paint_eraser"/>
          </div>
        </div>
      </xsl:when>

      <xsl:otherwise>
        <div class="pquizColoringTool" data-drawing-color="#ffffff">
          <div class="pquizColoringSample">
            <img class="pquizColoringEraser" src="{$route}/Images/eraser.png" alt="paint_eraser"/>
          </div>
        </div>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates select="palette/color"/>
  </xsl:template>

  <!--
      =========================================================================
      memory
      =========================================================================
  -->
  <xsl:template name="memory_backcard">
    <div class="back abs">
      <img src="{$route}/Images/back_card.png" alt="back_card"/>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      audio mode header
      =========================================================================
  -->
  <xsl:template match="audio" mode="header">
    <xsl:if test="$aud and @type='background'
                  and count(preceding::audio[@type='background'])=0">
      <xsl:call-template name="audio">
        <xsl:with-param name="controls" select="0"/>
        <xsl:with-param name="autoplay" select="1"/>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      Template audio_symbol
      =========================================================================
  -->
  <xsl:template name="audio_symbol">
    <xsl:param name="id" select="@id"/>
    <img src="{$route}Images/audio_play.png" alt="{$id}"/>
  </xsl:template>

  <!--
      =========================================================================
      Template math
      =========================================================================
  -->
  <xsl:template name="math">
    <xsl:apply-templates/>
  </xsl:template>

   <xsl:template match="latex">
    <xsl:choose>
      <xsl:when test="@plain='true'">
        <xsl:apply-templates/>
      </xsl:when>
      <xsl:when test="../@display='wide'">
        <xsl:text>\[</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>\]</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>\(</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>\)</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      PI hold
      =========================================================================
  -->
  <xsl:template match="processing-instruction('hold')">
    <xsl:text> </xsl:text>
  </xsl:template>

</xsl:stylesheet>
