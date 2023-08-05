
/*jshint globalstrict: true*/
/*global jQuery: true */
/*global CodeMirror: true */
/*global schema2tags: true */
/*global completeAfter: true */
/*global completeIfAfterLt: true */
/*global completeIfInTag: true */
/*global metaHideEmptyFields: true */
/*global protectAndAutoCheck: true */

"use strict";

var tags = schema2tags(
    jQuery.publidoc.schema, [
        "division", "topic",
        "!--", "header", "section", "bibliography", "footer",
        "!--", "keyword", "subject"
    ]);
var codemirrors = [];

jQuery(document).ready(function($) {
    metaHideEmptyFields($(".pdocMeta"));
    protectAndAutoCheck($("#content").children("[data-autocheck]"));
    $(".editor").each(function() {
        if (this.tagName == "TEXTAREA") {
            codemirrors.push(CodeMirror.fromTextArea(this, {
                mode: "xml",
                lineNumbers: true,
                extraKeys: {
                    "'<'": completeAfter,
                    "'/'": completeIfAfterLt,
                    "' '": completeIfInTag,
                    "'='": completeIfInTag,
                    "Alt-Enter": function(cm) {
                        CodeMirror.showHint(
                            cm, CodeMirror.xmlHint, {schemaInfo: tags});
                    }
                }
            }));
        }
    });
});
