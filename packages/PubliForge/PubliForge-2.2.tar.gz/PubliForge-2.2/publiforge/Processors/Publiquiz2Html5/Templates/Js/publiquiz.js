/**
 * @projectDescription publiquiz.js
 * Javascript for quiz on library jquery, define namespace publiquiz,
 * publiquiz.action and publiquiz.question
 *
 * @author Tien Haï NGUYEN
 * @version 0.6
 *
 * 0.6 :
 * - Add countdown and chrono
 *     - New action in scenario : stopTimer and resumeTimer
 *     - New event in scenario : onEndCountdown
 *     - New condition for goto : endCountdown
 * - Add state of quiz
 *   - Enabled, Validated, Corrected and Disabled
 *
 * 0.5 :
 * - Add new part in publiquiz "$publiquiz.context", save/load context for a quiz and action
 *     - quiz and action : add 2 new data "context-key" used for validate context and
 *       "context-ttl" for context life duration , none or -1 no context, 0
 *       for context session and more for context duration.
 *     - save context : save context in localStorage, sessionStorage if possible or
 *       in a cookie.
 *
 * 0.4 :
 * - Add quiz validation animation.
 *
 * 0.3 :
 * - Add quiz popUp message.
 *
 * 0.2 :
 * - Add publiquizAction, now we have 2 parts for quiz
 *     - questions : includes instruction, engine and button of quiz (help,...)
 *     - actions : manage all actions on quiz validate, retry, show answer...
 *       and scenario for action description.
 *
 * 0.1 :
 * - Initial release.
 */


/*jshint globalstrict: true*/
/*global jQuery: true */
/*global setTimeout: true */
/*global clearTimeout: true */
/*global setInterval: true */
/*global clearInterval: true */
/*global localStorage: true */
/*global sessionStorage: true */


"use strict";

