/**
 * @projectDescription publiquiz_loader.js
 * Javascript quiz loader.
 *
 * @author Tien Haï NGUYEN
 * @version 0.5
 *
 * 0.5 :
 * Add new part in publiquiz "$publiquiz.context", save/load context for a quiz and action
 *    - quiz and action : add 2 new data "context-key" used for validate context and
 *      "context-ttl" for context life duration , none or -1 no context, 0 
 *      for context session and more for context duration.
 *    - save context : save context in localStorage, sessionStorage if possible or
 *      in a cookie.
 *
 * 0.4 :
 * Add quiz validation animation.
 *
 * 0.3 :
 * Add quiz popUp message.
 *
 * 0.2 :
 *  Add publiquizAction, now we have 2 parts for quiz
 *  - questions : includes instruction, engine and button of quiz (help,...)
 *  - actions : manage all actions on quiz validate, retry, show answer...
 *    and scenario for action description.
 *
 * 0.1 :
 *   Initial release.
 */


/*jshint globalstrict: true*/
/*global jQuery: true */
/*global document: true */
/*global window: true */
/*global setInterval: true */
/*global clearInterval: true */


"use strict";


(function () {
    var windowLoaded = false;

    jQuery(window).on("load", function () {
        windowLoaded = true;
    });

    jQuery(function ($) {
        var $questions = $(".publiquiz");
        if ($questions.length === 0)
            return;

        // --------------------------------------------------------------------
        // Buffering
        var $elemBuffering = $("."+$.publiquiz.defaults.mainClass);
        $elemBuffering.addClass($.publiquiz.defaults.prefix+"StateLoading");
        $elemBuffering.append($("<div/>").addClass($.publiquiz.defaults.prefix+"Loading abs"));

        // --------------------------------------------------------------------
        // Ensure all images are load before draw something in canvas
        if (($.find("canvas").length > 0 || $.find("img").length > 0) && !windowLoaded) {
            $(window).on("load", function () {
                process();
            });
        } else {
            process();
        }

        function process() {
            // Publiquiz question plug-in
            $questions.publiquiz();

            // Publiquiz action plug-in
            $(".publiquizAction").publiquiz({
                "questions": $questions,
                "scenario": {
                    "validate": [
                        ["state(Validated)", "stopTimer", "hide(Submit)", "hide(VerifyUserAnswer)", "validate", "goto(endCountdown, -1, 2)", "goto(maxRetry, 1, 2)"],
                        ["showMessage(Encourage)", "userColor", "show(Retry)"],
                        ["showMessage(Congratulate)", "score", "answerText", "rightAnswer", "fullColor", "show(UserAnswer)", "show(Redo)"]
                    ],
                    "verify": [
                        ["userColor"]
                    ],
                    "retry": [
                        ["state(Enabled)", "hide(Retry)", "retry", "show(Submit)", "set(validate, 0)", "resumeTimer"]
                    ],
                    "redo": [
                        ["state(Enabled)",
                         "hide(Redo)", 
                         "hide(RightAnswer)",
                         "hide(UserAnswer)",
                         "hide(Retry)",
                         "hide(VerifyUserAnswer)",
                         "show(Submit)",
                         "redo"]
                    ],
                    "userAnswer": [
                        ["state(UserAnswer)", "hide(UserAnswer)", "show(RightAnswer)", "userAnswer", "userColor"]
                    ],
                    "rightAnswer": [
                        ["state(RightAnswer)", "hide(RightAnswer)", "show(UserAnswer)", "rightAnswer", "fullColor"]
                    ],
                    "onEndCountdown": [
                        ["state(Disabled)", "disable", "set(validate, 0)"]
                    ]
                }
            });

            // End loading 
            var max = 5000;
            var step = 100;
            var count = 0;
            var timer = setInterval(function () {
                if (!$.publiquiz.defaults.isLoadContext && $.publiquiz.defaults.contextLoading === 0
                    || (count * step > max)) {
                    clearInterval(timer);
                    $elemBuffering.removeClass($.publiquiz.defaults.prefix+"StateLoading");
                    $elemBuffering.find("."+$.publiquiz.defaults.prefix+"Loading").remove();
                }
                count += 1;
            }, step);
        }

    });
})();
