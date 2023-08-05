
/*global jQuery: true */

"use strict";

jQuery(document).ready(function($) {
    var $vcsParams = $('#vcsParams');
    
    if ($vcsParams.length) {
        var $vcsEngine = $('#vcs_engine');
        var $publicURL = $('#stgURL');
        
        if ($vcsEngine.val() == 'none' || $vcsEngine.val() == 'local') {
            $vcsParams.hide();
            $publicURL.show();
        } else {
            $vcsParams.show();
            $publicURL.hide();
        }

        $vcsEngine.change(function() {
            if ($vcsEngine.val() == 'none' || $vcsEngine.val() == 'local') {
                $vcsParams.slideUp();
                $publicURL.slideDown();
            } else {
                $vcsParams.slideDown();
                $publicURL.slideUp();
            }
        });
    }; 
});