(function ($) {


/*****************************************************************************
 *****************************************************************************
 *
 *                  Define namespace publiquiz if not exist
 *
 *****************************************************************************
 ****************************************************************************/


if (!$.publiquiz)
    $.publiquiz = {};


/*****************************************************************************
 *****************************************************************************
 *
 *                          Define publiquiz.defaults
 *
 *****************************************************************************
 ****************************************************************************/


$.publiquiz.defaults =  {
    mainClass: "pquizQuiz", // define class above all quiz
    prefix: "pquiz", // define prefix of publiquiz element class
    verifyDuration: 0, // set timer for verify quiz, 0 for no timer
    wrongAnswers: "color", // wrongAnswers can be set to "color", "clear" or "correct"
    multipageAnimation: true, // animate composite page transition
    centerRelativeTo: ".publiquiz", // "screen" for center to screen or selector
    isLoadContext: false, // define if we are in load context mode
    contextLoading: 0, // define how many context loading
    scale: {x: 1, y: 1}, // define page scale value
    popupContentClose: true // define where click for close dialog
};


/*****************************************************************************
 *****************************************************************************
 *
 *                          Define publiquiz.action
 *
 *****************************************************************************
 ****************************************************************************/


$.publiquiz.action = {

    currentTimerId: null,       // Identifiant du timer en cours
    currentTimer: null,         // Function timer en cours
    currentCountdownValue: 0,   // Decompte restant en cours
    currentChronoValue: 0,      // Valeur du chrono en cours

    /**
     * Method call when click on validate button.
     *
     * @param {Object} $action, jquery Object action.
     */
    validate: function($action) {
        var pqAction = this;

        // On arrete les timers
        if (pqAction.currentTimerId !== null) {
            clearInterval(pqAction.currentTimerId);
            pqAction.currentTimerId = null;
        }
        var prefix = $.publiquiz.defaults.prefix;
        var $countdown = $action.find("."+prefix+"Countdown");
        if ($countdown.length > 0) {
            $countdown.removeClass(prefix+"EndCountdown");
        }

        var scenario = $action.scenario.validate;
        var acts = scenario[$action.idxValidate];
        if (!acts)
            return;

        // If composite store current subquiz display
        $action.questions.each(function() {
            var $quiz = $(this);
            if ($quiz.data("engine") === "composite" && $quiz.data("engineDisplay")) {
                $.publiquiz.context.onQuizModified($.publiquiz.question, $quiz);
            }
        });

        pqAction.doActions($action, "validate", acts);
    },

    /**
     * Method call when click on verify button.
     *
     * @param {Object} $action, jquery Object action.
     */
    verify: function($action) {
        var pqAction = this;
        var scenario = $action.scenario.verify;
        var acts = scenario[$action.idxVerify];
        if (!acts)
            return;

        pqAction.doActions($action, "verify", acts);
    },

    /**
     * Method call when click on retry button.
     *
     * @param {Object} $action, jquery Object action.
     */
    retry: function($action) {
        var pqAction = this;
        var scenario = $action.scenario.retry;
        var acts = scenario[$action.idxRetry];
        if (!acts)
            return;

        pqAction.doActions($action, "retry", acts);
    },

    /**
     * Method call when click on redo button.
     *
     * @param {Object} $action, jquery Object action.
     */
    redo: function($action) {
        var pqAction = this;
        var scenario = $action.scenario.redo;
        var acts = scenario[$action.idxRetry];
        if (!acts)
            return;

        pqAction.doActions($action, "redo", acts);
    },

    /**
     * Method call when click on show user answer button.
     *
     * @param {Object} $action, jquery Object action.
     */
    userAnswer: function($action) {
        var pqAction = this;
        var scenario = $action.scenario.userAnswer;
        var acts = scenario[$action.idxUserAnswer];
        if (!acts)
            return;

        pqAction.doActions($action, "userAnswer", acts);
    },

    /**
     * Method call when click on show right answer button.
     *
     * @param {Object} $action, jquery Object action.
     */
    rightAnswer: function($action) {
        var pqAction = this;
        var scenario = $action.scenario.rightAnswer;
        var acts = scenario[$action.idxRightAnswer];
        if (!acts)
            return;

        pqAction.doActions($action, "rightAnswer", acts);
    },

    /**
     * Method call when quiz is modified.
     *
     * @param {Object} $action, jquery Object action.
     */
    onModified: function($action) {
        if (!$action || !$action.scenario)
            return;
        var pqAction = this;
        var scenario = $action.scenario.onModified;
        if (!scenario)
            return;
        var acts = scenario[0];
        if (!acts)
            return;

        pqAction.doActions($action, "onModified", acts);
    },

    /**
     * Function for timer countdown.
     *
     * @param {Object} $action, jquery Object action.
     */
    countdownTimer: function($action) {
        var pqAction = $.publiquiz.action;
        var prefix = $.publiquiz.defaults.prefix;
        var $elem = $action.find("."+prefix+"Countdown");
        pqAction.currentCountdownValue -= 1;

        // Counter ended
        if (pqAction.currentCountdownValue < 0) {
            clearInterval(pqAction.currentTimerId);
            pqAction.currentTimerId = null;

            if ($elem.length > 0) {
                $elem.addClass(prefix+"EndCountdown");
            }

            if ($action.scenario.onEndCountdown !== undefined) {
                var scenario = $action.scenario.onEndCountdown;
                var acts = scenario[0];
                if (acts !== undefined)
                    pqAction.doActions($action, "onEndCountdown", acts);
                return;
            }
        }

        // Display countdown
        if ($elem.length > 0) {
            $elem.data("current-value", pqAction.currentCountdownValue);
            $elem.text(pqAction.formatTimer(pqAction.currentCountdownValue));
            $.publiquiz.context.onActionModified($action, "countdown");
        }
    },

    /**
     * Function for timer chrono.
     *
     * @param {Object} $action, jquery Object action.
     */
    chronoTimer: function($action) {
        var pqAction = $.publiquiz.action;
        pqAction.currentChronoValue += 1;

        var prefix = $.publiquiz.defaults.prefix;
        var $elem = $action.find("."+prefix+"Chrono");
        if ($elem.length > 0) {
            $elem.data("current-value", pqAction.currentChronoValue);
            $elem.text(pqAction.formatTimer(pqAction.currentChronoValue));
            $.publiquiz.context.onActionModified($action, "chrono");
        }
    },

    /**
     * Start countdown
     *
     * @param {Object} $action - jquery Object action.
     */
    startCountdown: function($action) {
        var pqAction = this;
        if (pqAction.currentTimerId !== null)
            return;
        pqAction.currentTimer = pqAction.countdownTimer;
        pqAction.currentTimerId = setInterval(pqAction.currentTimer, 1000, $action);
    },

    /**
     * Start chrono
     *
     * @param {Object} $action - jquery Object action.
     */
    startChrono: function($action) {
        var pqAction = this;
        if (pqAction.currentTimerId !== null)
            return;
        pqAction.currentTimer = pqAction.chronoTimer;
        pqAction.currentTimerId = setInterval(pqAction.currentTimer, 1000, $action);
    },

    /**
     * Init timer.
     *
     * @param {jQuery} $memory - Memory engine.
     * @param {boolean} reset - RAZ timer variable.
     */
    initTimer: function($action, reset) {
        var pqAction = this;
        var prefix = $.publiquiz.defaults.prefix;
        pqAction.actionStopTimer($action);
        pqAction.currentTimer = null;
        pqAction.currentTimerId = null;

        if (reset) {
            pqAction.currentChronoValue = 0;
            pqAction.currentCountdownValue = 0;
            if ($action.data("countdown") !== undefined)
                pqAction.currentCountdownValue = parseInt($action.data("countdown"), 10);
        }

        var $countdown = $action.find("."+prefix+"Countdown");
        if ($countdown.length > 0) {
            $countdown.removeClass(prefix+"EndCountdown");
            $countdown.text(pqAction.formatTimer(pqAction.currentCountdownValue));
        }

        var $chrono = $action.find("."+prefix+"Chrono");
        if ($chrono.length > 0) {
            $chrono.text(pqAction.formatTimer(pqAction.currentChronoValue));
        }
    },

    /**
     * Helper, format timer.
     *
     * @param {Int} value - time in second.
     * @return {String} time formated.
     */
    formatTimer: function(value) {
        if (value < 0)
            value = 0;
        var minutes = Math.floor(value / 60);
        var seconds = value % 60;
        if (seconds <= 9)
            seconds = "0" + seconds;
        return minutes+":"+seconds;
    },


    /* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     *                          Action library function
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

    /**
     * Hide element by this id.
     *
     * @param {Object} $action, jquery Object action.
     * @param {String} funcName, name of function to call.
     * @param {Array} acts, array of actions.
     */
    doActions: function($action, funcName, acts) {
        var pqAction = this;
        $(acts).each( function() {
            var actName = this.match(new RegExp("^([^(]+)"));
            if (!actName)
                return true;
            actName = actName[0];
            var actArgs = this.replace(actName, "")
                                .replace("(", "")
                                .replace(/ /g, "");
            var pos = actArgs.lastIndexOf(")");
            actArgs = actArgs.substring(0, pos) + actArgs.substring(pos + 1);
            if (actArgs) {
                var idx = actArgs.lastIndexOf(")");
                if (idx > 0) {
                    var tmp = [];
                    tmp.push(actArgs.substring(0, idx + 1).trim());
                    $.each(actArgs.substring(idx + 1).split(","), function() {
                        if (this.length > 0 && this !== "")
                            tmp.push(this);
                    });
                    actArgs = tmp;
                }
                else {
                    actArgs = actArgs.split(",");
                }
            }
            else {
                actArgs = [];
            }

            if (actName === "validate") {
                pqAction.actionValidate($action);
            } else if (actName === "state") {
                pqAction.actionState($action, actArgs[0]);
            } else if (actName === "disable") {
                pqAction.actionDisable($action);
            } else if (actName === "retry") {
                pqAction.actionRetry($action);
            } else if (actName === "redo") {
                pqAction.actionRedo($action);
            } else if (actName === "showMessage") {
                pqAction.actionShowMessage($action, actArgs[0]);
            } else if (actName === "answerText") {
                pqAction.actionAnswerText($action);
            } else if (actName === "rightAnswer") {
                pqAction.actionRightAnswer($action);
            } else if (actName === "userAnswer") {
                pqAction.actionUserAnswer($action);
            } else if (actName === "score") {
                pqAction.actionScore($action);
            } else if (actName === "userColor") {
                pqAction.actionUserColor($action);
            } else if (actName === "rightColor") {
                pqAction.actionRightColor($action);
            } else if (actName === "fullColor") {
                pqAction.actionFullColor($action);
            } else if (actName === "resumeTimer") {
                pqAction.actionResumeTimer($action);
            } else if (actName === "stopTimer") {
                pqAction.actionStopTimer($action);
            } else if (actName === "hide") {
                pqAction.actionHide($action, actArgs);
            } else if (actName === "show") {
                pqAction.actionShow($action, actArgs);
            } else if (actName === "goto") {
                return pqAction.actionGoTo($action, funcName, actArgs);
            } else if (actName === "set") {
                pqAction.actionSet($action, actArgs);
            } else if (actName === "setif") {
                pqAction.actionSetIf($action, actArgs);
            } else {
                pqAction.actionCustom($action, actName, actArgs);
            }

            return true;
        });
    },

    /**
     * Action custom, use for manage customs action.
     *
     * @param {Object} $action, jquery Object action.
     * @param {String} actName, action name.
     * @param {Array} actArgs, action args.
     */
    actionCustom: function($action, actName, actArgs) {
        console.log("This action is not defined, used method 'actionCustom' for manage it: '" + actName + "'");
    },

    /**
     * Hide element by this id.
     *
     * @param {Object} $action, jquery Object action.
     * @param {Array} args, list of argument.
     */
    actionHide: function($action, args) {
        if (!args)
            return;

        var prefix = $.publiquiz.defaults.prefix;
        $.each(args, function() {
            var elemName = this;
            $action.find("."+prefix+elemName).addClass("hidden");
        });
    },

    /**
     * Show element by this id.
     *
     * @param {Object} $action, jquery Object action.
     * @param {Array} args, list of argument.
     */
    actionShow: function($action, args) {
        var prefix = $.publiquiz.defaults.prefix;
        $.each(args, function() {
            var elemName = this;
            $action.find("."+prefix+elemName).removeClass("hidden");
        });
    },

    /**
     * Action validate
     *
     * @param {Object} $action, jquery Object action.
     */
    actionValidate: function($action) {
        var $questions = $action.questions;

        // Disable event on freeblank
        $questions.each(function() {
            var $quiz = $(this);
            var prefix = $quiz.data("prefix");
            var freeblanks = $quiz.find("."+prefix+"Choice").filter(":not([id])");
            freeblanks.off("input");
            freeblanks.prop("disabled", true);
        });

        // Call publiquiz plugin function
        $questions.publiquiz("disable");
        $questions.publiquiz("insertUserAnswers");
    },

    /**
     * Action state
     *
     * @param {Object} $action, jquery Object action.
     * @param {String} state, current State.
     */
    actionState: function($action, state) {
        var $questions = $action.questions;
        var prefix = $.publiquiz.defaults.prefix;

        $questions.each(function() {
            var $quiz = $(this);
            var $engine = $quiz.find("."+prefix+"Engine");
            $engine.removeClass(
                    prefix+"StateValidated " +
                    prefix+"StateDisabled " +
                    prefix+"StateRightAnswer " +
                    prefix+"StateUserAnswer");
            if (state !== "Enabled") {
                $engine.addClass(prefix+"State"+state);
            }
        });
    },

    /**
     * Action disable
     *
     * @param {Object} $action, jquery Object action.
     */
    actionDisable: function($action) {
        var $questions = $action.questions;

        // Call publiquiz plugin function
        $questions.publiquiz("disable");
    },

    /**
     * Action retry
     *
     * @param {Object} $action, jquery Object action.
     */
    actionRetry: function($action) {
        $action.nbRetryQuiz -= 1 ;

        // Hide message
        var prefix = $.publiquiz.defaults.prefix;
        $action.find("."+prefix+"Message").addClass("hidden");

        // Call publiquiz plugin function
        var $questions = $action.questions;
        $questions.publiquiz("retry");
        $questions.publiquiz("enable");
    },

    /**
     * Action redo, permet de reload le quiz.
     *
     * @param {Object} $action, jquery Object action.
     */
    actionRedo: function($action) {
        var prefix = $.publiquiz.defaults.prefix;
        var $questions = $action.questions;

        // Internal function for hide slot
        function hideSlot($container, id) {
            var $instructionSlot = $container.find("#"+id+"_instruction-slot").filter(":not(."+prefix+"InstructionPopUp)");
            if ($instructionSlot.length > 0 && $instructionSlot.css("display") !== "none")
                $instructionSlot.slideToggle("slow");
            var $answerSlot = $container.find("#"+id+"_answer-slot").filter(":not(."+prefix+"AnswerPopUp)");
            if ($answerSlot.length > 0 && $answerSlot.css("display") !== "none")
                $answerSlot.slideToggle("slow");
            var $helpSlot = $container.find("#"+id+"_help-slot").filter(":not(."+prefix+"HelpPopUp)");
            if ($helpSlot.length > 0 && $helpSlot.css("display") !== "none")
                $helpSlot.slideToggle("slow");
            var $explanationSlot = $container.find("#"+id+"_explanation-slot").filter(":not(."+prefix+"ExplanationPopUp)");
            if ($explanationSlot.length > 0 && $explanationSlot.css("display") !== "none")
                $explanationSlot.slideToggle("slow");
            var $strategySlot = $container.find("#"+id+"_strategy-slot").filter(":not(."+prefix+"StrategyPopUp)");
            if ($strategySlot.length > 0 && $strategySlot.css("display") !== "none")
                $strategySlot.slideToggle("slow");
            var $scriptSlot = $container.find("#"+id+"_script-slot").filter(":not(."+prefix+"ScriptPopUp)");
            if ($scriptSlot.length > 0 && $scriptSlot.css("display") !== "none")
                $scriptSlot.slideToggle("slow");
        }

        // On arrete les timers
        var pqAction = this;
        pqAction.initTimer($action, true);

        // On vide les caches
        $.publiquiz.context.clearContext($action);

        // On replace l'html d'origine
        $questions.each(function() {
            var $quiz = $(this);
            var quizId = $quiz.data("quiz-id");
            var engine = $quiz.data("engine");

            // On reset les freeblanks
            $quiz.find("."+prefix+"Choice").filter(":not([id])").each(function() {
                $(this).val("");
            });

            // Reset de l'ancien score
            $quiz.removeData("quiz-result");

            // On se remet dans l'etat inital
            if (engine === "composite") {

                // On cache toutes les info "slot"
                $quiz.find("."+prefix+"Element").each(function() {
                    var $element = $(this);
                    var elemId = $element.data("quiz-id");

                    // Disable button events
                    $.publiquiz.question.disableSlotButtons($element);

                    // Hide
                    hideSlot($element, elemId);

                    // Show subQuiz
                    $element.show();
                });

                var options = $quiz.data("engine-options") || "";
                if (options.search("multipage") > -1)
                    $action.addClass("hidden");
                $quiz.find("."+prefix+"Element").data("action", $action);
            }

            // Disable event on popups
            $.publiquiz.question.disablePopupEvents($quiz);

            // Redo quiz
            $.publiquiz.question.redo[engine]($quiz);

            // On cache toute les dialogues du issue du quiz
            $quiz.find("."+prefix+"InstructionsPopUp,"+
                    "."+prefix+"AnswerPopUp,"+
                    "."+prefix+"HelpPopUp,"+
                    "."+prefix+"ExplanationPopUp,"+
                    "."+prefix+"StrategyPopUp,"+
                    "."+prefix+"ScriptPopUp").addClass("hidden");
            $quiz.find(".fadeBackground").removeClass("fadeBackground");

            // Disable button events
            $.publiquiz.question.disableSlotButtons($quiz);

            // On cache toutes les info "slot"
            hideSlot($quiz, quizId);

            // Set event on popups
            $.publiquiz.question.enablePopupEvents($quiz);

            // Set button events
            if (engine === "composite") {
                $quiz.find("."+prefix+"Element").each( function() {
                    var $element = $(this);
                    $.publiquiz.question.enableSlotButtons($element);
                });
            }
            $.publiquiz.question.enableSlotButtons($quiz);

            // On retire le blocage par audio
            $quiz.find(".pquizPopUp.audioBlock").remove();
        });

        // On arrete tous les audios
        $questions.find("audio").each(function() {
            var $aud = $(this).get(0);
            $aud.pause();
            $aud.currentTime = 0;
        });
        if ($.fn.player) {
            $(".pdocAudioPlayer").player();
            $("."+prefix+"AudioPlayer").player();
        }

        // On efface le score
        var $gScoreElem = $action.find("."+prefix+"GlobalScore");
        $gScoreElem.addClass("hidden").text("");

        // On cache les dialogues issue des actions
        $action.find("."+prefix+"Message").addClass("hidden");

        // On remet les variables de l'object action
        var nbRetryQuiz = -1;
        var $nbRetryQuizElem = $action.find("."+prefix+"NbRetry");
        if ($nbRetryQuizElem.length > 0)
            nbRetryQuiz = parseInt($nbRetryQuizElem.text(), 10);
        $action.nbRetryQuiz = nbRetryQuiz;
        $action.idxValidate = 0;
        $action.idxVerify = 0;
        $action.idxRetry = 0;
        $action.idxUserAnswer = 0;
        $action.idxRightAnswer = 0;

        // On active les quiz
        $questions.publiquiz("configure");
        $questions.publiquiz("enable");
        $questions.each(function () {
            $.publiquiz.question.setAudioBlockInteraction($(this));
        });

        // Set event on freeblank
        $questions.each(function() {
            var $quiz = $(this);
            var prefix = $quiz.data("prefix");
            var freeblanks = $quiz.find("."+prefix+"Choice").filter(":not([id])");
            freeblanks.off("input");
            freeblanks.on("input", function() {
                $.publiquiz.context.onQuizModified($.publiquiz.question, $quiz);
            });
            freeblanks.prop("disabled", false);
        });

        // Animation
        if (!$.publianim) {
            return;
        }
        $.each($.publianim.animRegister, function() {
            this.clear();
        });
    },

    /**
     * Action show message, display message by score.
     *
     * @param {Object} $action - jquery Object action.
     * @param {String} mode - mode of message "Congratulate" or "Encourage".
     */
    actionShowMessage: function($action, mode) {
        var prefix = $.publiquiz.defaults.prefix;

        // Get score
        var res = $.publiquiz.question.computeGlobalScore($action.questions);
        var percent = (res.score*100)/res.total;

        // Get the good message
        $action.find("."+prefix+mode+"Message").each( function() {
            var $messages = $(this);
            var range = $messages.data("score-range").split("-");
            if (percent >= range[0] && percent <= range[1]) {
                var rnd = 0;
                var $message = $messages.find("."+prefix+"Message");
                if ($message.length > 1)
                    rnd = Math.floor(Math.random() * $message.length);
                var $msg = $($message[rnd]);

                $('body').queue(function(next) {
                    // Display msg
                    $action.find("."+prefix+mode+"Messages").addClass("fadeBackground");
                    $msg.removeClass("hidden");
                    $msg.setOnCenterScreen();
                    $(window).on("resize", function() {
                        $msg.setOnCenterScreen();
                    });

                    // Audio
                    var $media = $msg.find("."+prefix+"Media");
                    if ($media.length > 0) {
                        var $audio = $msg.find("."+prefix+"Audio,.pdocAudio");
                        if ($audio.length > 0)
                            $audio[0].play();
                    }
                    next();
                });
                return false;
            }
            return true;
        });
    },

    /**
     * Action answer text, display fieldset "answerText".
     *
     * @param {Object} $action, jquery Object action.
     */
    actionAnswerText: function($action) {
        $action.questions.publiquiz("textAnswer");
    },

    /**
     * Action right answer, display right answer of quiz.
     *
     * @param {Object} $action, jquery Object action.
     */
    actionRightAnswer: function($action) {
        $action.questions.publiquiz("quizAnswer", "_correct");
    },

    /**
     * Action user answer, display user answer of quiz.
     *
     * @param {Object} $action, jquery Object action.
     */
    actionUserAnswer: function($action) {
        $action.questions.publiquiz("quizAnswer", "_user");
    },

    /**
     * Action score
     *
     * @param {Object} $action, jquery Object action.
     */
    actionScore: function($action) {
        $.publiquiz.question.displayGlobalScore($action);
    },

    /**
     * Action user color, verify user answer set color for right and false answer.
     *
     * @param {Object} $action, jquery Object action.
     */
    actionUserColor: function($action) {
        $action.questions.publiquiz("verifyUserAnswer");
    },

    /**
     * Action full color, color only right answer.
     *
     * @param {Object} $action, jquery Object action.
     */
    actionRightColor: function($action) {
        $action.questions.publiquiz("verifyRightAnswer");
    },

    /**
     * Action full color, color right and false answer for quiz.
     *
     * @param {Object} $action, jquery Object action.
     */
    actionFullColor: function($action) {
        $action.questions.publiquiz("verifyFullAnswer");
    },

    /**
     * Action resume timer, continue current timer.
     *
     * @param {Object} $action, jquery Object action.
     */
    actionResumeTimer: function($action) {
        var pqAction = this;
        if (pqAction.currentTimer === null)
            return;
        pqAction.actionStopTimer($action);
        pqAction.currentTimerId = setInterval(pqAction.currentTimer, 1000, $action);
    },

    /**
     * Action stop timer.
     *
     * @param {Object} $action, jquery Object action.
     */
    actionStopTimer: function($action) {
        var pqAction = this;
        if (pqAction.currentTimerId === null)
            return;
        clearInterval(pqAction.currentTimerId);
        pqAction.currentTimerId = null;
    },

    /**
     * Go to specific position of scenario.
     *
     * @param {Object} $action, jquery Object action.
     * @param {String} func, name of function to call.
     * @param {Array} args.
     * @return bool
     */
    actionGoTo: function($action, funcName, args) {
        if (args.length != 3)
            return false;

        var pqAction = this;
        var condition = args[0];
        var callAction = false;
        if (condition === "maxRetry") {
            if (!pqAction.conditionMaxRetry($action, funcName, args))
                return true;
            callAction = true;
        }
        else if (condition.match("^scoreEq")) {
            var res = $.publiquiz.question.computeGlobalScore($action.questions);
            var percent = (res.score*100)/res.total;
            if (!pqAction.conditionScoreEq($action, funcName, args, percent))
                return true;
            callAction = true;
        }
        else if (condition === "endCountdown") {
            if (!pqAction.conditionEndCountdown($action, funcName, args))
                return true;
            callAction = true;
        }
        else if (condition.match("^engine")) {
            if (!pqAction.conditionEngine($action, funcName, args))
                return true;
            callAction = true;
        }

        if (callAction) {
            if (funcName === "validate") {
                pqAction.validate($action);
                return false;
            }
        }

        return true;
    },

    /**
     * Action set, set variable to specific index.
     *
     * @param {Object} $action, jquery Object action.
     * @param {Array} args.
     */
    actionSet: function($action, args) {
        if (args.length != 2)
            return;
        var funcName = args[0];
        var idx = args[1];
        if (funcName === "" || idx === "")
            return;

        if (funcName === "validate")
            $action.idxValidate = parseInt(idx, 10);
    },

    /**
     * Action Set if, set variable to specific index with condition.
     *
     * @param {Object} $action, jquery Object action.
     * @param {Array} args.
     */
    actionSetIf: function($action, args) {
        if (args.length != 4)
            return;

        var pqAction = this;
        var condition = args[0];
        var funcName = args[1];
        var nok = args[2];
        var ok = args[3];

        if (condition === "maxRetry")
            pqAction.conditionMaxRetry($action, funcName, [condition, nok, ok]);
    },

    /**
     * Test condition type of engine.
     *
     * @param {Object} $action, jquery Object action.
     * @param {String} func, name of function to call.
     * @param {Array} args.
     * @return {bool} true: call funcName, false: do nothing
     */
    conditionEngine: function($action, funcName, args) {
        var condition = args[0];
        var nok = args[1];
        var ok = args[2];
        if (ok === "" || nok === "")
            return false;

        var idx = -1;
        if ($action.questions.filter("[data-engine='composite']").length > 0 || $action.questions.length > 1) {
            idx = parseInt(nok, 10);
        }
        else {
            var $quiz = $($action.questions.get(0));
            var engines = condition.replace("engine(", "")
                                   .replace(")", "")
                                   .split(",");
            if ($.inArray($quiz.data("engine"), engines) < 0)
                idx = parseInt(nok, 10);
            else
                idx = parseInt(ok, 10);
        }

        if (funcName === "validate" && idx >= 0) {
            $action.idxValidate = idx;
            return true;
        }

        return false;
    },

    /**
     * Test condition end countdown.
     *
     * @param {Object} $action, jquery Object action.
     * @param {String} func, name of function to call.
     * @param {Array} args.
     * @return {bool} true: call funcName, false: do nothing
     */
    conditionEndCountdown: function($action, funcName, args) {
        var nok = args[1];
        var ok = args[2];
        if (ok === "" || nok === "")
            return false;

        if ( $action.data("countdown") === undefined ||
                $.publiquiz.action.currentCountdownValue > 0)
            return false;

        var idx = parseInt(ok, 10);
        if (funcName === "validate" && idx >= 0) {
            $action.idxValidate = idx;
            return true;
        }

        return false;
    },

    /**
     * Test condition max retry.
     *
     * @param {Object} $action, jquery Object action.
     * @param {String} func, name of function to call.
     * @param {Array} args.
     * @return {bool} true: call funcName, false: do nothing
     */
    conditionMaxRetry: function($action, funcName, args) {
        var nok = args[1];
        var ok = args[2];
        if (ok === "" || nok === "")
            return false;

        var res = $.publiquiz.question.computeGlobalScore($action.questions);
        var score = res.score;
        var total = res.total;

        var nbRetryQuiz = $action.nbRetryQuiz;
        var idx = -1;
        if (nbRetryQuiz <= 0 || (score == total && total !== 0)) {
            if (ok == "none")
                return false;

            idx = parseInt(ok, 10);
            if (funcName === "validate" && idx >= 0) {
                $action.idxValidate = idx;
                return true;
            }
            return false;
        } else {
            if (nok == "none")
                return false;
            idx = parseInt(nok, 10);
            if (funcName === "validate" && idx >= 0) {
                $action.idxValidate = idx;
                return true;
            }
            return false;
        }
    },

    /**
     * text condition score equiv to specific percent.
     *
     * @param {Object} $action, jquery Object action.
     * @param {String} func, name of function to call.
     * @param {Array} args.
     * @param {Float} quiz score in percent.
     * @return bool
     */
    conditionScoreEq: function($action, funcName, args, percent) {
        var nok = args[1];
        var ok = args[2];
        if (ok === "" || nok === "")
            return false;

        var idx = -1;
        var p = parseInt(args[0].replace("scoreEq", ""), 10);
        if (p == percent) {
            if (ok == "none")
                return false;
            idx = parseInt(ok, 10);
            if (funcName === "validate" && idx >= 0) {
                $action.idxValidate = idx;
                return true;
            }
            return false;
        } else {
            if (nok == "none")
                return false;
            idx = parseInt(nok, 10);
            if (funcName === "validate" && idx >= 0) {
                $action.idxValidate = idx;
                return true;
            }
            return false;
        }
    }

};


/*****************************************************************************
 *****************************************************************************
 *
 *                          Define publiquiz.question
 *
 *****************************************************************************
 ****************************************************************************/


$.publiquiz.question = {

    /**
     * Define variables for register function.
     */
    enable: {},
    disable: {},
    configure: {},
    redo: {},
    help: {},
    retry: {},
    textAnswer: {},
    insertUserAnswers: {},
    quizAnswer: {},
    verifyUserAnswer: {},
    verifyRightAnswer: {},
    verifyFullAnswer: {},
    computeScore: {},
    quizScore: {},
    modified: {},
    loadContext: {},
    scoreFunc: {},

    // Référence au tableau contenant les timer pour la fonction "verify"
    timers: [],

    /**
     * Register function score by quiz id.
     *
     * @param {String} quzId, id of quiz.
     * @param {Object} $quiz, object jquery quiz.
     * @param {OBject} func, functions for compute score.
     */
    registerScoreFunc: function(quzId, $quiz, func) {
        this.scoreFunc[quzId] = {quiz: $quiz, func: func};
    },

    /**
     * Register function.
     *
     * @param {String} engine: type of engine apply function.
     * @param {Dictionnary} functions: function we want register.
     */
    register: function(engine, functions) {
        var pqQuestion = this;
        $.each(functions, function(key, func) {
            switch (key) {
                case ("enable"):
                case ("disable"):
                case ("configure"):
                case ("redo"):
                case ("help"):
                case ("retry"):
                case ("textAnswer"):
                case ("insertUserAnswers"):
                case ("quizAnswer"):
                case ("verifyUserAnswer"):
                case ("verifyRightAnswer"):
                case ("verifyFullAnswer"):
                case ("computeScore"):
                case ("quizScore"):
                case ("modified"):
                case ("loadContext"):
                    pqQuestion[key][engine] = func;
                    break;
                default:
                    console.log("Namespace publiquiz unknown function: '"+key+"' for engine: '"+engine+"'");
            }
        });
    },

    /* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     *                               Quiz Ui function
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

    /**
     * Enable button of quiz.
     *
     * @param {Object} $quiz : jQuery object quiz.
     */
    enableSlotButtons: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var $action = $quiz.data("action");
        var buttons = $quiz.find("."+prefix+"Button");
        var instruction = $action.find("#"+quzId+"_instructions-link");
        if (instruction.length > 0) {
            $.merge(buttons, instruction);
        }

        $.each(buttons, function() {
            var $btn = $(this);
            var id = $btn.attr("id") || "";
            if (id.substring(0, quzId.length+1) !== quzId+"_")
                return;

            var type = "";
            if (id === quzId+"_help-link") {
                type = "help";
            }
            else if (id === quzId+"_instructions-link") {
                type = "Instructions";
            }
            else if (id === quzId+"_answer-link") {
                type = "Answer";
            }
            else if (id === quzId+"_explanation-link") {
                type = "Explanation";
            }
            else if (id === quzId+"_script-link") {
                type = "Script";
            }
            else if (id === quzId+"_strategy-link") {
                type = "Strategy";
            }

            if (type === "")
                return;

            $btn.on("click", function(ev) {
                ev.preventDefault();
                if (type === "help") {
                    var engine = $quiz.data("engine");
                    $.publiquiz.question.help[engine]($quiz);
                } else {
                    $.publiquiz.question.displayInfo($quiz, type, id.replace("link", "slot"));
                }
            });
        });
    },

    /**
     * Disable button of quiz.
     *
     * @param {Object} $quiz : jQuery object quiz.
     */
    disableSlotButtons: function($quiz) {
        var $action = $quiz.data("action");
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var buttons = $quiz.find("."+prefix+"Button");
        var instruction = $action.find("#"+quzId+"_instructions-link");
        if (instruction.length > 0) {
            $.merge(buttons, instruction);
        }

        $.each(buttons, function() {
            var $btn = $(this);
            var id = $btn.attr("id") || "";
            if (id.substring(0, quzId.length+1) !== quzId+"_")
                return;

            $btn.off("click");
        });
    },

    /**
     * Add drag on item.
     *
     * @param {Object} $quiz : jQuery object quiz.
     * @param {Object} $item : jQuery object item.
     * @param {String} suffix : String suffix class name.
     */
    setDraggableItem: function($quiz, $item, suffix) {
        if ($item.length === 0)
            return;
        var pqQuestion = this;
        var prefix = $quiz.data("prefix");

        var evtStart = "mousedown touchstart";
        var evtMove = "mousemove touchmove";
        var evtEnd = "mouseup touchend";

        if ($item.find("img").length > 0)
            $item.find("img").on("dragstart", function(ev) { ev.preventDefault(); });

        $item.bind(evtStart, function(ev) {
            var $target = $(ev.target);
            if ($target.closest("[data-player='button-play']").length > 0) {
                return;
            }
            $.publiquiz.question.loadAudio();
            ev.preventDefault();
            ev.stopPropagation();
            while (!$target.hasClass(prefix+suffix+"Item"))
                $target = $target.parent();
            pqQuestion.clearVerify();
            $target.addClass("dragging");
            var $ghost = pqQuestion.makeGhost($quiz, $target, ev, suffix);
            var $dropbox = null;
            $(document).bind(evtMove, function(e) {
                if (!$target.hasClass("dragging"))
                    return;
                e.preventDefault();
                $dropbox = pqQuestion.dragItem($quiz, $ghost, suffix, e);
            });
            $(document).bind(evtEnd, function(e) {
                $ghost.remove();
                if (!$target.hasClass("dragging"))
                    return;
                pqQuestion.dropItem($quiz, $dropbox, $target, suffix);
                $dropbox = null;
            });
        });
    },

    /**
     * Helper, drag item and return a valide dropbox object.
     *
     * @param {Object} $quiz : jQuery object quiz.
     * @param {Object} $ghost : jQuery object ghost.
     * @param {String} suffix : String suffix class name.
     * @param {Event} ev : Object event.
     * @return Object dropbox.
     */
    dragItem: function($quiz, $ghost, suffix, ev) {
        var $dropbox = null;
        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");
        $quiz.find("."+prefix+suffix+"Drop").removeClass("dragOver");

        var pos = $.publiquiz.question.eventPosition($ghost, ev);
        $ghost.offset({
            top: pos[1] - $ghost.height(),
            left: pos[0] - $ghost.width()
        });

        var scrollHeight = $(window).scrollTop();
        var pageHeight = $(window).height();
        var elemPosY = pos[1]+$ghost.height();
        if (elemPosY > (pageHeight+scrollHeight)) {
            var offset = elemPosY - (pageHeight+scrollHeight);
            window.scrollTo(0, scrollHeight+offset);
        }

        var scale = $.publiquiz.defaults.scale;
        var pointX = pos[0] * scale.x;
        var pointY = pos[1] * scale.y - scrollHeight;
        $ghost.css("display", "none");
        var $elementOver = $(document.elementFromPoint(pointX, pointY));
        $ghost.css("display", "block");

        if ($elementOver.length === 0)
            return $dropbox;

        // On détermine si l'élément sous le ghost est pas un "Item".
        if ($elementOver[0].tagName.toLowerCase() == "img") {
            var isItem = false;
            var $tmp = $elementOver;
            while($tmp[0] != $("body")[0]) {
                $tmp = $tmp.parent();
                if ($tmp.hasClass(prefix+suffix+"Item")) {
                    isItem = true;
                    break;
                }
            }
            if (isItem)
                $elementOver = $tmp.parent();
        }

        var dropId = $elementOver.attr("id");
        if ($elementOver.attr("class") &&
                $elementOver.attr("class").search(prefix+suffix+"Drop") > -1 &&
                dropId !== undefined) {
            dropId = dropId.substring(0, dropId.length - 4);
            if (dropId == quzId) {
                $dropbox = $elementOver;
                $dropbox.addClass("dragOver");
            }
        } else if ($elementOver.hasClass(prefix+suffix+"Item") &&
                $elementOver.parent().hasClass(prefix+suffix+"Drop")) {
            if (dropId.search("_legend_item") > -1 )
                dropId = dropId.substring(0, dropId.length - 15);
            else
                dropId = dropId.substring(0, dropId.length - 8);
            if (dropId == quzId) {
                $dropbox = $elementOver.parent();
                $dropbox.addClass("dragOver");
            }
        } else {
            $dropbox = null;
        }

        return $dropbox;
    },

    /**
     * Helper, drop item.
     *
     * @param {Object} $quiz : jQuery object quiz.
     * @param {Object} $dropbox : jQuery object dropbox.
     * @param {Object} $item : jQuery object item.
     * @param {String} suffix : String suffix class name.
     */
    dropItem: function($quiz, $dropbox, $item, suffix) {
        var pqQuestion = this;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var engine = $quiz.data("engine");
        var options = $quiz.data("engine-options") || "";
        var evtStart = "mousedown touchstart";
        var evtMove = "mousemove touchmove";
        var evtEnd = "mouseup touchend";
        var $parent = $item.parent();

        var isMultiple = (options.search("multiple") > -1);
        var isCounter = (options.search("counter") > -1);

        $quiz.find("."+prefix+suffix+"Drop").removeClass("dragOver");
        $item.removeClass("dragging");

        // Pas de dropbox on remet l'item que l'on déplace dans sa boite à items
        if ($dropbox === null) {
            $(document).unbind(evtMove);
            $(document).unbind(evtEnd);

            if ($parent.hasClass(prefix+suffix+"Drop")) {
                pqQuestion.cancelItemDrop($quiz, $item, suffix);
                if ($parent.hasClass(prefix+"Dropzone"))
                    $parent.addClass(prefix+"Dropzone-visible");
                else if (engine !== "categories")
                    $parent.addClass(prefix+"Dots");
            }
            return;
        }

        // Si le block a déjà un élément, on enlève celui en place
        if (engine != "categories" || (engine == "categories" && suffix.search("Legend") > -1) ) {
            var $itm = $dropbox.find("."+prefix+suffix+"Item");
            if ($itm.length > 0)
                pqQuestion.cancelItemDrop($quiz, $itm, suffix);

            // Si l'ancien emplacement de l'item était un pquizDrop
            if ($parent.hasClass(prefix+"Dropzone"))
                $parent.addClass(prefix+"Dropzone-visible");
            if ($parent.hasClass(prefix+suffix+"Drop") && !$parent.hasClass(prefix+"Dropzone"))
                $parent.addClass(prefix+"Dots");
        } else {
            // On vérifie que la boite de drop n'as pas encore l'item
            var $find = $dropbox.find("."+prefix+suffix+"Item").filter("[data-item-value=\""+$item.data("item-value")+"\"]");
            if ((isCounter || isMultiple) && $find.length > 0) {
                $dropbox.removeClass("dragOver");
                if ($parent.hasClass(prefix+suffix+"Drop")) {
                    pqQuestion.cancelItemDrop($quiz, $item, suffix);
                } else {
                    $item.unbind(evtStart);
                    $(document).unbind(evtMove);
                    $(document).unbind(evtEnd);
                    pqQuestion.setDraggableItem($quiz, $item, suffix);
                    pqQuestion.setAudioPlayable($quiz, $item);
                }
                return;
            }
        }

        // On déplace l'item dans la dropbox
        $item.unbind(evtStart);
        $(document).unbind(evtMove);
        $(document).unbind(evtEnd);
        var count = 0;
        var countAvailable = false;
        if (engine == "categories") {
            $dropbox.removeClass("dragOver");
            if ($parent.closest("."+prefix+"CategoriesItems")) {
                if (isCounter)
                    countAvailable = $.publiquiz.question.counterItemAvailable($quiz, $item);
                if (isMultiple || countAvailable) {
                    count = $quiz.find("."+prefix+suffix+"Item").length;
                    pqQuestion.setDraggableItem($quiz, $item, suffix);
                    pqQuestion.setAudioPlayable($quiz, $item);
                    $item = $item.clone();
                    $item.attr("id", quzId+"_item"+pqQuestion.formatNumber(count += 100, 3));
                }
            }
            if (suffix.search("Legend") > -1) {
                $dropbox.removeClass(prefix+"Dots");
                $dropbox.text("");
                $item.appendTo($dropbox)
                    .addClass(prefix+"CategoryLegendItemDropped");
            } else {
                $item.appendTo($dropbox)
                    .addClass(prefix+"CategoryItemDropped");
            }
            $dropbox.find("."+prefix+suffix+"Item").removeClass("dragOver");
            pqQuestion.setDraggableItem($quiz, $item, suffix);
            pqQuestion.setAudioPlayable($quiz, $item);
        } else {
            $dropbox.removeClass(prefix+"Dots");
            $dropbox.text("");
            $dropbox.removeClass("dragOver");
            if ($parent.hasClass(prefix+suffix+"Items")) {
                if (isCounter)
                    countAvailable = $.publiquiz.question.counterItemAvailable($quiz, $item);
                if (isMultiple || countAvailable) {
                    count = $quiz.find("."+prefix+suffix+"Item").length;
                    pqQuestion.setDraggableItem($quiz, $item, suffix);
                    pqQuestion.setAudioPlayable($quiz, $item);
                    $item = $item.clone();
                    $item.attr("id", quzId+"_item"+pqQuestion.formatNumber(count += 100, 3));
                }
            }
            $item.appendTo($dropbox).addClass(prefix+"ItemDropped");
            pqQuestion.setDraggableItem($quiz, $item, suffix);
            pqQuestion.setAudioPlayable($quiz, $item);
            if ($dropbox.hasClass(prefix+"Dropzone"))
                $dropbox.removeClass(prefix+"Dropzone-visible");

            // Specific par type d'engine
            if (engine == "sort" && $item.children("img").length > 0) {
                $item.addClass(prefix+"InlineItemImageDropped");
            } else if (engine == "matching" && $item.children("img").length > 0) {
                $item.addClass(prefix+"BlockItemImageDropped");
            } else if (engine == "blanks-media") {
                if ($item.children("img").length > 0 && $item.text().trim() === "")
                    $item.addClass(prefix+"ItemImageDropped");
                $item.each( function() {
                    var $itm = $(this);
                    $itm.find("audio").each( function() {
                        var $audioPlayer = $(this).parent();
                        if ($audioPlayer.attr("class").indexOf("AudioPlayer") >= 0) {
                            $audioPlayer.css("margin-right", "");
                        }
                    });
                });
            }
        }
        $.publiquiz.context.onQuizModified(pqQuestion, $quiz);
    },

    /**
     * Helper, get event position (mouse or touch).
     *
     * @params {Object} $target : jQuery object.
     * @params {Event} ev : Object event.
     * @return Array: position X/Y, original position
     */
    eventPosition: function($target, ev) {
        var posX = null;
        var posY = null;
        var scale = $.publiquiz.defaults.scale;

        if (ev.originalEvent.changedTouches) {
            var touch = ev.originalEvent.changedTouches[0];
            posX = touch.pageX;
            posY = touch.pageY;
        } else {
            posX = ev.pageX;
            posY = ev.pageY;
        }

        posX /= scale.x;
        posY /= scale.y;

        return [posX, posY];
    },

    /**
     * Helper, make ghost of item touch.
     *
     * @params {Object} $quiz : jQuery object quiz.
     * @params {Object} $target : jQuery object.
     * @params {Event} ev : Object event.
     * @params {String} suffix : String suffix class name.
     * @return Object ghost.
     */
    makeGhost: function($quiz, $target, ev, suffix) {
        var pqQuestion = this;
        var prefix = $quiz.data("prefix");
        var $ghost = $target.clone();
        var pos = pqQuestion.eventPosition($target, ev);
        var $mainClass = $quiz.closest("."+$.publiquiz.defaults.mainClass);

        // Specific when we are in opener
        if ($target.children("img").length > 0) {
            $ghost.children("img").css("width", $target.children("img").css("width"));
            $ghost.children("img").css("height", $target.children("img").css("height"));
        }

        $ghost.appendTo($mainClass);
        $ghost.css("opacity", "0.25");
        $ghost.css("position", "absolute");
        $ghost.offset({
            top: pos[1] - $ghost.height(),
            left: pos[0] - $ghost.width()
        });
        $ghost.css("height", "initial");
        $ghost.removeClass(prefix+"ItemDropped " +
                prefix+suffix+"ItemDropped " +
                prefix+"ItemImageDropped " +
                prefix+"InlineItemImageDropped " +
                prefix+"BlockItemImageDropped");
        return $ghost;
    },

    /**
     * Helper, cancel a item dropped.
     *
     * @params {Object} $quiz : jQuery object quiz.
     * @params {Object} $item : jQuery object item.
     * @params {String} suffix : String suffix class name.
     */
    cancelItemDrop: function($quiz, $item, suffix) {
        var pqQuestion = this;
        var options = $quiz.data("engine-options") || "";
        if (options.search("multiple") > -1 ) {
            $item.remove();
            $.publiquiz.context.onQuizModified(pqQuestion, $quiz);
            return;
        }

        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var evtStart = "mousedown touchstart";
        var evtMove = "mousemove touchmove";
        var evtEnd = "mouseup touchend";
        var isCounter = (options.search("counter") > -1);

        var itemId = $item.attr("id");
        itemId = itemId.substring(quzId.length, itemId.length-3);
        var $items = $quiz.find("#"+quzId+itemId+"s");

        // Check for ItemsCat when no-shuffle=type
        if ($items.find("."+prefix+"ItemsCat").length > 0) {
            var classes = " " + $item.attr("class") + " ";
            var cat = classes.match(" cat[0-9]+ ");
            if (cat.length > 0) {
                cat = cat[0].trim();
                cat = cat.substr(0, 1).toUpperCase() + cat.substr(1);
                $items = $items.find("."+prefix+"Items"+cat);
            }
        }

        if (isCounter) {
            var $oldItem = $items.find('[data-item-value="'+$item.data("item-value")+'"]');
            if ($oldItem.length > 0) {
                var currentNumber = $oldItem.data("item-count-current");
                $oldItem.data("item-count-current", currentNumber-1);
                $item.remove();
                $.publiquiz.context.onQuizModified(pqQuestion, $quiz);
                return;
            } else {
                var maxNumber = $item.data("item-count");
                $item.data("item-count-current", maxNumber-1);
            }
        }

        $item.removeClass(prefix+"ItemDropped " +
                prefix+suffix+"ItemDropped " +
                prefix+"ItemImageDropped " +
                prefix+"InlineItemImageDropped " +
                prefix+"BlockItemImageDropped")
            .appendTo($items);
        $item.unbind(evtStart);
        $(document).unbind(evtMove);
        $(document).unbind(evtEnd);
        pqQuestion.setDraggableItem($quiz, $item, suffix);
        pqQuestion.setAudioPlayable($quiz, $item);
        $.publiquiz.context.onQuizModified(pqQuestion, $quiz);
    },

    /**
     * Set enable player audio after drop it
     *
     * @params {Object} $quiz : jQuery object quiz.
     * @params {Object} $item : jQuery object item.
     */
    setAudioPlayable: function($quiz, $item) {
        $item.find("audio").each( function() {
            var $audioPlayer = $(this).parent();
            if ($audioPlayer.attr("class").indexOf("AudioPlayer") >= 0) {
                $audioPlayer.unbind();
                $audioPlayer.find("[data-player='duration']").unbind();
                $audioPlayer.find("[data-player='button-play']").unbind();
                $audioPlayer.find("[data-player='timeline']").unbind();
                $audioPlayer.find("[data-player='cursor']").unbind();
                $audioPlayer.player();
            }
        });
    },

    /**
     * Function call for display/hide help
     *
     * @param {Object} $quiz, object jquery quiz.
     */
    displayHelp: function($quiz) {
        $.publiquiz.question.displayInfo($quiz, "Help", $quiz.data("quiz-id")+"_help-slot");
    },

    /**
     * Function call for display/hide help/explanation/script/strategy slots.
     *
     * @param {jQuery} $quiz - Quiz element.
     * @param {string} type - Type of the slot to display.
     * @param {string} id - Id of the slot to display.
     */
    displayInfo: function($quiz, type, id) {
        var prefix = $quiz.data("prefix");
        var $slot = $quiz.find("#"+id);

        $slot.find("audio").each(function() {
            $(this).get(0).pause();
        });

        if ($slot.hasClass(prefix+type+"PopUp")) {
            $slot.closest("."+prefix+"PopUp").toggleClass("fadeBackground");
            $slot.toggleClass("hidden");
            $slot.setOnCenterScreen();
            $(window).on("resize", function() {
                $slot.setOnCenterScreen();
            });
        } else {
            $slot.slideToggle("slow");
        }
    },

    /**
     * Display quiz text answer.
     *
     * @param {Object} $quiz - Quiz element.
     */
    displayTextAnswer: function($quiz) {
        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");
        var $answer = $quiz.find("#"+quzId+"_answer-slot");
        if ($answer.length > 0) {
            if ($answer.hasClass(prefix+"AnswerPopUp")) {
                $quiz.find("#"+quzId+"_answer-link").removeClass("hidden");
            }
            else {
                $answer.slideDown("slow");
            }
        }
    },

    /**
     * Hide quiz text answer.
     *
     * @param {Object} $quiz - Quiz element.
     */
    hideTextAnswer: function($quiz) {
        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");
        var $answer = $quiz.find("#"+quzId+"_answer-slot");
        if ($answer.length > 0) {
            var $link = $quiz.find("#"+quzId+"_answer-link");
            if ($answer.hasClass(prefix+"AnswerPopUp") && !$link.hasClass("hidden")) {
                $link.addClass("hidden");
            }
            else if ($answer.css("display") != "none") {
                $answer.slideUp("slow");
            }
        }
    },

    /* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     *                              Quiz retry function
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

    /**
     * Retry quiz choices, keep only right answer.
     *
     * @param {Object} quiz.
     * @params {String} suffix : suffix string for select object.
     */
    retryChoices: function($quiz, suffix) {
        var pqQuestion = this;
        pqQuestion.clearVerify();
        var prefix = $quiz.data("prefix");
        var engine = $quiz.data("engine");
        var isCheckRadio = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("radio") > -1 )
            isCheckRadio = true;

        var quzId = $quiz.data("quiz-id");
        var res = pqQuestion.correction($quiz.find("#"+quzId+"_correct"));

        if (isCheckRadio && engine != "pointing") {
            var $engine = $quiz.find("#"+quzId+"_engine");

            // Get group
            var choices = [];
            $quiz.find("."+prefix+"Choice").each( function() {
                var group = $(this).data("group");
                if ($.inArray(group, choices) < 0 )
                    choices.push(group);
            });

            // Keep only right choice
            $.each(choices, function() {
                var group = this;
                var $item = null;
                if (res[group] && $engine.find("."+prefix+"Choice")
                                    .filter("[data-group=\""+group+"\"]")
                                    .filter("[data-name=\"false\"]")
                                    .hasClass("selected")) {
                    $item = $engine.find("."+prefix+"Choice")
                                    .filter("[data-group=\""+group+"\"]")
                                    .filter("[data-name=\"false\"]");
                    $item.find("input").prop("checked", false);
                    $item.removeClass("selected");
                } else if (!res[group] && $engine.find("."+prefix+"Choice")
                                    .filter("[data-group=\""+group+"\"]")
                                    .filter("[data-name=\"true\"]")
                                    .hasClass("selected")) {
                    $item = $engine.find("."+prefix+"Choice")
                                    .filter("[data-group=\""+group+"\"]")
                                    .filter("[data-name=\"true\"]");
                    $item.find("input").prop("checked", false);
                    $item.removeClass("selected");
                }
            });
        } else {
            $quiz.find("."+prefix+suffix).each( function() {
                var $elem = $(this);
                var _id = $elem.attr("id");
                var key = _id.substring(_id.length - 3, _id.length);

                if ($elem.hasClass("selected") && !(key in res)) {
                    $elem.find("input").prop("checked", false);
                    $elem.removeClass("selected");
                }
            });
        }
    },

    /**
     * Retry quiz blanks, keep only right answer.
     *
     * @param {Object} quiz.
     */
    retryBlanks: function($quiz) {
        var pqQuestion = this;
        pqQuestion.clearVerify();
        var engine = $quiz.data("engine");
        if (engine == "blanks-fill") {
            var quzId = $quiz.data("quiz-id");
            var isStrict = false;
            var options = [];
            if ($quiz.data("engine-options") &&
                    $quiz.data("engine-options").search("strict") > -1 ) {
                isStrict = true;
                var opts = $quiz.data("engine-options").replace("strict", "").trim();
                if (opts !== "")
                    options = opts.split(" ");
            }

            var res = pqQuestion.correction($quiz.find("#"+quzId+"_correct"));
            $.each(res, function(key, value) {
                var $item = $quiz.find("#"+quzId+"_"+key);
                var data = $item.val().trim();

                if (!pqQuestion.isValideBlanksFillAnswer(data, value, isStrict, options))
                    $item.val("");

            });
        } else {
            pqQuestion.retryQuizCmp($quiz);
        }
    },

    /**
     * Retry quiz pointing category, keep only right answer.
     *
     * @param {Object} quiz.
     */
    retryPointingCategory: function($quiz) {
        var pqQuestion = this;
        pqQuestion.clearVerify();
        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");
        var res = pqQuestion.correctionCategories($quiz.find("#"+quzId+"_correct"));

        $quiz.find("."+prefix+"Point").each( function() {
            var $point = $(this);
            var category = $point.data("category-id");
            var pointId = $point.data("choice-id");
            if (category && res[category] && res[category].search(pointId) == -1) {
                var classList = $point.attr("class").split(/\s+/);
                if (classList.length > 1)
                    $point.removeClass(classList[classList.length - 1]);
            }

        });
    },

    /**
     * Retry quiz categories, keep only right answer.
     *
     * @param {Object} quiz.
     */
    retryCategories: function($quiz) {
        var pqQuestion = this;
        pqQuestion.clearVerify();
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var options = $quiz.data("engine-options") || "";
        var isMultiple = (options.search("multiple") > -1);
        var isCounter = (options.search("counter") > -1);
        var res = pqQuestion.correctionCategories($quiz.find("#"+quzId+"_correct"));

        if (options.search("color") > -1 ) {
            $quiz.find("."+prefix+"Choice").each( function() {
                var $choice = $(this);
                var value = $choice.data("choice-value").toString();
                if (isMultiple) {
                    $choice.find("."+prefix+"ItemColor").each( function() {
                        var $item = $(this);
                        var category = $item.data("category-id");
                        if (category && $.inArray(value, res[category].split("|")) == -1)
                            $item.remove();
                    });
                } else {
                    var category = $choice.data("category-id");
                    if (category && $.inArray(value, res[category].split("|")) == -1) {
                        var classList = $choice.attr("class").split(/\s+/);
                        if (classList.length > 1)
                            $choice.removeClass(classList[classList.length - 1]);
                    }
                }
            });
        } else {
            var $items = $quiz.find("#"+quzId+"_items");

            if (options.search("float") > -1 ) {
                var $legends = $quiz.find("#"+quzId+"_legend_items");
                $quiz.find("."+prefix+"CategoryLegendDrop").each( function() {
                    var $dropboxLegend = $(this);
                    var $dropbox = $dropboxLegend.parent().find("."+prefix+"CategoryDrop");
                    var $legend = $dropboxLegend.find("."+prefix+"CategoryLegendItem");
                    if ($legend.length === 0 )
                        return true;
                    var legendId = $legend.attr("id");
                    legendId = legendId.substring(legendId.length - 3, legendId.length);
                    if (!res[legendId]) {
                        $dropbox.find("."+prefix+"CategoryItemDropped")
                            .appendTo($items)
                            .removeClass(prefix+"CategoryItemDropped");
                        $legend.appendTo($legends).removeClass(prefix+"CategoryLegendItemDropped");
                        $dropboxLegend.addClass(prefix+"Dots");
                        return true;
                    }
                    //
                    var values = res[legendId].split("|");
                    $dropbox.find("."+prefix+"CategoryItem").each( function() {
                        var $item = $(this);
                        var data = $item.data("item-value").toString();
                        if ($.inArray(data, values) == -1) {
                            if (isMultiple)
                                $item.remove();
                            else
                                $item.appendTo($items).removeClass(prefix+"CategoryItemDropped");
                        }
                    });
                });
            } else {
                $.each(res, function(key, value) {
                    var $dropbox = $quiz.find("#"+quzId+"_"+key);
                    var values = value.split("|");
                    $dropbox.find("."+prefix+"CategoryItem").each( function() {
                        var $item = $(this);
                        var data = $item.data("item-value").toString();
                        if ($.inArray(data, values) == -1) {
                            if (isMultiple) {
                                $item.remove();
                            } else if (isCounter) {
                                $.publiquiz.question.counterRemoveItem($quiz, $item, $items, "Category");
                            } else {
                                $item.appendTo($items).removeClass(prefix+"CategoryItemDropped");
                            }
                        }
                    });
                });
            }
        }
    },

    /**
     * Retry quiz engine compared mode check.
     *
     * @params {Object} $quiz : Object jquery quiz.
     */
    retryQuizCmp: function($quiz) {
        var pqQuestion = this;
        pqQuestion.clearVerify();
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var options = $quiz.data("engine-options") || "";
        var isMultiple = (options.search("multiple") > -1);
        var isCounter = (options.search("counter") > -1);
        var $items = $quiz.find("#"+quzId+"_items");
        var res = pqQuestion.correction($quiz.find("#"+quzId+"_correct"));

        $.each(res, function(key, value) {
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            var $item = $dropbox.find("."+prefix+"Item");
            if ($item.length > 0 && $.inArray($item.data("item-value"), value.split("|")) < 0) {
                if (isMultiple) {
                    $item.remove();
                } else if (isCounter) {
                    $item.removeClass(prefix+"ItemImageDropped " +
                                      prefix+"InlineItemImageDropped " +
                                      prefix+"BlockItemImageDropped");
                    $item.each(function () {
                        $.publiquiz.question.counterRemoveItem($quiz, $(this), $items, "");
                    });
                } else {
                    $item.removeClass(prefix+"ItemDropped "+
                        prefix+"ItemImageDropped " +
                        prefix+"InlineItemImageDropped " +
                        prefix+"BlockItemImageDropped")
                        .appendTo($items);
                }

                if (!$dropbox.hasClass(prefix+"Dropzone"))
                    $dropbox.addClass(prefix+"Dots");
            } else if (!value && $dropbox.hasClass(prefix+"Dropzone")) {
                    $dropbox.addClass(prefix+"Dropzone-visible");
            }
        });
    },

    /* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     *                       Quiz insert user anwer function
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

    /**
     * User answers for quiz "choices"
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} suffix : suffix string for select object.
     * return {Array}
     */
    userAnswersQuizChoices: function($quiz, suffix) {
        var prefix = $quiz.data("prefix");
        var options = $quiz.data("engine-options") || "";
        var isCheckRadio = (options.search("radio") > -1 );
        var engine = $quiz.data("engine");
        var answer = [];

        if (isCheckRadio && engine != "pointing") {
            $quiz.find("."+prefix+suffix+".selected").each( function() {
                var $choice = $(this);
                var grp = $choice.data("group");
                var name = $choice.data("name");
                answer.push(grp+name);
            });
        } else {
            $quiz.find("."+prefix+suffix+".selected").each( function() {
                var $choice = $(this);
                var id = $choice.attr("id");
                id = id.substring(id.length - 3, id.length);
                answer.push(id+"x");
            });
        }
        return answer;
    },

    /**
     * Insert user answers in html for quiz drop
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    inserUserAnswersQuizDrop: function ($quiz) {
        var pqQuestion = this;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var answer = [];

        $quiz.find("."+prefix+"Drop").each( function() {
            var $dropbox = $(this);
            var $item = $dropbox.find("."+prefix+"Item");
            if ($item.length > 0) {
                var value = $item.data("item-value");
                var id = $dropbox.attr("id");
                answer.push(id.substring(id.length - 3, id.length) + value);
            }
        });

        pqQuestion.writeUserAnswers($quiz, quzId, answer.join("::"));
    },

    /* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     *                          Quiz score function
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

    /**
     * Show quiz score.
     */
    displayQuizScore: function($quiz) {
    },

    /**
     * Show global score for specific action and questions.
     *
     * @params {Object} $action : object jquery publiquiz action.
     */
    displayGlobalScore: function($action) {
        var result = this.computeGlobalScore($action.questions);
        var score = result.score;
        var total = result.total;

        if (total === 0)
            return;

        var prefix = $.publiquiz.defaults.prefix;
        var baseScore = -1;
        var baseScoreElem = $action.find("."+prefix+"BaseScore");
        if (baseScoreElem.length > 0)
            baseScore = parseInt(baseScoreElem.text(), 10);

        if (baseScore > -1) {
            score = (score * baseScore) / total.toFixed(1);
            score = Math.round(score);
            total = baseScore;
        }

        var $gScoreElem = $action.find("."+prefix+"GlobalScore");
        $gScoreElem.text(score + " / " + total);
        $gScoreElem.removeClass("hidden");
    },

    /**
     * Compute score for specific questions.
     *
     * @params {Object} $questions : array of object jquery publiquiz.
     * @return {Dictionnary}.
     */
    computeGlobalScore: function($questions) {
        var pqQuestion = this;
        var score = 0.0;
        var total = 0;
        $questions.each( function(){
            var $quiz = $(this);
            var quzId = $quiz.data("quiz-id");
            var res = pqQuestion.scoreFunc[quzId].func($quiz);
            score += res.score;
            total += res.total;
        });
        var result = {};
        result.score = score;
        result.total = total;
        return result;
    },

    /**
     * Score for quiz engine choices mode radio.
     *
     * @param {Object} jquery Object quiz.
     * @return {Dictionnary}.
     */
    scoreForQuizChoicesRadio: function($quiz) {
        var pqQuestion = this;
        var quzId = $quiz.data("quiz-id");
        var total = 1;
        var score = 0;
        var correct = true;
        var res = pqQuestion.correction($quiz.find("#"+quzId+"_correct"));
        $.each(res, function(key, value) {
            var $item = $quiz.find("#"+quzId+"_"+key);
            if (! $item.hasClass("selected")) {
                correct = false;
                return false;
            }
            return false;
        });
        if (correct)
            score = 1;

        var result = {};
        result.score = score;
        result.total = total;
        return result;
    },

    /**
     * Score for quiz engine choices mode check.
     * Le score se calcule par rapport au poids de la réponse, la réponse
     * fausse vaut toujours '-1' point.
     *
     * @param {Object} jquery Object quiz.
     * @params {String} suffix : suffix string for select object.
     * @return {Dictionnary}.
     */
    scoreForQuizChoicesCheck: function($quiz, suffix) {
        var pqQuestion = this;
        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");
        var score = 0.0;
        var total = $quiz.find("."+prefix+suffix).length;
        var res = pqQuestion.correction($quiz.find("#"+quzId+"_correct"));

        // On determine le poids d'une reponse correcte
        var weight_correct = total / Object.keys(res).length;

        $quiz.find("."+prefix+suffix).each( function() {
            var $elem = $(this);
            var _id = $elem.attr("id");
            var key = _id.substring(_id.length - 3, _id.length);

            if ($elem.hasClass("selected") && key in res)
                score += weight_correct;
            else if ($elem.hasClass("selected") && !(key in res))
                score -= 1;
        });

        score = Math.round(score);
        if (score < 0)
            score = 0;

        var result = {};
        result.score = score;
        result.total = total;
        return result;
    },

    /**
     * Score for quiz engine compared mode check.
     * the mode explain how compute score.
     *
     * @params {Object} $quiz : Object jquery quiz.
     * @return {Dictionnary}.
     */
    scoreForQuizCmpCheck: function($quiz) {
        var pqQuestion = this;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var res = pqQuestion.correction($quiz.find("#"+quzId+"_correct"));

        var total = 0;
        var score = 0;
        $.each(res, function(key, value) {
            total += 1;
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            var $item = $dropbox.find("."+prefix+"Item");
            if ($item.length > 0 && ($.inArray($item.data("item-value").toString(), value.split("|") ) >= 0 ))
                score += 1;
        });

        var result = {};
        result.score = score;
        result.total = total;
        return result;
    },

    /**
     * Score for quiz engine compared mode radio.
     * the mode explain how compute score.
     *
     * @params {Object} $quiz : Object jquery quiz.
     * @return {Dictionnary}.
     */
    scoreForQuizCmpRadio: function($quiz) {
        var pqQuestion = this;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var total = 1;
        var score = 0;
        var correct = true;
        var res = pqQuestion.correction($quiz.find("#"+quzId+"_correct"));

        $.each(res, function(key, value) {
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            var $item = $dropbox.find("."+prefix+"Item");
            if ($item.length === 0) {
                correct = false;
                return false;
            }
            if ($item.data("item-value") != value) {
                correct = false;
                return false;
            }
            return null;
        });

        if (correct)
            score = 1;

        var result = {};
        result.score = score;
        result.total = total;
        return result;
    },

    /**
     * Score for quiz engine "pointin-categories".
     *
     * @params {Object} $quiz : Object jquery quiz.
     * @return {Dictionnary}.
     */
    scoreForQuizPointingCategories: function($quiz) {
        var pqQuestion = this;
        var result = {};
        var noMark = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("nomark") > -1 )
            noMark = true;

        if (noMark) {
            result.score = 0;
            result.total = 0;
            return result;
        }

        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");
        var score = 0;
        var total = 0;
        var res = pqQuestion.correctionCategories($quiz.find("#"+quzId+"_correct"));

        $.each(res, function(key, value) {
            total += value.split("|").length;
        });

        $quiz.find("."+prefix+"Point").each( function() {
            var $point = $(this);
            var category = $point.data("category-id");
            var pointId = $point.data("choice-id");
            if (category && !res[category])
                score -= 1;
            else if (category && res[category].search(pointId) > -1)
                score += 1;
            else if (category && res[category].search(pointId) == -1)
                score -= 1;
        });

        if (score < 0)
            score = 0;

        result.score = score;
        result.total = total;
        return result;
    },

    /* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     *                              Quiz verify function
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

    /**
     * Suppression des informations de verification du quiz
     */
    clearVerify: function() {
        $.each($.publiquiz.question.timers, function() {
            clearTimeout(this);
        });
        $('.animated').finish();
        $('body').finish();
        $($.find(".answer")).removeClass("answer");
        $($.find(".answerKo")).removeClass("answerKo");
        $($.find(".answerOk")).removeClass("answerOk");
    },

    /**
     * Verify answer for quiz qcm.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : "full", "right" or "user" color.
     */
    verifyQuizChoicesAnswer: function($quiz, mode) {
        var pqQuestion = this;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var engine = $quiz.data("engine");
        var isCheckRadio = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("radio") > -1 )
            isCheckRadio = true;
        var paramWrongAnswers = $.publiquiz.defaults.wrongAnswers;

        var rightAnswers = pqQuestion.correction($quiz.find("#"+quzId+"_correct"));
        var userAnswers = pqQuestion.correction($quiz.find("#"+quzId+"_user"));

        if (isCheckRadio && engine != "pointing") {
            var $engine = $quiz.find("#"+quzId+"_engine");

            // Get group
            var choices = [];
            $quiz.find("."+prefix+"Choice").each( function() {
                var group = $(this).data("group");
                if ($.inArray(group, choices) < 0 )
                    choices.push(group);
            });

            // Verify user answer
            $.each(choices, function() {
                var group = this;
                var $choices = $engine.find("."+prefix+"Choice")
                        .filter("[data-group=\""+group+"\"]");
                var $true;
                var $false;
                if (rightAnswers[group]) {
                    $true = $choices.filter("[data-name=\"true\"]");
                    $false = $choices.filter("[data-name=\"false\"]");
                    if ($true.hasClass("selected")) {
                        $.publiquiz.question.addClassColorAnswer($quiz, $true, true);
                    }
                    else if ($false.hasClass("selected")) {
                        $.publiquiz.question.addClassColorAnswer($quiz, $false, false);
                    }
                }
                else {
                    $true = $choices.filter("[data-name=\"true\"]");
                    $false = $choices.filter("[data-name=\"false\"]");
                    if ($false.hasClass("selected")) {
                        $.publiquiz.question.addClassColorAnswer($quiz, $false, true);
                    }
                    else if ($true.hasClass("selected")) {
                        $.publiquiz.question.addClassColorAnswer($quiz, $true, false);
                    }
                }
            });

        } else {
            var suffix = "Choice";
            if (engine == "pointing")
                suffix = "Point";
            var inputs = $quiz.find("."+prefix+suffix);
            if (mode == "user" || mode == "right")
                inputs = inputs.filter('.selected');

            inputs.each( function() {
                var $item = $(this);
                var key = $item.attr("id");
                key = key.substring(key.length - 3, key.length);
                if (mode == "user") {
                    var valid = rightAnswers[key];
                    $.publiquiz.question.addClassColorAnswer($quiz, $item, valid);
                    if (!valid && paramWrongAnswers == "clear") {
                        $('body').queue(function(next) {
                            $item.find("input").prop("checked", false);
                            $item.removeClass("selected answerKo");
                            next();
                        });
                    }
                } else if (mode == "right") {
                    if (rightAnswers[key])
                        $item.addClass("answerOk");
                } else {
                    if (isCheckRadio || engine == "choices-radio") {
                        if (rightAnswers[key] && userAnswers[key])
                            $item.addClass("answerOk");
                        else if (rightAnswers[key] && !userAnswers[key])
                            $item.addClass("answerKo");
                    } else {
                        if (rightAnswers[key] == userAnswers[key])
                            $item.addClass("answerOk");
                        else
                            $item.addClass("answerKo");
                    }
                }
            });

        }

        var duration = $quiz.data("verify-duration");
        if (duration < 0) {
            var timer = setTimeout(pqQuestion.clearVerify, duration);
            pqQuestion.timers.push(timer);
        }
    },

    /**
     * Verify user answer for quiz cmp.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    verifyQuizCmpAnswer: function($quiz, mode) {
        var pqQuestion = this;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var rightAnswers = pqQuestion.correction($quiz.find("#"+quzId+"_correct"));
        var userAnswers = pqQuestion.correction($quiz.find("#"+quzId+"_user"));
        var $items = $quiz.find("#"+quzId+"_items");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;

        var paramWrongAnswers = $.publiquiz.defaults.wrongAnswers;
        $.each(rightAnswers, function(key, value) {
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            var $item = $dropbox.find("."+prefix+"Item");
            if ($item.length > 0) {
                var valid;
                if (mode == "user") {
                    valid = $.inArray($item.data("item-value").toString(), value.split("|")) >= 0;
                    $.publiquiz.question.addClassColorAnswer($quiz, $dropbox, valid);
                    if (!valid && paramWrongAnswers == "clear") {
                        $("body").queue(function(next) {
                            if (isMultiple) {
                                $item.remove();
                            }
                            else {
                                $item.removeClass(prefix+"ItemDropped "+
                                                  prefix+"ItemImageDropped " +
                                                  prefix+"InlineItemImageDropped " +
                                                  prefix+"BlockItemImageDropped")
                                    .animateMoveElement($items);
                            }
                            if (!$dropbox.hasClass(prefix+"Dropzone"))
                                $dropbox.addClass(prefix+"Dots");
                            $dropbox.removeClass("answerKo");
                            next();
                        });
                    }
                } else if (mode == "right") {
                    if ($.inArray($item.data("item-value").toString(), value.split("|")) >= 0)
                        $.publiquiz.question.addClassColorAnswer($quiz, $dropbox, true);
                } else {
                    valid = userAnswers[key] && $.inArray(userAnswers[key], value.split("|")) >= 0;
                    $.publiquiz.question.addClassColorAnswer($quiz, $dropbox, valid);
                }
            } else if (!value && $item.length === 0) {
                if ($dropbox.hasClass(prefix+"Dropzone")) {
                    $dropbox.addClass("answer");
                    $dropbox.removeClass(prefix+"Dropzone-visible");
                }
                $.publiquiz.question.addClassColorAnswer($quiz, $dropbox, true);
            }
        });

        if (mode == "user")
            return;

        // Gestion des intrus
        var userValues = [];
        var rightValues = [];

        $.each(userAnswers, function(key, value) { userValues.push(value); });
        $.each(rightAnswers, function(key, value) {
            $(value.split("|")).each( function(i, v) {
                if ($.inArray(v, rightValues) < 0)
                    rightValues.push(v);
            });
        });

        $quiz.find("#"+quzId+"_items").find("."+prefix+"Item").each( function() {
            var $item = $(this);
            var value = $item.data("item-value").toString();

            // S'il y a plusieurs etiquette de meme valeur dans la correction on les cache
            if ($.inArray(value, rightValues) >= 0)
                $item.addClass("hidden");

            if (mode == "right") {
                if ($.inArray(value, rightValues) < 0)
                    $item.addClass("answerOk");
            } else {
                if ($.inArray(value, userValues) >= 0 && $.inArray(value, rightValues) < 0)
                    $item.addClass("answerKo");
                else
                    $item.addClass("answerOk");
            }
        });

        var duration = $quiz.data("verify-duration");
        if (duration > 0) {
            var timer = setTimeout(pqQuestion.clearVerify, duration);
            pqQuestion.timers.push(timer);
        }
    },

    /* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     *                          Quiz correction function
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

    /**
     * Display right/user answer for quiz qcm.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} suffix : suffix string for select object.
     * @params {String} mode : mode "correct" or "user".
     */
    displayQuizChoicesAnswer: function($quiz, suffix, mode) {
        var pqQuestion = this;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        // Reset quiz
        $quiz.find("."+prefix+suffix+" input").prop("checked", false);
        $quiz.find("."+prefix+suffix).removeClass("selected answerOk answerKo");

        // Display pquizChoice selected
        var answers = pqQuestion.correction($quiz.find("#"+quzId+mode));

        $quiz.find("."+prefix+suffix).each( function() {
            var $item = $(this);
            var key = $item.attr("id");
            key = key.substring(key.length - 3, key.length);
            if (answers[key]) {
                $item.addClass("selected");

                // If Input set checked
                $item.find("input").prop("checked", true);
            }
        });
    },

    /**
     * Display right/user answer for quiz drag and drop.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : mode "correct" or "user".
     */
    displayQuizCmpAnswer: function($quiz, mode) {
        var pqQuestion = this;
        var quzId = $quiz.data("quiz-id");
        var engine = $quiz.data("engine");
        var prefix = $quiz.data("prefix");
        var options = $quiz.data("engine-options") || "";
        var isMultiple = (options.search("multiple") > -1);
        var isCounter = (options.search("counter") > -1);
        var showAllAnswer = (options.search("show-all-answer") > -1);
        var answers = pqQuestion.correction($quiz.find("#"+quzId+mode));
        var $items = $quiz.find("#"+quzId+"_items");

        // On vide les champs
        var classDropped = prefix+"ItemDropped " +
            prefix+"ItemImageDropped " +
            prefix+"InlineItemImageDropped " +
            prefix+"BlockItemImageDropped";
        $quiz.find("."+prefix+"Drop").each( function() {
            var $dropbox = $(this);
            // Manage item
            var $item = $dropbox.find("."+prefix+"Item");
            if ($item.length === 0)
                return true;
            if (isMultiple || $item.hasClass(prefix+"ItemCloned")) {
                $item.remove();
            } else {
                $item.removeClass(classDropped);
                if (isCounter)
                    $item.each(function () {
                        $.publiquiz.question.counterRemoveItem($quiz, $(this), $items, "");
                    });
                else
                    $item.appendTo($items);
            }
            // Manage Dropbox
            $dropbox.find("."+prefix+"Separator").remove();
            if ($dropbox.hasClass(prefix+"Dropzone"))
                $dropbox.addClass(prefix+"Dropzone-visible");
            else
                $dropbox.addClass(prefix+"Dots");
            $dropbox.removeClass("answer answerOk answerKo");
            return true;
        });

        $items.find("."+prefix+"Item").removeClass("answerKo answerOk hidden");

        // On place la correction en deplacant les items
        $.each(answers, function(key, value) {
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            var $res = [];
            $(value.split("|")).each( function(i, v) {
                v = v.replace(/\\/g, '\\\\');
                var $item = $items.find("."+prefix+"Item").filter("[data-item-value=\""+v+"\"]");
                if (showAllAnswer && $item.length === 0) {
                    $quiz.find("."+prefix+"Drop ."+prefix+"Item").filter("[data-item-value=\""+v+"\"]").each( function() {
                        $item.push($(this).clone().addClass(prefix+"ItemCloned"));
                    });
                }
                if ($item.length > 0)
                    $res.push($($item[0]));
            });
            $dropbox.removeClass(prefix+"Dots answer").text("");
            if ($dropbox.hasClass(prefix+"Dropzone"))
                $dropbox.removeClass(prefix+"Dropzone-visible");
            if (showAllAnswer && $res.length > 1) {
                $.each($res, function(i, v) {
                    if (isCounter && !this.hasClass(prefix+"ItemCloned")) {
                        if (value) {
                            $.publiquiz.question.counterPickItem($quiz, this, $dropbox, "");
                        } else {
                            if ($dropbox.hasClass(prefix+"Dropzone"))
                                $dropbox.addClass("answer");
                            else
                                $dropbox.addClass(prefix+"Dots");
                        }
                    } else {
                        _appendItem(this, $dropbox, engine, isMultiple);
                    }
                    if (i < $res.length -1)
                        $dropbox.append('<span class="'+prefix+'Separator"></span>');
                });
            } else {
                if (isCounter) {
                    if (value) {
                        $.publiquiz.question.counterPickItem($quiz, $res[0], $dropbox, "");
                    } else {
                        if ($dropbox.hasClass(prefix+"Dropzone"))
                            $dropbox.addClass("answer");
                        else
                            $dropbox.addClass(prefix+"Dots");
                    }
                } else {
                    _appendItem($res[0], $dropbox, engine, isMultiple);
                }
            }
        });

        function _appendItem($item, $dropbox, engine, isMultiple) {
            if ($item === undefined) {
                if ($dropbox.hasClass(prefix+"Dropzone"))
                    $dropbox.addClass("answer");
                else
                    $dropbox.addClass(prefix+"Dots");
                return;
            }
            if (isMultiple) {
                $item = $item.clone();
                pqQuestion.setAudioPlayable($quiz, $item);
            }
            $item.appendTo($dropbox).addClass(prefix+"ItemDropped");

            // Specific par type d'engine
            if (engine == "sort" && $item.children("img").length > 0) {
                $item.addClass(prefix+"InlineItemImageDropped");
            } else if (engine == "matching" && $item.children("img").length > 0) {
                $item.addClass(prefix+"BlockItemImageDropped");
            } else if (engine == "blanks-media") {
                if ($item.children("img").length > 0 && $item.text().trim() === "")
                    $item.addClass(prefix+"ItemImageDropped");
            }
        }
    },

    /**
     * Display right/user answer for quiz engine blanks-fill.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @params {String} mode : display correct/user answer.
     */
    displayQuizAnswerBlanksFill: function($quiz, mode) {
        var pqQuestion = this;
        var prefix = $quiz.data("prefix");
        var options = $quiz.data("engine-options") || "";
        var showAllAnswer = (options.search("show-all-answer") > -1);

        // On vide les champs
        $quiz.find("."+prefix+"Choice").each( function() {
            var $item = $(this);
            $item.val("");
            $item.removeClass("answerOk answerKo");
        });

        var quzId = $quiz.data("quiz-id");
        var answers = pqQuestion.correction($quiz.find("#"+quzId+mode));
        $.each(answers, function(key, value) {
            var $item = $quiz.find("#"+quzId+"_"+key);
            if ($item.length > 0) {
                var data;
                if (showAllAnswer) {
                    data = value.split("|").join(" / ");
                    data = data.replace(new RegExp(/_/g), " ");
                } else {
                    data = value.split("|")[0].trim();
                }
                $item.val(data);
            }
        });
    },

    /* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     *                          Quiz library function
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

    /**
     * Shuffle items.
     *
     * @params {Object} $items : object jquery items.
     */
    shuffleItems: function($items) {
        $items.each( function() {
            var $container = $(this);
            var shuffle = $container.hasClass("shuffle");
            if (!shuffle)
                $container.shuffle();
        });
    },

    /**
     * Shuffle items and control not give the right answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {Array} dropzones : array of drop zone.
     * @params {Dict} res : dict of correction of quiz.
     * @return bool
     */
    shuffleAndControlItems: function($quiz, $dropzones, res) {
        var prefix = $quiz.data("prefix");
        var answer = true;
        var count = 0;

        if ($.isEmptyObject(res))
            return false;

        $.publiquiz.question.shuffleItems($quiz.find("."+prefix+"Items"));
        var items = $quiz.find("."+prefix+"Item");
        $dropzones.each(function() {
            var $dropzone = $(this);
            var $item = $(items[count]);
            var dropId = $dropzone.attr("id");
            dropId = dropId.substring(dropId.length - 3, dropId.length);
            if (res[dropId] != $item.data("item-value")) {
                answer = false;
                return false;
            }
            count ++;
        });

        return answer;
    },

    /**
     * Get the correction of quiz in dico.
     *
     * @param {Object} $elem, object contain correction.
     * @return {Dictionnary} the result is in a dico.
     */
    correction: function ($elem) {
        var res = {};
        var data = $elem.text().trim();
        if (!data)
            return res;
        data = data.replace(/(\r\n|\n|\r)/gm,"");
        data = data.replace(new RegExp(/’/g), "'");
        $.each(data.split("::"), function() {
            var value = this;
            if (value && value.length > 0) {
                var k = value.substring(0, 3);
                var v = value.substring(3, value.length);
                res[k] = v;
            }
        });
        return res;
    },

    /**
     * Get the correction of quiz categories in dico.
     *
     * @param {Object} $elem, object contain correction.
     * @return {Dictionnary} the result is in a dico.
     */
    correctionCategories: function($elem){
        var res = {};
        var data = $elem.text();
        if (!data)
            return res;
        data = data.replace(/(\r\n|\n|\r)/gm,"");
        data = data.replace(new RegExp(/’/g), "'");
        $.each(data.split("::"), function(idx, value) {
            if (value && value.length > 0) {
                value = value.trim();
                var key = value.substring(0, 3);
                var data = value.substring(3, value.length);
                if ($.inArray(key, Object.keys(res)) >= 0 )
                    data = res[key] + "|" + data;
                res[key] = data;
            }
        });

        return res;
    },

    /**
     * Write user answer in DOM.
     *
     * @param {Object} quiz.
     * @param {String} quiz id.
     * @param {String} user answer.
     */
    writeUserAnswers: function($quiz, quzId, answer) {
        answer = answer.replace(new RegExp(/’/g), "'");
        var $userAnswer = $quiz.find("#"+quzId+"_user");
        if ($userAnswer.length === 0) {
            var prefix = $quiz.data("prefix");
            var engine = $quiz.data("engine");
            var $quizAnswer = null;
            if (engine != "production")
                $quizAnswer = $quiz.find("#"+quzId+"_correct");
            else
                $quizAnswer = $quiz.find("."+prefix+"Production");

            $userAnswer = $("<div>")
                    .attr("id", quzId+"_user")
                    .addClass("hidden");
            $userAnswer.insertAfter($quizAnswer);
        }
        $userAnswer.text(answer);
    },

    /**
     * Helper, function contruct string for compare.
     *
     * @param {String} text origin.
     * @params {Boolean} isStrict : mode strict or not.
     * @params {Array} options : strict options.
     * @return {String} text for compare.
     */
    constructCmpString: function(text, isStrict, options) {
        var r = text.trim(); // TODO: rewrite.
        r = r.replace("-", " - ");
        r = r.replace("+", " + ");
        r = r.replace("/", " / ");
        r = r.replace("*", " * ");
        r = r.replace("=", " = ");
        r = r.replace(new RegExp(/’/g), "'");
        r = r.replace(new RegExp(/æ/g),"ae");
        r = r.replace(new RegExp(/œ/g),"oe");
        r = r.replace(new RegExp(/\s{2,}/g)," ");

        if (!isStrict) {
            r = r.toLowerCase();
            r = this.removePunctuation(r);
            r = this.removeAccent(r);
            r = r.replace(new RegExp(/\s/g),"");
            return r;
        }

        if ($.inArray("total", options) > -1 || options.length < 1)
            return r;

        if ($.inArray("accent", options) == -1)
            r = this.removeAccent(r);

        if ($.inArray("punctuation", options) == -1)
            r = this.removePunctuation(r);

        if ($.inArray("upper", options) == -1)
            r = r.toLowerCase();

        r = r.replace(new RegExp(/\s/g),"");
        return r;
    },

    removePunctuation: function(text) {
        return text.replace(new RegExp(/[\.,#!?$%\^&;:{}\_`~()]/g)," ");
    },

    removeAccent: function(text) {
        var r = text.replace(new RegExp(/[àáâ]/g),"a");
        r = r.replace(new RegExp(/ç/g),"c");
        r = r.replace(new RegExp(/[èéê]/g),"e");
        r = r.replace(new RegExp(/[îï]/g),"i");
        r = r.replace(new RegExp(/[ùúû]/g),"u");
        return r;
    },

    /**
     * Helper, use for validate user answer for engine blanks-fill.
     *
     * @params {String} userAnswer : answer of player.
     * @params {String} rightAnswer : the right answer.
     * @params {Boolean} isStrict : mode strict or not.
     * @params {Array} options : strict options.
     * @return {Boolean}.
     */
    isValideBlanksFillAnswer: function (userAnswer, rightAnswer, isStrict, options) {
        var pqQuestion = this;
        if (!userAnswer)
            userAnswer = "";

        userAnswer = pqQuestion.constructCmpString(userAnswer, isStrict, options);

        // Test first with full string
        var answer = [];
        $.each(rightAnswer.split("|"), function() {
            var txt = this;
            txt = pqQuestion.constructCmpString(txt, isStrict, options);
            answer.push(txt);
        });

        if ($.inArray(userAnswer, answer) > -1)
            return true;

        // Try again with first part of string, in case it's the correct answer with multiple values
        userAnswer = userAnswer.split("/")[0].trim();
        answer = [];
        $.each(rightAnswer.split("|"), function() {
            var txt = this;
            txt = pqQuestion.constructCmpString(txt, isStrict, options);
            answer.push(txt);
        });

        if ($.inArray(userAnswer, answer) > -1)
            return true;

        return false;
    },

    /**
     * Helper, function format number "3" -> "003".
     *
     * @param {String} str, number to format.
     * @return {Int} max, length max of format.
     */
    formatNumber: function (str, max) {
        str = str.toString();
        return str.length < max ? this.formatNumber("0" + str, max) : str;
    },

    /**
     * Add color class to answers.
     * If timerValidation is set, classes are toggle multiple times
     * before stopping on the Ok or Ko class.
     *
     * @param {Object} $quiz, jQuery object publiquiz.
     * @param {Object} $item, jQuery item to add class on.
     * @param {Boolean} right, True if answer is valid.
     */
    addClassColorAnswer: function($quiz, $item, right) {
        $('body').queue(function(next) {
            if (right)
                $item.addClass("answerOk");
            else
                $item.addClass("answerKo");
            next();
        });

        var $sound = $('#validation_' + (right?'right':'wrong'));
        if ($sound.length > 0) {
            $('body').queue(function(next) {
                $sound[0].pause();
                $sound[0].currentTime = 0;
                $sound[0].play();
                next();
            }).delay($sound[0].duration*1000);
        }
    },

    loadAudio: function() {
        var prefix = $.publiquiz.defaults.prefix;
        $('audio').filter(function() {
            var $parent = $(this).parent();
            return !($parent.hasClass("pdocAudioPlayer") || $parent.hasClass(prefix+"AudioPlayer"));
        }).each(function(){
            this.load();
        });
        $.publiquiz.question.loadAudio = function() {};
    },

    /**
     * Add event on audio with "pdocAudioBlocking" class to prevent interaction with
     * quiz during audio play.
     *
     * @param {jQuery} $quiz - Quiz element.
     */
    setAudioBlockInteraction: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("audio.pdocAudioBlocking").each(function() {
            var $audio = $(this);
            var $player = $audio.closest(".pdocAudioPlayer");
            $audio.on("play", function() {
                if ($quiz.find("."+prefix+"PopUp.audioBlock").length > 0)
                    return;

                var $popup = $("<div>").addClass(prefix+"PopUp audioBlock");
                $popup.css({
                    position: "absolute",
                    top: -5,
                    left: -5
                });
                var resizePopup = function() {
                    $popup.css({
                        height: $quiz.height()+10,
                        width: $quiz.width()+10
                    });
                };
                resizePopup();
                $(window).on("resize.pquizPopup", resizePopup);
                $player.addClass("audioBlock");
                $quiz.append($popup);
            });

            $audio.on("ended", function() {
                var $popup = $quiz.find("."+prefix+"PopUp.audioBlock");
                $popup.remove();
                $player.removeClass("audioBlock");
                $(window).off("resize.pquizPopup");
            });
        });
    },

    /**
     * Helper, to know device.
     */
    isIosDevice: function() {
        if (navigator.userAgent.match(/iPhone|iPad|iPod/i))
            return true;
        return false;
    },

    isAndroidDevice: function() {
        if (navigator.userAgent.match(/Android/i))
            return true;
        return false;
    },

    isBlackBerryDevice: function() {
        return navigator.userAgent.match(/BlackBerry/i);
    },

    isWindowsDevice: function() {
        if (navigator.userAgent.match(/IEMobile/i))
            return true;
        return false;
    },

    isOperaDevice: function() {
        if (navigator.userAgent.match(/Opera Mini/i))
            return true;
        return false;
    },

    valueInAnswers: function(value, answers) {
        for (var prop in answers) {
            if (answers.hasOwnProperty(prop) && answers[prop] == value)
                return true;
        }
        return false;
    },

    /**
     * With option counter, check if an item must be cloned or moved.
     * Also increment count of used items.
     *
     * @param {jQuery} $quiz - Quiz element.
     * @param {jQuery} $item - Item to check.
     * @returns {bool} True when item must be cloned, else false.
     */
    counterItemAvailable: function($quiz, $item) {
        var maxNumber = $item.data("item-count");
        var currentNumber = $item.data("item-count-current") || 0;
        currentNumber++;
        $item.data("item-count-current", currentNumber);
        return (currentNumber < maxNumber);
    },

    /**
     * Pick an item from deck and place it an a drop
     *
     * @param {jQuery} $quiz - Quiz element.
     * @param {jQuery} $item - Item to place.
     * @param {jQuery} $drop - Drop to put item into.
     * @param {string} suffix - Item class suffix.
     * @param {bool} [animate] - Animate the element going in the drop.
     * @returns {jQuery} New item if cloned, or old item.
     */
    counterPickItem: function($quiz, $item, $drop, suffix, animate) {
        var prefix = $quiz.data("prefix");
        var maxNumber = $item.data("item-count");
        var currentNumber = $item.data("item-count-current") || 0;
        currentNumber++;
        $item.data("item-count-current", currentNumber);
        if (currentNumber < maxNumber) {
            $item = $item.clone().insertBefore($item);
        }
        if (animate)
            $item.animateMoveElement($drop);
        else
            $item.appendTo($drop);
        $item.addClass(prefix+suffix+"ItemDropped");
        return $item;
    },

    /**
     * Remove an item from answers and add one in the deck.
     *
     * @param {jQuery} $quiz - Quiz element.
     * @param {jQuery} $item - Item to remove.
     * @param {jQuery} $deck - Deck of items.
     * @param {string} suffix - Item class suffix.
     * @param {bool} [animate] - Animate the element going back in the deck.
     */
    counterRemoveItem: function($quiz, $item, $deck, suffix, animate) {
        var prefix = $quiz.data("prefix");
        var $deckItem = $deck.find('[data-item-value="'+$item.data("item-value")+'"]');
        if ($deckItem.length > 0) {
            if (animate) {
                $item.removeClass(prefix+suffix+"ItemDropped")
                    .animateMoveElement($deckItem)
                    .queue(function(next) {
                        $item.remove();
                        next();
                    });
            } else {
                $item.remove();
            }
            var currentNumber = $deckItem.data("item-count-current");
            $deckItem.data("item-count-current", currentNumber-1);
        } else {
            var maxNumber = $item.data("item-count");
            $item.removeClass(prefix+suffix+"ItemDropped");
            if (animate)
                $item.animateMoveElement($deck);
            else
                $item.appendTo($deck);
            $item.data("item-count-current", maxNumber-1);
        }
    },

    /**
     * Disable events on popups to close them.
     *
     * @param {jQuery} $quiz - Quiz element.
     */
    disablePopupEvents: function($quiz) {
        var prefix = $quiz.data("prefix");

        if ($.publiquiz.defaults.popupContentClose) {
            $quiz.find("."+prefix+"InstructionsPopUp,"+
                       "."+prefix+"AnswerPopUp,"+
                       "."+prefix+"HelpPopUp,"+
                       "."+prefix+"ExplanationPopUp,"+
                       "."+prefix+"ScriptPopUp,"+
                       "."+prefix+"StrategyPopUp").off("click");
        }
        else {
            $quiz.find(".instructionsClose,"+
                       ".answerClose,"+
                       ".helpClose,"+
                       ".explanationClose,"+
                       ".scriptClose,"+
                       ".strategyClose").off("click");
        }

        $(document).off("click", "."+prefix+"PopUp");
    },

    /**
     * Set events on popups to close them.
     *
     * @param {jQuery} $quiz - Quiz element.
     */
    enablePopupEvents: function($quiz) {
        var prefix = $quiz.data("prefix");

        var popupClose = function(ev) {
            var $this = $(this);
            $this = $this.closest("."+prefix+"InstructionsPopUp,"+
                                  "."+prefix+"AnswerPopUp,"+
                                  "."+prefix+"HelpPopUp,"+
                                  "."+prefix+"ExplanationPopUp,"+
                                  "."+prefix+"ScriptPopUp,"+
                                  "."+prefix+"StrategyPopUp");
            $this.addClass("hidden");
            $this.closest(".fadeBackground").removeClass("fadeBackground");
            $this.find("audio").each(function() {
                $(this).get(0).pause();
            });
        };

        if ($.publiquiz.defaults.popupContentClose) {
            $quiz.find("."+prefix+"InstructionsPopUp,"+
                       "."+prefix+"AnswerPopUp,"+
                       "."+prefix+"HelpPopUp,"+
                       "."+prefix+"ExplanationPopUp,"+
                       "."+prefix+"ScriptPopUp,"+
                       "."+prefix+"StrategyPopUp").on("click", popupClose);
        }
        else {
            $quiz.find(".instructionsClose,"+
                       ".answerClose,"+
                       ".helpClose,"+
                       ".explanationClose,"+
                       ".scriptClose,"+
                       ".strategyClose").on("click", popupClose);
        }

        $("."+prefix+"PopUp").on("click", function(ev) {
            if (!$(ev.target).hasClass("fadeBackground")) return;
            var $this = $(this);
            $this.removeClass("fadeBackground");
            $this.find("."+prefix+"InstructionsPopUp,"+
                       "."+prefix+"AnswerPopUp,"+
                       "."+prefix+"HelpPopUp,"+
                       "."+prefix+"ExplanationPopUp,"+
                       "."+prefix+"ScriptPopUp,"+
                       "."+prefix+"StrategyPopUp")
                .addClass("hidden")
                .find("audio").each(function() {
                    $(this).get(0).pause();
                });
        });
    },

    /**
     *
     */
    clearAnimations: function() {
        while ($("body").queue().length > 0)
            $("body").stop(false, true);
        $(".animated").each( function() {
            var $anim = $(this);
            while ($anim.queue().length > 0)
                $anim.stop(false, true);
        });
    }

};


/*****************************************************************************
 *****************************************************************************
 *
 *                          Define publiquiz.context
 *
 *****************************************************************************
 ****************************************************************************/


$.publiquiz.context = {

    /* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     *                      Action save/load context function
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

    /**
     * Call when click on button action bar.
     *
     * @param {jQuery} $action - action element.
     * @param {String} action - action name.
     */
    onActionModified: function($action, action) {
        var ttl = $action.data("context-ttl");
        if (ttl === undefined || ttl < 0)
            return;

        var changes = {};
        var $questions = $action.questions;
        var ctxId = $($questions.get(0)).data("quiz-id")+"_action";
        var $data = $action.find("#"+ctxId+"_context .action");

        //
        var actions = [];
        if ($data.length > 0 && $data.text() !== "")
            actions = $data.text().split("::");

        if ((action === "userAnswer" && actions[actions.length-1] === "rightAnswer") ||
                (action === "rightAnswer" && actions[actions.length-1] === "userAnswer")) {
            actions.pop();
        } else if (action === "chrono") {
            changes.chrono = $.publiquiz.action.currentChronoValue;
        } else if (action === "countdown") {
            if (actions.length > 0 && actions[actions.length-1].match("^countdown_")) {
                actions.pop();
            }
            actions.push(action+"_"+$.publiquiz.action.currentCountdownValue);
        } else {
            actions.push(action);
        }
        changes.action = actions.join("::");

        //
        if (action === "validate") {
            var scores = {};
            $questions.each( function() {
                var $quiz = $(this);
                scores[$quiz.data("quiz-id")] = $quiz.data("quiz-result");
            });
            changes.score = JSON.stringify(scores);
            this.saveScore(ctxId, scores);
        }

        //
        this.writeActionChange($action, changes);
    },

    /**
     * Write action on page.
     *
     * @param {jQuery} $action - action element.
     * @param {Hash} changes - action values to write on page.
     */
    writeActionChange: function($action, changes) {
        var ttl = $action.data("context-ttl");
        if (ttl !== undefined && ttl < 0)
            return;

        var $questions = $action.questions;
        var ctxId = $($questions.get(0)).data("quiz-id")+"_action";
        changes.key = $action.data("context-key");

        // Add div id_context
        var $context = $action.find("#"+ctxId+"_context");
        if ($context.length === 0) {
            $context = $("<div>")
                .attr("id", ctxId+"_context")
                .addClass("hidden");
            $action.append($context);
        }

        //
        $.each(changes, function(k, v) {
            var $elem = $context.find("."+k);
            if ($elem.length === 0) {
                $elem = $("<div>").addClass(k);
                $context.append($elem);
            }
            $elem.text(v);
        });

        //
        if (changes.date === undefined) {
            var $date = $context.find(".date");
            if ($date.length === 0) {
                $date = $("<div>").addClass("date");
                $context.append($date);
            }
            var dt = new Date();
            var day = dt.getDate();
            var month = dt.getMonth();
            var year = dt.getFullYear();
            month++;
            $date.text(year+"-"+("0"+month).slice(-2)+"-"+("0"+day).slice(-2));
        }

        // Save
        this.saveActionContext($action);
    },

    /**
     * Save the action context.
     *
     * @param {jQuery} $action - action element.
     */
    saveActionContext: function($action) {
        var ttl = $action.data("context-ttl");
        if (ttl === undefined || ttl < 0)
            return;

        var $questions = $action.questions;
        var ctxId = $($questions.get(0)).data("quiz-id")+"_action";
        var $context = $action.find("#"+ctxId+"_context");
        this.saveContext(ctxId, ttl, $context);
    },

    /**
     * Load action from context.
     *
     * @param {jQuery} $action - action element.
     */
    loadActionContext: function($action) {
        var ttl = $action.data("context-ttl");
        if (ttl === undefined || ttl < 0)
            return;

        var $questions = $action.questions;
        var ctxId = $($questions.get(0)).data("quiz-id")+"_action";

        // Get context
        this.loadContext(null, $action, ctxId, this.setActionContext);
    },

    /**
     * Set action context.
     */
    setActionContext: function($action, objectJSON) {
        var ttl = $action.data("context-ttl");
        if (objectJSON === null || !$.publiquiz.context.isContextExpired(ttl, objectJSON))
            return;
        if (objectJSON.key !== $action.data("context-key"))
            return;
        $.publiquiz.context.writeActionChange($action, objectJSON);
        var $questions = $action.questions;
        var ctxId = $($questions.get(0)).data("quiz-id")+"_action";

        // Block anim
        var multipageAnimation = $.publiquiz.defaults.multipageAnimation;
        $.publiquiz.defaults.multipageAnimation = false;

        // Timer
        var $chrono = $action.find("#"+ctxId+"_context .chrono");
        if ($chrono.length > 0) {
            $.publiquiz.action.currentChronoValue = parseInt($chrono.text(), 10);
            $.publiquiz.action.initTimer($action, false);
        }

        // Actions
        var $data = $action.find("#"+ctxId+"_context .action");
        if ($data.length > 0) {
            $.each($data.text().split("::"), function(i, action) {
                if (action === "validate") {
                    $.publiquiz.action.validate($action);
                    $.publiquiz.question.clearAnimations();
                    if ($action.nbRetryQuiz < 0) {
                        $questions.each( function() {
                            var $quiz = $(this);
                            if ($quiz.data("engine") === "composite")
                                $action.removeClass("hidden");
                            $.publiquiz.question.composite._multipageGoTo($quiz, 0);
                        });
                    }
                } else if (action.match("^countdown_")) {
                    var countdown = action.split("_")[1];
                    $.publiquiz.action.currentCountdownValue = parseInt(countdown, 10);
                    $.publiquiz.action.initTimer($action, false);
                    if ($.publiquiz.action.currentCountdownValue === 0 && $action.scenario.onEndCountdown !== undefined) {
                        var prefix = $.publiquiz.defaults.prefix;
                        var $elem = $action.find("."+prefix+"Countdown");
                        if ($elem.length > 0) {
                            $elem.addClass(prefix+"EndCountdown");
                        }
                        var scenario = $action.scenario.onEndCountdown;
                        var acts = scenario[0];
                        if (acts !== undefined)
                            $.publiquiz.action.doActions($action, "onEndCountdown", acts);
                    }
                } else if (action === "userAnswer") {
                    $.publiquiz.action.userAnswer($action);
                } else if (action === "rightAnswer") {
                    $.publiquiz.action.rightAnswer($action);
                } else if (action === "verify") {
                    $.publiquiz.action.verify($action);
                } else if (action === "retry") {
                    $.publiquiz.action.retry($action);
                    if ($action.nbRetryQuiz >= 0) {
                        $questions.each( function() {
                            var $quiz = $(this);
                            if ($quiz.data("engine") === "composite") {
                                $quiz.find("."+$quiz.data("prefix")+"Element").each( function() {
                                    $.publiquiz.context.setQuizContext($.publiquiz.question, $(this));
                                });
                            }
                            $.publiquiz.context.setQuizContext($.publiquiz.question, $quiz);
                        });
                    }
                }
            });
        }

        // Set up anim
        $.publiquiz.defaults.multipageAnimation = multipageAnimation;
    },

    /**
     * Clear action and quiz context.
     *
     * @param {jQuery} $action - action element.
     */
    clearContext: function($action) {
        var pqContext = this;
        var $questions = $action.questions;
        var ttl = $action.data("context-ttl");

        // Actions
        var ctxId = $($questions.get(0)).data("quiz-id")+"_action";
        pqContext.removeItemContext(ctxId, ttl);
        $action.find("#"+ctxId+"_context").remove();

        // Questions
        _clear($questions);

        function _clear($elem){
            $elem.each(function() {
                var $quiz = $(this);
                var quzId = $quiz.data("quiz-id");
                var prefix = $quiz.data("prefix");
                var ttl = $quiz.data("context-ttl");

                pqContext.removeItemContext(quzId, ttl);
                $quiz.find("#"+quzId+"_context").remove();

                var $subElements = $quiz.find("."+prefix+"Element");
                if ($subElements.length > 0)
                    _clear($subElements);
            });
        }
    },

    /* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     *                          Quiz library function
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

    /**
     * Call when quiz modified.
     *
     * @param {jQuery} pqQuestion - object jquery pointing on publiquiz implementation.
     * @param {jQuery} $quiz - quiz element.
     */
    onQuizModified: function(pqQuestion, $quiz) {
        if ($.publiquiz.defaults.isLoadContext)
            return;

        var $action = $quiz.data("action");
        if ($action) {
            $.publiquiz.action.onModified($action);

            //
            if ($action.data("countdown") !== undefined)
                $.publiquiz.action.startCountdown($action);

            //
            if ($action.find("."+$.publiquiz.defaults.prefix+"Chrono").length > 0)
                $.publiquiz.action.startChrono($action);
        }

        //
        var ttl = $quiz.data("context-ttl");
        if (ttl === undefined || ttl < 0)
            return;

        var engine = $quiz.data("engine");
        var prefix = $quiz.data("prefix");
        var changes = pqQuestion.modified[engine]($quiz);

        var freeblanks = {};
        $quiz.find("."+prefix+"Choice").filter(":not([id])").each(function(idx, freeblank) {
            var $freeblank = $(freeblank);
            if ($freeblank.val().trim()) {
                freeblanks["fb_"+idx] = $freeblank.val();
            }
        });
        if (!$.isEmptyObject(freeblanks)) {
            changes.freeblanks = JSON.stringify(freeblanks);
        }

        this.writeQuizChange($quiz, changes);

        // If quiz is in composite, trigger event "subQuizChange"
        if ($quiz.hasClass(prefix+"Element")) {
            $quiz.trigger("subQuizChange");
        }
    },

    /**
     * Write quiz changes.
     *
     * @param {jQuery} $quiz - quiz element.
     * @param {Hash} changes - action values to write on page.
     */
    writeQuizChange: function($quiz, changes) {
        var ttl = $quiz.data("context-ttl");
        if (ttl === undefined || ttl < 0)
            return;

        changes.key = $quiz.data("context-key");
        var quzId = $quiz.data("quiz-id");
        var engine = $quiz.data("engine");
        var prefix = $quiz.data("prefix");
        var $action = $quiz.data("action");
        var nbRetryQuiz = -1;
        if ($action !== undefined)
            nbRetryQuiz = $action.nbRetryQuiz;

        // Add div id_context
        var $context = $quiz.find("#"+quzId+"_context");
        if ($context.length === 0) {
            $context = $("<div>")
                .attr("id", quzId+"_context")
                .addClass("hidden");

            var $elem = null;
            if (engine === "production")
                $elem = $quiz.find("."+prefix+"Production");
            else if (engine === "composite")
                $elem = $quiz.find("."+prefix+"Elements");
            else
                $elem = $quiz.find("#"+quzId+"_correct");
            $context.insertAfter($elem);
        }

        //
        $.each(changes, function(k, v) {
            if (nbRetryQuiz >= 0 && k === "data")
                k = "data_"+nbRetryQuiz;

            var $elem = $context.find("."+k);
            if ($elem.length === 0) {
                $elem = $("<div>").addClass(k);
                $context.append($elem);
            }
            v = String(v).replace(new RegExp(/’/g), "'");
            $elem.text(v);
        });

        //
        if (changes.date === undefined) {
            var $date = $context.find(".date");
            if ($date.length === 0) {
                $date = $("<div>").addClass("date");
                $context.append($date);
            }
            var dt = new Date();
            var day = dt.getDate();
            var month = dt.getMonth();
            var year = dt.getFullYear();
            month++;
            $date.text(year+"-"+("0"+month).slice(-2)+"-"+("0"+day).slice(-2));
        }

        // Save
        this.saveQuizContext($quiz);
    },

    /**
     * Save quiz changes.
     *
     * @param {jQuery} $quiz - quiz element.
     */
    saveQuizContext: function($quiz) {
        var ttl = $quiz.data("context-ttl");
        if (ttl === undefined || ttl < 0)
            return;

        var quzId = $quiz.data("quiz-id");
        var $context = $quiz.find("#"+quzId+"_context");
        var $data = $context.find(".data");
        if ($data.length > 0)
            $data.text($data.text().replace(new RegExp(/’/g), "'"));
        this.saveContext(quzId, ttl, $context);
    },

    /**
     * Start load quiz context.
     *
     * @param {jQuery} pqQuestion - object jquery pointing on publiquiz implementation.
     * @param {jQuery} $quiz - quiz element.
     */
    loadQuizContext: function(pqQuestion, $quiz) {
        var ttl = $quiz.data("context-ttl");
        if (ttl === undefined || ttl < 0)
            return;

        $.publiquiz.defaults.contextLoading += 1;
        var quzId = $quiz.data("quiz-id");

        // Get context
        $.publiquiz.context.loadContext(pqQuestion, $quiz, quzId, this.setDataQuizContext);
    },

    /**
     * Callback, finish retrieve data context, write context on page.
     *
     * @param {jQuery} pqQuestion - object jquery pointing on publiquiz implementation.
     * @param {jQuery} $quiz - quiz element.
     * @param {jQuery} objectJSON - data context.
     */
    setDataQuizContext: function(pqQuestion, $quiz, objectJSON) {
        var ttl = $quiz.data("context-ttl");
        if (objectJSON === null || !$.publiquiz.context.isContextExpired(ttl, objectJSON)) {
            $.publiquiz.defaults.contextLoading -= 1;
            return;
        }
        if (objectJSON.key !== $quiz.data("context-key")) {
            $.publiquiz.defaults.contextLoading -= 1;
            return;
        }
        $.publiquiz.context.writeQuizChange($quiz, objectJSON);
        if (objectJSON.freeblanks) {
            var prefix = $quiz.data("prefix");
            var freeblanks = JSON.parse(objectJSON.freeblanks);
            $quiz.find("."+prefix+"Choice").filter(":not([id])").each(function(idx, freeblank) {
                if (freeblanks["fb_"+idx]) {
                    var $freeblank = $(freeblank);
                    $freeblank.val(freeblanks["fb_"+idx]);
                }
            });
        }
        $.publiquiz.context.setQuizContext(pqQuestion, $quiz);
        $.publiquiz.defaults.contextLoading -= 1;
    },

    /**
     * Set quiz context.
     *
     * @param {jQuery} pqQuestion - object jquery pointing on publiquiz implementation.
     * @param {jQuery} $quiz - quiz element.
     */
    setQuizContext: function(pqQuestion, $quiz) {
        var engine = $quiz.data("engine");
        var $action = $quiz.data("action");
        var nbRetryQuiz = -1;
        if ($action !== undefined)
            nbRetryQuiz = $action.nbRetryQuiz;

        var $ctx = $quiz.find("#"+$quiz.data("quiz-id")+"_context");
        var $ctxEngine = $ctx.find(".engine");
        if ($ctxEngine.length === 0 || $ctxEngine.text() !== engine)
            return;
        var dataClass = ".data";
        if (nbRetryQuiz >= 0)
            dataClass = ".data_"+nbRetryQuiz;
        var $data = $ctx.find(dataClass);
        if ($data.length === 0)
            return;
        $.publiquiz.defaults.isLoadContext = true;
        var multipageAnimation = $.publiquiz.defaults.multipageAnimation;
        $.publiquiz.defaults.multipageAnimation = false;
        pqQuestion.loadContext[engine]($quiz, dataClass);
        $.publiquiz.defaults.multipageAnimation = multipageAnimation;
        $.publiquiz.defaults.isLoadContext = false;
        $.publiquiz.action.onModified($action);
    },


    /* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     *                          Helpers modify quiz context
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

    /**
     * Load quiz context for type "compare".
     */
    modifyQuizCmpContext: function($quiz) {
        var changes = [];
        var engine = $quiz.data("engine");
        var prefix = $quiz.data("prefix");

        $quiz.find("."+prefix+"Drop").each( function() {
            var $drop = $(this);
            var dropId = $drop.attr("id");
            dropId = dropId.substring(dropId.length - 3, dropId.length);
            var $item = $drop.find("."+prefix+"Item");
            if ($item.length > 0)
                changes.push(dropId+$item.data("item-value"));
        });

        return {"data": changes.join("::"), "engine": engine};
    },

    /* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     *                          Helpers load quiz context
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

    /**
     * Load quiz context for type "compare".
     *
     * @param {jQuery} $quiz - quiz element.
     */
    loadQuizCmpContext: function($quiz, dataClass) {
        var quzId = $quiz.data("quiz-id");
        var engine = $quiz.data("engine");
        var $context = $quiz.find("#"+quzId+"_context");
        var $data = $context.find(dataClass);

        var values = $.publiquiz.question.correction($data);
        var prefix = $quiz.data("prefix");
        var options = $quiz.data("engine-options") || "";
        var isMultiple = (options.search("multiple") > -1);
        var isCounter = (options.search("counter") > -1);
        var $items = $quiz.find("#"+quzId+"_items");
        var countAvailable = false;
        $.each(values, function(k, v) {
            var $drop = $quiz.find("#"+quzId+"_"+k);
            var $item = $items.find("."+prefix+"Item").filter("[data-item-value=\""+v+"\"]");
            if ($item.length === 0)
                return true;
            if ($item.length > 1)
                $item = $($item.get(0));
            $drop.removeClass(prefix+"Dots");
            $drop.text("");
            if ($drop.hasClass(prefix+"Dropzone"))
                $drop.removeClass(prefix+"Dropzone-visible");
            if (isCounter)
                countAvailable = $.publiquiz.question.counterItemAvailable($quiz, $item);
            if (isMultiple || countAvailable) {
                var count = $quiz.find("."+prefix+"Item").length;
                $item = $item.clone();
                $item.attr("id", quzId+"_item"+$.publiquiz.question.formatNumber(count += 100, 3));
                $.publiquiz.question.setDraggableItem($quiz, $item, "");
                $.publiquiz.question.setAudioPlayable($quiz, $item);
            }
            $item.appendTo($drop).addClass(prefix+"ItemDropped");

            // Specific par type d'engine
            if (engine == "blanks-media" &&
                    $item.children("img").length > 0 &&
                    $item.text().trim() === "") {
                $item.addClass(prefix+"ItemImageDropped");
            } else if (engine == "sort" && $item.children("img").length > 0) {
                $item.addClass(prefix+"InlineItemImageDropped");
            } else if (engine == "matching" && $item.children("img").length > 0) {
                $item.addClass(prefix+"BlockItemImageDropped");
            }

            return true;
        });
    },

    /**
     * Load quiz context for type "choices".
     *
     * @param {jQuery} $quiz - quiz element.
     * @param {String} dataClass - class of data context element.
     */
    loadQuizChoicesContext: function($quiz, dataClass) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var $context = $quiz.find("#"+quzId+"_context");
        var options = $quiz.data("engine-options") || "";
        var isCheckRadio = (options.search("radio") > -1 );
        var engine = $quiz.data("engine");
        var $data = $context.find(dataClass);

        var values = $.publiquiz.question.correction($data);
        if (isCheckRadio && engine != "pointing") {
            $.each(values, function(k, v) {
                var $choice = $quiz.find("."+prefix+"Choice")
                    .filter("[data-group=\""+k+"\"]")
                    .filter("[data-name=\""+v+"\"]");
                $choice.addClass("selected");
                var $input = $choice.find("input");
                if ($input)
                    $input.prop("checked", true);
            });
        } else {
            $.each(values, function(k, v) {
                var $elem = $quiz.find("#"+quzId+"_"+k);
                $elem.addClass("selected");
                var $input = $elem.find("input");
                if ($input)
                    $input.prop("checked", true);
            });
        }
    },

    /* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     *                          Helpers library function
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

    /**
     * Verify date of context is validate.
     *
     * @param {Int} ttl - context life duration.
     * @param {Hash} changes - values to write on page.
     * @return {Boolean}
     */
    isContextExpired: function(ttl, changes) {
        var date = changes.date;
        if (ttl > 0 && date !== undefined) {
            var days = (ttl / 3600) / 24;
            var dt = new Date(date);
            dt.setHours(0,0,0,0);
            var expire = new Date(new Date() - days);
            expire.setHours(0,0,0,0);
            if (expire > dt)
                return false;
        }
        return true;
    },

    /**
     * Save score in context.
     *
     * @param {Hash} scores - values to write on page.
     */
    saveScore: function(quzId, scores) {
    },

    /**
     * Save context.
     *
     * @param {String} key - Item key in localStorage, sessionStorage and cookie.
     * @param {Int} ttl - context life duration.
     * @param {jQuery} $context - context element.
     */
    saveContext: function(key, ttl, $context) {
        // Data
        var res = {};
        $context.children().each( function() {
            var $elem = $(this);
            var className = $elem[0].className;
            res[className] = $elem.text();
        });

        // Save
        if (this.isLocalStorageEnable()) {
            if (ttl > 0)
                localStorage.setItem(key, JSON.stringify(res));
            else
                sessionStorage.setItem(key, JSON.stringify(res));
        } else {
            this.writeCookie(key, JSON.stringify(res), null);
        }
    },

    /**
     * Load context.
     *
     * @param {String} key - Item key in localStorage, sessionStorage and cookie.
     * @param {Int} ttl - context life duration.
     * @param {Function} callBack - function.
     */
    loadContext: function(pqQuestion, $obj, key, callBack) {
        var ttl = $obj.data("context-ttl");
        var res = null;
        if (this.isLocalStorageEnable()) {
            if (ttl > 0)
                res = localStorage.getItem(key);
            else
                res = sessionStorage.getItem(key);
        } else {
            res = this.readCookie(key);
        }
        if (res === undefined || res === null) {
            if ($.publiquiz.defaults.contextLoading > 0)
                $.publiquiz.defaults.contextLoading -= 1;
            return;
        }

        if (pqQuestion === null)
            callBack($obj, JSON.parse(res));
        else
            callBack(pqQuestion, $obj, JSON.parse(res));
    },

    /**
     * Remove item context.
     *
     * @param {String} key - Item key in localStorage, sessionStorage and cookie.
     * @param {number} ttl - Time to live of context.
     */
    removeItemContext: function(key, ttl) {
        if (this.isLocalStorageEnable()) {
            if (ttl > 0)
                localStorage.removeItem(key);
            else
                sessionStorage.removeItem(key);
        } else {
            var day = 3600 * 24; // one day
            var date = new Date(new Date() - day);
            this.writeCookie(key, null, date);
        }
    },

    /**
     * Define if we have localStorage.
     */
    isLocalStorageEnable: function() {
        try {
            if (typeof localStorage !== "undefined" && localStorage !== null)
                return true;
        } catch (DOMException) {
            return false;
        }
        return false;
    },

    /**
     * Write a cookie
     *
     * @param {String} name: Data name.
     * @param {String} value: Data value.
     * @param {Date} dt: Date value.
     */
    writeCookie: function(name, value, dt) {
        var date = dt;
        if (date === null) {
            date = new Date();
            date.setTime(date.getTime()+(365*24*3600));
        }
        var expires = "; expires="+date.toGMTString();
        document.cookie = name+"="+value+expires+"; path=/";
    },

    /**
     * Read a cookie
     *
     * @param {String} name: Data name.
     * @return String
     */
    readCookie: function(name) {
        var nameEQ = name + "=";
        var ca = document.cookie.split(';');
        for(var i=0;i < ca.length;i++) {
            var c = ca[i];
            while (c.charAt(0)==' ') c = c.substring(1,c.length);
            if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length,c.length);
        }
        return null;
    }
};

}(jQuery));


