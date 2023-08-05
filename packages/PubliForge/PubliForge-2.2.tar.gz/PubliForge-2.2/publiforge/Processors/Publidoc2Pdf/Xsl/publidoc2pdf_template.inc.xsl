<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!--
      *************************************************************************
                                    CALLABLE TEMPLATES
      *************************************************************************
  -->
  <!--
      =========================================================================
      Template packages
      =========================================================================
  -->
  <xsl:template name="packages">
\usepackage[<xsl:value-of select="$paper_size"/>,
  layoutwidth=<xsl:value-of select="$layout_width"/>mm,
  layoutheight=<xsl:value-of select="$layout_height"/>mm,
  layoutoffset=<xsl:value-of select="$layout_offset"/>mm,
  width=<xsl:value-of select="$body_width"/>mm,
  height=<xsl:value-of select="$body_height"/>mm,
  left=<xsl:value-of select="$margin_left"/>mm,
  top=<xsl:value-of select="$margin_top"/>mm,
  bindingoffset=<xsl:value-of select="$bindingoffset"/>mm,
  headsep=<xsl:value-of select="$headsep"/>mm,
  footskip=<xsl:value-of select="$footskip"/>mm]{geometry}
\usepackage{fontspec}
\usepackage{scrlayer-scrpage}
\usepackage{ifthen}
\usepackage{graphicx}
\usepackage{tabulary}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{lettrine}
\usepackage[frenchb]{babel}
\usepackage[
  unicode=true,
  pdfcreator=PubliForge,
  bookmarksopen=true,
  bookmarksopenlevel=0,
  breaklinks=true,
  colorlinks=true,
  allcolors=black,
  urlcolor=blue]{hyperref}
<xsl:call-template name="extra_packages"/>
  </xsl:template>

  <!--
      =========================================================================
      Template extra_packages
      =========================================================================
  -->
  <xsl:template name="extra_packages">
%\usepackage{lipsum}
  </xsl:template>

  <!--
      =========================================================================
      Template font_families
      =========================================================================
  -->
  <xsl:template name="font_families">
% Font families
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
\newfontfeature{Microtype}{protrusion=default;expansion=default}
\setmainfont
    [Microtype, Ligatures=TeX]{Linux Libertine O}
\setsansfont
    [Microtype, Ligatures=TeX]{Linux Biolinum O}
\setmonofont
    [Microtype, Ligatures=TeX]{FreeMono}
<!-- \setmonofont -->
<!--     [Microtype, Ligatures=TeX]{Linux Libertine Mono O} (Not on Wheezy)-->

\newfontfamily\fontfamilySerif
    [Microtype, Ligatures=TeX]{Linux Libertine O}
\newfontfamily\fontfamilySans
    [Microtype, Ligatures=TeX]{Linux Biolinum O}
\newfontfamily\fontfamilyMono
    [Microtype, Ligatures=TeX]{FreeMono}
<!-- \newfontfamily\fontfamilyMono -->
<!--     [Microtype, Ligatures=TeX]{Linux Libertine Mono O} -->
\newfontfamily\fontfamilyScript
    [Microtype, Ligatures=TeX, Path=<xsl:value-of select="$font_dir"/>,
     Extension=.otf]{Script}
   </xsl:template>

   <!--
      =========================================================================
      Template fonts
      =========================================================================
  -->
  <xsl:template name="fonts">
