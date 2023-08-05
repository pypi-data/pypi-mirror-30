/**
 * @projectDescription publiquiz_basics.js
 * Plugin jQuery for quiz choices.
 *
 * @author Tien Haï NGUYEN
 * @version 0.5
 *
 * 0.5 :
 * Add new part in publiquiz "$publiquiz.context", save/load context for a quiz and action
 *    - quiz and action : add 2 new data "context-key" used for validate context and
 *      "context-ttl" for context life duration , none or -1 no context, 0
 *      for context session and more for context duration.
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
/*global setTimeout: true */
/*global clearTimeout: true */
/*global setInterval: true */
/*global clearInterval: true */


/*****************************************************************************
 *
 *                              Plugin publiquiz
 *
 ****************************************************************************/

"use strict";

(function ($) {

$.fn.publiquiz = function(options, args) {

    var $this = this;

    // Options
    var opts = handleOptions(options, args);
    if (opts === false)
        return $this;
    $.publiquiz.defaults.prefix = opts.prefix;
    if (opts.baseScore > -1)
        $.publiquiz.defaults.baseScore = opts.baseScore;

    /* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     *                              Library
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

    /**
     * Process the args that were passed to the plugin fn
     *
     * @param {Object} options, object can be String or {}.
     */
    function handleOptions(options, args) {
        if (options && options.constructor == String) {

            $.publiquiz.question.clearVerify();

            $this.each( function() {
                var $quiz = $(this);
                if (!$quiz.attr("data-engine"))
                    return;
                var engine = $quiz.data("engine");
                var prefix = $quiz.data("prefix");

                switch (options) {
                    case ("validate"):
                        $.publiquiz.question.disable[engine]($quiz);
                        $.publiquiz.question.textAnswer[engine]($quiz);
                        $.publiquiz.question.insertUserAnswers[engine]($quiz);
                        break;
                    case ("configure"):
                        $.publiquiz.question.configure[engine]($quiz);
                        break;
                    case ("enable"):
                        $.publiquiz.question.enable[engine]($quiz);
                        $.publiquiz.question.hideTextAnswer($quiz);
                        break;
                    case ("quizAnswer"):
                        $.publiquiz.question.quizAnswer[engine]($quiz, args);
                        break;
                    case ("loadContext"):
                        //
                        if (engine === "composite") {
                            $quiz.find("."+prefix+"Element").each( function() {
                                var $element = $(this);
                                $.publiquiz.context.loadQuizContext($.publiquiz.question, $element);
                            });
                        }
                        $.publiquiz.context.loadQuizContext($.publiquiz.question, $quiz);

                        //
                        var $action = $quiz.data("action");
                        if ($.publiquiz.defaults.contextLoading === 0) {
                            $.publiquiz.context.loadActionContext($action);
                        } else {
                            var max = 5000;
                            var step = 100;
                            var count = 0;
                            var timer = setInterval(function() {
                                if ($.publiquiz.defaults.contextLoading === 0) {
                                    $.publiquiz.context.loadActionContext($action);
                                    clearInterval(timer);
                                }
                                if (count > max)
                                    clearInterval(timer);
                                count += step;
                            }, step);
                        }
                        break;
                    case ("disable"):
                    case ("retry"):
                    case ("textAnswer"):
                    case ("insertUserAnswers"):
                    case ("verifyUserAnswer"):
                    case ("verifyRightAnswer"):
                    case ("verifyFullAnswer"):
                        $.publiquiz.question[options][engine]($quiz);
                        break;
                    default:
                        $.publiquiz.question[options]($quiz, args);
                }
            });
            return false;
        }

        return $.extend({}, $.publiquiz.defaults, options || {});
    }

    /**
     * Quiz process, set quiz enable.
     *
     * @param {Object} jquery Object quiz.
     */
    function quizProcess($quiz) {
        var engine = $quiz.data("engine");

        // Verify quiz is valide
        if (!$.publiquiz.question.enable[engine])
            return;

        activateQuiz($quiz);
    }

    /**
     * Action process, set action on quiz.
     *
     * @param {Object} $action, jquery Object action.
     */
    function actionProcess($action) {
        var prefix = opts.prefix;
        var $questions = opts.questions;
        var $scenario = opts.scenario;

        if (!opts.questions || !opts.scenario)
            return;

        // Configure timer
        $.publiquiz.action.initTimer($action, true);

        // Retrieve nb retry for quiz
        var nbRetryQuiz = -1;
        var $nbRetryQuizElem = $action.find("."+prefix+"NbRetry");
        if ($nbRetryQuizElem.length > 0)
            nbRetryQuiz = parseInt($nbRetryQuizElem.text(), 10);

        $questions.data("action", $action);
        if ($questions.data("engine") == "composite")
            $questions.find("."+prefix+"Element").data("action", $action);

        $action.questions = $questions;
        $action.scenario = opts.scenario;
        $action.nbRetryQuiz = nbRetryQuiz;
        $action.idxValidate = 0;
        $action.idxVerify = 0;
        $action.idxRetry = 0;
        $action.idxUserAnswer = 0;
        $action.idxRightAnswer = 0;

        // Set button events
        $action.find("."+prefix+"Button").click( function(ev) {
            $.publiquiz.question.loadAudio();
            ev.preventDefault();
            var $btn = $(this);
            if ($btn.hasClass(prefix+"Submit")) {
                if ($scenario.validate) {
                    $.publiquiz.action.validate($action);
                    $.publiquiz.context.onActionModified($action, "validate");
                }
            } else if ($btn.hasClass(prefix+"UserAnswer")) {
                if ($scenario.userAnswer) {
                    $.publiquiz.action.userAnswer($action);
                    $.publiquiz.context.onActionModified($action, "userAnswer");
                }
            } else if ($btn.hasClass(prefix+"RightAnswer")) {
                if ($scenario.rightAnswer) {
                    $.publiquiz.action.rightAnswer($action);
                    $.publiquiz.context.onActionModified($action, "rightAnswer");
                }
            } else if ($btn.hasClass(prefix+"VerifyUserAnswer")) {
                if ($scenario.verify) {
                    $.publiquiz.action.verify($action);
                    $.publiquiz.context.onActionModified($action, "verify");
                }
            } else if ($btn.hasClass(prefix+"Retry")) {
                if ($scenario.retry) {
                    $.publiquiz.action.retry($action);
                    $.publiquiz.context.onActionModified($action, "retry");
                }
            } else if ($btn.hasClass(prefix+"Redo")) {
                if ($scenario.redo)
                    $.publiquiz.action.redo($action);
            }
        });

        //
        $questions.each( function() {
            var $quiz = $(this);
            var engine = $quiz.data("engine");
            if (engine === "composite") {
                $quiz.find("."+prefix+"Element").each( function() {
                    var $element = $(this);
                    $.publiquiz.context.loadQuizContext($.publiquiz.question, $element);
                    $.publiquiz.question.enableSlotButtons($element);
                });
            }
            $.publiquiz.context.loadQuizContext($.publiquiz.question, $quiz);
            $.publiquiz.question.enableSlotButtons($quiz);
        });

        if ($.publiquiz.defaults.contextLoading === 0) {
            $.publiquiz.context.loadActionContext($action);
        } else {
            var max = 5000;
            var step = 100;
            var count = 0;
            var timer = setInterval(function() {
                if ($.publiquiz.defaults.contextLoading === 0) {
                    $.publiquiz.context.loadActionContext($action);
                    clearInterval(timer);
                }
                if (count > max)
                    clearInterval(timer);
                count += step;
            }, step);
        }
    }

    /**
     * Activate quiz.
     *
     * @param {Object} jquery Object quiz.
     */
    function activateQuiz($quiz) {
        var engine = $quiz.data("engine");
        var quzId = $quiz.data("quiz-id");
        var prefix = opts.prefix;
        $quiz.data("prefix", opts.prefix);
        $quiz.data("verify-duration", opts.verifyDuration);

        // Configure quiz
        $.publiquiz.question.configure[engine]($quiz);

        // Set enable quiz
        $.publiquiz.question.enable[engine]($quiz);

        // Register score function
        $.publiquiz.question.registerScoreFunc(
                quzId,
                $quiz,
                $.publiquiz.question.computeScore[engine]
            );

        // Set event on popups
        $.publiquiz.question.enablePopupEvents($quiz);

        // Set event on freeblank
        var freeblanks = $quiz.find("."+prefix+"Choice").filter(":not([id])");
        freeblanks.on("input", function() {
            $.publiquiz.context.onQuizModified($.publiquiz.question, $quiz);
        });

        // Message mode dialog
        $("."+prefix+"Message").click( function(ev) {
            var $this = $(this);
            $this.closest(".fadeBackground").removeClass("fadeBackground");
            $this.addClass("hidden");
            $this.find("audio").each(function() {
                $(this).get(0).pause();
            });
        });
        $("."+prefix+"CongratulateMessages").on("click", function() {
            $(this).removeClass("fadeBackground");
            $(this).find("."+prefix+"Message").addClass("hidden")
                .find("audio").each(function() {
                    $(this).get(0).pause();
                });
        });

        $.publiquiz.question.setAudioBlockInteraction($quiz);
    }

    /* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     *                          Plug-in main function
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

    // Questions
    $this.filter("[data-engine]").each( function() {
        quizProcess($(this));
    });

    // Actions
    $this.filter(":not([data-engine])").each( function() {
        actionProcess($(this));
    });

    return $this;
};

}(jQuery));


/*****************************************************************************
 *
 *                                  Choices
 *
 ****************************************************************************/

(function ($) {

$.publiquiz.question.choices = {

    /**
     * Configure quiz.
     */
    choicesConfigure: function($quiz) {
        var prefix = $quiz.data("prefix");
        var $engine = $quiz.find("."+prefix+"Engine");
        if ($engine.data("original-state") === undefined)
            $engine.data("original-state", $engine.html());
    },

    /**
     * Set event click on Choice.
     *
     * @param {Object} jquery Object quiz.
     */
    choicesEnable: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Choice input").removeAttr("disabled");
        $quiz.find("."+prefix+"Choice").click( function(ev) {
            var $target = $(this);
            if(ev.target.nodeName.toLowerCase() == "audio")
                return;
            while (!$target.hasClass(prefix+"Choice"))
                $target = $target.parentNode;
            $.publiquiz.question.choices._onChoice($quiz, $target);
            $.publiquiz.context.onQuizModified($.publiquiz.question, $quiz);
        });
    },

    /**
     * Remove events listener on quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    choicesDisable: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Choice").unbind("click");
        $quiz.find("."+prefix+"Choice input").attr("disabled", "disabled");
    },

    /**
     * Redo quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    choicesRedo: function($quiz) {
        var prefix = $quiz.data("prefix");
        var $engine = $quiz.find("."+prefix+"Engine");
        if ($engine.data("original-state"))
            $engine.html($engine.data("original-state"));
    },

    /**
     * Display help of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    choicesHelp: function($quiz) {
        $.publiquiz.question.displayHelp($quiz);
    },

    /**
     * Retry quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    choicesRetry: function($quiz) {
        $quiz.removeData("quiz-result");
        $.publiquiz.question.retryChoices($quiz, "Choice");
    },

    /**
     * Compute score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Dictionnary}.
     */
    choicesComputeScore: function($quiz) {
        var noMark = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("nomark") > -1 )
            noMark = true;

        var result = {};
        if (noMark) {
            result.score = 0;
            result.total = 0;
            return result;
        }

        result = $quiz.data("quiz-result");
        if (result !== undefined)
            return result;

        var engine = $quiz.data("engine");
        var isCheckRadio = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("radio") > -1 )
            isCheckRadio = true;

        if (engine == "choices-radio") {
            result = $.publiquiz.question.scoreForQuizChoicesRadio($quiz);
        } else {
            if (isCheckRadio)
                result = $.publiquiz.question.choices._scoreForQuizChoicesCheckRadio($quiz);
            else
                result = $.publiquiz.question.scoreForQuizChoicesCheck($quiz, "Choice");
        }
        $quiz.data("quiz-result", result);
        return result;
    },

    /**
     * Display score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    choicesScore: function($quiz) {
    },

    /**
     * Display quiz text answer.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    choicesTextAnswer: function($quiz) {
        $.publiquiz.question.displayTextAnswer($quiz);
    },

    /**
     * Insert user answers in html
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    choicesInsertUserAnswers: function($quiz) {
        var answer = [];
        var quzId = $quiz.data("quiz-id");
        var isCheckRadio = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("radio") > -1 )
            isCheckRadio = true;

        if (isCheckRadio)
            answer = $.publiquiz.question.choices._userAnswersQuizChoicesCheckRadio($quiz);
        else
            answer = $.publiquiz.question.userAnswersQuizChoices($quiz, "Choice");

        $.publiquiz.question.writeUserAnswers($quiz, quzId, answer.join("::"));
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    choicesQuizAnswer: function($quiz, mode) {
        var isCheckRadio = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("radio") > -1 )
            isCheckRadio = true;

        if (isCheckRadio)
            $.publiquiz.question.choices._displayQuizChoicesAnswerCheckRadio($quiz, mode);
        else
            $.publiquiz.question.displayQuizChoicesAnswer($quiz, "Choice", mode);
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    choicesVerifyUserAnswer: function($quiz) {
        $.publiquiz.question.verifyQuizChoicesAnswer($quiz, "user");
    },

    /**
     * Verify only right answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    choicesVerifyRightAnswer: function($quiz) {
        $.publiquiz.question.verifyQuizChoicesAnswer($quiz, "right");
    },

    /**
     * Verify full answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    choicesVerifyFullAnswer: function($quiz) {
        $.publiquiz.question.verifyQuizChoicesAnswer($quiz, "full");
    },

    /**
     * Choices modified
     */
    choicesModified: function($quiz) {
        var engine = $quiz.data("engine");
        var changes = $.publiquiz.question.userAnswersQuizChoices($quiz, "Choice");
        return {"data": changes.join("::"), "engine": engine};
    },

    /**
     * Reload context
     */
    choicesLoadContext: function($quiz, dataClass) {
        $.publiquiz.context.loadQuizChoicesContext($quiz, dataClass);
    },


    /**********************************************************************
     *                          Private Library
    **********************************************************************/

    /**
     * This function call when click on choice.
     *
     * @params {Object} $quiz: object jquery publiquiz.
     * @param {Object} $elem: object jquery receive click.
     */
    _onChoice: function($quiz, $elem) {
        $.publiquiz.question.clearVerify();

        var prefix = $quiz.data("prefix");
        var engine = $quiz.data("engine");
        var quzId = $quiz.data("quiz-id");
        var options = $quiz.data("engine-options") || "";
        var $input = $elem.find("input");
        var $engine = $quiz.find("#"+quzId+"_engine");
        if (engine == "choices-radio" || options.search("radio") > -1) {
            if ($elem.hasClass("selected"))
                return;

            var selected = $engine.find("."+prefix+"Choice.selected");
            if (options.search("radio") > -1) {
                var group = $elem.data("group");
                selected = selected.filter('[data-group="'+group+'"]');
            }
            selected.removeClass("selected");

            $elem.addClass("selected");
            if ($input)
                $input.prop("checked", true);
        } else {
            $elem.toggleClass("selected");
            if ($input)
                $input.prop("checked", $elem.hasClass("selected"));
        }
    },

    /**
     * Score for quiz engine choice-check with option "radio".
     *
     * @params {Object} $quiz : Object jquery quiz.
     * @return {Dictionnary}.
     */
    _scoreForQuizChoicesCheckRadio: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var $engine = $quiz.find("#"+quzId+"_engine");
        var res = $.publiquiz.question.correction(
                $quiz.find("#"+quzId+"_correct"));

        // Get group
        var choices = [];
        $quiz.find("."+prefix+"Choice").each( function() {
            var group = $(this).data("group");
            if ($.inArray(group, choices) < 0 )
                choices.push(group);
        });

        // Compute score
        var total = choices.length;
        var score = 0;
        $.each(choices, function() {
            var group = this;
            if (res[group] && $engine.find("."+prefix+"Choice")
                                .filter("[data-group=\""+group+"\"]")
                                .filter("[data-name=\"true\"]")
                                .hasClass("selected"))
                score += 1;
            else if (!res[group] && $engine.find("."+prefix+"Choice")
                                .filter("[data-group=\""+group+"\"]")
                                .filter("[data-name=\"false\"]")
                                .hasClass("selected"))
                score += 1;
        });

        var result = {};
        result.score = score;
        result.total = total;
        return result;
    },

    /**
     * User answers for quiz choices-check with option "radio"
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @return {Array}
     */
    _userAnswersQuizChoicesCheckRadio: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var answer = [];

        $quiz.find("."+prefix+"Choice.selected").each( function() {
            var $item = $(this);
            var name = $item.data("name");
            var group = $item.data("group");
            answer.push(group+name);
        });
        return answer;
    },

    /**
     * Display right/user answer for quiz choices-check with option "radio".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : mode "correct" or "user".
     */
    _displayQuizChoicesAnswerCheckRadio: function($quiz, mode) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        // Reset quiz
        $quiz.find("."+prefix+"Choice input").prop("checked", false);
        $quiz.find("."+prefix+"Choice").removeClass(
                "selected answerOk answerKo");

        // Get group
        var choices = [];
        $quiz.find("."+prefix+"Choice").each( function() {
            var group = $(this).data("group");
            if ($.inArray(group, choices) < 0 )
                choices.push(group);
        });

        // Display pquizChoice selected
        var $engine = $quiz.find("#"+quzId+"_engine");
        var answers = $.publiquiz.question.correction(
                $quiz.find("#"+quzId+mode));
        var userAnswers = null;
        if(mode == "_correct")
            userAnswers = $.publiquiz.question.correction(
                    $quiz.find("#"+quzId+"_user"));

        $.each(choices, function() {
            var group = this;
            var $choice = null;
            if(mode == "_correct") {
                if (answers[group])
                    $choice = $engine.find("."+prefix+"Choice")
                        .filter("[data-group=\""+group+"\"]")
                        .filter("[data-name=\"true\"]");
                else
                    $choice = $engine.find("."+prefix+"Choice")
                        .filter("[data-group=\""+group+"\"]")
                        .filter("[data-name=\"false\"]");
            } else {
                if (answers[group])
                    $choice = $engine.find("."+prefix+"Choice")
                        .filter("[data-group=\""+group+"\"]")
                        .filter("[data-name=\""+answers[group]+"\"]");
            }

            if ($choice) {
                $choice.addClass("selected");
                var $input = $choice.find("input");
                if ($input.length > 0)
                    $input.prop("checked", true);
            }
        });
    }
};

// Register function
$.publiquiz.question.register("choices-radio", {
        configure: $.publiquiz.question.choices.choicesConfigure,
        enable: $.publiquiz.question.choices.choicesEnable,
        disable: $.publiquiz.question.choices.choicesDisable,
        redo: $.publiquiz.question.choices.choicesRedo,
        help: $.publiquiz.question.choices.choicesHelp,
        retry: $.publiquiz.question.choices.choicesRetry,
        textAnswer: $.publiquiz.question.choices.choicesTextAnswer,
        insertUserAnswers: $.publiquiz.question.choices.choicesInsertUserAnswers,
        quizAnswer: $.publiquiz.question.choices.choicesQuizAnswer,
        verifyUserAnswer: $.publiquiz.question.choices.choicesVerifyUserAnswer,
        verifyRightAnswer: $.publiquiz.question.choices.choicesVerifyRightAnswer,
        verifyFullAnswer: $.publiquiz.question.choices.choicesVerifyFullAnswer,
        computeScore: $.publiquiz.question.choices.choicesComputeScore,
        quizScore: $.publiquiz.question.choices.choicesScore,
        modified: $.publiquiz.question.choices.choicesModified,
        loadContext: $.publiquiz.question.choices.choicesLoadContext
    });

