<?xml version='1.0' encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml">

  <!--
      *************************************************************************
                                        AUDIO
      *************************************************************************
  -->
  <!--
      =========================================================================
      audio
      =========================================================================
  -->
  <xsl:template match="audio">
    <xsl:choose>
      <xsl:when test=".!=''">
        <xsl:choose>
          <xsl:when test="$aud">
	    <xsl:call-template name="audio_on_text"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="."/>
        </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:otherwise>
        <xsl:if test="$aud">
          <xsl:choose>
            <xsl:when test="$js and $aud_custom">
              <span class="pdocAudioPlayer">
                <xsl:call-template name="audio">
                  <xsl:with-param name="controls" select="0"/>
                </xsl:call-template>
                <span data-player="button-play" class="play">
                  <xsl:text> </xsl:text>
                </span>
              </span>
            </xsl:when>
            <xsl:otherwise>
              <xsl:call-template name="audio"/> 
            </xsl:otherwise>
          </xsl:choose>
        </xsl:if>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="audio" mode="media">
    <xsl:if test="$aud">
      <xsl:choose>
        <xsl:when test="@type='background'">
          <xsl:call-template name="audio">
            <xsl:with-param name="controls" select="0"/>
            <xsl:with-param name="autoplay" select="1"/>
          </xsl:call-template>
        </xsl:when>
        <xsl:when test="$js and $aud_custom">
          <div class="pdocAudioPlayer">
            <xsl:call-template name="audio">
              <xsl:with-param name="controls" select="0"/>
              <xsl:with-param name="preload" select="1"/>
            </xsl:call-template>
            <div data-player="button-play" class="play">
              <xsl:text> </xsl:text>
            </div>
            <div data-player="player-info">
              <div data-player="duration">0:00 / 0:00</div>
              <div data-player="timeline">
                <div data-player="cursor"><xsl:text> </xsl:text></div>
              </div>
            </div>
          </div>
        </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name="audio"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:if>
  </xsl:template>

  <xsl:template name="audio_on_text">
    <span>
      <xsl:attribute name="id">
	 <xsl:value-of select="concat('n', count(preceding::audio[(.)])+1)"/>
      </xsl:attribute>
      <xsl:attribute name="class">
	<xsl:text>pdocHotspot pdocHotspot-text</xsl:text>
      </xsl:attribute>
      <span style="display: none;"><xsl:text>show; </xsl:text></span>
      <xsl:value-of select="."/>
    </span>
    <span>
      <xsl:attribute name="id">
	 <xsl:value-of select="concat('n', count(preceding::audio[(.)])+1)"/>
         <xsl:text>s</xsl:text>
      </xsl:attribute>
      <xsl:attribute name="class">
	<xsl:text>pdocHotspotSpot hidden</xsl:text>
      </xsl:attribute>
      <xsl:call-template name="audio">
	<xsl:with-param name="controls" select="0"/>
      </xsl:call-template>
    </span>
  </xsl:template>

</xsl:stylesheet>