% Fonts
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
\newcommand{\fontmain}{<xsl:call-template name="font"><xsl:with-param name="fnt" select="$font_main"/></xsl:call-template>\selectfont}
\newcommand{\fontheader}{<xsl:call-template name="font"><xsl:with-param name="fnt" select="$font_header"/></xsl:call-template>\selectfont}
\newcommand{\fontfolio}{<xsl:call-template name="font"><xsl:with-param name="fnt" select="$font_folio"/></xsl:call-template>\selectfont}
\newcommand{\fonttitleA}{<xsl:call-template name="font"><xsl:with-param name="fnt" select="$font_title1"/></xsl:call-template>\selectfont}
\newcommand{\fonttitleB}{<xsl:call-template name="font"><xsl:with-param name="fnt" select="$font_title2"/></xsl:call-template>\selectfont}
\newcommand{\fonttitleC}{<xsl:call-template name="font"><xsl:with-param name="fnt" select="$font_title3"/></xsl:call-template>\selectfont}
\newcommand{\fonttitleD}{<xsl:call-template name="font"><xsl:with-param name="fnt" select="$font_title4"/></xsl:call-template>\selectfont}
\newcommand{\fonttitleE}{<xsl:call-template name="font"><xsl:with-param name="fnt" select="$font_title5"/></xsl:call-template>\selectfont}
\newcommand{\fontnote}{<xsl:call-template name="font"><xsl:with-param name="fnt" select="$font_note"/></xsl:call-template>\selectfont}
\newcommand{\fontquote}{<xsl:call-template name="font"><xsl:with-param name="fnt" select="$font_quote"/></xsl:call-template>\selectfont}
\newcommand{\fontfront}{<xsl:call-template name="font"><xsl:with-param name="fnt">, /, ,</xsl:with-param><xsl:with-param name="dlt" select="2"/></xsl:call-template>\fontfamilySans\selectfont}
<xsl:call-template name="extra_fonts"/>
  </xsl:template>

  <!--
      =========================================================================
      Template extra_fonts
      =========================================================================
  -->
  <xsl:template name="extra_fonts"/>

  <!--
      =========================================================================
      Template font
      =========================================================================
  -->
  <xsl:template name="font">
    <xsl:param name="fnt"/>
    <xsl:param name="dlt" select="0"/>

    <xsl:text>\fontfamily</xsl:text>
    <xsl:choose>
      <xsl:when test="substring-before($fnt, ',')">
        <xsl:value-of select="substring-before($fnt, ',')"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="substring-before($font_main, ',')"/>
      </xsl:otherwise>
    </xsl:choose>

    <xsl:text>\fontsize{</xsl:text>
    <xsl:choose>
      <xsl:when test="substring-before(substring-after($fnt, ', '), '/')">
        <xsl:value-of select="translate(substring-before(substring-after($fnt, ', '), '/') + $dlt, ',', '.')"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="translate(substring-before(substring-after($font_main, ', '), '/') + $dlt, ',', '.')"/>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:text>}{</xsl:text>
    <xsl:choose>
      <xsl:when test="contains($fnt, '+') and substring-before(substring-after($fnt, '/'), '+')">
        <xsl:value-of select="translate(substring-before(substring-after($fnt, '/'), '+') + $dlt, ',', '.')"/>
      </xsl:when>
      <xsl:when test="not(contains($fnt, '+')) and substring-before(substring-after($fnt, '/'), ',')">
        <xsl:value-of select="translate(substring-before(substring-after($fnt, '/'), ',') + $dlt, ',', '.')"/>
      </xsl:when>
      <xsl:when test="contains($font_main, '+')">
        <xsl:value-of select="translate(substring-before(substring-after($font_main, '/'), '+') + $dlt, ',', '.')"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="translate(substring-before(substring-after($font_main, '/'), ',') + $dlt, ',', '.')"/>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:choose>
      <xsl:when test="contains($fnt, '+') and substring-before(substring-after($fnt, '+'), ',')">
        <xsl:text>pt plus </xsl:text><xsl:value-of select="substring-before(substring-after($fnt, '+'), ',')"/>
      </xsl:when>
      <xsl:when test="contains($font_main, '+')">
        <xsl:text>pt plus </xsl:text><xsl:value-of select="substring-before(substring-after($font_main, '+'), ',')"/>
      </xsl:when>
    </xsl:choose>
    <xsl:text>pt}</xsl:text>

    <xsl:text>\fontseries{</xsl:text>
    <xsl:choose>
      <xsl:when test="substring-before(substring-after(substring-after($fnt, ', '), ', '), ',')">
        <xsl:value-of select="substring-before(substring-after(substring-after($fnt, ', '), ', '), ',')"/>
      </xsl:when>
      <xsl:otherwise>m</xsl:otherwise>
    </xsl:choose>
    <xsl:text>}</xsl:text>

    <xsl:text>\fontshape{</xsl:text>
    <xsl:choose>
      <xsl:when test="substring-after(substring-after(substring-after($fnt, ', '), ', '), ', ')">
        <xsl:value-of select="substring-after(substring-after(substring-after($fnt, ', '), ', '), ', ')"/>
      </xsl:when>
      <xsl:otherwise>n</xsl:otherwise>
    </xsl:choose>
    <xsl:text>}</xsl:text>
  </xsl:template>

  <!--
      =========================================================================
      Template variables_defines
      =========================================================================
  -->
  <xsl:template name="variables_defines">