$.publiquiz.question.register("choices-check", {
        configure: $.publiquiz.question.choices.choicesConfigure,
        enable: $.publiquiz.question.choices.choicesEnable,
        disable: $.publiquiz.question.choices.choicesDisable,
        redo: $.publiquiz.question.choices.choicesRedo,
        help: $.publiquiz.question.choices.choicesHelp,
        retry: $.publiquiz.question.choices.choicesRetry,
        textAnswer: $.publiquiz.question.choices.choicesTextAnswer,
        insertUserAnswers: $.publiquiz.question.choices.choicesInsertUserAnswers,
        quizAnswer: $.publiquiz.question.choices.choicesQuizAnswer,
        verifyUserAnswer: $.publiquiz.question.choices.choicesVerifyUserAnswer,
        verifyRightAnswer: $.publiquiz.question.choices.choicesVerifyRightAnswer,
        verifyFullAnswer: $.publiquiz.question.choices.choicesVerifyFullAnswer,
        computeScore: $.publiquiz.question.choices.choicesComputeScore,
        quizScore: $.publiquiz.question.choices.choicesScore,
        modified: $.publiquiz.question.choices.choicesModified,
        loadContext: $.publiquiz.question.choices.choicesLoadContext
    });

}(jQuery));


/******************************************************************************
 *
 *                                  Blanks
 *
******************************************************************************/

(function ($) {

$.publiquiz.question.blanks = {

    /**
     * Configure quiz.
     */
    blanksConfigure: function($quiz) {
        var prefix = $quiz.data("prefix");
        var $engine = $quiz.find("."+prefix+"Engine");
        if ($engine.data("original-state") === undefined)
            $engine.data("original-state", $engine.html());

        var quzId = $quiz.data("quiz-id");
        var engine = $quiz.data("engine");
        var options = $quiz.data("engine-options") || "";
        var noShuffle = (options.search("no-shuffle") > -1);
        var comboBox = (options.search("combobox") > -1);
        var isMultiple = (options.search("multiple") > -1);

        if (engine == "blanks-media" && !noShuffle) {
            $.publiquiz.question.shuffleItems($quiz.find("."+prefix+"Items"));
        } else if (engine == "blanks-fill" && !comboBox) {
            $.publiquiz.question.blanks._configureBlanksFill($quiz);
        } else if (engine == "blanks-select" && !noShuffle && !comboBox) {
            var $dropzones = $quiz.find("."+prefix+"Drop");
            var res = $.publiquiz.question.correction($quiz.find("#"+quzId+"_correct"));
            var i = 0, answer = true;
            while(answer && i < 20) {
                answer = $.publiquiz.question.shuffleAndControlItems($quiz, $dropzones, res);
                i++;
            }
        } else if (comboBox) {
            var $box = $quiz.find("."+prefix+"SelectItem");
            if (!noShuffle)
                $box.shuffle();
            $box.each( function() {
                var $combo = $(this);
                $combo.children('option[value=""]').detach().prependTo($combo);
                $combo.val("").prop("selected", true);

                if (isMultiple) {
                    var used = [];
                    $combo.children().each( function(i, child) {
                        var $child = $(child);
                        if ($.inArray($child.val(), used) >= 0)
                            $child.hide();
                        else
                            used.push($child.val());
                    });
                }
            });
        }
    },

    /**
     * Set event click on Choice.
     *
     * @param {Object} jquery Object quiz.
     */
    blanksEnable: function($quiz) {
        var pqQuestion = $.publiquiz.question;
        var prefix = $quiz.data("prefix");
        var options = $quiz.data("engine-options") || "";

        // Event change on choice
        var $choices = $quiz.find("."+prefix+"Choice");
        $choices.each( function() {
            var $choice = $(this);
            $choice.prop("disabled", false);
            $choice.removeClass("disabled");
        }).on("focus", function(ev) {
            pqQuestion.clearVerify();
        });

        if (options.search("auto-tab") > -1) {
            $choices.on({
                keydown: function(e) {
                    var $input = $(this);
                    var index = $choices.index($input);
                    if (e.keyCode == 8) { // Backspace
                        if ($input.val() === "") {
                            var $choice = $choices.eq(index-1);
                            $choice.focus();
                            $choice.val("");
                        }
                    }
                },
                input: function(e) {
                    var $input = $(this);
                    var index = $choices.index($input);
                    var val = $input.val();
                    $input.val(val.substring(val.length-1));
                    if ($input.val() !== "")
                        $choices.eq(index+1).focus();
                    $.publiquiz.context.onQuizModified($.publiquiz.question, $quiz);
                }
            });
        } else {
            $choices.on("input", function() {
                $.publiquiz.context.onQuizModified($.publiquiz.question, $quiz);
            });
        }


        // Event "draggable" on item
        pqQuestion.setDraggableItem($quiz, $quiz.find("."+prefix+"Item"), "");

        // Event "select" on combo box
        $quiz.find("."+prefix+"SelectItem").prop("disabled", false).change( function() {
            pqQuestion.clearVerify( );
            var $combo = $(this);
            pqQuestion.blanks._onChangeSelectedItem($quiz, $combo);
            $.publiquiz.context.onQuizModified($.publiquiz.question, $quiz);
        });
    },

    /**
     * Remove events listener on quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    blanksDisable: function($quiz) {
        var prefix = $quiz.data("prefix");

        // Event change on choice
        $quiz.find("."+prefix+"Choice").each( function() {
            var $choice = $(this);
            $choice.prop("disabled", true);
            $choice.addClass("disabled");
        }).unbind("input");

        // Event "draggable" on item
        var evtStart = "mousedown touchstart";
        var $items = $quiz.find("."+prefix+"Item");
        $items.unbind(evtStart);

        // Event "select" on combo box
        $quiz.find("."+prefix+"SelectItem").unbind("change").prop("disabled", true);
    },

    /**
     * Redo quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    blanksRedo: function($quiz) {
        var prefix = $quiz.data("prefix");
        var $engine = $quiz.find("."+prefix+"Engine");
        if ($engine.data("original-state"))
            $engine.html($engine.data("original-state"));
    },

    /**
     * Display help of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    blanksHelp: function($quiz) {
        $.publiquiz.question.displayHelp($quiz);
    },

    /**
     * Retry quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    blanksRetry: function($quiz) {
        $quiz.removeData("quiz-result");
        var options = $quiz.data("engine-options") || "";
        var comboBox = (options.search("combobox") > -1);

        if (comboBox)
            $.publiquiz.question.blanks._retryBlanksComboBox($quiz);
        else
            $.publiquiz.question.retryBlanks($quiz);
    },

    /**
     * Compute score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Dictionnary}.
     */
    blanksComputeScore: function($quiz) {
        var options = $quiz.data("engine-options") || "";
        var noMark = (options.search("nomark") > -1);
        var comboBox = (options.search("combobox") > -1);

        var result = {};
        if (noMark) {
            result.score = 0;
            result.total = 0;
            return result;
        }

        result = $quiz.data("quiz-result");
        if (result !== undefined)
            return result;

        var engine = $quiz.data("engine");
        if (engine == "blanks-fill") {
            result = $.publiquiz.question.blanks._computeScoreBlanksFill($quiz);
        } else {
            if (comboBox)
                result = $.publiquiz.question.blanks._computeScoreBlanksComboBox($quiz);
            else
                result = $.publiquiz.question.scoreForQuizCmpCheck($quiz);
        }
        $quiz.data("quiz-result", result);
        return result;
    },

    /**
     * Display score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    blanksScore: function($quiz) {
    },

    /**
     * Display quiz text answer.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    blanksTextAnswer: function($quiz) {
        $.publiquiz.question.displayTextAnswer($quiz);
    },

    /**
     * Insert user answers in html
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    blanksInsertUserAnswers: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var engine = $quiz.data("engine");
        var options = $quiz.data("engine-options") || "";
        var comboBox = (options.search("combobox") > -1);

        var answer = [];
        if (engine == "blanks-fill") {
            $quiz.find("."+prefix+"Choice").each( function() {
                var $item = $(this);
                var id = $item.attr("id");
                var value = $item.val().trim();
                if (value !== "")
                    answer.push(id.substring(id.length - 3, id.length) + value);
            });
            $.publiquiz.question.writeUserAnswers($quiz, quzId, answer.join("::"));
        } else {
            if (comboBox) {
                $quiz.find("."+prefix+"SelectItem").each( function() {
                    var $item = $(this);
                    var id = $item.attr("id");
                    var value = $item.data("item-value");
                    if (value)
                        answer.push(id.substring(id.length - 3, id.length) + value);
                });
                $.publiquiz.question.writeUserAnswers($quiz, quzId, answer.join("::"));
            } else {
                $.publiquiz.question.inserUserAnswersQuizDrop($quiz);
            }
        }
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    blanksQuizAnswer: function($quiz, mode) {
        var engine = $quiz.data("engine");
        var options = $quiz.data("engine-options") || "";
        var comboBox = (options.search("combobox") > -1);

        if (engine == "blanks-fill") {
            $.publiquiz.question.displayQuizAnswerBlanksFill($quiz, mode);
        } else {
            if (comboBox)
                $.publiquiz.question.blanks._displayQuizAnswerBlanksComboBox($quiz, mode);
            else
                $.publiquiz.question.displayQuizCmpAnswer($quiz, mode);
        }
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    blanksVerifyUserAnswer: function($quiz) {
        var engine = $quiz.data("engine");
        var options = $quiz.data("engine-options") || "";
        var comboBox = (options.search("combobox") > -1);

        if (engine == "blanks-fill") {
            $.publiquiz.question.blanks._verifyBlanksFill($quiz, "user");
        } else {
            if (comboBox)
                $.publiquiz.question.blanks._verifyBlanksComboBox($quiz, "user");
            else
                $.publiquiz.question.verifyQuizCmpAnswer($quiz, "user");
        }
    },

    /**
     * Verify right answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    blanksVerifyRightAnswer: function($quiz) {
        var engine = $quiz.data("engine");
        var options = $quiz.data("engine-options") || "";
        var comboBox = (options.search("combobox") > -1);

        if (engine == "blanks-fill") {
            $.publiquiz.question.blanks._verifyBlanksFill($quiz, "right");
        } else {
            if (comboBox)
                $.publiquiz.question.blanks._verifyBlanksComboBox($quiz, "right");
            else
                $.publiquiz.question.verifyQuizCmpAnswer($quiz, "right");
        }
    },

    /**
     * Verify full answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    blanksVerifyFullAnswer: function($quiz) {
        var engine = $quiz.data("engine");
        var options = $quiz.data("engine-options") || "";
        var comboBox = (options.search("combobox") > -1);

        if (engine == "blanks-fill") {
            $.publiquiz.question.blanks._verifyBlanksFill($quiz, "full");
        } else {
            if (comboBox)
                $.publiquiz.question.blanks._verifyBlanksComboBox($quiz, "full");
            else
                $.publiquiz.question.verifyQuizCmpAnswer($quiz, "full");
        }
    },

    /**
     * Blanks modified
     */
    blanksModified: function($quiz) {
        var changes = [];
        var engine = $quiz.data("engine");
        var prefix = $quiz.data("prefix");

        if (engine == "blanks-fill") {
            $quiz.find("."+prefix+"Choice").each( function() {
                var $choice = $(this);
                var id = $choice.attr("id");
                id = id.substring(id.length - 3, id.length);
                var value = $choice.val().replace(/\n/g, "#R#");
                if (value)
                    changes.push(id+value);
            });
        } else {
            var options = $quiz.data("engine-options") || "";
            var comboBox = (options.search("combobox") > -1);
            if (comboBox) {
                $quiz.find("."+prefix+"SelectItem").each( function() {
                    var $item = $(this);
                    var id = $item.attr("id");
                    id = id.substring(id.length - 3, id.length);
                    var value = $item.data("item-value");
                    if (value)
                        changes.push(id+value);
                });
            } else {
                return $.publiquiz.context.modifyQuizCmpContext($quiz);
            }
        }
        return {"data": changes.join("::"), "engine": engine};
    },

    /**
     * Reload context
     */
    blanksLoadContext: function($quiz, dataClass) {
        var quzId = $quiz.data("quiz-id");
        var engine = $quiz.data("engine");
        var $context = $quiz.find("#"+quzId+"_context");
        var $data = $context.find(dataClass);
        var values = $.publiquiz.question.correction($data);

        if (engine == "blanks-fill") {
            $.each(values, function(k, v) {
                var $choice = $quiz.find("#"+quzId+"_"+k);
                $choice.val(v.replace(/#R#/g, "\n"));
            });
        } else {
            var prefix = $quiz.data("prefix");
            var options = $quiz.data("engine-options") || "";
            var comboBox = (options.search("combobox") > -1);
            var isMultiple = (options.search("multiple") > -1);
            if (comboBox) {
                $.each(values, function(k, v) {
                    var $combo = $quiz.find("#"+quzId+"_"+k);
                    $combo.val(v).prop("selected", true);
                    $combo.data("item-value", v);
                    if (!isMultiple) {
                        $quiz.find("."+prefix+"SelectItem").each( function() {
                            var $combobox = $(this);
                            if ($combobox !== $combo)
                                $combobox.children('option[value="'+v+'"]').attr("disabled", "disabled");
                        });
                    }
                });
            } else {
                $.publiquiz.context.loadQuizCmpContext($quiz, dataClass);
            }
        }
    },


    /**********************************************************************
     *                          Private Library
     **********************************************************************/

    /**
     * On change selected item in combobox.
     *
     * @params {jQuery} $quiz : object jquery publiquiz.
     * @params {jQuery} $combo : object select.
     */
    _onChangeSelectedItem: function($quiz, $combo) {
        var prefix = $quiz.data("prefix");
        var options = $quiz.data("engine-options") || "";
        var isMultiple = (options.search("multiple") > -1);

        var $item = $($combo.find(":selected"));
        var value = $item.val();

        if (!isMultiple) {
            var oldValue = $combo.data("item-value");
            $quiz.find("."+prefix+"SelectItem").each( function() {
                var $combobox = $(this);
                if ($combobox !== $combo && value !== "")
                    $combobox.children('option[value="'+value+'"]').attr("disabled", "disabled");
                if (oldValue)
                    $combobox.children('option[value="'+oldValue+'"]').removeAttr("disabled");
            });
        }

        $combo.data("item-value", value);
    },

    /**
     * Retry quiz blanks option combobox.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    _retryBlanksComboBox: function($quiz) {
        $.publiquiz.question.clearVerify();
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var options = $quiz.data("engine-options") || "";
        var isMultiple = (options.search("multiple") > -1);

        var valuesToShow = [];
        var res = $.publiquiz.question.correction($quiz.find("#"+quzId+"_correct"));

        // On retrouve les valeurs mal placé
        $.each(res, function(key, value) {
            var $combo = $quiz.find("#"+quzId+"_"+key);
            var data = $combo.data("item-value");
            if (data && $.inArray(data, value.split("|")) < 0) {
                valuesToShow.push(data);
                $combo.data("item-value", "");
                $combo.val("").prop("selected", true);
            }
        });

        if (isMultiple)
            return;

        // On re-affiche les valeurs qui on été mal placer dans les selects
        $quiz.find("."+prefix+"SelectItem").each( function() {
            var $combo = $(this);
            $.each(valuesToShow, function(idx, value) {
                $combo.children('option[value="'+value+'"]').removeAttr("disabled");
            });
        });
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    _displayQuizAnswerBlanksComboBox: function($quiz, mode) {
        var quzId = $quiz.data("quiz-id");
        var engine = $quiz.data("engine");
        var prefix = $quiz.data("prefix");
        var options = $quiz.data("engine-options") || "";
        var isMultiple = (options.search("multiple") > -1);
        var showAllAnswer = (options.search("show-all-answer") > -1);
        var answers = $.publiquiz.question.correction($quiz.find("#"+quzId+mode));
        var userAnswers = null;
        if (mode == "_correct")
            userAnswers = $.publiquiz.question.correction($quiz.find("#"+quzId+"_user"));

        // On vide les champs
        $quiz.find("."+prefix+"SelectItem").each( function() {
            var $combo = $(this);
            $combo.find("option").each( function() {
                var $option = $(this);
                if ($option.data("ori-text") !== undefined)
                    $option.text($option.data("ori-text"));
                else
                    $option.data("ori-text", $option.text());
            });
            $combo.removeClass("answerOk answerKo");
            $combo.find("option").removeAttr("disabled");
            $combo.val("").prop("selected", true);
            $combo.removeData("item-value");
        });

        // On place la correction en selection la bonne option
        var used = [];
        $.each(answers, function(key, value) {
            var $combo = $quiz.find("#"+quzId+"_"+key);
            var $values = $(value.split("|"));
            $combo.data("item-value", $values[0]);
            if (showAllAnswer) {
                $combo.val($values[0]).prop("selected", true);
                var txt = "";
                $values.each(function (i, v) {
                    if (txt !== "")
                        txt += " / ";
                    var option = $combo.find("option[value=\""+v+"\"]")[0];
                    txt += $(option).text();
                });
                var $option = $combo.find("option:selected");
                $option.text(txt);
            } else {
                if (isMultiple) {
                    $combo.val($values[0]).prop("selected", true);
                } else {
                    $values.each(function (i, v) {
                        if ($.inArray(v, used) < 0) {
                            $combo.val(v).prop("selected", true);
                            used.push(v);
                            return false;
                        }
                        return true;
                    });
                }
            }

        });
    },

    /**
     * Verify answer for quiz blanks-fill.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : "full", "right" or "user" color.
     */
    _verifyBlanksFill: function($quiz, mode) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        var isStrict = false;
        var options = [];
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("strict") > -1 ) {
            isStrict = true;
            var opts = $quiz.data("engine-options").replace("strict", "").trim();
            if (opts !== "")
                options = opts.split(" ");
        }

        var rightAnswers = $.publiquiz.question.correction($quiz.find("#"+quzId+"_correct"));
        var userAnswers = $.publiquiz.question.correction($quiz.find("#"+quzId+"_user"));

        var paramWrongAnswers = $.publiquiz.defaults.wrongAnswers;
        $.each(rightAnswers, function(key, value) {
            var $item = $quiz.find("#"+quzId+"_"+key);
            if ($item.length > 0) {
                var data = $item.val().trim();
                if (data !== "") {
                    var valid = $.publiquiz.question.isValideBlanksFillAnswer(data, value, isStrict, options);
                    if (mode == "user") {
                        $.publiquiz.question.addClassColorAnswer($quiz, $item, valid);
                        if (!valid && paramWrongAnswers == "clear") {
                            $('body').queue(function(next) {
                                $item.val("");
                                $item.removeClass("answerKo");
                                next();
                            });
                        }
                    } else if (mode == "right") {
                        if (valid)
                            $.publiquiz.question.addClassColorAnswer($quiz, $item, true);
                    } else {
                        var userAnswer = userAnswers[key];
                        valid = userAnswer && $.publiquiz.question.isValideBlanksFillAnswer(userAnswer, value, isStrict, options);
                        $.publiquiz.question.addClassColorAnswer($quiz, $item, valid);
                    }
                }
            }
        });

        var duration = $quiz.data("verify-duration");
        if (duration > 0) {
            var timer = setTimeout($.publiquiz.question.clearVerify, duration);
            $.publiquiz.question.timers.push(timer);
        }
    },

    /**
     * Verify answer for quiz blanks-select option combobox.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    _verifyBlanksComboBox: function($quiz, mode) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var rightAnswers = $.publiquiz.question.correction($quiz.find("#"+quzId+"_correct"));
        var paramWrongAnswers = $.publiquiz.defaults.wrongAnswers;

        $.each(rightAnswers, function(key, value) {
            var $combo = $quiz.find("#"+quzId+"_"+key);
            var data = $combo.data("item-value");
            var valid;
            if (data) {
                if (mode == "user") {
                    valid = $.inArray(data, value.split("|")) >= 0;
                    if (!valid && paramWrongAnswers == "clear") {
                        $('body').queue(function(next) {
                            $combo.removeClass("answerKo");
                            $combo.data("item-value", "");
                            $combo.val("").prop("selected", true);
                            $quiz.find("."+prefix+"SelectItem").children('option[value="'+data+'"]').removeAttr("disabled");
                            next();
                        });
                    }
                } else if (mode == "right") {
                    if ($.inArray(data, value.split("|")) >= 0)
                        valid = true;
                } else {
                    valid = $.inArray(data, value.split("|")) >= 0;
                }
                $.publiquiz.question.addClassColorAnswer($quiz, $combo, valid);
            } else {
                if (!value)
                    $.publiquiz.question.addClassColorAnswer($quiz, $combo, true);
            }
        });

        var duration = $quiz.data("verify-duration");
        if (duration > 0) {
            var timer = setTimeout($.publiquiz.question.clearVerify, duration);
            $.publiquiz.question.timers.push(timer);
        }
    },

    /**
     * Configure quiz blanks fill.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    _configureBlanksFill: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Choice").each( function() {
            if (this.parentNode.nodeName.toLowerCase() == "td" ||
                this.parentNode.parentNode.nodeName.toLowerCase == "td")
                return;
            if (this.nodeName.toLowerCase() == "textarea")
                return;

            var $choice = $(this);
            var id = $choice.attr("id");
            var key = id.substring(id.length - 3, id.length);
            var answers = $.publiquiz.question.correction($("#"+quzId+"_correct"));
            var value = answers[key];

            var answer = "";
            $(value.split("|")).each( function(ids, data) {
                if (data.length > answer)
                    answer = data;
            });

            var w = answer.length * 1.2;
            if(w < 20)
                w = 20;
            if (!$choice.attr("style"))
                $choice.css("width", w+"em");
        });
    },

    /**
     * This function use for compute score for engine blanks-fill.
     *
     * @params {Object} $quiz : Object jquery quiz.
     * @return {Dictionnary}.
     */
    _computeScoreBlanksFill: function ($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        var isStrict = false;
        var options = [];
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("strict") > -1 ) {
            isStrict = true;
            var opts = $quiz.data("engine-options").replace("strict", "").trim();
            if (opts !== "")
                options = opts.split(" ");
        }

        var total = $quiz.find("."+prefix+"Choice").length;
        var score = 0.0;

        var res = $.publiquiz.question.correction($quiz.find("#"+quzId+"_correct"));
        $.each(res, function(key, value) {
            var $item = $quiz.find("#"+quzId+"_"+key);
            if ($item.length > 0) {
                var data = $item.val().trim();
                if ($.publiquiz.question.isValideBlanksFillAnswer(data, value, isStrict, options))
                    score += 1;
            }
        });

        var result = {};
        result.score = score;
        result.total = total;
        return result;
    },

    /**
     * This function use for compute score for engine blanks-select option combobox.
     *
     * @param $quiz {Object}: Object jquery quiz.
     * @return {Dictionnary}.
     */
    _computeScoreBlanksComboBox: function ($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var res = $.publiquiz.question.correction($quiz.find("#"+quzId+"_correct"));

        var total = $quiz.find("."+prefix+"SelectItem").length;
        var score = 0;

        $.each(res, function(key, value) {
            var $combo = $quiz.find("#"+quzId+"_"+key);
            if ($combo.data("item-value") && $.inArray($combo.data("item-value"), value.split("|")) >= 0)
                score += 1;
        });

        var result = {};
        result.score = score;
        result.total = total;
        return result;
    }
};

// Register function
$.publiquiz.question.register("blanks-fill", {
        configure: $.publiquiz.question.blanks.blanksConfigure,
        enable: $.publiquiz.question.blanks.blanksEnable,
        disable: $.publiquiz.question.blanks.blanksDisable,
        redo: $.publiquiz.question.blanks.blanksRedo,
        help: $.publiquiz.question.blanks.blanksHelp,
        retry: $.publiquiz.question.blanks.blanksRetry,
        textAnswer: $.publiquiz.question.blanks.blanksTextAnswer,
        insertUserAnswers: $.publiquiz.question.blanks.blanksInsertUserAnswers,
        quizAnswer: $.publiquiz.question.blanks.blanksQuizAnswer,
        verifyUserAnswer: $.publiquiz.question.blanks.blanksVerifyUserAnswer,
        verifyRightAnswer: $.publiquiz.question.blanks.blanksVerifyRightAnswer,
        verifyFullAnswer: $.publiquiz.question.blanks.blanksVerifyFullAnswer,
        computeScore: $.publiquiz.question.blanks.blanksComputeScore,
        quizScore: $.publiquiz.question.blanks.blanksScore,
        modified: $.publiquiz.question.blanks.blanksModified,
        loadContext: $.publiquiz.question.blanks.blanksLoadContext
    });

$.publiquiz.question.register("blanks-select", {
        configure: $.publiquiz.question.blanks.blanksConfigure,
        enable: $.publiquiz.question.blanks.blanksEnable,
        disable: $.publiquiz.question.blanks.blanksDisable,
        redo: $.publiquiz.question.blanks.blanksRedo,
        help: $.publiquiz.question.blanks.blanksHelp,
        retry: $.publiquiz.question.blanks.blanksRetry,
        textAnswer: $.publiquiz.question.blanks.blanksTextAnswer,
        insertUserAnswers: $.publiquiz.question.blanks.blanksInsertUserAnswers,
        quizAnswer: $.publiquiz.question.blanks.blanksQuizAnswer,
        verifyUserAnswer: $.publiquiz.question.blanks.blanksVerifyUserAnswer,
        verifyRightAnswer: $.publiquiz.question.blanks.blanksVerifyRightAnswer,
        verifyFullAnswer: $.publiquiz.question.blanks.blanksVerifyFullAnswer,
        computeScore: $.publiquiz.question.blanks.blanksComputeScore,
        quizScore: $.publiquiz.question.blanks.blanksScore,
        modified: $.publiquiz.question.blanks.blanksModified,
        loadContext: $.publiquiz.question.blanks.blanksLoadContext
    });

$.publiquiz.question.register("blanks-media", {
        configure: $.publiquiz.question.blanks.blanksConfigure,
        enable: $.publiquiz.question.blanks.blanksEnable,
        disable: $.publiquiz.question.blanks.blanksDisable,
        redo: $.publiquiz.question.blanks.blanksRedo,
        help: $.publiquiz.question.blanks.blanksHelp,
        retry: $.publiquiz.question.blanks.blanksRetry,
        textAnswer: $.publiquiz.question.blanks.blanksTextAnswer,
        insertUserAnswers: $.publiquiz.question.blanks.blanksInsertUserAnswers,
        quizAnswer: $.publiquiz.question.blanks.blanksQuizAnswer,
        verifyUserAnswer: $.publiquiz.question.blanks.blanksVerifyUserAnswer,
        verifyRightAnswer: $.publiquiz.question.blanks.blanksVerifyRightAnswer,
        verifyFullAnswer: $.publiquiz.question.blanks.blanksVerifyFullAnswer,
        computeScore: $.publiquiz.question.blanks.blanksComputeScore,
        quizScore: $.publiquiz.question.blanks.blanksScore,
        modified: $.publiquiz.question.blanks.blanksModified,
        loadContext: $.publiquiz.question.blanks.blanksLoadContext
    });

}(jQuery));



