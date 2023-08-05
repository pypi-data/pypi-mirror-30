/**
 * @projectDescription publiquiz_flashcard.js
 * Plugin jQuery for quiz flashcard.
 *
 * @author Patrick PIERRE
 * @version 0.1
 */

/*jshint globalstrict: true*/
/*global jQuery: true */
/*global setTimeout: true */


"use strict";


/******************************************************************************
 *
 *                                  Flashcard
 *
 *****************************************************************************/

jQuery(document).ready(function($) {

    $("."+$.publiquiz.defaults.prefix+"Flashcard").each(function() {
        var prefix = $.publiquiz.defaults.prefix;
        var $flashcard = $(this);
        var $side1 = $flashcard.find(".side1");
        var $side2 = $flashcard.find(".side2");
        var $turnOverButton = $flashcard.parent()
            .find("."+prefix+"FlashcardTurnOver ."+prefix+"Button");
        var $quizButtons = $flashcard.parents("div[data-engine]")
            .parent().find("."+prefix+"Buttons");
        $side2.hide();

        $turnOverButton.click(function() {
            if (!$flashcard.hasClass("flipped")) {
                if (!$turnOverButton.data("inProgress")) {
                    $turnOverButton.data("inProgress", true).addClass("disabled");
                    $quizButtons.find("."+prefix+"Submit").show();
                }
                $side1.css("position", "absolute"); $side2.show();
                setTimeout(function() { $flashcard.addClass("flipped"); }, 100);
            } else if (!$turnOverButton.data("inProgress")
                       || $quizButtons.find("."+prefix+"Score").is(":visible")) {
                $flashcard.removeClass("flipped");
                setTimeout(function() {
                    $side1.css("position", "relative"); $side2.hide(); }, 400);
            }
        });

        $quizButtons.find("."+prefix+"Submit").hide().click(function() {
            $turnOverButton.removeClass("disabled"); });

        $quizButtons.find("."+prefix+"Redo")
            .click(function() {
                $turnOverButton.data("inProgress", false).removeClass("disabled");
                $quizButtons.find("."+prefix+"Submit").hide();
                if ($flashcard.hasClass("flipped"))
                    $turnOverButton.click();
            });
    });
});
