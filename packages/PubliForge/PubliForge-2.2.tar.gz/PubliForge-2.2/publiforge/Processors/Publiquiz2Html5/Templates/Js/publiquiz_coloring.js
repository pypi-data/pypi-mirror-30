/**
 * @projectDescription Coloring
 */

/*jshint globalstrict: true*/
/*global Image*/
/*global jQuery*/

"use strict";

(function ($) {
    var Drawing = $.publianim.Drawing;

    var oldClear = Drawing.prototype.clear;

    $.extend(Drawing.prototype.defaults, {
        /**
         * @type {Object}
         */
        correction: null
    });

    $.extend(Drawing.prototype, {
        /**
         * @type {Object}
         */
        userAnswer: null,

        /**
         * @type {Object}
         */
        score: null,

        clear: function () {
            oldClear.apply(this);
            this.score = null;
        },

        verifyAnswer: function () {
            this.userAnswer = this._zonesColor;
        },

        showUserAnswer: function () {
            this._clearCanvas();
            this._repaintZones(this.userAnswer);
        },

        showRightAnswer: function () {
            this._clearCanvas();
            this._repaintZones(this.options.correction);
        },

        getScore: function () {
            if (!this.score) {
                var val = 0;
                var total = 0;
                for (var z in this.options.correction) {
                    if (this._zonesPixel[z]) {
                        if (this.options.correction[z] === this.userAnswer[z])
                            val += 1;
                        total += 1;
                    }
                }

                this.score = {
                    value: val,
                    total: total
                };
            }

            return this.score;
        }

    });

}(jQuery));