/******************************************************************************
 ******************************************************************************
 *
 *                                  Plugins
 *
 ******************************************************************************
 *****************************************************************************/


/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ shuffle ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

(function ($) {

/**
 * To shuffle all <li> elements within each '.member' <div>:
 * $(".member").shuffle("li");
 *
 * To shuffle all children of each <ul>:
 * $("ul").shuffle();
*/
$.fn.shuffle = function(selector) {
    var $elems = selector ? $(this).find(selector) : $(this).children(),
        $parents = $elems.parent();

    $parents.each(function(){
        $(this).children(selector).sort(function() {
            return Math.round(Math.random()) - 0.5;
        }).detach().appendTo(this);
    });

    return this;
};

/**
 * To shuffle an array
 */
$.shuffle = function(array) {
    for (var i = array.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var temp = array[i];
        array[i] = array[j];
        array[j] = temp;
    }
    return array;
};

})(jQuery);

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ setOnCenterScreen ~~~~~~~~~~~~~~~~~~~~~~~~~~ */

(function ($) {

$.fn.setOnCenterScreen = function() {
    var $this = $(this);
    var posX, posY;
    var relativeTo = $.publiquiz ? $.publiquiz.defaults.centerRelativeTo : "screen";
    var $relativeTo = $(relativeTo);
    if (relativeTo !== "screen" && $relativeTo.length > 0) {
        var relToPosition = $relativeTo.offset();
        posX = $relativeTo.width() / 2 + relToPosition.left;
        posY = $relativeTo.height() / 2 + relToPosition.top;
    } else {
        var $win = $(window);
        posX = $win.width() / 2;
        posY = ($win.height() / 2) + $win.scrollTop();
    }

    posX = posX - $this.width() / 2;
    posY = posY - $this.height() / 2;

    $this.offset({
        left: posX,
        top: posY
    });

    return this;
};

})(jQuery);

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ animateMoveElement ~~~~~~~~~~~~~~~~~~~~~~~~~ */