/******************************************************************************
 *
 *                                  Blanks-choices
 *
 *****************************************************************************/

(function ($) {

$.publiquiz.question.blanksChoices = {

    /**
     * Configure quiz.
     *
     * @param {jQuery} $quiz - jquery Object quiz.
     */
    blanksChoicesConfigure: function($quiz) {
        var prefix = $quiz.data("prefix");
        var $engine = $quiz.find("."+prefix+"Engine");
        if ($engine.data("original-state") === undefined)
            $engine.data("original-state", $engine.html());

        var options = $quiz.data("engine-options") || "";
        var noShuffle = (options.search("no-shuffle") > -1);

        if (noShuffle)
            return;

        var $selectChoices = $quiz.find("."+prefix+"SelectChoices");
        if ($selectChoices.length > 0) {
            $selectChoices.shuffle();
            $selectChoices.each( function() {
                var $select = $(this);
                $select.children('option[value=""]').detach().prependTo($select);
                $select.val("").prop("selected", true);
            });
        }
    },

    /**
     * Set event click on Choice.
     *
     * @param {jQuery} $quiz - jquery Object quiz.
     */
    blanksChoicesEnable: function($quiz) {
        var pqQuestion = $.publiquiz.question;
        var pqContext = $.publiquiz.context;
        var prefix = $quiz.data("prefix");

        // Event "select" on combo box
        $quiz.find("."+prefix+"SelectChoices").prop("disabled", false).change( function() {
            pqQuestion.clearVerify();
            var $select = $(this);
            pqQuestion.blanksChoices._onChangeSelectedChoice($quiz, $select);
            pqContext.onQuizModified(pqQuestion, $quiz);
        });

        // Event "click" for point
        $quiz.find("."+prefix+"Point").click( function(ev) {
            var $target = $(this);
            pqQuestion.clearVerify();
            while (!$target.hasClass(prefix+"Point"))
                $target = $target.parentNode;
            pqQuestion.blanksChoices._onPoint($quiz, $target);
            pqContext.onQuizModified(pqQuestion, $quiz);
        });
    },

    /**
     * Remove events listener on quiz.
     *
     * @param {jQuery} $quiz - jquery Object quiz.
     */
    blanksChoicesDisable: function($quiz) {
        var prefix = $quiz.data("prefix");

        // Event "select" on combo box
        $quiz.find("."+prefix+"SelectChoices").off("change").prop("disabled", true);

        // Event "click" on point
        $quiz.find("."+prefix+"Point").off("click");
    },

    /**
     * Redo quiz.
     *
     * @param {jQuery} $quiz - jquery Object quiz.
     */
    blanksChoicesRedo: function($quiz) {
        var prefix = $quiz.data("prefix");
        var $engine = $quiz.find("."+prefix+"Engine");
        if ($engine.data("original-state"))
            $engine.html($engine.data("original-state"));
    },

    /**
     * Display help of quiz.
     *
     * @param {jQuery} $quiz - jquery Object quiz.
     */
    blanksChoicesHelp: function($quiz) {
        $.publiquiz.question.displayHelp($quiz);
    },

    /**
     * Retry quiz.
     *
     * @param {jQuery} $quiz - jquery Object quiz.
     */
    blanksChoicesRetry: function($quiz) {
        $quiz.removeData("quiz-result");
        $.publiquiz.question.clearVerify();

        var quzId = $quiz.data("quiz-id");
        var options = $quiz.data("engine-options") || "";
        var render = (options.search("pointing") > -1) ? "pointing" : "combobox";
        var res = $.publiquiz.question.correction($quiz.find("#"+quzId+"_correct"));

        // Les valeurs mal placé sont enlevé, on laisse les bonnes réponses.
        if (render === "combobox") {
            $.each(res, function(key, values) {
                var $combo = $quiz.find("#"+quzId+"_"+key);
                var value = $combo.data("choice-value");
                if (value === undefined)
                    return true;
                var valid = ($.inArray(value, values.split("|")) >= 0);
                if (!valid) {
                    $combo.removeData("choice-value");
                    $combo.val("").prop("selected", true);
                }
                return true;
            });
        } else {
            $.each(res, function(key, values) {
                var $choices = $quiz.find("#"+quzId+"_"+key);
                var value = $choices.data("choice-value");
                if (value === undefined)
                    return true;
                var valid = ($.inArray(value, values.split("|")) >= 0);
                if (!valid) {
                    var prefix = $quiz.data("prefix");
                    var $point = $choices.find("."+prefix+"Point").filter("[data-choice-value=\""+value+"\"]");
                    $point.removeClass("selected answerKo");
                    $choices.removeData("choice-value");
                }
                return true;
            });
        }
    },

    /**
     * Compute score of quiz.
     *
     * @param {JQuery} $quiz - jquery Object quiz.
     * @return {Dictionnary}.
     */
    blanksChoicesComputeScore: function($quiz) {
        var options = $quiz.data("engine-options") || "";
        var noMark = (options.search("nomark") > -1);
        var result = {};

        if (noMark) {
            result.score = 0;
            result.total = 0;
            return result;
        }

        var score = 0;
        var total = 0;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var render = (options.search("pointing") > -1) ? "pointing" : "combobox";
        var res = $.publiquiz.question.correction($quiz.find("#"+quzId+"_correct"));

        if (render === "combobox") {
            // Chaque zone vaut 1 point, le total est sur le nombre de zone.
            //  - right selectionner vaut 1 point
            //   - wrong selectionner vaut 0 point
            // pas de right dans la zone :
            //   - si aucune selection alors 1 point
            var $choices = $quiz.find("."+prefix+"SelectChoices");
            total = $choices.length;
            $.each(res, function(key, value) {
                var $combo = $quiz.find("#"+quzId+"_"+key);
                var choice = $combo.data("choice-value");
                if ((choice !== undefined && $.inArray(String(choice), value.split("|")) >= 0) ||
                        ($combo.data("choice-value") === undefined && value === ""))
                    score += 1;
            });
        } else {
            // Chaque zone vaut 1 point, le total est sur le nombre de zone.
            // 1 ou plusieur right dans la zone :
            //   - right selectionner vaut 1 point
            //   - wrong selectionner vaut 0 point
            // pas de right dans la zone :
            //   - si aucune selection alors 1 point
            total = $quiz.find("."+prefix+"PointChoices").length;
            $.each(res, function(key, value) {
                var $choices = $quiz.find("#"+quzId+"_"+key);
                var choice = $choices.data("choice-value");
                if ((choice !== undefined && $.inArray(String(choice), value.split("|")) >= 0) ||
                        (choice === undefined && value === ""))
                    score += 1;
            });
        }

        result.score = score;
        result.total = total;
        $quiz.data("quiz-result", result);
        return result;
    },

    /**
     * Display score of quiz.
     *
     * @param {jQuery} $quiz - jquery Object quiz.
     */
    blanksChoicesScore: function($quiz) {
    },

    /**
     * Display quiz text answer.
     *
     * @param {jQuery} $quiz - jquery Object quiz.
     */
    blanksChoicesTextAnswer: function($quiz) {
        $.publiquiz.question.displayTextAnswer($quiz);
    },

    /**
     * Insert user answers in html
     *
     * @param {jQuery} $quiz - jquery Object quiz.
     */
    blanksChoicesInsertUserAnswers: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var options = $quiz.data("engine-options") || "";
        var render = (options.search("pointing") > -1) ? "pointing" : "combobox";
        var answer = [];

        if (render === "combobox") {
            $quiz.find("."+prefix+"SelectChoices").each(function() {
                var $choices = $(this);
                var id = $choices.attr("id");
                var value = $choices.data("choice-value");
                if (value)
                    answer.push(id.substring(id.length - 3, id.length) + value);
            });
        } else {
            $quiz.find("."+prefix+"PointChoices").each(function() {
                var $choices = $(this);
                var id = $choices.attr("id");
                var value = $choices.data("choice-value");
                if (value)
                    answer.push(id.substring(id.length - 3, id.length) + value);
            });
        }
        $.publiquiz.question.writeUserAnswers($quiz, quzId, answer.join("::"));
    },

    /**
     * Display right/user answer for quiz.
     *
     * @param {jQuery} $quiz - jquery Object quiz.
     * @params {String} mode - display correct/user answer.
     */
    blanksChoicesQuizAnswer: function($quiz, mode) {
        var quzId = $quiz.data("quiz-id");
        var engine = $quiz.data("engine");
        var prefix = $quiz.data("prefix");
        var options = $quiz.data("engine-options") || "";
        var render = (options.search("pointing") > -1) ? "pointing" : "combobox";
        var answers = $.publiquiz.question.correction($quiz.find("#"+quzId+mode));

        if (render === "combobox") {
            // On vide les champs
            $quiz.find("."+prefix+"SelectChoices").each( function() {
                var $combo = $(this);
                $combo.find("option").each( function() {
                    var $option = $(this);
                    if ($option.data("ori-text") !== undefined)
                        $option.text($option.data("ori-text"));
                    else
                        $option.data("ori-text", $option.text());
                });
                $combo.removeClass("answerOk answerKo");
                $combo.find("option").removeAttr("disabled");
                $combo.val("").prop("selected", true);
                $combo.removeData("choice-value");
            });

            // Selection l'option
            var showAllAnswer = (options.search("show-all-answer") > -1);
            var used = [];
            $.each(answers, function(key, value) {
                var $combo = $quiz.find("#"+quzId+"_"+key);
                $combo.data("choice-value", value.split("|")[0]);
                $combo.val(value.split("|")[0]).prop("selected", true);
                if (showAllAnswer) {
                    var txt = "";
                    $.each(value.split("|"), function (i, v) {
                        if (txt !== "")
                            txt += " / ";
                        txt += $combo.find("option[value=\""+v+"\"]").text();
                    });
                    $combo.find("option:selected").text(txt);
                }
            });
        } else {
            // On vide les selections precedentes
            $quiz.find("."+prefix+"Point").each( function() {
                var $point = $(this);
                $point.removeClass("selected answerOk answerKo");
            });

            // Nouvelle selection
            $.each(answers, function(key, value) {
                var $choices = $quiz.find("#"+quzId+"_"+key);
                $.each(value.split("|"), function(i, v) {
                    var $point = $choices.find("."+prefix+"Point")
                        .filter("[data-choice-value=\""+v+"\"]");
                    $point.addClass("selected");
                });
            });
        }
    },

    /**
     * Verify user answer.
     *
     * @param {jQuery} $quiz - jquery Object quiz.
     */
    blanksChoicesVerifyUserAnswer: function($quiz) {
        var options = $quiz.data("engine-options") || "";
        var render = (options.search("pointing") > -1) ? "pointing" : "combobox";
        if (render === "combobox")
            $.publiquiz.question.blanksChoices._verifySelectChoices($quiz, "user");
        else
            $.publiquiz.question.blanksChoices._verifyPointChoices($quiz, "user");
    },

    /**
     * Verify right answer.
     *
     * @param {jQuery} $quiz - jquery Object quiz.
     */
    blanksChoicesVerifyRightAnswer: function($quiz) {
        var options = $quiz.data("engine-options") || "";
        var render = (options.search("pointing") > -1) ? "pointing" : "combobox";
        if (render === "combobox")
            $.publiquiz.question.blanksChoices._verifySelectChoices($quiz, "right");
        else
            $.publiquiz.question.blanksChoices._verifyPointChoices($quiz, "right");
    },

    /**
     * Verify full answer.
     *
     * @param {jQuery} $quiz - jquery Object quiz.
     */
    blanksChoicesVerifyFullAnswer: function($quiz) {
        var options = $quiz.data("engine-options") || "";
        var render = (options.search("pointing") > -1) ? "pointing" : "combobox";
        if (render === "combobox")
            $.publiquiz.question.blanksChoices._verifySelectChoices($quiz, "full");
        else
            $.publiquiz.question.blanksChoices._verifyPointChoices($quiz, "full");
    },

    /**
     * Modified
     *
     * @param {jQuery} $quiz - jquery Object quiz.
     */
    blanksChoicesModified: function($quiz) {
        var changes = [];
        var engine = $quiz.data("engine");
        var prefix = $quiz.data("prefix");
        var options = $quiz.data("engine-options") || "";
        var render = (options.search("pointing") > -1) ? "pointing" : "combobox";

        if (render === "combobox") {
            $quiz.find("."+prefix+"SelectChoices").each( function() {
                var $select = $(this);
                var id = $select.attr("id");
                id = id.substring(id.length - 3, id.length);
                var value = $select.data("choice-value");
                if (value)
                    changes.push(id+value);
            });
        } else {
            $quiz.find("."+prefix+"PointChoices").each( function() {
                var $choices = $(this);
                var id = $choices.attr("id");
                id = id.substring(id.length - 3, id.length);
                var value = $choices.data("choice-value");
                if (value)
                    changes.push(id+value);
            });
        }

        return {"data": changes.join("::"), "engine": engine};
    },

    /**
     * Reload context
     *
     * @param {jQuery} $quiz - jquery Object quiz.
     */
    blanksChoicesLoadContext: function($quiz, dataClass) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var options = $quiz.data("engine-options") || "";
        var render = (options.search("pointing") > -1) ? "pointing" : "combobox";

        var $context = $quiz.find("#"+quzId+"_context");
        var $data = $context.find(dataClass);
        var values = $.publiquiz.question.correction($data);

        if (render === "combobox") {
            $.each(values, function(k, v) {
                var $combo = $quiz.find("#"+quzId+"_"+k);
                $combo.val(v).prop("selected", true);
                $combo.data("choice-value", v);
            });
        } else {
            $.each(values, function(k, v) {
                var $choices = $quiz.find("#"+quzId+"_"+k);
                $choices.data("choice-value", v);
                $.each(v.split("|"), function(i, value) {
                    var $point = $choices.find("."+prefix+"Point")
                        .filter("[data-choice-value=\""+value+"\"]");
                    $point.addClass("selected");
                });
            });
        }
    },


    /**********************************************************************
     *                          Private Library
     *********************************************************************/

    /**
     * On change selected choice.
     *
     * @param {jQuery} $quiz - jquery Object quiz.
     * @params {jQuery} $select - object select.
     */
    _onChangeSelectedChoice: function($quiz, $select) {
        var $item = $($select.find(":selected"));
        var value = $item.val();
        $select.data("choice-value", value);
    },

    /**
     * Click on point.
     *
     * @param {jQuery} $quiz - jquery Object quiz.
     * @param {jQuery} $point - jquery Object point.
     */
    _onPoint: function($quiz, $point) {
        var prefix = $quiz.data("prefix");
        var options = $quiz.data("engine-options") || "";
        var $choices = $point.parent();

        if ($point.hasClass("selected")) {
            $point.removeClass("selected");
            $choices.removeData("choice-value");
        } else {
            $choices.find("."+prefix+"Point").removeClass("selected");
            $point.addClass("selected");
            $choices.data("choice-value", $point.data("choice-value"));
        }
    },

    /**
     * Verify answer for quiz option combobox.
     *
     * @param {jQuery} $quiz - jquery Object quiz.
     * @param {String} mode - .
     */
    _verifySelectChoices: function($quiz, mode) {
        var pqQuestion = $.publiquiz.question;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var rightAnswers = pqQuestion.correction($quiz.find("#"+quzId+"_correct"));
        var paramWrongAnswers = $.publiquiz.defaults.wrongAnswers;

        $.each(rightAnswers, function(key, value) {
            var $combo = $quiz.find("#"+quzId+"_"+key);
            var data = $combo.data("choice-value");
            var valid;
            if (data) {
                if (mode == "user") {
                    valid = $.inArray(data, value.split("|")) >= 0;
                    if (!valid && paramWrongAnswers == "clear") {
                        $('body').queue(function(next) {
                            $combo.removeClass("answerKo");
                            $combo.removeData("choice-value");
                            $combo.val("").prop("selected", true);
                            $quiz.find("."+prefix+"SelectChoices").children('option[value="'+data+'"]').removeAttr("disabled");
                            next();
                        });
                    }
                } else if (mode == "right") {
                    if ($.inArray(data, value.split("|")) >= 0)
                        valid = true;
                } else {
                    valid = $.inArray(data, value.split("|")) >= 0;
                }
                pqQuestion.addClassColorAnswer($quiz, $combo, valid);
            } else {
                if (!value)
                    pqQuestion.addClassColorAnswer($quiz, $combo, true);
            }
        });

        var duration = $quiz.data("verify-duration");
        if (duration > 0) {
            var timer = setTimeout(pqQuestion.clearVerify, duration);
            pqQuestion.timers.push(timer);
        }
    },

    /**
     * Verify answer for quiz option pointing.
     *
     * @param {jQuery} $quiz - jquery Object quiz.
     * @param {String} mode - .
     */
    _verifyPointChoices: function($quiz, mode) {
        var pqQuestion = $.publiquiz.question;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var options = $quiz.data("engine-options") || "";
        var rightAnswers = pqQuestion.correction($quiz.find("#"+quzId+"_correct"));
        var userAnswers = pqQuestion.correction($quiz.find("#"+quzId+"_user"));
        var paramWrongAnswers = $.publiquiz.defaults.wrongAnswers;

        var choices = $quiz.find("."+prefix+"Point");
        if (mode == "user" || mode == "right")
            choices = choices.filter('.selected');

        choices.each(function() {
            var $choice = $(this);
            var key = $choice.parent().attr("id");
            key = key.substring(key.length - 3, key.length);
            if (mode == "user") {
                var valid = ($.inArray(String($choice.data("choice-value")), rightAnswers[key].split("|")) >= 0);
                pqQuestion.addClassColorAnswer($quiz, $choice, valid);
                if (!valid && paramWrongAnswers == "clear") {
                    $('body').queue(function(next) {
                        $choice.find("input").prop("checked", false);
                        $choice.removeClass("selected answerKo");
                        next();
                    });
                }
            } else if (mode == "right") {
                if ($.inArray(String($choice.data("choice-value")), rightAnswers[key].split("|")) >= 0)
                    $choice.addClass("answerOk");
            } else {
                if (rightAnswers[key] && userAnswers[key])
                    $choice.addClass("answerOk");
                else if (rightAnswers[key] && !userAnswers[key])
                    $choice.addClass("answerKo");
            }
        });

        var duration = $quiz.data("verify-duration");
        if (duration > 0) {
            var timer = setTimeout(pqQuestion.clearVerify, duration);
            pqQuestion.timers.push(timer);
        }
    }
};

