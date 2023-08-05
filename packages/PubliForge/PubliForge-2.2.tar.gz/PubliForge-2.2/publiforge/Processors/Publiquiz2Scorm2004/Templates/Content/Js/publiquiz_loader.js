
/*jshint globalstrict: true*/
/*global jQuery: true */
/*global doInitialize: true */
/*global doTerminate: true */
/*global doSetValue: true */
/*global doGetValue: true */

"use strict";


(function () {
    var windowLoaded = false;

    jQuery(window).on("load", function () {
        windowLoaded = true;
    });

    jQuery(function ($) {

        // ========================================================================
        //                               SCORM ACTION
        // ========================================================================

        $.publiquiz.action.actionCustom = function($action, name, args) {
            if (name == "scormScore") {
                var score = $.publiquiz.question.computeGlobalScore(
                    $action.questions);
                var threshold = parseFloat(
                    $action.children(".pquizSuccessThreshold").text());
                if (score.total) {
                    doSetValue("cmi.score.min", "0");
                    doSetValue("cmi.score.max", score.total);
                    doSetValue("cmi.score.raw", score.score);
                    doSetValue("cmi.score.scaled", score.score/score.total);
                    if (score.score / score.total >= threshold)
                        doSetValue("cmi.success_status", "passed");
                    else
                        doSetValue("cmi.success_status", "failed");
                }
            }
        };

        // ========================================================================
        //                                  LOADER
        // ========================================================================

        // Publiquiz default options
        var prefix = "pquiz";
        $.publiquiz.defaults.prefix = prefix;

        // Ensure all images are load before draw something in canvas
        if ($.find("canvas").length > 0 && $.find("img").length > 0 && !windowLoaded) {
            $(window).on("load", function () {
                process();
            });
        } else {
            process();
        }

        function process() {
            // Publiquiz question plug-in
            var $questions = $(".publiquiz");
            $questions.publiquiz();

            // Publiquiz action plug-in
            var $action = $(".publiquizAction");
            $action.publiquiz({
                "questions": $questions,
                "scenario": {
                    "validate": [
                        ["hide(Submit)", "validate", "showMessage", "goto(maxRetry, 1, 2)"],
                        ["userColor", "show(Retry)"],
                        ["score", "scormScore", "answerText", "rightAnswer", "fullColor", "show(UserAnswer)"]
                    ],
                    "verify": [
                        ["userColor"]
                    ],
                    "retry": [
                        ["hide(Retry)", "retry", "show(Submit)", "set(validate, 0)"]
                    ],
                    "userAnswer": [
                        ["hide(UserAnswer)", "show(RightAnswer)", "userAnswer", "userColor"]
                    ],
                    "rightAnswer": [
                        ["hide(RightAnswer)", "show(UserAnswer)", "rightAnswer", "fullColor"]
                    ]
                }
            });

            // SCORM initialization
            doInitialize();
            doSetValue("cmi.completion_status", "incomplete");

            // SCORM finalization
            //$(window).bind('beforeunload', function() {
            $(window).unload(function() {
                doSetValue("cmi.completion_status", "completed");
                doSetValue("cmi.exit", "normal");
                doTerminate();
            });
        }

    });
})();