(function ($) {

/**
 * Animate moving element to new parent in page.
 *
 * @param {Object} $newParent - Destination.
 * @return {Object} The element, to enable chaining.
 */
$.fn.animateMoveElement = function($newParent) {
    var $item = this;
    var $clone = $item.clone().insertAfter($item);
    var $mainClass = $item.closest("."+$.publiquiz.defaults.mainClass);
    $item.appendTo($mainClass);
    var cloneOffset = $clone.offset();
    $item
        .css('position', 'absolute')
        .css('left', cloneOffset.left)
        .css('top', cloneOffset.top)
        .css('zIndex', 1000);
    $clone.appendTo($newParent);
    cloneOffset = $clone.offset();
    $clone.hide();
    $item.addClass("animated");
    $item.animate({
        'top': cloneOffset.top,
        'left': cloneOffset.left
    }, 'slow', function(){
        $clone.remove();
        $item.removeClass("animated");
        $item.appendTo($newParent);
        $item
            .css('position', '')
            .css('left', '')
            .css('top', '')
            .css('zIndex', '');
    });

    return $item;
};

}(jQuery));

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ getTransformObj ~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

(function($) {

/**
 * Convert a transform matrix into an object.
 *
 * @return {Object} Transform object.
 */
$.fn.getTransformObj = function() {
    var obj = {
        rotate: 0,
        scale: {x: 1, y: 1},
        translate: {x: 0, y: 0}
    };
    var transform = this.css("transform");
    if (transform !== 'none') {
        var matrix = transform.match(/([-+]?[\d\.]+)/g);

        obj.translate.x = matrix[4];
        obj.translate.y = matrix[5];

        obj.rotate = Math.round(Math.atan2(parseFloat(matrix[1]), parseFloat(matrix[0])) * (180/Math.PI));

        obj.scale.x = Math.sqrt(matrix[0]*matrix[0] + matrix[1]*matrix[1]);
        obj.scale.y = Math.sqrt(matrix[2]*matrix[2] + matrix[3]*matrix[3]);
    }

    obj.toString = function() {
        return "transform: translate("+obj.translate.x+"px,"+obj.translate.y+"px) rotate("+obj.rotate+"deg) scale("+obj.scale.x+","+obj.scale.y+");";
    };

    return obj;
};

}(jQuery));