// Register function
$.publiquiz.question.register("blanks-choices", {
    configure: $.publiquiz.question.blanksChoices.blanksChoicesConfigure,
    enable: $.publiquiz.question.blanksChoices.blanksChoicesEnable,
    disable: $.publiquiz.question.blanksChoices.blanksChoicesDisable,
    redo: $.publiquiz.question.blanksChoices.blanksChoicesRedo,
    help: $.publiquiz.question.blanksChoices.blanksChoicesHelp,
    retry: $.publiquiz.question.blanksChoices.blanksChoicesRetry,
    textAnswer: $.publiquiz.question.blanksChoices.blanksChoicesTextAnswer,
    insertUserAnswers: $.publiquiz.question.blanksChoices.blanksChoicesInsertUserAnswers,
    quizAnswer: $.publiquiz.question.blanksChoices.blanksChoicesQuizAnswer,
    verifyUserAnswer: $.publiquiz.question.blanksChoices.blanksChoicesVerifyUserAnswer,
    verifyRightAnswer: $.publiquiz.question.blanksChoices.blanksChoicesVerifyRightAnswer,
    verifyFullAnswer: $.publiquiz.question.blanksChoices.blanksChoicesVerifyFullAnswer,
    computeScore: $.publiquiz.question.blanksChoices.blanksChoicesComputeScore,
    quizScore: $.publiquiz.question.blanksChoices.blanksChoicesScore,
    modified: $.publiquiz.question.blanksChoices.blanksChoicesModified,
    loadContext: $.publiquiz.question.blanksChoices.blanksChoicesLoadContext
});

}(jQuery));



/******************************************************************************
 *
 *                                  Sort
 *
 *****************************************************************************/

(function ($) {

$.publiquiz.question.sort = {

    /**
     * Configure quiz.
     */
    sortConfigure: function($quiz) {
        var prefix = $quiz.data("prefix");
        var $engine = $quiz.find("."+prefix+"Engine");
        if ($engine.data("original-state") === undefined)
            $engine.data("original-state", $engine.html());

        var quzId = $quiz.data("quiz-id");
        var $dropzones = $($quiz.find("."+prefix+"Drop"));
        var res = $.publiquiz.question.correction($quiz.find("#"+quzId+"_correct"));

        // Control not give the right answer
        var i = 0, answer = true;
        while(answer && i < 20) {
            answer = $.publiquiz.question.shuffleAndControlItems($quiz, $dropzones, res);
            i++;
        }
    },

    /**
     * Set event click on Choice.
     *
     * @param {Object} jquery Object quiz.
     */
    sortEnable: function($quiz) {
        var prefix = $quiz.data("prefix");

        // Event "draggable" on item
        $.publiquiz.question.setDraggableItem($quiz, $quiz.find("."+prefix+"Item"), "");
    },

    /**
     * Remove events listener on quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    sortDisable: function($quiz) {
        var prefix = $quiz.data("prefix");
        var evtStart = "mousedown touchstart";
        var $items = $quiz.find("."+prefix+"Item");
        $items.unbind(evtStart);
    },

    /**
     * Redo quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    sortRedo: function($quiz) {
        var prefix = $quiz.data("prefix");
        var $engine = $quiz.find("."+prefix+"Engine");
        if ($engine.data("original-state"))
            $engine.html($engine.data("original-state"));
    },

    /**
     * Display help of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    sortHelp: function($quiz) {
        $.publiquiz.question.displayHelp($quiz);
    },

    /**
     * Retry quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    sortRetry: function($quiz) {
        $quiz.removeData("quiz-result");
        $.publiquiz.question.retryQuizCmp($quiz);
    },

    /**
     * Compute score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Dictionnary}.
     */
    sortComputeScore: function($quiz) {
        var noMark = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("nomark") > -1 )
            noMark = true;

        var result = {};
        if (noMark) {
            result.score = 0;
            result.total = 0;
            return result;
        }

        result = $quiz.data("quiz-result");
        if (result !== undefined)
            return result;

        result = $.publiquiz.question.scoreForQuizCmpRadio($quiz);
        $quiz.data("quiz-result", result);
        return result;
    },

    /**
     * Display score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    sortScore: function($quiz) {
    },

    /**
     * Display quiz text answer.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    sortTextAnswer: function($quiz) {
        $.publiquiz.question.displayTextAnswer($quiz);
    },

    /**
     * Insert user answers in html
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    sortInsertUserAnswers: function($quiz) {
        $.publiquiz.question.inserUserAnswersQuizDrop($quiz);
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    sortQuizAnswer: function($quiz, mode) {
        $.publiquiz.question.displayQuizCmpAnswer($quiz, mode);
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    sortVerifyUserAnswer: function($quiz) {
        $.publiquiz.question.verifyQuizCmpAnswer($quiz, "user");
    },

    /**
     * Verify right answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    sortVerifyRightAnswer: function($quiz) {
        $.publiquiz.question.verifyQuizCmpAnswer($quiz, "right");
    },

    /**
     * Verify full answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    sortVerifyFullAnswer: function($quiz) {
        $.publiquiz.question.verifyQuizCmpAnswer($quiz, "full");
    },


    /**
     * Modified
     */
    sortModified: function($quiz) {
        return $.publiquiz.context.modifyQuizCmpContext($quiz);
    },

    /**
     * Reload context
     */
    sortLoadContext: function($quiz, dataClass) {
        $.publiquiz.context.loadQuizCmpContext($quiz, dataClass);
    }

    /**********************************************************************
     *                          Private Library
    **********************************************************************/

};

// Register function
$.publiquiz.question.register("sort", {
        configure: $.publiquiz.question.sort.sortConfigure,
        enable: $.publiquiz.question.sort.sortEnable,
        disable: $.publiquiz.question.sort.sortDisable,
        redo: $.publiquiz.question.sort.sortRedo,
        help: $.publiquiz.question.sort.sortHelp,
        retry: $.publiquiz.question.sort.sortRetry,
        textAnswer: $.publiquiz.question.sort.sortTextAnswer,
        insertUserAnswers: $.publiquiz.question.sort.sortInsertUserAnswers,
        quizAnswer: $.publiquiz.question.sort.sortQuizAnswer,
        verifyUserAnswer: $.publiquiz.question.sort.sortVerifyUserAnswer,
        verifyRightAnswer: $.publiquiz.question.sort.sortVerifyRightAnswer,
        verifyFullAnswer: $.publiquiz.question.sort.sortVerifyFullAnswer,
        computeScore: $.publiquiz.question.sort.sortComputeScore,
        quizScore: $.publiquiz.question.sort.sortScore,
        modified: $.publiquiz.question.sort.sortModified,
        loadContext: $.publiquiz.question.sort.sortLoadContext
    });

}(jQuery));


/******************************************************************************
 *
 *                                  Matching
 *
 *****************************************************************************/

(function ($) {

$.publiquiz.question.matching = {

    /**
     * Configure quiz.
     */
    matchingConfigure: function($quiz) {
        var prefix = $quiz.data("prefix");
        var $engine = $quiz.find("."+prefix+"Engine");
        if ($engine.data("original-state") === undefined)
            $engine.data("original-state", $engine.html());

        var quzId = $quiz.data("quiz-id");
        var options = $quiz.data("engine-options") || "";
        var noShuffle = (options.search("no-shuffle") > -1);
        var $dropzones = $($quiz.find("."+prefix+"Drop"));
        var res = $.publiquiz.question.correction($quiz.find("#"+quzId+"_correct"));

        if (!noShuffle) {
            // Control not give the right answer
            var i = 0, answer = true;
            while(answer && i < 20) {
                answer = $.publiquiz.question.shuffleAndControlItems($quiz, $dropzones, res);
                i++;
            }
        }
    },

    /**
     * Set event click on Choice.
     *
     * @param {Object} jquery Object quiz.
     */
    matchingEnable: function($quiz) {
        var prefix = $quiz.data("prefix");

        // Event "draggable" on item
        $.publiquiz.question.setDraggableItem($quiz, $quiz.find("."+prefix+"Item"), "");
    },

    /**
     * Remove events listener on quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    matchingDisable: function($quiz) {
        var prefix = $quiz.data("prefix");

        // Draggable item
        var evtStart = "mousedown touchstart";
        var $items = $quiz.find("."+prefix+"Item");
        $items.unbind(evtStart);
    },

    /**
     * Redo quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    matchingRedo: function($quiz) {
        var prefix = $quiz.data("prefix");
        var $engine = $quiz.find("."+prefix+"Engine");
        if ($engine.data("original-state"))
            $engine.html($engine.data("original-state"));
    },

    /**
     * Display help of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    matchingHelp: function($quiz) {
        $.publiquiz.question.displayHelp($quiz);
    },

    /**
     * Retry quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    matchingRetry: function($quiz) {
        $quiz.removeData("quiz-result");
        $.publiquiz.question.retryQuizCmp($quiz);
    },

    /**
     * Compute score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Dictionnary}.
     */
    matchingComputeScore: function($quiz) {
        var noMark = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("nomark") > -1 )
            noMark = true;

        var result = {};
        if (noMark) {
            result.score = 0;
            result.total = 0;
            return result;
        }

        result = $quiz.data("quiz-result");
        if (result !== undefined)
            return result;

        result = $.publiquiz.question.scoreForQuizCmpCheck($quiz);
        $quiz.data("quiz-result", result);
        return result;
    },

    /**
     * Display score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    matchingScore: function($quiz) {
    },

    /**
     * Display quiz text answer.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    matchingTextAnswer: function($quiz) {
        $.publiquiz.question.displayTextAnswer($quiz);
    },

    /**
     * Insert user answers in html
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    matchingInsertUserAnswers: function($quiz) {
        $.publiquiz.question.inserUserAnswersQuizDrop($quiz);
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    matchingQuizAnswer: function($quiz, mode) {
        $.publiquiz.question.displayQuizCmpAnswer($quiz, mode);
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    matchingVerifyUserAnswer: function($quiz) {
        $.publiquiz.question.verifyQuizCmpAnswer($quiz, "user");
    },

    /**
     * Verify right answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    matchingVerifyRightAnswer: function($quiz) {
        $.publiquiz.question.verifyQuizCmpAnswer($quiz, "right");
    },

    /**
     * Verify full answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    matchingVerifyFullAnswer: function($quiz) {
        $.publiquiz.question.verifyQuizCmpAnswer($quiz, "full");
    },

    /**
     * Modified
     */
    matchingModified: function($quiz) {
        return $.publiquiz.context.modifyQuizCmpContext($quiz);
    },

    /**
     * Reload context
     */
    matchingLoadContext: function($quiz, dataClass) {
        $.publiquiz.context.loadQuizCmpContext($quiz, dataClass);
    }

    /**********************************************************************
     *                          Private Library
    **********************************************************************/

};

// Register function
$.publiquiz.question.register("matching", {
        configure: $.publiquiz.question.matching.matchingConfigure,
        enable: $.publiquiz.question.matching.matchingEnable,
        disable: $.publiquiz.question.matching.matchingDisable,
        redo: $.publiquiz.question.matching.matchingRedo,
        help: $.publiquiz.question.matching.matchingHelp,
        retry: $.publiquiz.question.matching.matchingRetry,
        textAnswer: $.publiquiz.question.matching.matchingTextAnswer,
        insertUserAnswers: $.publiquiz.question.matching.matchingInsertUserAnswers,
        quizAnswer: $.publiquiz.question.matching.matchingQuizAnswer,
        verifyUserAnswer: $.publiquiz.question.matching.matchingVerifyUserAnswer,
        verifyRightAnswer: $.publiquiz.question.matching.matchingVerifyRightAnswer,
        verifyFullAnswer: $.publiquiz.question.matching.matchingVerifyFullAnswer,
        computeScore: $.publiquiz.question.matching.matchingComputeScore,
        quizScore: $.publiquiz.question.matching.matchingScore,
        modified: $.publiquiz.question.matching.matchingModified,
        loadContext: $.publiquiz.question.matching.matchingLoadContext
    });

}(jQuery));


/******************************************************************************
 *
 *                                 Pointing
 *
 *****************************************************************************/

