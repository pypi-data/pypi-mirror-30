
/*global jQuery: true */
/*global CodeMirror: true */

var codemirrors = [];

jQuery(document).ready(function($) {
    $(".editor").each(function() {
        if (this.tagName == "TEXTAREA") {
            codemirrors.push(CodeMirror.fromTextArea(this, {
                lineNumbers: true
            }));
        }
    });
});