% Variables and defines
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
\newcounter{topicfirstpage}
\newcommand{\headtitleeven}{}
\newcommand{\headtitleodd}{}
\newcommand{\header}{}
\newcommand{\footer}{}

\setlength{\unitlength}{1mm}
\setlength{\fboxsep}{4mm}
\renewcommand{\arraystretch}{1.4}
\setlength{\parindent}{<xsl:value-of select="$indentation"/>mm}
<xsl:if test="not($toc_numbering)">
\setcounter{secnumdepth}{-2}
</xsl:if>
  </xsl:template>

  <!--

      =========================================================================
      Template layout
      =========================================================================
  -->
  <xsl:template name="layout">
% Layout
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
<xsl:if test="not($web)">\geometry{showcrop}</xsl:if>
<xsl:if test="$debug">\geometry{showframe}</xsl:if>
<xsl:call-template name="layout_header_footer"/>
<xsl:call-template name="layout_headings"/>
<xsl:call-template name="layout_note"/>
<xsl:call-template name="layout_extra"/>
  </xsl:template>

  <!--
      =========================================================================
      Template layout_header_footer
      =========================================================================
  -->
  <xsl:template name="layout_header_footer">
<!--\cehead{ -->
<!--    \ifthenelse{\equal{\thepage}{\thetopicfirstpage}}{}{\fontheader\headtitleeven} -->
<!--} -->
\cehead[]{\fontheader\headtitleeven}
\cohead[]{\fontheader\headtitleodd}
\ofoot[]{\fontfolio\thepage}
  </xsl:template>

  <!--
      =========================================================================
      Template layout_headings
      =========================================================================
  -->
  <xsl:template name="layout_headings">
\addto\captionsfrench{\def\partname{}}
\addtokomafont{part}{\fonttitleA}
\addtokomafont{chapter}{\fonttitleB}
\addtokomafont{section}{\fonttitleC}
\addtokomafont{subsection}{\fonttitleD}
\addtokomafont{subsubsection}{\fonttitleE}
  </xsl:template>

  <!--
      =========================================================================
      Template layout_note
      =========================================================================
  -->
  <xsl:template name="layout_note">
\makeatletter
\long\def\@makefntextFB#1{%
    \noindent
    {\fontnote\@thefnmark.\,}#1%
}
\makeatother
  </xsl:template>

  <!--
      =========================================================================
      Template layout_extra
      =========================================================================
  -->
  <xsl:template name="layout_extra">
\sloppy
%\widowpenalty=8000
%\clubpenalty=8000
  </xsl:template>

  <!--
      =========================================================================
      Template pdfinfo
      =========================================================================
  -->
  <xsl:template name="pdfinfo">
    <xsl:if test="*/head/title or */head/contributors/contributor[role='author']">
      <xsl:text>\hypersetup{</xsl:text>

      <xsl:if test="*/head/title">
        <xsl:text>pdftitle={</xsl:text>
        <xsl:apply-templates select="*/head/title" mode="text"/>
        <xsl:text>}</xsl:text>
      </xsl:if>

      <xsl:if test="*/head/contributors/contributor[role='author']">
        <xsl:if test="*/head/title">, </xsl:if>
        <xsl:text>pdfauthor={</xsl:text>
        <xsl:for-each select="*/head/contributors/contributor[role='author']">
          <xsl:if test="position()!=1">, </xsl:if>
          <xsl:apply-templates select="firstname" mode="text"/>
          <xsl:text> </xsl:text>
          <xsl:apply-templates select="lastname|label" mode="text"/>
        </xsl:for-each>
        <xsl:text>}</xsl:text>
      </xsl:if>

      <xsl:text>}</xsl:text>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      Template title_page
      =========================================================================
  -->
  <xsl:template name="title_page">
    <xsl:if test="$title_page">
      <xsl:choose>
        <xsl:when test="not(.//topic[@type='title']) and */head/title">
% Title page
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
\begin{titlepage}
\begin{center}
~\par\vspace{3cm}
{\fontsize{24}{28pt}\fontshape{sc}\selectfont <xsl:apply-templates select="*/head/title"/>\\[2cm]}
<xsl:if test="*/head/subtitle">
  <xsl:for-each select="*/head/subtitle">{\fontsize{18}{22pt}\selectfont <xsl:apply-templates/>\\[1cm]}</xsl:for-each>