(function ($) {

$.publiquiz.question.pointing = {

    /**
     * Configure quiz.
     */
    pointingConfigure: function($quiz) {
        var prefix = $quiz.data("prefix");
        var $engine = $quiz.find("."+prefix+"Engine");
        if ($engine.data("original-state") === undefined)
            $engine.data("original-state", $engine.html());
    },

    /**
     * Set event click on point.
     *
     * @param {Object} jquery Object quiz.
     */
    pointingEnable: function($quiz) {
        var prefix = $quiz.data("prefix");

        // Event "click" for point
        $quiz.find("."+prefix+"Point").click( function(ev) {
            var $target = $(this);
            $.publiquiz.question.clearVerify();
            while (!$target.hasClass(prefix+"Point"))
                $target = $target.parentNode;
            $.publiquiz.question.pointing._onPoint($quiz, $target);
            $.publiquiz.context.onQuizModified($.publiquiz.question, $quiz);
        });
    },

    /**
     * Remove events listener on quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingDisable: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Point").unbind("click");
    },

    /**
     * Redo quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingRedo: function($quiz) {
        var prefix = $quiz.data("prefix");
        var $engine = $quiz.find("."+prefix+"Engine");
        if ($engine.data("original-state"))
            $engine.html($engine.data("original-state"));
    },

    /**
     * Display help of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingHelp: function($quiz) {
        $.publiquiz.question.displayHelp($quiz);
    },

    /**
     * Retry quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    pointingRetry: function($quiz) {
        $quiz.removeData("quiz-result");
        $.publiquiz.question.retryChoices($quiz, "Point");
    },

    /**
     * Compute score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Dictionnary}.
     */
    pointingComputeScore: function($quiz) {
        var noMark = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("nomark") > -1 )
            noMark = true;

        var result = {};
        if (noMark) {
            result.score = 0;
            result.total = 0;
            return result;
        }

        result = $quiz.data("quiz-result");
        if (result !== undefined)
            return result;

        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("radio") > -1 ) {
            result = $.publiquiz.question.scoreForQuizChoicesRadio($quiz);
        } else {
            result = $.publiquiz.question.scoreForQuizChoicesCheck($quiz, "Point");
        }
        $quiz.data("quiz-result", result);
        return result;
    },

    /**
     * Display score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingScore: function($quiz) {
    },

    /**
     * Display quiz text answer.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingTextAnswer: function($quiz) {
        $.publiquiz.question.displayTextAnswer($quiz);
    },

    /**
     * Insert user answers in html
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingInsertUserAnswers: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var answer = $.publiquiz.question.userAnswersQuizChoices($quiz, "Point");
        $.publiquiz.question.writeUserAnswers($quiz, quzId, answer.join("::"));
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    pointingQuizAnswer: function($quiz, mode) {
        $.publiquiz.question.displayQuizChoicesAnswer($quiz, "Point", mode);
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    pointingVerifyUserAnswer: function($quiz) {
        $.publiquiz.question.verifyQuizChoicesAnswer($quiz, "user");
    },

    /**
     * Verify only right answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    pointingVerifyRightAnswer: function($quiz) {
        $.publiquiz.question.verifyQuizChoicesAnswer($quiz, "right");
    },

    /**
     * Verify full answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    pointingVerifyFullAnswer: function($quiz) {
        $.publiquiz.question.verifyQuizChoicesAnswer($quiz, "full");
    },

    /**
     * Modified
     */
    pointingModified: function($quiz) {
        var engine = $quiz.data("engine");
        var changes = $.publiquiz.question.userAnswersQuizChoices($quiz, "Point");
        return {"data": changes.join("::"), "engine": engine};
    },

    /**
     * Reload context
     */
    pointingLoadContext: function($quiz, dataClass) {
        $.publiquiz.context.loadQuizChoicesContext($quiz, dataClass);
    },


    /**********************************************************************
     *                          Private Library
    **********************************************************************/

    /**
     * This function call when click on object with class pquizPoint.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @param {Object} Jquery object, object element pquizPoint.
     */
    _onPoint: function($quiz, $elem) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("radio") > -1 ) {
            $quiz.find("."+prefix+"Point").removeClass("selected");
            $elem.addClass("selected");
        } else {
            if ($elem.hasClass("selected"))
                $elem.removeClass("selected");
            else
                $elem.addClass("selected");
        }
    }

};

// Register function
$.publiquiz.question.register("pointing", {
        configure: $.publiquiz.question.pointing.pointingConfigure,
        enable: $.publiquiz.question.pointing.pointingEnable,
        disable: $.publiquiz.question.pointing.pointingDisable,
        redo: $.publiquiz.question.pointing.pointingRedo,
        help: $.publiquiz.question.pointing.pointingHelp,
        retry: $.publiquiz.question.pointing.pointingRetry,
        textAnswer: $.publiquiz.question.pointing.pointingTextAnswer,
        insertUserAnswers: $.publiquiz.question.pointing.pointingInsertUserAnswers,
        quizAnswer: $.publiquiz.question.pointing.pointingQuizAnswer,
        verifyUserAnswer: $.publiquiz.question.pointing.pointingVerifyUserAnswer,
        verifyRightAnswer: $.publiquiz.question.pointing.pointingVerifyRightAnswer,
        verifyFullAnswer: $.publiquiz.question.pointing.pointingVerifyFullAnswer,
        computeScore: $.publiquiz.question.pointing.pointingComputeScore,
        quizScore: $.publiquiz.question.pointing.pointingScore,
        modified: $.publiquiz.question.pointing.pointingModified,
        loadContext: $.publiquiz.question.pointing.pointingLoadContext
    });

}(jQuery));


/******************************************************************************
 *
 *                              Pointing-categories
 *
 *****************************************************************************/

(function ($) {

$.publiquiz.question.pointingCategories = {

    /**
     * Configure quiz.
     */
    pointingConfigure: function($quiz) {
        var prefix = $quiz.data("prefix");
        var $engine = $quiz.find("."+prefix+"Engine");
        if ($engine.data("original-state") === undefined)
            $engine.data("original-state", $engine.html());
    },

    /**
     * Set event click on point.
     *
     * @param {Object} jquery Object quiz.
     */
    pointingEnable: function($quiz) {
        var prefix = $quiz.data("prefix");

        // Event "click" for category
        $quiz.find("."+prefix+"Category").click( function(ev) {
            var $target = $(this);
            while (!$target.hasClass(prefix+"Category"))
                $target = $target.parentNode;
            $.publiquiz.question.pointingCategories._onCategory($quiz, $target);
        });

        // Event "click" for point
        $quiz.find("."+prefix+"Point").click( function(ev) {
            var $target = $(this);
            while (!$target.hasClass(prefix+"Point"))
                $target = $target.parentNode;
            $.publiquiz.question.pointingCategories._onPoint($quiz, $target);
            $.publiquiz.context.onQuizModified($.publiquiz.question, $quiz);
        });
    },

    /**
     * Remove events listener on quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingDisable: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Point").unbind("click");
        $quiz.find("."+prefix+"Category").unbind("click");
    },

    /**
     * Redo quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingRedo: function($quiz) {
        var prefix = $quiz.data("prefix");
        var $engine = $quiz.find("."+prefix+"Engine");
        if ($engine.data("original-state"))
            $engine.html($engine.data("original-state"));
    },

    /**
     * Display help of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingHelp: function($quiz) {
        $.publiquiz.question.displayHelp($quiz);
    },

    /**
     * Retry quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    pointingRetry: function($quiz) {
        $quiz.removeData("quiz-result");
        $.publiquiz.question.retryPointingCategory($quiz);
    },

    /**
     * Compute score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Dictionnary}.
     */
    pointingComputeScore: function($quiz) {
        var result = $quiz.data("quiz-result");
        if (result !== undefined)
            return result;

        result = $.publiquiz.question.scoreForQuizPointingCategories($quiz);
        $quiz.data("quiz-result", result);
        return result;
    },

    /**
     * Display score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingScore: function($quiz) {
    },

    /**
     * Display quiz text answer.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingTextAnswer: function($quiz) {
        $.publiquiz.question.displayTextAnswer($quiz);
    },

    /**
     * Insert user answers in html
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingInsertUserAnswers: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var answer = $.publiquiz.question.pointingCategories._userAnswer($quiz);
        $.publiquiz.question.writeUserAnswers($quiz, quzId, answer.join("::"));
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    pointingQuizAnswer: function($quiz, mode) {
        var quzId = $quiz.data("quiz-id");
        var answers = $.publiquiz.question.correctionCategories($quiz.find("#"+quzId+mode));
        $.publiquiz.question.pointingCategories._displayUserAnswer($quiz, answers);
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    pointingVerifyUserAnswer: function($quiz) {
        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");
        var res = $.publiquiz.question.correctionCategories($quiz.find("#"+quzId+"_correct"));
        var paramWrongAnswers = $.publiquiz.defaults.wrongAnswers;

        $quiz.find("."+prefix+"Point").each( function() {
            var $point = $(this);
            var category = $point.data("category-id");
            if (category && res[category]) {
                var pointId = $point.data("choice-id");
                var valid = res[category].search(pointId) > -1;
                $.publiquiz.question.addClassColorAnswer($quiz, $point, valid);
                if (!valid && paramWrongAnswers == "clear") {
                    $('body').queue(function(next) {
                        $point.removeClass("answerKo");
                        var classList = $point.attr("class").split(/\s+/);
                        if (classList.length > 1)
                            $point.removeClass(classList[classList.length - 1]);
                        next();
                    });
                }
           }
        });

        var duration = $quiz.data("verify-duration");
        if (duration > 0) {
            var timer = setTimeout($.publiquiz.question.clearVerify, duration);
            $.publiquiz.question.timers.push(timer);
        }
    },

    /**
     * Verify right answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    pointingVerifyRightAnswer: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var res = $.publiquiz.question.correctionCategories($quiz.find("#"+quzId+"_correct"));

        $quiz.find("."+prefix+"Point").each( function() {
            var $point = $(this);
            var category = $point.data("category-id");
            if (category) {
                var pointId = $point.data("choice-id");
                if (res[category].search(pointId) > -1)
                    $point.addClass("answerOk");
            }
        });
    },

    /**
     * Verify full answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    pointingVerifyFullAnswer: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var rightAnswers = $.publiquiz.question.correctionCategories($quiz.find("#"+quzId+"_correct"));
        var userAnswers = $.publiquiz.question.correctionCategories($quiz.find("#"+quzId+"_user"));

        $.each(rightAnswers, function(key, value) {
            var $category = $quiz.find("."+prefix+"Category").filter("[data-category-id=\""+key+"\"]");
            var res = [];
            if (userAnswers[key])
                res = userAnswers[key].split("|");
            $.each(value.split("|"), function(idx, data) {
                var $point = $quiz.find("."+prefix+"Point").filter("[data-choice-id=\""+data+"\"]");
                if ($.inArray(data, res) > -1)
                    $point.addClass("answerOk");
                else
                    $point.addClass("answerKo");
            });
        });
    },

    /**
     * Modified
     */
    pointingModified: function($quiz) {
        var engine = $quiz.data("engine");
        var changes = $.publiquiz.question.pointingCategories._userAnswer($quiz);
        return {"data": changes.join("::"), "engine": engine};
    },

    /**
     * Reload context
     */
    pointingLoadContext: function($quiz, dataClass) {
        var quzId = $quiz.data("quiz-id");
        var $context = $quiz.find("#"+quzId+"_context");
        var $data = $context.find(dataClass);
        var values = $.publiquiz.question.correctionCategories($data);
        $.publiquiz.question.pointingCategories._displayUserAnswer($quiz, values);
    },

    /**********************************************************************
     *                          Private Library
     **********************************************************************/

    /**
     * User answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @return {Array}
     */
    _userAnswer: function($quiz) {
        var answer = [];
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Point").each( function() {
            var $point = $(this);
            var category = $point.data("category-id");
            var pointId = $point.data("choice-id");
            if (category)
                answer.push(category + pointId);
        });

        return answer;
    },
    /**
     * Display answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {Object} $answer.
     */
    _displayUserAnswer: function($quiz, answer) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        // On enleve la category selected
        $quiz.find("."+prefix+"Category").removeClass("selected");

        // On enleve les couleurs
        $quiz.find("."+prefix+"Point").each( function() {
            var $point = $(this);
            $point.removeClass("answerOk answerKo");
            $point.data("category-id", "");
            var classList = $point.attr("class").split(/\s+/);
            if (classList.length > 1)
                $point.removeClass(classList[classList.length - 1]);
        });

        // On place les couleurs de la correction
        $.each(answer, function(key, value) {
            var $category = $quiz.find("."+prefix+"Category").filter("[data-category-id=\""+key+"\"]");
            var $categoryColor = $category.find("."+prefix+"CategoryColor");
            var color = $categoryColor.attr("class").split(/\s+/)[1];

            $.each(value.split("|"), function(idx, data) {
                var $point = $quiz.find("."+prefix+"Point").filter("[data-choice-id=\""+data+"\"]");
                $point.addClass(color);
                $point.data("category-id", key);
            });
        });
    },

    /**
     * This function call when click on object with class pquizCategory.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @param {Object} Jquery object, object element pquizCategory.
     */
    _onCategory: function($quiz, $elem) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        $quiz.find("."+prefix+"Category").removeClass("selected");
        $elem.addClass("selected");
    },

    /**
     * This function call when click on object with class pquizPoint.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @param {Object} Jquery object, object element pquizPoint.
     */
    _onPoint: function($quiz, $elem) {
        $.publiquiz.question.clearVerify();
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        var category = null;
        var color = null;
        var $selected = $quiz.find("."+prefix+"Category.selected");
        if ($selected.length > 0) {
            category = $selected.data("category-id");
            var $categoryColor = $selected.find("."+prefix+"CategoryColor");
            color = $categoryColor.attr("class").split(/\s+/)[1];
        }

        if (!category)
            return;

        var classList = $elem.attr("class").split(/\s+/);
        var categoryId = $elem.data("category-id");
        if (classList.length > 1 && categoryId == category) {
            $elem.removeClass(classList[classList.length - 1]);
            $elem.data("category-id", "");
            return;
        } else if (classList.length > 1) {
            $elem.removeClass(classList[classList.length - 1]);
        }
        $elem.data("category-id", category);
        $elem.addClass(color);
    }

};

// Register function
$.publiquiz.question.register("pointing-categories", {
        configure: $.publiquiz.question.pointingCategories.pointingConfigure,
        enable: $.publiquiz.question.pointingCategories.pointingEnable,
        disable: $.publiquiz.question.pointingCategories.pointingDisable,
        redo: $.publiquiz.question.pointingCategories.pointingRedo,
        help: $.publiquiz.question.pointingCategories.pointingHelp,
        retry: $.publiquiz.question.pointingCategories.pointingRetry,
        textAnswer: $.publiquiz.question.pointingCategories.pointingTextAnswer,
        insertUserAnswers: $.publiquiz.question.pointingCategories.pointingInsertUserAnswers,
        quizAnswer: $.publiquiz.question.pointingCategories.pointingQuizAnswer,
        verifyUserAnswer: $.publiquiz.question.pointingCategories.pointingVerifyUserAnswer,
        verifyRightAnswer: $.publiquiz.question.pointingCategories.pointingVerifyRightAnswer,
        verifyFullAnswer: $.publiquiz.question.pointingCategories.pointingVerifyFullAnswer,
        computeScore: $.publiquiz.question.pointingCategories.pointingComputeScore,
        quizScore: $.publiquiz.question.pointingCategories.pointingScore,
        modified: $.publiquiz.question.pointingCategories.pointingModified,
        loadContext: $.publiquiz.question.pointingCategories.pointingLoadContext
    });

}(jQuery));



/******************************************************************************
 *
 *                                  Categories
 *
 *****************************************************************************/


