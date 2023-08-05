/**
 * @projectDescription Memory Loader
 *
 * @author Tien Haï NGUYEN
 * @version 0.1
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

        var $effect = $(".pquizMemory");
        if ($effect.length === 0)
            return;

        // ------------------------------------------------------------------------
        // Abs
        $("<style>").text(".abs { position: absolute; }").appendTo("head");

        // ------------------------------------------------------------------------
        // Audio player
        if ($.fn.player) {
            $(".pdocAudioPlayer").player();
        }

        // ------------------------------------------------------------------------
        // Start loading
        var $body = $("body");
        $.publianim.addLoading($body, $.memory.defaults.prefix);

        // ------------------------------------------------------------------------
        // Memory
        $effect.memory({hideRightAnswer: true});

        // ------------------------------------------------------------------------
        // Memory action
        var $action = $(".publiquizAction");
        $action.memoryAction($effect, {
            scenario: {
                redo: ["hide(Redo)", "hide(RightAnswer)", "hide(UserAnswer)", "redo", "state(Enabled)"],
                rightAnswer: ["state(RightAnswer)", "hide(RightAnswer)", "show(UserAnswer)", "rightAnswer"],
                userAnswer: ["state(UserAnswer)", "hide(UserAnswer)", "show(RightAnswer)", "userAnswer"],
                onModified: ["show(Redo)"],
                onEndCountdown: ["state(Disabled)", "disable", "show(RightAnswer)", "score"],
                onFinishGame: ["state(Corrected)", "stopTimer", "disable", "hide(UserAnswer)", "show(RightAnswer)", "score", "userAnswer"]}
        });

        // Context
        $effect.memory("loadContext");

        // ------------------------------------------------------------------------
        // End loading
        var max = 5000;
        var step = 100;
        var count = 0;
        var timer = setInterval(function () {
            if ($.memory.defaults.isReady && !$.memory.defaults.isLoading || (count * step > max)) {
                clearInterval(timer);
                $.publianim.removeLoading($body, $.memory.defaults.prefix);
            }
            count += 1;
        }, step);
    });

})();