</xsl:if>
\vfill
<xsl:for-each select="*/head/contributors/contributor[role='author']">
  <xsl:apply-templates select="firstname"/>
  <xsl:text> </xsl:text>
  <xsl:apply-templates select="lastname|label"/>\par
</xsl:for-each>
\end{center}
\end{titlepage}
        </xsl:when>

        <xsl:otherwise>
          <xsl:apply-templates select=".//topic[@type='title']" mode="corpus"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      Template toc
      =========================================================================
  -->
  <xsl:template name="toc">
    <xsl:if test="$toc_depth!='-1'">
% Table of content
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
\cleardoublepage
\pagestyle{plain.scrheadings}
\renewcommand{\headtitleeven}{}
\renewcommand{\headtitleodd}{}
\renewcommand{\header}{}
\renewcommand{\footer}{}
\setcounter{tocdepth}{<xsl:value-of select="$toc_depth"/>}
\tableofcontents
\newpage
\pagestyle{scrheadings}
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      Template toc_title
      =========================================================================
  -->
  <xsl:template name="toc_title">
    <xsl:param name="title" select="head/title"/>
    <xsl:param name="front" select="front"/>

    <xsl:if test="$title">
      <xsl:variable name="nodivision" select="not(//division)"/>
      <xsl:variable
          name="depth"
          select="count(ancestor::division|ancestor::topic|ancestor::section)
                  + $nodivision"/>
      <xsl:if test="$depth=0 and $front">{\let\newpage\relax</xsl:if>
      <xsl:choose>
        <xsl:when test="$depth=0">\part</xsl:when>
        <xsl:when test="$depth=1">\chapter</xsl:when>
        <xsl:when test="$depth=2">\section</xsl:when>
        <xsl:when test="$depth=3">\subsection</xsl:when>
        <xsl:when test="$depth=4">\subsubsection</xsl:when>
        <xsl:when test="$depth=5">\paragraph</xsl:when>
        <xsl:otherwise>\subparagraph</xsl:otherwise>
      </xsl:choose>
      <xsl:text>[</xsl:text>
      <xsl:apply-templates select="$title" mode="link"/>
      <xsl:text>]{</xsl:text>
      <xsl:apply-templates select="$title"/>
      <xsl:text>}</xsl:text>
      <xsl:if test="$depth=0 and $front">}</xsl:if>
      <xsl:text>\nopagebreak </xsl:text>
      <xsl:if test="$front">
{\fontfront <xsl:apply-templates select="$front"/>}
<xsl:if test="$depth=0">\newpage </xsl:if>
<xsl:if test="$depth &gt; 0">\bigskip </xsl:if>
      </xsl:if>
    </xsl:if>
  </xsl:template>


  <!--
      *************************************************************************
                                 PROCESSING INSTRUCTIONS
      *************************************************************************
  -->
  <!--
      =========================================================================
      PI tune-latex
      =========================================================================
  -->
  <xsl:template match="processing-instruction('tune-latex-newpage')">
\null\newpage
  </xsl:template>

  <xsl:template match="processing-instruction('tune-latex-font-size')" mode="tune">
\fontsize{<xsl:value-of select="substring-before(normalize-space(), '/')"/>}%
         {<xsl:value-of select="substring-after(normalize-space(), '/')"/>}\selectfont
  </xsl:template>

  <!--
      =========================================================================
      PI latex
      =========================================================================
  -->
  <xsl:template match="processing-instruction('latex')">
    <xsl:choose>
      <xsl:when test="ancestor::latex"><xsl:value-of select="."/></xsl:when>
      <xsl:when test=".='\'">{\textbackslash}</xsl:when>
      <xsl:when test=".='~'">\~{}</xsl:when>
      <xsl:when test=".='^'">\^{}</xsl:when>
      <xsl:when test=".='['">{[}</xsl:when>
      <xsl:when test=".=']'">{]}</xsl:when>
      <xsl:when test=".='pi'">$\pi$</xsl:when>
      <xsl:when test=".='simeq'">$\simeq$</xsl:when>
      <xsl:when test=".='&amp;amp;'">\&amp;</xsl:when>
      <xsl:otherwise>\<xsl:value-of select="."/></xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