(function ($) {

$.publiquiz.question.categories = {

    /**
     * Configure quiz.
     */
    categoriesConfigure: function($quiz) {
        var prefix = $quiz.data("prefix");
        var $engine = $quiz.find("."+prefix+"Engine");
        var options = $quiz.data("engine-options") || "";
        if ($engine.data("original-state") === undefined)
            $engine.data("original-state", $engine.html());

        var noShuffle = (options.search("no-shuffle") > -1 );

        if (!noShuffle) {
            // Shuffle items for mode "basket"
            var $categoriesItems = $quiz.find("."+prefix+"CategoriesItems");
            // -- When multiple item categories, shuffle items inside "ItemsCat"
            if ($categoriesItems.find("."+prefix+"ItemsCat").length > 0) {
                $.publiquiz.question.shuffleItems($categoriesItems.find("."+prefix+"ItemsCat"));
            }
            else {
                $.publiquiz.question.shuffleItems($categoriesItems);
            }
            $.publiquiz.question.shuffleItems($quiz.find("."+prefix+"CategoriesLegendItems"));

            // Shuffle items for mode "color"
            if (options.search("color") > -1)
                $.publiquiz.question.shuffleItems($quiz.find("."+prefix+"CategoriesChoices"));

            // Shuffle "<tbody>" content for mode "grid"
            if (options.search("grid") > -1 )
                $.publiquiz.question.shuffleItems($quiz.find("table tbody"));
        }
    },

    /**
     * Set event click on Choice.
     *
     * @param {Object} jquery Object quiz.
     */
    categoriesEnable: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var options = $quiz.data("engine-options") || "";

        // ========== Event "draggable" on item for mode "basket"
        $.publiquiz.question.setDraggableItem($quiz, $quiz.find("."+prefix+"CategoryItem"), "Category");
        $.publiquiz.question.setDraggableItem($quiz, $quiz.find("."+prefix+"CategoryLegendItem"), "CategoryLegend");

        // ========== Event for mode "color"
        if (options.search("color") > -1 ) {

            // Event "click" on category for mode "color"
            $quiz.find("."+prefix+"Category").click( function(ev) {
                var $target = $(this);
                while (!$target.hasClass(prefix+"Category"))
                    $target = $target.parentNode;
                $.publiquiz.question.categories._onCategory($quiz, $target);
            });

            // Event "click" for point
            $quiz.find("."+prefix+"Choice").click( function(ev) {
                var $target = $(this);
                while (!$target.hasClass(prefix+"Choice"))
                    $target = $target.parentNode;
                $.publiquiz.question.categories._onChoice($quiz, $target);
                $.publiquiz.context.onQuizModified($.publiquiz.question, $quiz);
            });
        }

        // =========== Event for mode "grid"
        if (options.search("grid") > -1) {
            $quiz.find("."+prefix+"CategoryChoice input").removeAttr("disabled");
            $quiz.find("."+prefix+"CategoryChoice").click( function(ev) {
                var $target = $(this);
                $.publiquiz.question.categories._onCategoryChoice($quiz, $target);
                $.publiquiz.context.onQuizModified($.publiquiz.question, $quiz);
            });
        }
    },

    /**
     * Remove events listener on quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    categoriesDisable: function($quiz) {
        var prefix = $quiz.data("prefix");

        // ========== Disable event "draggable" on item for mode "basket"
        var evtStart = "mousedown touchstart";
        var $items = $quiz.find("."+prefix+"CategoryItem");
        var $legends = $quiz.find("."+prefix+"CategoryLegendItem");
        $items.unbind(evtStart);
        $legends.unbind(evtStart);

        // ========== Disable event for mode "color"
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("color") > -1 ) {
            $quiz.find("."+prefix+"Choice").unbind("click");
            $quiz.find("."+prefix+"Category").unbind("click");
        }

        // =========== Disable Event for mode "grid"
        $quiz.find("."+prefix+"CategoryChoice").unbind("click");
        $quiz.find("."+prefix+"CategoryChoice input").attr("disabled", "disabled");
    },

    /**
     * Redo quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    categoriesRedo: function($quiz) {
        var prefix = $quiz.data("prefix");
        var $engine = $quiz.find("."+prefix+"Engine");
        if ($engine.data("original-state"))
            $engine.html($engine.data("original-state"));
    },

    /**
     * Display help of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    categoriesHelp: function($quiz) {
        $.publiquiz.question.displayHelp($quiz);
    },

    /**
     * Retry quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    categoriesRetry: function($quiz) {
        $quiz.removeData("quiz-result");
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("grid") > -1 )
            $.publiquiz.question.categories._retryCategoryChoices($quiz);
        else
            $.publiquiz.question.retryCategories($quiz);
    },

    /**
     * Compute score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Dictionnary}.
     */
    categoriesComputeScore: function($quiz) {
        var noMark = false;
        var options = $quiz.data("engine-options") || "";
        if (options.search("nomark") > -1 )
            noMark = true;

        var result = {};
        if (noMark) {
            result.score = 0;
            result.total = 0;
            return result;
        }

        result = $quiz.data("quiz-result");
        if (result !== undefined)
            return result;

        if (options.search("color") > -1 )
            result = $.publiquiz.question.categories._computeScoreColor($quiz);
        else if (options.search("grid") > -1 )
            result = $.publiquiz.question.categories._computeScoreChoices($quiz);
        else if (options.search("float") > -1 )
            result = $.publiquiz.question.categories._computeScoreFloatBasket($quiz);
        else
            result = $.publiquiz.question.categories._computeScoreBasket($quiz);
        $quiz.data("quiz-result", result);
        return result;
    },

    /**
     * Display score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    categoriesScore: function($quiz) {
    },

    /**
     * Display quiz text answer.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    categoriesTextAnswer: function($quiz) {
        $.publiquiz.question.displayTextAnswer($quiz);
    },

    /**
     * Insert user answers in html
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    categoriesInsertUserAnswers: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var options = $quiz.data("engine-options") || "";
        var answer = [];
        if (options.search("color") > -1 ) {
            answer = $.publiquiz.question.categories._userAnswersColor($quiz);
        } else if (options.search("grid") > -1 ) {
            answer = $.publiquiz.question.categories._userAnswersChoices($quiz);
        } else if (options.search("float") > -1 ) {
            var res = $.publiquiz.question.categories._userAnswersFloatBasket($quiz);
            var legend = res[0];
            answer = res[1];

            // Write legend
            var $userAnswerLegend = $quiz.find("#"+quzId+"_legend_user");
            if ($userAnswerLegend.length === 0) {
                var $quizAnswer = $quiz.find("#"+quzId+"_correct");
                $userAnswerLegend = $("<div>")
                    .attr("id", quzId+"_legend_user")
                    .addClass("hidden");
                $userAnswerLegend.insertAfter($quizAnswer);
            }
            $userAnswerLegend.text(legend.join("::"));
        } else {
            answer = $.publiquiz.question.categories._userAnswersBasket($quiz);
        }

        $.publiquiz.question.writeUserAnswers($quiz, quzId, answer.join("::"));
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    categoriesQuizAnswer: function($quiz, mode) {
        var quzId = $quiz.data("quiz-id");
        var options = $quiz.data("engine-options") || "";
        var answers;
        if (options.search("color") > -1 ) {
            answers = $.publiquiz.question.correctionCategories($quiz.find("#"+quzId+mode));
            $.publiquiz.question.categories._quizAnswersColor($quiz, answers);
        } else if (options.search("grid") > -1 ) {
            answers = $.publiquiz.question.correctionCategories($quiz.find("#"+quzId+mode));
            $.publiquiz.question.categories._quizAnswersChoices($quiz, answers);
        } else if (options.search("float") > -1 ) {
            $.publiquiz.question.categories._quizAnswersFloatBasket($quiz, mode);
        } else {
            $.publiquiz.question.categories._quizAnswersBasket($quiz, mode);
        }
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    categoriesVerifyUserAnswer: function($quiz) {
        var options = $quiz.data("engine-options") || "";
        if (options.search("color") > -1 )
            $.publiquiz.question.categories._verifyAnswersColor($quiz, "user");
        else if (options.search("grid") > -1 )
            $.publiquiz.question.categories._verifyAnswersChoices($quiz, "user");
        else if (options.search("float") > -1 )
            $.publiquiz.question.categories._verifyAnswersFloatBasket($quiz, "user");
        else
            $.publiquiz.question.categories._verifyAnswersBasket($quiz, "user");
    },

    /**
     * Verify right answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    categoriesVerifyRightAnswer: function($quiz) {
        var options = $quiz.data("engine-options") || "";
        if (options.search("color") > -1 )
            $.publiquiz.question.categories._verifyAnswersColor($quiz, "right");
        else if (options.search("grid") > -1 )
            $.publiquiz.question.categories._verifyAnswersChoices($quiz, "right");
        else if (options.search("float") > -1 )
            $.publiquiz.question.categories._verifyAnswersFloatBasket($quiz, "right");
        else
            $.publiquiz.question.categories._verifyAnswersBasket($quiz, "right");
    },

    /**
     * Verify full answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    categoriesVerifyFullAnswer: function($quiz) {
        var options = $quiz.data("engine-options") || "";
        if (options.search("color") > -1 )
            $.publiquiz.question.categories._verifyAnswersColor($quiz, "full");
        else if (options.search("grid") > -1 )
            $.publiquiz.question.categories._verifyAnswersChoices($quiz, "full");
        else if (options.search("float") > -1 )
            $.publiquiz.question.categories._verifyAnswersFloatBasket($quiz, "full");
        else
            $.publiquiz.question.categories._verifyAnswersBasket($quiz, "full");
    },

    /**
     * Modified
     */
    categoriesModified: function($quiz) {
        var changes = [];
        var quzId = $quiz.data("quiz-id");
        var engine = $quiz.data("engine");
        var prefix = $quiz.data("prefix");
        var options = $quiz.data("engine-options") || "";

        if (options.search("color") > -1 ) {
            changes = $.publiquiz.question.categories._userAnswersColor($quiz);
        } else if (options.search("grid") > -1 ) {
            changes = $.publiquiz.question.categories._userAnswersChoices($quiz);
        } else if (options.search("float") > -1 ) {
            var res = $.publiquiz.question.categories._userAnswersFloatBasket($quiz);
            var legends = res[0];
            changes = res[1];
            return {"data": changes.join("::"), "engine": engine, "legend": legends.join("::")};
        } else {
            changes = $.publiquiz.question.categories._userAnswersBasket($quiz);
        }

        return {"data": changes.join("::"), "engine": engine};
    },

    /**
     * Reload context
     */
    categoriesLoadContext: function($quiz, dataClass) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var engine = $quiz.data("engine");
        var options = $quiz.data("engine-options") || "";
        var isMultiple = (options.search("multiple") > -1);
        var isCounter = (options.search("counter") > -1);
        var $context = $quiz.find("#"+quzId+"_context");
        var $data = $context.find(dataClass);
        var countAvailable = false;

        var values = $.publiquiz.question.correctionCategories($data);

        if (options.search("color") > -1 ) {
            $.publiquiz.question.categories._quizAnswersColor($quiz, values);
        } else if (options.search("grid") > -1 ) {
            $.publiquiz.question.categories._quizAnswersChoices($quiz, values);
        } else if (options.search("float") > -1 ) {
            var $legends = $quiz.find("#"+quzId+"_legend_items");
            var $userLegends = $context.find(".legend");
            $.each($userLegends, function(key, value) {
                var $legend = $legends.find("."+prefix+"CategoryLegendItem").filter("[data-item-value=\""+value+"\"]");
                var $legendDrop = $quiz.find("#"+quzId+"_"+key);
                $legendDrop.text("");
                $legendDrop.removeClass(prefix+"Dots");
                $legend.appendTo($legendDrop)
                    .addClass(prefix+"CategoryLegendItemDropped");
            });

            $.each(values, function(k, v) {
                var $dropbox = $quiz.find("#"+quzId+"_"+k);
                $.each(v.split("|"), function(idx, data) {
                    var $item = $items.find("."+prefix+"CategoryItem")
                        .filter("[data-item-value=\""+data+"\"]");
                    if (isMultiple)
                        $item = $item.clone();
                    $item.appendTo($dropbox)
                        .addClass(prefix+"CategoryItemDropped");
                });
            });
        } else {
            var $items = $quiz.find("#"+quzId+"_items");
            $.each(values, function(k, v) {
                var $drop = $quiz.find("#"+quzId+"_"+k);
                $.each(v.split("|"), function(idx, data) {
                    var $item = $items.find("."+prefix+"CategoryItem")
                        .filter("[data-item-value=\""+data+"\"]");
                    if ($item.length === 0)
                        return true;
                    if (isCounter)
                        countAvailable = $.publiquiz.question.counterItemAvailable($quiz, $item);
                    if (isMultiple || countAvailable) {
                        var count = $quiz.find("."+prefix+"CategoryItem").length;
                        $item = $item.clone();
                        $item.attr("id", quzId+"_item"+$.publiquiz.question.formatNumber(count += 100, 3));
                    }
                    $item.appendTo($drop).addClass(prefix+"CategoryItemDropped");
                    $.publiquiz.question.setAudioPlayable($quiz, $item);
                    return true;
                });
            });
        }
    },


    /**********************************************************************
     *                          Private Library
     **********************************************************************/

    /**
     * This function call when click on object with class pquizCategory.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @param {Object} Jquery object, object element pquizCategory.
     */
    _onCategory: function($quiz, $elem) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        $quiz.find("."+prefix+"Category").removeClass("selected");
        $elem.addClass("selected");
    },

    /**
     * This function call when click on object with class pquizChoice.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @param {Object} Jquery object, object element pquizPoint.
     */
    _onChoice: function($quiz, $elem) {
        $.publiquiz.question.clearVerify();
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;

        var category = null;
        var color = null;
        var $selected = $quiz.find("."+prefix+"Category.selected");
        if ($selected.length > 0) {
            category = $selected.data("category-id");
            var $categoryColor = $selected.find("."+prefix+"CategoryColor");
            var $classList = $categoryColor.attr("class").split(/\s+/);
            color = $classList[$classList.length - 1];
        }

        if (!category)
            return;

        if (isMultiple) {
            // On verifie que le target n'appartient pas deja cette categorie si
            // c'est le cas on retire la categorie
            var hasCategory = false;
            $elem.find("."+prefix+"ItemColor").each( function() {
                var $item = $(this);
                if ($item.data("category-id") == category) {
                    $item.remove();
                    hasCategory = true;
                    return false;
                }
                return true;
            });

            if (hasCategory)
                return;

            // Ajout d'un item color
            var $item = $(document.createElement("span"));
            $item.addClass(prefix+"ItemColor " + color);
            $item.data("category-id", category);
            $item.appendTo($elem);

        } else {
            var classList = $elem.attr("class").split(/\s+/);
            if (classList.length > 1)
                $elem.removeClass(classList[classList.length - 1]);
            $elem.data("category-id", category);
            $elem.addClass(color);
        }
    },

    /**
     * This function call when click on object class pquizCategoryChoice.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @param {Object} Jquery object, object element pquizCategoryChoice.
     */
    _onCategoryChoice: function($quiz, $elem) {
        $.publiquiz.question.clearVerify();
        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");
        var $engine = $quiz.find("#"+quzId+"_engine");
        var $input = $elem.find("input");
        var options = $quiz.data("engine-options") || "";
        var isMultiple = (options.search("multiple") > -1 );

        if ($elem.hasClass("selected")) {
            $elem.removeClass("selected");
            if ($input)
                $input.prop("checked", false);
            return;
        }

        var group = $elem.data("group");
        if (!isMultiple) {
            $engine.find("."+prefix+"CategoryChoice")
                .filter("[data-group=\""+group+"\"]")
                .removeClass("selected");
        }
        $elem.addClass("selected");
        if ($input)
            $input.prop("checked", true);
    },

    /**
     * Retry quiz categories option grid, keep only right answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    _retryCategoryChoices: function($quiz) {
        $.publiquiz.question.clearVerify();
        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");
        var res = $.publiquiz.question.correctionCategories(
                $quiz.find("#"+quzId+"_correct"));

        $quiz.find("."+prefix+"CategoryChoice").filter(".selected").each( function() {
            var $this = $(this);
            var grp = $this.data("group");
            var $item = $quiz.find("#"+quzId+"_item"+grp);
            if ($.inArray($item.data("item-value"),
                    res[$this.data("category-id")].split("|")) == -1) {
                $this.find("input").prop("checked", false);
                $this.removeClass("selected");
            }
        });
    },

    /**
     * This function compute score for categories mode "basket" option "float".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @return {Dictionnary}.
     */
    _computeScoreFloatBasket: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;

        var total = 0;
        var score = 0;
        var res = $.publiquiz.question.correctionCategories(
                $quiz.find("#"+quzId+"_correct"));

        // Listes des intrus
        var values = [];
        var intrus = [];
        $.each(res, function(key, value) { values = $.merge(values, value.split("|")); });
        $quiz.find("."+prefix+"CategoryItem").each( function() {
            var $item = $(this);
            var value = $item.data("item-value").toString();
            if ($.inArray(value, values) == -1)
                intrus.push(value);
            else
                total += 1;
        });

        $quiz.find("."+prefix+"CategoryLegendDrop").each( function() {
            var $dropboxLegend = $(this);
            var $legend = $dropboxLegend.find("."+prefix+"CategoryLegendItem");
            if ($legend.length === 0 )
                return true;
            var legendId = $legend.attr("id");
            legendId = legendId.substring(legendId.length - 3, legendId.length);
            if (!res[legendId])
                return true;
            var $dropbox = $dropboxLegend.parent().find("."+prefix+"CategoryDrop");
            // Vrai items
            $.each(res[legendId].split("|"), function(idx, data) {
                var $item = $dropbox.find("."+prefix+"CategoryItem")
                    .filter("[data-item-value=\""+data+"\"]");
                if ($item.length > 0)
                    score += 1;
            });
            // Intrus
            $.each(intrus, function(idx, data) {
                var $item = $dropbox.find("."+prefix+"CategoryItem")
                    .filter("[data-item-value=\""+data+"\"]");
                if ($item.length > 0)
                    score -= 1;
            });
        });

        if (score < 0)
            score = 0;

        var result = {};
        result.score = score;
        result.total = total;
        return result;
    },

    /**
     * This function compute score for categories mode "basket".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @return {Dictionnary}.
     */
    _computeScoreBasket: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;

        var total = 0;
        var score = 0;
        var res = $.publiquiz.question.correctionCategories(
                $quiz.find("#"+quzId+"_correct"));

        // Listes des intrus
        var values = [];
        var intrus = [];
        $.each(res, function(key, value) { values = $.merge(values, value.split("|")); });
        $quiz.find("."+prefix+"CategoryItem").each( function() {
            var $item = $(this);
            var value = $item.data("item-value").toString();
            if( $.inArray(value, values) == -1)
                intrus.push(value);
        });

        // Score
        $.each(res, function(key, value) {
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            // Vrai items
            $.each(value.split("|"), function(idx, data) {
                data = data.replace(/\\/g, '\\\\');
                var $item = $dropbox.find("."+prefix+"CategoryItem")
                    .filter("[data-item-value=\""+data+"\"]");
                if ($item.length > 0)
                    score += 1;
                total += 1;
            });

            // Intrus
            $.each(intrus, function(idx, data) {
                var $item = $dropbox.find("."+prefix+"CategoryItem")
                    .filter("[data-item-value=\""+data+"\"]");
                if ($item.length > 0)
                    score -= 1;
            });
        });

        if (score < 0)
            score = 0;

        var result = {};
        result.score = score;
        result.total = total;
        return result;
    },

    /**
     * This function compute score for categories mode "color".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @return {Dictionnary}.
     */
    _computeScoreColor: function($quiz) {
        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;

        var score = 0;
        var total = 0;
        var res = $.publiquiz.question.correctionCategories(
            $quiz.find("#"+quzId+"_correct"));

        // Total
        $.each(res, function(key, value) {
            total += value.split("|").length;
        });

        // Score
        $quiz.find("."+prefix+"Choice").each( function() {
            var $choice = $(this);
            var value = String($choice.data("choice-value"));
            if (isMultiple) {
                $choice.find("."+prefix+"ItemColor").each( function() {
                    var $item = $(this);
                    var category = $item.data("category-id");
                    if ($.inArray(value, res[category].split("|")) >= 0)
                        score += 1;
                });
            } else {
                var category = $choice.data("category-id");
                if (category && $.inArray(value, res[category].split("|")) >= 0)
                    score += 1;
            }
        });

        var result = {};
        result.score = score;
        result.total = total;
        return result;
    },

    /**
     * This function compute score for categories mode "grid".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @return {Dictionnary}.
     */
    _computeScoreChoices: function($quiz) {
        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");

        var score = 0;
        var total = 0;
        var res = $.publiquiz.question.correctionCategories(
            $quiz.find("#"+quzId+"_correct"));
        var $engine = $quiz.find("#"+quzId+"_engine");

        // Get group
        var choices = [];
        $quiz.find("."+prefix+"CategoryChoice").each( function() {
            var group = $(this).data("group");
            if ($.inArray(group, choices) < 0 )
                choices.push(group);
        });

        // Compute score
        // Total
        $.each(res, function(key, value) {
            total += value.split("|").length;
        });

        // Score
        $.each(choices, function() {
            var group = this;
            var items = $engine.find("."+prefix+"CategoryChoice")
                            .filter("[data-group=\""+group+"\"]")
                            .filter(".selected");
            $.each(items, function() {
                var $item = $(this);
                var catId = $item.data("category-id");
                var _$item = $engine.find("#"+quzId+"_item"+group);
                if (res[catId] && $.inArray(_$item.data("item-value").toString(),
                        res[catId].split("|")) >= 0)
                    score += 1;
            });
        });

        var result = {};
        result.score = score;
        result.total = total;
        return result;
    },

    /**
     * Insert user answers in html for mode "basket" option "float"
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Array}
     */
    _userAnswersFloatBasket: function($quiz) {
        var res = [];
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        // Legend
        var legend = [];
        $quiz.find("."+prefix+"CategoryLegendDrop").each( function() {
            var $dropbox = $(this);
            var key = $dropbox.attr("id");
            key = key.substring(key.length - 3, key.length);
            $dropbox.find("."+prefix+"CategoryLegendItem").each( function() {
                var $item = $(this);
                var value = $item.data("item-value");
                legend.push(key + value);
            });
        });
        res.push(legend);

        // Item
        var answer = [];
        $quiz.find("."+prefix+"CategoryDrop").each( function() {
            var $dropbox = $(this);
            var key = $dropbox.attr("id");
            key = key.substring(key.length - 3, key.length);
            $dropbox.find("."+prefix+"CategoryItem").each( function() {
                var $item = $(this);
                var value = $item.data("item-value");
                answer.push(key + value);
            });
        });
        res.push(answer);

        return res;
    },

    /**
     * User answers in html for mode "basket"
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Array}
     */
    _userAnswersBasket: function($quiz) {
        var answer = [];
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"CategoryDrop").each( function() {
            var $dropbox = $(this);
            var key = $dropbox.attr("id");
            key = key.substring(key.length - 3, key.length);
            $dropbox.find("."+prefix+"CategoryItem").each( function() {
                answer.push(key + $(this).data("item-value"));
            });
        });
        return answer;
    },

    /**
     * User answers in html for mode "color"
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Array}
     */
    _userAnswersColor: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;

        var answer = [];
        $quiz.find("."+prefix+"Choice").each( function() {
            var $choice = $(this);
            var value = String($choice.data("choice-value"));
            if (isMultiple) {
                $choice.find("."+prefix+"ItemColor").each( function() {
                    var $item = $(this);
                    var category = $item.data("category-id");
                    answer.push(category + value);
                });
            } else {
                var category = $choice.data("category-id");
                if (category)
                    answer.push(category + value);
            }
        });
        return answer;
    },

    /**
     * User answers in html for mode "grid"
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Array}
     */
    _userAnswersChoices: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        var answer = [];
        $quiz.find("."+prefix+"CategoryChoice").filter(".selected").each( function() {
            var $choice = $(this);
            var grp = $choice.data("group");
            var $item = $quiz.find("#"+quzId+"_item"+grp);
            var value = $item.data("item-value");
            answer.push($choice.data("category-id") + value);
        });

        return answer;
    },

    /**
     * Display right/user answer for quiz mode "basket" option "float".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    _quizAnswersFloatBasket: function($quiz, mode) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;
        var $answers = $.publiquiz.question.correctionCategories($quiz.find("#"+quzId+mode));
        var $items = $quiz.find("#"+quzId+"_items");
        var $legends = $quiz.find("#"+quzId+"_legend_items");

        // On enleve la correction
        $quiz.find("."+prefix+"CategoryLegendItemDropped")
            .appendTo($legends)
            .removeClass(prefix+"CategoryLegendItemDropped");
        $quiz.find("."+prefix+"CategoryLegendDrop").addClass(prefix+"Dots");
        if (isMultiple) {
            $quiz.find("."+prefix+"CategoryItemDropped").remove();
        } else {
            $quiz.find("."+prefix+"CategoryItemDropped")
                .appendTo($items)
                .removeClass(prefix+"CategoryItemDropped answerKo");
        }

        // On place la correction/réponse en déplacant les items
        // ou bien en les clonant si "isMultiple" est a true
        $items.removeClass("answer");
        if (mode == "_user") {
            var $userLegends = $.publiquiz.question.correction($quiz.find("#"+quzId+"_legend"+mode));
            $.each($userLegends, function(key, value) {
                var $legend = $legends.find("."+prefix+"CategoryLegendItem").filter("[data-item-value=\""+value+"\"]");
                var $legendDrop = $quiz.find("#"+quzId+"_"+key);
                $legendDrop.text("");
                $legendDrop.removeClass(prefix+"Dots");
                $legend.appendTo($legendDrop)
                    .addClass(prefix+"CategoryLegendItemDropped");
            });
        }

        $.each($answers, function(key, value) {
            var $dropbox = null;
            var $legend = $quiz.find("#"+quzId+"_legend_item"+key);

            if (mode == "_correct") {
                // On place la legend
                $quiz.find("."+prefix+"CategoriesBasket").each( function() {
                    var $basket = $(this);
                    var $legendDrop = $basket.find("."+prefix+"CategoryLegendDrop");
                    $dropbox = $basket.find("."+prefix+"CategoryDrop");

                    if ($legendDrop.find("."+prefix+"CategoryLegendItem").length === 0) {
                        $legendDrop.text("");
                        $legendDrop.removeClass(prefix+"Dots");
                        $legend.appendTo($legendDrop)
                            .addClass(prefix+"CategoryLegendItemDropped");
                        return false;
                    }
                });
            } else {
                $dropbox = $quiz.find("#"+quzId+"_"+key);
            }

            // On place les items
            $dropbox.removeClass("answer");
            $.each(value.split("|"), function(idx, data) {
                var $item = $items.find("."+prefix+"CategoryItem").filter("[data-item-value=\""+data+"\"]");
                if (isMultiple)
                    $item = $item.clone();
                $item.appendTo($dropbox)
                    .addClass(prefix+"CategoryItemDropped");
            });

            if (mode == "_correct")
                $dropbox.addClass("answer");
        });
    },

    /**
     * Display right/user answer for quiz mode "basket".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    _quizAnswersBasket: function($quiz, mode) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var options = $quiz.data("engine-options") || "";
        var isMultiple = (options.search("multiple") > -1);
        var isCounter = (options.search("counter") > -1);
        var answers = $.publiquiz.question.correctionCategories($quiz.find("#"+quzId+mode));
        var $items = $quiz.find("#"+quzId+"_items");

        // On enleve la correction
        if (isMultiple) {
            $quiz.find("."+prefix+"CategoryItemDropped").remove();
        } else if (isCounter) {
            $quiz.find("."+prefix+"CategoryItemDropped").each(function() {
                var $item = $(this);
                $item.removeClass("answerKo");
                $.publiquiz.question.counterRemoveItem($quiz, $item, $items, "Category");
            });
        } else {
            $quiz.find("."+prefix+"CategoryItemDropped")
                .appendTo($items)
                .removeClass(prefix+"CategoryItemDropped answerKo");
        }

        // On place la correction en deplacant les items
        // ou bien en les clonant si "isMultiple" est a true
        $items.removeClass("answer");
        $.each(answers, function(key, value) {
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            $dropbox.removeClass("answer");
            $.each(value.split("|"), function(idx, data) {
                data = data.replace(/\\/g, '\\\\');
                var $item = $items.find("."+prefix+"CategoryItem").filter("[data-item-value=\""+data+"\"]");
                if (isCounter) {
                    $.publiquiz.question.counterPickItem($quiz, $item, $dropbox, "Category");
                } else {
                    if (isMultiple)
                        $item = $item.clone();
                    $item.appendTo($dropbox)
                        .addClass(prefix+"CategoryItemDropped");
                }
            });

            if (mode == "_correct")
                $dropbox.addClass("answer");
        });
    },

    /**
     * Display answer for quiz mode "color".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {Object} answers : display correct/user answer.
     */
    _quizAnswersColor: function($quiz, answers) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;

        // On enleve la category selected
        $quiz.find("."+prefix+"Category").removeClass("selected");

        // On enleve les couleurs
        $quiz.find("."+prefix+"Choice").each( function() {
            var $choice = $(this);
            if (isMultiple) {
                $choice.find("."+prefix+"ItemColor").remove();
            } else {
                $choice.removeClass("answerOk answerKo");
                $choice.data("category-id", "");
                var classList = $choice.attr("class").split(/\s+/);
                if (classList.length > 1)
                    $choice.removeClass(classList[classList.length - 1]);
            }
        });

        // On place les couleurs de la correction
        $.each(answers, function(key, data) {
            var $category = $quiz.find("."+prefix+"Category")
                .filter("[data-category-id=\""+key+"\"]");
            var $categoryColor = $category.find("."+prefix+"CategoryColor");
            var $classList = $categoryColor.attr("class").split(/\s+/);
            var color = $classList[$classList.length-1];

            $.each(data.split("|"), function(idx, value) {
                var $choice = $quiz.find("."+prefix+"Choice")
                    .filter("[data-choice-value=\""+value+"\"]");
                if ($choice.length > 0) {
                    if (isMultiple) {
                        var $item = $(document.createElement("span"));
                        $item.addClass(prefix+"ItemColor " + color);
                        $item.data("category-id", key);
                        $item.appendTo($choice);
                    } else {
                        $choice.addClass(color);
                        $choice.data("category-id", key);
                    }
                }
            });
        });
    },

    /**
     * Display answer for quiz mode "grid".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {Object} answers.
     */
    _quizAnswersChoices: function($quiz, answers) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        // Reset quiz
        $quiz.find("."+prefix+"CategoryChoice input").prop("checked", false);
        $quiz.find("."+prefix+"CategoryChoice").removeClass(
                "selected answerOk answerKo");

        $.each(answers, function(key, data) {
            var values = data.split("|");
            var $items = $quiz.find("."+prefix+"CategoryChoice")
                            .filter("[data-category-id=\""+key+"\"]");
            $items.each(function() {
                var $choice = $(this);
                var grp = $choice.data("group");
                var $item = $quiz.find("#"+quzId+"_item"+grp);
                var value = $item.data("item-value").toString();
                if ($.inArray(value, values) >= 0) {
                    $choice.find("input").prop("checked", true);
                    $choice.addClass("selected");
                }
            });
        });
    },

    /**
     * Verify user answer for mode "basket" option "float".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : "full", "right" or "user" color.
     */
    _verifyAnswersFloatBasket: function($quiz, mode) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;
        var rightAnswers = $.publiquiz.question.correctionCategories(
                $quiz.find("#"+quzId+"_correct"));
        var userAnswers = $.publiquiz.question.correctionCategories(
                $quiz.find("#"+quzId+"_user"));
        var legendAnswers = $.publiquiz.question.correction(
                $quiz.find("#"+quzId+"_legend_user"));
        var $items = $quiz.find("#"+quzId+"_items");

        $quiz.find("."+prefix+"CategoryLegendDrop").each( function() {
            var $dropboxLegend = $(this);
            var $dropbox = $dropboxLegend.parent().find("."+prefix+"CategoryDrop");
            $dropbox.addClass("answer");
            var $legend = $dropboxLegend.find("."+prefix+"CategoryLegendItem");
            if ($legend.length === 0 )
                return true;
            var legendId = $legend.attr("id");
            legendId = legendId.substring(legendId.length - 3, legendId.length);

            // Validation des catégories intrus
            if (!rightAnswers[legendId]) {
                if (mode == "user" || mode == "full") {
                    $.publiquiz.question.addClassColorAnswer($quiz, $legend, false);
                    $dropbox.find("."+prefix+"CategoryItem").each( function() {
                        $.publiquiz.question.addClassColorAnswer($quiz, $(this), false);
                    });
                }
                return true;
            }

            // Validation de la legend
            var dropboxId = "";
            var legendUsed = false;
            var legendValue = $legend.data("item-value");
            $.each(legendAnswers, function(k, v) {
                if (legendValue == v) {
                    legendUsed = true;
                    return false;
                }
                return true;
            });

            if (mode == "user" || mode == "full" || (mode == "right" && legendUsed))
                $.publiquiz.question.addClassColorAnswer($quiz, $legend, legendUsed);

            // On récupére les réponse de l'utilisateur pour cette légende
            $.each(legendAnswers, function(key, value) {
                if ($legend.data("item-value") == value) {
                    var _$dropbox = $quiz.find("#"+quzId+"_"+key).parent().find("."+prefix+"CategoryDrop");
                    dropboxId = _$dropbox.attr("id");
                    dropboxId = dropboxId.substring(dropboxId.length - 3, dropboxId.length);
                    return false;
                }
            });

            // Validation des items
            var values = rightAnswers[legendId].split("|");
            $dropbox.find("."+prefix+"CategoryItem").each( function() {
                var $item = $(this);
                var data = $item.data("item-value").toString();
                if (mode == "user") {
                    var valid = $.inArray(data, values) >= 0;
                    $.publiquiz.question.addClassColorAnswer($quiz, $item, valid);
                } else if (mode == "right") {
                    if ($.inArray(data, values) >= 0)
                        $.publiquiz.question.addClassColorAnswer($quiz, $item, true);
                } else {
                    var userAnswer = userAnswers[dropboxId];
                    if (userAnswer) {
                        userAnswer = userAnswer.split("|");
                        if ($.inArray(data, values) >= 0 && $.inArray(data, userAnswer) >= 0)
                            $.publiquiz.question.addClassColorAnswer($quiz, $item, true);
                        else
                            $.publiquiz.question.addClassColorAnswer($quiz, $item, false);
                    } else {
                        $.publiquiz.question.addClassColorAnswer($quiz, $item, false);
                    }
                }
            });
        });

        var duration = $quiz.data("verify-duration");
        if (duration > 0) {
            var timer = setTimeout($.publiquiz.question.clearVerify, duration);
            $.publiquiz.question.timers.push(timer);
        }

        if (mode == "user" || isMultiple)
            return;

        // Gestion des intrus
        var $legends = $quiz.find("#"+quzId+"_legend_items");
        $legends.addClass("answer");
        $legends.find("."+prefix+"CategoryLegendItem").each( function() {
            var $legend = $(this);
            var lId = $legend.attr("id");
            lId = lId.substring(lId.length - 3, lId.length);
            var value = $legend.data("item-value").toString();
            var used = false;
            var isIntru = true;

            $.each(legendAnswers, function(k, v) {
                if (value == v) {
                    used = true;
                    return false;
                }
                return true;
            });

            if (rightAnswers[lId])
                isIntru = false;

            if (isIntru && !used)
                $legend.addClass("answerOk");
            else
                if (mode != "right")
                    $legend.addClass("answerKo");
        });

        $items.addClass("answer");
        $items.find("."+prefix+"CategoryItem").each( function() {
            var $item = $(this);
            var value = $item.data("item-value").toString();
            var used = false;
            var isIntru = true;
            $.each(userAnswers, function(k, v) {
                if ($.inArray(value, v.split("|")) > -1) {
                    used = true;
                    return false;
                }
                return true;
            });
            $.each(rightAnswers, function(k, v) {
                if ($.inArray(value, v.split("|")) > -1) {
                    isIntru = false;
                    return false;
                }
                return true;
            });

            if (isIntru && !used)
                $item.addClass("answerOk");
            else
                if (mode != "right")
                    $item.addClass("answerKo");
        });
    },

    /**
     * Verify user answer for mode "basket".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : "full", "right" or "user" color.
     */
    _verifyAnswersBasket: function($quiz, mode) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;
        var rightAnswers = $.publiquiz.question.correctionCategories(
                $quiz.find("#"+quzId+"_correct"));
        var userAnswers = $.publiquiz.question.correctionCategories(
                $quiz.find("#"+quzId+"_user"));
        var $items = $quiz.find("#"+quzId+"_items");

        var paramWrongAnswers = $.publiquiz.defaults.wrongAnswers;
        $.each(rightAnswers, function(key, value) {
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            $dropbox.addClass("answer");
            var values = value.split("|");
            $dropbox.find("."+prefix+"CategoryItem").each( function() {
                var $item = $(this);
                var data = $item.data("item-value").toString();
                var valid;
                if (mode == "user") {
                    valid = $.inArray(data, values) >= 0;
                    $.publiquiz.question.addClassColorAnswer($quiz, $item, valid);
                    if (!valid && paramWrongAnswers == "clear") {
                        $('body').queue(function(next) {
                            if (isMultiple)
                                $item.remove();
                            else
                                $item.removeClass(prefix+"CategoryItemDropped").animateMoveElement($items);
                            next();
                        });
                    }
                } else if (mode == "right") {
                    if ($.inArray(data, values) >= 0)
                        $.publiquiz.question.addClassColorAnswer($quiz, $item, true);
                } else {
                    var userAnswer = userAnswers[key];
                    if (userAnswer) {
                        userAnswer = userAnswer.split("|");
                        if ($.inArray(data, values) >= 0 && $.inArray(data, userAnswer) >= 0)
                            $.publiquiz.question.addClassColorAnswer($quiz, $item, true);
                        else
                            $.publiquiz.question.addClassColorAnswer($quiz, $item, false);
                    } else {
                        $.publiquiz.question.addClassColorAnswer($quiz, $item, false);
                    }
                }

            });

        });

        var duration = $quiz.data("verify-duration");
        if (duration > 0) {
            var timer = setTimeout($.publiquiz.question.clearVerify, duration);
            $.publiquiz.question.timers.push(timer);
        }

        if (mode == "user" || isMultiple)
            return;

        // Gestion des intrus
        $items.addClass("answer");
        $items.find("."+prefix+"CategoryItem").each( function() {
            var $item = $(this);
            var value = $item.data("item-value").toString();
            var used = false;
            var isIntru = true;
            $.each(userAnswers, function(k, v) {
                if ($.inArray(value, v.split("|")) > -1) {
                    used = true;
                    return false;
                }
                return true;
            });
            $.each(rightAnswers, function(k, v) {
                if ($.inArray(value, v.split("|")) > -1) {
                    isIntru = false;
                    return false;
                }
                return true;
            });

            if (isIntru && !used)
                $item.addClass("answerOk");
            else
                if (mode != "right")
                    $item.addClass("answerKo");
        });
    },

    /**
     * Verify user answer for mode "color".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : "full", "right" or "user" color.
     */
    _verifyAnswersColor: function($quiz, mode) {
        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;
        var rightAnswers = $.publiquiz.question.correctionCategories(
                $quiz.find("#"+quzId+"_correct"));
        var userAnswers = $.publiquiz.question.correctionCategories(
                $quiz.find("#"+quzId+"_user"));

        $quiz.find("."+prefix+"Choice").each( function() {
            var $choice = $(this);
            var value = String($choice.data("choice-value"));
            if (isMultiple) {
                $choice.find("."+prefix+"ItemColor").each( function() {
                    var $item = $(this);
                    var category = $item.data("category-id");
                    if (mode == "user") {
                        var valid = $.inArray(value, rightAnswers[category].split("|")) >= 0;
                        $.publiquiz.question.addClassColorAnswer($quiz, $item, valid);
                        if (!valid) {
                            $("body").queue(function(next) {
                                $item.remove();
                                next();
                            });
                        }
                    } else if (mode == "right") {
                        if ($.inArray(value, rightAnswers[category].split("|")) >= 0)
                            $item.addClass("answerOk");
                    } else {
                        var userAnswer = userAnswers[category];
                        var rightAnswer = rightAnswers[category].split("|");
                        if (userAnswer) {
                            userAnswer = userAnswer.split("|");
                            if ($.inArray(value, userAnswer) >= 0 && $.inArray(value, rightAnswer) >= 0)
                                $item.addClass("answerOk");
                            else
                                $item.addClass("answerKo");
                        } else {
                            $item.addClass("answerKo");
                        }
                    }
                });
            } else {
                var category = $choice.data("category-id");
                var rightAnswer = null;
                if (mode == "user") {
                    if (category) {
                        rightAnswer = rightAnswers[category].split("|");
                        if ($.inArray(value, rightAnswer) > -1)
                            $choice.addClass("answerOk");
                        else
                            $choice.addClass("answerKo");
                    }
                } else if (mode == "right") {
                    if (category) {
                        rightAnswer = rightAnswers[category].split("|");
                        if ($.inArray(value, rightAnswer) > -1)
                            $choice.addClass("answerOk");
                    }
                } else {
                    var userAnswer = userAnswers[category];
                    rightAnswer = rightAnswers[category].split("|");
                    if (userAnswer) {
                        userAnswer = userAnswer.split("|");
                        if ($.inArray(value, userAnswer) >= 0 && $.inArray(value, rightAnswer) >= 0)
                            $choice.addClass("answerOk");
                        else
                            $choice.addClass("answerKo");
                    } else {
                        $choice.addClass("answerKo");
                    }
                }
            }
        });

        var duration = $quiz.data("verify-duration");
        if (duration > 0) {
            var timer = setTimeout($.publiquiz.question.clearVerify, duration);
            $.publiquiz.question.timers.push(timer);
        }
    },

    /**
     * Verify user answer for mode "grid".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : "full", "right" or "user" color.
     */
    _verifyAnswersChoices: function($quiz, mode) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var rightAnswers = $.publiquiz.question.correctionCategories(
                $quiz.find("#"+quzId+"_correct"));
        var userAnswers = $.publiquiz.question.correctionCategories(
                $quiz.find("#"+quzId+"_user"));

        if (mode == "user") {
            $quiz.find("."+prefix+"CategoryChoice").filter(".selected").each( function() {
                var $this = $(this);
                var catId = $this.data("category-id");
                var grp = $this.data("group");
                var $item = $quiz.find("#"+quzId+"_item"+grp);
                if (rightAnswers[catId] && $.inArray($item.data("item-value")+"",
                        rightAnswers[catId].split("|")) >= 0)
                    $this.addClass("answerOk");
                else
                    $this.addClass("answerKo");
            });
        } else if (mode == "right") {
            $quiz.find("."+prefix+"CategoryChoice").filter(".selected").each( function() {
                var $this = $(this);
                var catId = $this.data("category-id");
                var grp = $this.data("group");
                var $item = $quiz.find("#"+quzId+"_item"+grp);
                if (rightAnswers[catId] && $.inArray($item.data("item-value")+"",
                        rightAnswers[catId].split("|")) >= 0)
                    $this.addClass("answerOk");
            });
        } else {
            $quiz.find("."+prefix+"CategoryChoice").filter(".selected").each( function() {
                var $this = $(this);
                var grp = $this.data("group");
                var catId = $this.data("category-id");
                var $item = $quiz.find("#"+quzId+"_item"+grp);

                if (userAnswers[catId] && $.inArray($item.data("item-value")+"",
                                                    userAnswers[catId].split("|")) >= 0)
                        $this.addClass("answerOk");
                else
                    $this.addClass("answerKo");
            });
        }

        var duration = $quiz.data("verify-duration");
        if (duration > 0) {
            var timer = setTimeout($.publiquiz.question.clearVerify, duration);
            $.publiquiz.question.timers.push(timer);
        }
    }
};