(function ($) {
    $.publiquiz.question.coloring = {

        /**
         * Configure quiz.
         * @param {jQuery} $quiz - Quiz element.
         */
        coloringConfigure: function ($quiz) {
            var prefix = $quiz.data("prefix");
            var $engine = $quiz.find("."+prefix+"Engine");
            if ($engine.data("original-state") === undefined)
                $engine.data("original-state", $engine.html());

            var $pquizColoringCanvas = $quiz.find(".pquizColoringCanvas");

            var engineOptions = $quiz.data("engineOptions") || "";
            var optNoMark = (engineOptions.search("nomark") > -1);

            var context = {
                ttl: $quiz.data("contextTtl"),
                key: $quiz.data("contextKey")
            };

            var $colors, $tools;
            if (optNoMark) {
                $colors = $quiz.find(".pquizColoringPalette .pquizColoringColor");
                $tools = $quiz.find(".pquizColoringPalette .pquizColoringTool");
            }
            else {
                $colors = $quiz.find(".pquizColoringPalette .pquizColoringTool, .pquizColoringPalette .pquizColoringColor");
            }
            var $toolSize = $quiz.find(".pquizColoringPalette .pquizColoringToolSize");

            var drawingOutline = $pquizColoringCanvas.data("coloringOutline");
            var drawingMask = $pquizColoringCanvas.data("coloringMask");

            if (!drawingOutline)
                drawingOutline = $quiz.find(".pquizColoringOutline").attr("src");
            if (!drawingMask)
                drawingMask = $quiz.find(".pquizColoringMask").attr("src");

            var quizId = $quiz.data("quizId");
            var correction = JSON.parse($quiz.find("#"+quizId+"_correct").text());

            var options = {
                $colors: $colors,
                outline: drawingOutline,
                mask: drawingMask,
                correction: correction,
                maskIgnoreColor: "#ffffff"
            };

            if ($tools && $tools.length > 0) {
                options.$tools = $tools;
            }

            if ($toolSize && $toolSize.length > 0) {
                var $value = $toolSize.find(".pquizColoringToolSizeValue");
                options.$toolSize = $value;

                $toolSize.find(".pquizColoringToolSizeMinus").on("touchstart mousedown", function (e) {
                    e.preventDefault();
                    var decrement = function () {
                        var val = Number($value.text()) - 1;
                        if (val >= 1) {
                            if (val < 10)
                                val = "0" + val;
                            $value.text(val);
                        }
                    };
                    var timer = window.setInterval(decrement, 100);
                    decrement();

                    $(document).on("touchend.coloringSize mouseup.coloringSize", function () {
                        $(document).off(".coloringSize");
                        window.clearInterval(timer);
                    });
                });

                $toolSize.find(".pquizColoringToolSizePlus").on("touchstart mousedown", function (e) {
                    e.preventDefault();
                    var increment = function () {
                        var val = Number($value.text()) + 1;
                        if (val <= 99) {
                            if (val < 10)
                                val = "0" + val;
                            $value.text(val);
                        }
                    };
                    var timer = window.setInterval(increment, 100);
                    increment();

                    $(document).on("touchend.coloringSize mouseup.coloringSize", function () {
                        $(document).off(".coloringSize");
                        window.clearInterval(timer);
                    });
                });
            }

            if (context) {
                options.context = context;
            }
            
            $.publianim.initEffect(
                $.publianim.Drawing, $pquizColoringCanvas, options);

            $pquizColoringCanvas.on("drawingModified", function () {
                $.publiquiz.context.onQuizModified($.publiquiz.question, $quiz);
            });
        },

        /**
         * Set event click.
         * @param {jQuery} $quiz - Quiz element.
         */
        coloringEnable: function ($quiz) {
            var $pquizColoringCanvas = $quiz.find(".pquizColoringCanvas");
            var drawing = $pquizColoringCanvas.data("init"+$.publianim.Drawing.animName);

            drawing.enable();
        },

        /**
         * Remove events listener on quiz.
         * @param {jQuery} $quiz - Quiz element.
         */
        coloringDisable: function ($quiz) {
            var $pquizColoringCanvas = $quiz.find(".pquizColoringCanvas");
            var drawing = $pquizColoringCanvas.data("init"+$.publianim.Drawing.animName);

            drawing.disable();
        },

        /**
         * Redo quiz.
         * @param {jQuery} $quiz - Quiz element.
         */
        coloringRedo: function ($quiz) {
            var prefix = $quiz.data("prefix");
            var $engine = $quiz.find("."+prefix+"Engine");
            if ($engine.data("original-state"))
                $engine.html($engine.data("original-state"));
        },

        /**
         * Display help of quiz.
         * @param {jQuery} $quiz - Quiz element.
         */
        coloringHelp: function ($quiz) {
            $.publiquiz.question.displayHelp($quiz);
        },

        /**
         * Retry quiz, keep only right answer.
         * @param {jQuery} _$quiz - Quiz element.
         */
        coloringRetry: function (_$quiz) {
        },

        /**
         * Compute score of quiz.
         * @param {jQuery} $quiz - Quiz element.
         * @return {Dictionnary}.
         */
        coloringComputeScore: function ($quiz) {
            var $pquizColoringCanvas = $quiz.find(".pquizColoringCanvas");
            var drawing = $pquizColoringCanvas.data("init"+$.publianim.Drawing.animName);

            if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("nomark") > -1 )
                return {score: 0, total: 0};

            var result = drawing.getScore();
            result = {
                score: result.value,
                total: result.total
            };

            return result;
        },

        /**
         * Display score of quiz.
         * @param {jQuery} _$quiz - Quiz element.
         */
        coloringScore: function (_$quiz) {
        },

        /**
         * Display quiz text answer.
         * @param {jQuery} $quiz - Quiz element.
         */
        coloringTextAnswer: function ($quiz) {
            $.publiquiz.question.displayTextAnswer($quiz);
        },

        /**
         * Insert user answers in html
         * @param {jQuery} $quiz - Quiz element.
         */
        coloringInsertUserAnswers: function ($quiz) {
            var $pquizColoringCanvas = $quiz.find(".pquizColoringCanvas");
            var drawing = $pquizColoringCanvas.data("init"+$.publianim.Drawing.animName);

            drawing.verifyAnswer();
        },

        /**
         * Display right/user answer for quiz.
         * @param {jQuery} $quiz - Quiz element.
         * @param {String} mode - display correct/user answer.
         */
        coloringQuizAnswer: function ($quiz, mode) {
            var $pquizColoringCanvas = $quiz.find(".pquizColoringCanvas");
            var drawing = $pquizColoringCanvas.data("init"+$.publianim.Drawing.animName);

            if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("nomark") > -1 )
                return;

            if (mode === "_correct") {
                drawing.showRightAnswer();
            }
            else if (mode === "_user") {
                drawing.showUserAnswer();
            }
        },

        /**
         * Verify user answer.
         * @param {jQuery} _$quiz - Quiz element.
         */
        coloringVerifyAnswer: function (_$quiz) {
        },

        coloringModified: function ($quiz) {
            var engine = $quiz.data("engine");
            var $pquizColoringCanvas = $quiz.find(".pquizColoringCanvas");
            var drawing = $pquizColoringCanvas.data("init"+$.publianim.Drawing.animName);
            var data = drawing.save();

            return {"data": JSON.stringify(data), "engine": engine};
        },

        coloringLoadContext: function ($quiz, dataClass) {
            var $pquizColoringCanvas = $quiz.find(".pquizColoringCanvas");
            var drawing = $pquizColoringCanvas.data("init"+$.publianim.Drawing.animName);
            var quzId = $quiz.data("quiz-id");
            var $context = $quiz.find("#"+quzId+"_context");
            var $data = $context.find(dataClass);
            var data = JSON.parse($data.text());

            $.publiquiz.defaults.contextLoading += 1;
            drawing.load(data);

            window.setInterval(function () {
                if (drawing.isReady()) {
                    $.publiquiz.defaults.contextLoading -= 1;
                }
            }, 100);
        }
    };

    // Register function
    $.publiquiz.question.register("coloring", {
        configure: $.publiquiz.question.coloring.coloringConfigure,
        enable: $.publiquiz.question.coloring.coloringEnable,
        disable: $.publiquiz.question.coloring.coloringDisable,
        redo: $.publiquiz.question.coloring.coloringRedo,
        help: $.publiquiz.question.coloring.coloringHelp,
        textAnswer: $.publiquiz.question.coloring.coloringTextAnswer,
        insertUserAnswers: $.publiquiz.question.coloring.coloringInsertUserAnswers,
        quizAnswer: $.publiquiz.question.coloring.coloringQuizAnswer,
        verifyUserAnswer: $.publiquiz.question.coloring.coloringVerifyAnswer,
        verifyRightAnswer: $.publiquiz.question.coloring.coloringVerifyAnswer,
        verifyFullAnswer: $.publiquiz.question.coloring.coloringVerifyAnswer,
        computeScore: $.publiquiz.question.coloring.coloringComputeScore,
        quizScore: $.publiquiz.question.coloring.coloringScore,
        modified: $.publiquiz.question.coloring.coloringModified,
        loadContext: $.publiquiz.question.coloring.coloringLoadContext
    });
}(jQuery));
