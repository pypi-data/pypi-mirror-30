<?xml version='1.0' encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:variable name="i18n_type">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Type</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Tipo</xsl:when>
      <xsl:when test="starts-with($lang, 'it')">Tipo</xsl:when>
      <xsl:otherwise>Type</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_language">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Langue</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Idioma</xsl:when>
      <xsl:when test="starts-with($lang, 'it')">Lingua</xsl:when>
      <xsl:otherwise>Language</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_title">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Titre</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Título</xsl:when>
      <xsl:when test="starts-with($lang, 'it')">Titolo</xsl:when>
      <xsl:otherwise>title</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_shorttitle">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Titre court</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Título corto</xsl:when>
      <xsl:when test="starts-with($lang, 'it')">Titolo corto</xsl:when>
      <xsl:otherwise>Short title</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_subtitle">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Sous-titre</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Subtítulo</xsl:when>
      <xsl:when test="starts-with($lang, 'it')">Sottotitolo</xsl:when>
      <xsl:otherwise>Subtitle</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_identifier">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Identifiant</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Identificador</xsl:when>
      <xsl:when test="starts-with($lang, 'it')">Identificatore</xsl:when>
      <xsl:otherwise>Identifier</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  <xsl:variable name="i18n_identifier_ean">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">EAN</xsl:when>
      <xsl:otherwise>EAN</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  <xsl:variable name="i18n_identifier_ean_epub">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">EAN ePub</xsl:when>
      <xsl:otherwise>EAN for ePub</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  <xsl:variable name="i18n_identifier_ean_print">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">EAN papier</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">EAN papel</xsl:when>
      <xsl:otherwise>EAN for print</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  <xsl:variable name="i18n_identifier_uri">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">URI</xsl:when>
      <xsl:otherwise>URI</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_copyright">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Copyright</xsl:when>
      <xsl:otherwise>Copyright</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_dedication">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Dédicace</xsl:when>
      <xsl:otherwise>Dedication</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_inscription">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Exergue</xsl:when>
      <xsl:otherwise>Inscription</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_collection">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Collection</xsl:when>
      <xsl:otherwise>Collection</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_contributors">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Contributeurs</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Contributors</xsl:when>
      <xsl:when test="starts-with($lang, 'it')">Collaboratori</xsl:when>
      <xsl:otherwise>Contributors</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_date">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Date</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Fecha</xsl:when>
      <xsl:when test="starts-with($lang, 'it')">Giorno</xsl:when>
      <xsl:otherwise>Date</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_place">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Lieu</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Lugar</xsl:when>
      <xsl:when test="starts-with($lang, 'it')">Luogo</xsl:when>
      <xsl:otherwise>Place</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_source">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Source</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Origen</xsl:when>
      <xsl:when test="starts-with($lang, 'it')">Fonte</xsl:when>
      <xsl:otherwise>Source</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_subjects">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Thèmes</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Temas</xsl:when>
      <xsl:when test="starts-with($lang, 'it')">Temi</xsl:when>
      <xsl:otherwise>Subjects</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_keywords">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Mots clés</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Palabras llaves</xsl:when>
      <xsl:when test="starts-with($lang, 'it')">Parola Chiave</xsl:when>
      <xsl:otherwise>Keywords</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_abstract">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Résumé</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Resumen</xsl:when>
      <xsl:when test="starts-with($lang, 'it')">Riepilogo</xsl:when>
      <xsl:otherwise>Abstract</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_annotation">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Annotation</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Anotación</xsl:when>
      <xsl:when test="starts-with($lang, 'it')">Annotazione</xsl:when>
      <xsl:otherwise>Annotation</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_cover">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Couverture</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Cobertura</xsl:when>
      <xsl:when test="starts-with($lang, 'it')">Copertina</xsl:when>
      <xsl:otherwise>Cover</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_toc">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Sommaire</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Tabla de contenidos</xsl:when>
      <xsl:when test="starts-with($lang, 'it')">Sommario</xsl:when>
      <xsl:otherwise>Table of Contents</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_title_page">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Page de titre</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Página de título</xsl:when>
      <xsl:when test="starts-with($lang, 'it')">Pagina de titolo</xsl:when>
      <xsl:otherwise>Title Page</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_note">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Note</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Nota</xsl:when>
      <xsl:when test="starts-with($lang, 'it')">Note</xsl:when>
      <xsl:otherwise>Note</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_back">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Retour au texte</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Volver al texto</xsl:when>
      <xsl:when test="starts-with($lang, 'it')">Torna al testo</xsl:when>
      <xsl:otherwise>Back to the text</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_bibliography">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Bibliographie</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Bibliografía</xsl:when>
      <xsl:when test="starts-with($lang, 'it')">Bibliografia</xsl:when>
      <xsl:otherwise>Bibliography</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_index">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Index</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Índice</xsl:when>
      <xsl:when test="starts-with($lang, 'it')">Indice</xsl:when>
      <xsl:otherwise>Index</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_glossary">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Glossaire</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Glosario</xsl:when>
      <xsl:when test="starts-with($lang, 'it')">Glossario</xsl:when>
      <xsl:otherwise>Glossary</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_definition">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Définition</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Definición</xsl:when>
      <xsl:when test="starts-with($lang, 'it')">Definizione</xsl:when>
      <xsl:otherwise>Definition</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_example">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Exemple</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Ejemplo</xsl:when>
      <xsl:when test="starts-with($lang, 'it')">Esempio</xsl:when>
      <xsl:otherwise>Example</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_synonym">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Synonyme</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Sinónimo</xsl:when>
      <xsl:when test="starts-with($lang, 'it')">Sinonimo</xsl:when>
      <xsl:otherwise>Synonym</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_antonym">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Antonyme</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Antónimo</xsl:when>
      <xsl:when test="starts-with($lang, 'it')">Antonimo</xsl:when>
      <xsl:otherwise>Antonym</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_translation">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Traduction</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Traducción</xsl:when>
      <xsl:when test="starts-with($lang, 'it')">Traduzione</xsl:when>
      <xsl:otherwise>Translation</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_seealso">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Voir aussi</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Ver también</xsl:when>
      <xsl:when test="starts-with($lang, 'it')">Vedere anche</xsl:when>
      <xsl:otherwise>See also</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_noaudio">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Votre navigateur ne supporte pas la balise audio.</xsl:when>
      <xsl:when test="starts-with($lang, 'it')">L'applicazione non supporta il formato audio.</xsl:when>
      <xsl:otherwise>Your browser does not support the audio tag.</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_novideo">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Votre navigateur ne supporte pas la vidéo HTML5.</xsl:when>
      <xsl:when test="starts-with($lang, 'it')">L'applicazione non supporta il formato video HTML5.</xsl:when>
      <xsl:otherwise>Your browser does not support HTML5 video.</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_listen">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Écoutez</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Escuche</xsl:when>
      <xsl:when test="starts-with($lang, 'it')">Ascolta</xsl:when>
      <xsl:otherwise>Listen</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_nocanvas">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Balise &lt;canvas&gt; non supportée</xsl:when>
      <xsl:otherwise>&lt;canvas&gt; tag not supported</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
</xsl:stylesheet>