// Register function
$.publiquiz.question.register("categories", {
        configure: $.publiquiz.question.categories.categoriesConfigure,
        enable: $.publiquiz.question.categories.categoriesEnable,
        disable: $.publiquiz.question.categories.categoriesDisable,
        redo: $.publiquiz.question.categories.categoriesRedo,
        help: $.publiquiz.question.categories.categoriesHelp,
        retry: $.publiquiz.question.categories.categoriesRetry,
        textAnswer: $.publiquiz.question.categories.categoriesTextAnswer,
        insertUserAnswers: $.publiquiz.question.categories.categoriesInsertUserAnswers,
        quizAnswer: $.publiquiz.question.categories.categoriesQuizAnswer,
        verifyUserAnswer: $.publiquiz.question.categories.categoriesVerifyUserAnswer,
        verifyRightAnswer: $.publiquiz.question.categories.categoriesVerifyRightAnswer,
        verifyFullAnswer: $.publiquiz.question.categories.categoriesVerifyFullAnswer,
        computeScore: $.publiquiz.question.categories.categoriesComputeScore,
        quizScore: $.publiquiz.question.categories.categoriesScore,
        modified: $.publiquiz.question.categories.categoriesModified,
        loadContext: $.publiquiz.question.categories.categoriesLoadContext
    });

}(jQuery));



/******************************************************************************
 *
 *                              Production
 *
 *****************************************************************************/

(function ($) {

$.publiquiz.question.production = {

    /**
     * Configure quiz.
     */
    productionConfigure: function($quiz) {
        var prefix = $quiz.data("prefix");
        var $engine = $quiz.find("."+prefix+"Engine");
        if ($engine.data("original-state") === undefined)
            $engine.data("original-state", $engine.html());
    },

    /**
     * Set event click on point.
     *
     * @param {Object} jquery Object quiz.
     */
    productionEnable: function($quiz) {
        var prefix = $quiz.data("prefix");
        var $production = $quiz.find("."+prefix+"Production");
        $production.each( function() {
            var $this= $(this);
            $this.removeAttr("disabled");
            $this.removeClass("disabled");
        });

        $production.on("input", function() {
            $.publiquiz.context.onQuizModified($.publiquiz.question, $quiz);
        });
    },

    /**
     * Remove events listener on quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    productionDisable: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Production").each( function() {
            var $this= $(this);
            $this.attr("disabled", "true");
            $this.addClass("disabled");
        });
    },

    /**
     * Redo quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    productionRedo: function($quiz) {
        var prefix = $quiz.data("prefix");
        var $engine = $quiz.find("."+prefix+"Engine");
        if ($engine.data("original-state"))
            $engine.html($engine.data("original-state"));
    },

    /**
     * Display help of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    productionHelp: function($quiz) {
        $.publiquiz.question.displayHelp($quiz);
    },

    /**
     * Retry quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    productionRetry: function($quiz) {
    },

    /**
     * Compute score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Dictionnary}.
     */
    productionComputeScore: function($quiz) {
        var result = {};
        result.score = 0;
        result.total = 0;
        return result;
    },

    /**
     * Display score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    productionScore: function($quiz) {
    },

    /**
     * Display quiz text answer.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    productionTextAnswer: function($quiz) {
        $.publiquiz.question.displayTextAnswer($quiz);
    },

    /**
     * Insert user answers in html
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    productionInsertUserAnswers: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var answer = $quiz.find("."+prefix+"Production").val();
        if (answer) {
            answer = answer.replace(/\n/g, "#R#");
            $.publiquiz.question.writeUserAnswers($quiz, quzId, answer);
        }
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    productionQuizAnswer: function($quiz, mode) {
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    productionVerifyAnswer: function($quiz) {
    },

    /**
     * Modified
     */
    productionModified: function($quiz) {
        var engine = $quiz.data("engine");
        var prefix = $quiz.data("prefix");
        var changes = $quiz.find("."+prefix+"Production").val();
        changes = changes.replace(/\n/g, "#R#");
        return {"data": changes, "engine": engine};
    },

    /**
     * Reload context
     */
    productionLoadContext: function($quiz, dataClass) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var $context = $quiz.find("#"+quzId+"_context");
        var $data = $context.find(dataClass);

       $quiz.find("."+prefix+"Production").val(
               $data.text().replace(/#R#/g, "\n"));
    }

    /**********************************************************************
     *                          Private Library
     **********************************************************************/

};

// Register function
$.publiquiz.question.register("production", {
        configure: $.publiquiz.question.production.productionConfigure,
        enable: $.publiquiz.question.production.productionEnable,
        disable: $.publiquiz.question.production.productionDisable,
        redo: $.publiquiz.question.production.productionRedo,
        help: $.publiquiz.question.production.productionHelp,
        retry: $.publiquiz.question.production.productionRetry,
        textAnswer: $.publiquiz.question.production.productionTextAnswer,
        insertUserAnswers: $.publiquiz.question.production.productionInsertUserAnswers,
        quizAnswer: $.publiquiz.question.production.productionQuizAnswer,
        verifyUserAnswer: $.publiquiz.question.production.productionVerifyAnswer,
        verifyRightAnswer: $.publiquiz.question.production.productionVerifyAnswer,
        verifyFullAnswer: $.publiquiz.question.production.productionVerifyAnswer,
        computeScore: $.publiquiz.question.production.productionComputeScore,
        quizScore: $.publiquiz.question.production.productionScore,
        modified: $.publiquiz.question.production.productionModified,
        loadContext: $.publiquiz.question.production.productionLoadContext
    });

}(jQuery));


/******************************************************************************
 *
 *                                  Composite
 *
 *****************************************************************************/

(function ($) {

$.publiquiz.question.composite = {

    /**
     * Configure quiz.
     */
    compositeConfigure: function($quiz) {
        var prefix = $quiz.data("prefix");
        var options = $quiz.data("engine-options") || "";

        // Sauvegarde de l'html d'origine
        var $elements = $quiz.find("."+prefix+"Elements");
        if ($elements.data("original-state") === undefined) {
            $elements.data("original-state", $elements.html());

            $quiz.find("."+prefix+"Element").each( function() {
                var $element = $(this);

                // Register score function
                $.publiquiz.question.registerScoreFunc(
                        $element.data("quiz-id"),
                        $element,
                        $.publiquiz.question.computeScore[$element.data("engine")]
                    );
            });
        }

        // Mélange des elements
        if (options.search("shuffle") > -1)
            $quiz.shuffle("li."+prefix+"Element");

        // Nombre d'element a afficher
        if ($quiz.data("engineDisplay")) {
            var display = $quiz.data("engineDisplay");
            var $subQuiz = $quiz.find("."+prefix+"Element");
            $subQuiz.removeClass("hidden").removeAttr("style");
            if (display >= $subQuiz.length)
                return;
            var subQuiz = $subQuiz.splice(display, $subQuiz.length);
            $(subQuiz).addClass("hidden");
        }

        // Activation des sub quiz
        $quiz.find("."+prefix+"Element").each( function() {
            var $element = $(this);
            var subEngine = $element.data("engine");
            $element.data("prefix", prefix);
            $element.data("verify-duration", $.publiquiz.defaults.verifyDuration);
            var ttl = $quiz.data("context-ttl");
            if (ttl !== undefined)
                $element.data("context-ttl", ttl);
            var key = $quiz.data("context-key");
            if (key !== undefined)
                $element.data("context-key", key);

            // Configure sub quiz
            $.publiquiz.question.configure[subEngine]($element);
        });

        // Gestion du multipage
        if (options.search("multipage") > -1)
            $.publiquiz.question.composite._handleMultipage($quiz);
    },

    /**
     * Set event click on point.
     *
     * @param {Object} jquery Object quiz.
     */
    compositeEnable: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.data("quiz-state", "enabled");
        $quiz.find("."+prefix+"Element").filter(":not(.hidden)").each( function() {
            var $element = $(this);
            var subEngine = $element.data("engine");
            $.publiquiz.question.enable[subEngine]($element);
            $.publiquiz.question.hideTextAnswer($element);
            $element.on("subQuizChange", function() {
                $.publiquiz.context.onQuizModified($.publiquiz.question, $quiz);
            });
        });
    },

    /**
     * Remove events listener on quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    compositeDisable: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.data("quiz-state", "disabled");
        $quiz.find("."+prefix+"Element").filter(":not(.hidden)").each( function() {
            var $element = $(this);
            var subEngine = $element.data("engine");
            $.publiquiz.question.disable[subEngine]($element);
            $element.off("subQuizChange");
        });
    },

    /**
     * Redo quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    compositeRedo: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Element").each(function() {
            var $element = $(this);
            var subEngine = $element.data("engine");
            $element.removeData("quiz-result");
            $.publiquiz.question.redo[subEngine]($element);
        });
    },

    /**
     * Display help of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    compositeHelp: function($quiz) {
        $.publiquiz.question.displayHelp($quiz);
    },

    /**
     * Retry quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    compositeRetry: function($quiz) {
        $quiz.removeData("quiz-result");
        var prefix = $quiz.data("prefix");
        var options = $quiz.data("engine-options") || "";
        $quiz.find("."+prefix+"Element").filter(":not(.hidden)").each( function() {
            var $element = $(this);
            var subEngine = $element.data("engine");
            $.publiquiz.question.retry[subEngine]($element);
        });
        if (options.search("multipage") > -1) {
            $.publiquiz.question.composite._multipageGoTo($quiz, 0);
            $quiz.data("action").addClass("hidden");
        }
    },

    /**
     * Compute score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Dictionnary}.
     */
    compositeComputeScore: function($quiz) {
        var result = $quiz.data("quiz-result");
        if (result !== undefined)
            return result;

        var options = $quiz.data("engine-options") || "";
        var noMark = (options.search("nomark") > -1);

        if (noMark) {
            return {
                score: 0,
                total: 0
            };
        }

        var prefix = $quiz.data("prefix");
        var score = 0;
        var total = 0;
        $quiz.find("."+prefix+"Element").filter(":not(.hidden)").each( function() {
            var $element = $(this);
            var subEngine = $element.data("engine");
            var res = $.publiquiz.question.computeScore[subEngine]($element);
            score += res.score;
            total += res.total;
        });
        result = {
            score: score,
            total: total
        };
        $quiz.data("quiz-result", result);
        return result;
    },

    /**
     * Display score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    compositeScore: function($quiz) {
    },

    /**
     * Display quiz text answer.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    compositeTextAnswer: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Element").filter(":not(.hidden)").each( function() {
            var $element = $(this);
            var subEngine = $element.data("engine");
            $.publiquiz.question.textAnswer[subEngine]($element);
        });
        $.publiquiz.question.displayTextAnswer($quiz);
    },

    /**
     * Insert user answers in html
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    compositeInsertUserAnswers: function($quiz) {
        var prefix = $quiz.data("prefix");
        var options = $quiz.data("engine-options") || "";
        $quiz.find("."+prefix+"Element").filter(":not(.hidden)").each( function() {
            var $element = $(this);
            var subEngine = $element.data("engine");
            $.publiquiz.question.insertUserAnswers[subEngine]($element);
        });
        if (options.search("multipage") > -1) {
            $.publiquiz.question.composite._multipageGoTo($quiz, 0);
        }
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    compositeQuizAnswer: function($quiz, mode) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Element").filter(":not(.hidden)").each( function() {
            var $element = $(this);
            var subEngine = $element.data("engine");
            $.publiquiz.question.quizAnswer[subEngine]($element, mode);
        });
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    compositeVerifyUserAnswer: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Element").filter(":not(.hidden)").each( function() {
            var $element = $(this);
            var subEngine = $element.data("engine");
            $.publiquiz.question.verifyUserAnswer[subEngine]($element);
        });
    },

    /**
     * Verify right answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    compositeVerifyRightAnswer: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Element").filter(":not(.hidden)").each( function() {
            var $element = $(this);
            var subEngine = $element.data("engine");
            $.publiquiz.question.verifyRightAnswer[subEngine]($element);
        });
    },

    /**
     * Verify full answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    compositeVerifyFullAnswer: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Element").filter(":not(.hidden)").each( function() {
            var $element = $(this);
            var subEngine = $element.data("engine");
            $.publiquiz.question.verifyFullAnswer[subEngine]($element);
        });
    },

    /**
     * Modified
     */
    compositeModified: function($quiz) {
        var res = {};
        res.data = "";
        res.engine = $quiz.data("engine");

        if ($quiz.data("currentPage")) {
            res.page = $quiz.data("currentPage");
        }

        if ($quiz.data("engineDisplay")) {
            var prefix = $quiz.data("prefix");
            var ids = [];
            var $subElement = $quiz.find("."+prefix+"Element").filter(":not(.hidden)");
            $subElement.each(function() {
                ids.push($(this).data("quizId"));
            });
            res.display = ids.join("::");
        }

        return res;
    },

    /**
     * Reload context
     */
    compositeLoadContext: function($quiz, dataClass) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var $context = $quiz.find("#"+quzId+"_context");

        //var $page = $context.find(".page");
        //$.publiquiz.question.composite._multipageGoTo($quiz, parseInt($page.text(), 10));

        var display = $context.find(".display");
        if (display.length > 0) {
            var options = $quiz.data("engine-options") || "";
            var elements = $quiz.find("."+prefix+"Element");

            // On desactive tous les subquiz
            $.publiquiz.question.composite.compositeDisable($quiz);
            elements.removeClass("hidden");

            // On affiche les subquiz du context
            var filterTxt = "";
            var ids = display.text().split("::");
            $.each(ids.reverse(), function() {
                var sub = elements.filter('[data-quiz-id="'+this+'"]');
                $quiz.find("."+prefix+"Elements").prepend(sub);
                filterTxt += '[data-quiz-id!="'+this+'"]';
            });
            elements.filter(filterTxt).addClass("hidden");

            if (options.search("multipage") > -1)
                $.publiquiz.question.composite._handleMultipage($quiz);

            // On active les subquiz afficher
            $.publiquiz.question.composite.compositeEnable($quiz);
        }
    },


    /**********************************************************************
     *                          Private Library
     **********************************************************************/

    /**
     * With multipage option, add events to navigation buttons.
     *
     * @param {jQuery} $quiz - Quiz element.
     */
    _handleMultipage: function($quiz) {
        var prefix = $quiz.data("prefix");
        var $subquizzes = $quiz.find("."+prefix+"Element").filter(":not(.hidden)");
        $subquizzes.each(function(index) {
            $(this).find("."+prefix+"Numbering").text((index+1) + " / " + $subquizzes.length);
        });
        var $previous = $quiz.find("."+prefix+"CompositePrevious");
        var $next = $quiz.find("."+prefix+"CompositeNext");
        $subquizzes.slice(1).hide();
        $quiz.data("current-page", 0);
        $previous.addClass("disabled");
        $previous.off("click");
        $previous.on("click", function(e) {
            e.preventDefault();
            if ($previous.hasClass("disabled"))
                return;
            $.publiquiz.question.composite._multipagePrevious($quiz);
            $.publiquiz.context.onQuizModified($.publiquiz.question, $quiz);
        });
        if ($subquizzes.length <= 1)
            $next.addClass("disabled");
        else
            $next.removeClass("disabled");
        $next.off("click");
        $next.on("click", function(e) {
            e.preventDefault();
            if ($next.hasClass("disabled"))
                return;
            $.publiquiz.question.composite._multipageNext($quiz);
            $.publiquiz.context.onQuizModified($.publiquiz.question, $quiz);
        });
    },

    /**
     * With multipage option, show previous page.
     *
     * @param {jQuery} $quiz - Quiz element.
     */
    _multipagePrevious: function($quiz) {
        var prefix = $quiz.data("prefix");
        var $subquizzes = $quiz.find("."+prefix+"Element").filter(":not(.hidden)");
        var $previous = $quiz.find("."+prefix+"CompositePrevious");
        var $next = $quiz.find("."+prefix+"CompositeNext");
        $subquizzes.finish();
        $next.removeClass("disabled");
        var current = $quiz.data("current-page");
        if (current > 0) {
            if ($.publiquiz.defaults.multipageAnimation) {
                $subquizzes.eq(current).slideToggle();
                $subquizzes.eq(current-1).slideToggle();
            } else {
                $subquizzes.eq(current).hide();
                $subquizzes.eq(current-1).show();
            }
            $quiz.data("current-page", current-1);
            if (current-1 <= 0)
                $previous.addClass("disabled");
        }
    },

    /**
     * With multipage option, show next page.
     *
     * @param {jQuery} $quiz - Quiz element.
     */
    _multipageNext: function($quiz) {
        var prefix = $quiz.data("prefix");
        var options = $quiz.data("engine-options") || "";
        var $subquizzes = $quiz.find("."+prefix+"Element").filter(":not(.hidden)");
        var $previous = $quiz.find("."+prefix+"CompositePrevious");
        var $next = $quiz.find("."+prefix+"CompositeNext");
        $subquizzes.finish();
        if (options.search("one-way") == -1 ||
            $quiz.data("quiz-state") == "disabled")
            $previous.removeClass("disabled");
        var current = $quiz.data("current-page");
        if (current < $subquizzes.length-1) {
            if ($.publiquiz.defaults.multipageAnimation) {
                $subquizzes.eq(current).slideToggle();
                $subquizzes.eq(current+1).slideToggle();
            } else {
                $subquizzes.eq(current).hide();
                $subquizzes.eq(current+1).show();
            }
            $quiz.data("current-page", current+1);
            if (current+1 >= $subquizzes.length-1) {
                $next.addClass("disabled");
                if (options.search("multipage") > -1 && $quiz.data("action"))
                    $quiz.data("action").removeClass("hidden");
            }
        }
    },

    /**
     * With multipage option, go to given page.
     *
     * @param {jQuery} $quiz - Quiz element.
     * @param {int} [page] - Page number to show. If not specified, go to next page.
     */
    _multipageGoTo: function($quiz, page) {
        var prefix = $quiz.data("prefix");
        var $subquizzes = $quiz.find("."+prefix+"Element").filter(":not(.hidden)");
        var current = $quiz.data("current-page");
        var diff, i;

        if (page === undefined)
            page = current+1==$subquizzes.length?0:current+1;

        if (current == page || page < 0 || page >= $subquizzes.length)
            return;
        if (current > page) {
            diff = current - page;
            for (i = 0; i < diff; i++)
                $.publiquiz.question.composite._multipagePrevious($quiz);
        } else {
            diff = page - current;
            for (i = 0; i < diff; i++)
                $.publiquiz.question.composite._multipageNext($quiz);
        }
    }
};

// Register function
$.publiquiz.question.register("composite", {
        configure: $.publiquiz.question.composite.compositeConfigure,
        enable: $.publiquiz.question.composite.compositeEnable,
        disable: $.publiquiz.question.composite.compositeDisable,
        redo: $.publiquiz.question.composite.compositeRedo,
        help: $.publiquiz.question.composite.compositeHelp,
        retry: $.publiquiz.question.composite.compositeRetry,
        textAnswer: $.publiquiz.question.composite.compositeTextAnswer,
        insertUserAnswers: $.publiquiz.question.composite.compositeInsertUserAnswers,
        quizAnswer: $.publiquiz.question.composite.compositeQuizAnswer,
        verifyUserAnswer: $.publiquiz.question.composite.compositeVerifyUserAnswer,
        verifyRightAnswer: $.publiquiz.question.composite.compositeVerifyRightAnswer,
        verifyFullAnswer: $.publiquiz.question.composite.compositeVerifyFullAnswer,
        computeScore: $.publiquiz.question.composite.compositeComputeScore,
        quizScore: $.publiquiz.question.composite.compositeScore,
        modified: $.publiquiz.question.composite.compositeModified,
        loadContext: $.publiquiz.question.composite.compositeLoadContext
    });

}(jQuery));
