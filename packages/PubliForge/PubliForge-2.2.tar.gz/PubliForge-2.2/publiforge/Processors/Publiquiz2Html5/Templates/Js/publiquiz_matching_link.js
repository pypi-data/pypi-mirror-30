/**
 * @projectDescription publiquiz_matching_link.js
 * Plugin jQuery for quiz engine "matching" render "link".
 *
 * @author Tien Haï NGUYEN
 * @version 0.1
 */


/*jshint globalstrict: true*/
/*global jQuery: true */
/*global clearTimeout: true */
/*global Image: true */



/******************************************************************************
 *
 *                                Matching Link
 *
 *****************************************************************************/

"use strict";

(function ($) {

// Rappel des méthode précédentes
var matchingConfigureBase = $.publiquiz.question.matching.matchingConfigure;
var matchingEnableBase = $.publiquiz.question.matching.matchingEnable;
var matchingDisableBase =  $.publiquiz.question.matching.matchingDisable;
var matchingRedoBase = $.publiquiz.question.matching.matchingRedo;
var matchingHelpBase = $.publiquiz.question.matching.matchingHelp;
var matchingRetryBase = $.publiquiz.question.matching.matchingRetry;
var matchingTextAnswerBase = $.publiquiz.question.matching.matchingTextAnswer;
var matchingInsertUserAnswersBase = $.publiquiz.question.matching.matchingInsertUserAnswers;
var matchingQuizAnswerBase = $.publiquiz.question.matching.matchingQuizAnswer;
var matchingVerifyUserAnswerBase = $.publiquiz.question.matching.matchingVerifyUserAnswer;
var matchingVerifyRightAnswerBase = $.publiquiz.question.matching.matchingVerifyRightAnswer;
var matchingVerifyFullAnswerBase = $.publiquiz.question.matching.matchingVerifyFullAnswer;
var matchingComputeScoreBase = $.publiquiz.question.matching.matchingComputeScore;
var matchingScoreBase = $.publiquiz.question.matching.matchingScore;
var matchingModifiedBase = $.publiquiz.question.matching.matchingModified;
var matchingLoadContextBase = $.publiquiz.question.matching.matchingLoadContext;


// Redéfinition du plugin matching
$.publiquiz.question.matching = {

    // Référence a l'object image qui va saugarder un etat du canvas
    canvasImg: null,
    // Référence a l'object image qui va saugarder un l'etat d'origine du canvas
    canvasImgOrigin: null,
    // Référence au coter du point A choisie
    canvasSelectionSide: null,
    // Référence a l'index du point choisie
    canvasPointIdx: null,
    // Référence au tableau contenant les point selectionne a gauche
    canvasPointLeftSelected: [],
    // Référence au tableau contenant les point selectionne a droite
    canvasPointRightSelected: [],
    // Référence à l'objet contenant la validité de la ligne à partir de son point gauche
    canvasValidLine: {},
    // Référence a l'index du point A
    canvasPointA: null,
    // Référence du coter du point A
    canvasSidePointA: null,
    // Référence a la position en X des points
    canvasOffsetPointX: 20,
    // Référence au rayon des points de l'interface
    canvasPointRadius: 10,
    // Référence a la taille du trait tracer
    canvasdrawLineWidth: 2,
    // Référence au couleur de la ligne entre les points
    canvasLineColor: "#7f7f7f",
    // Référence au couleur de la ligne entre les points correcte
    canvasLineColorOk: "#1fbe1f",
    // Référence au couleur de la ligne entre les points correcte
    canvasLineColorKo: "#ff0000",
    // Référence a la marge pour la detection du point
    canvasMarginDetection: 10,

    // Référence durée de la fonction "verify"
    duration: 3000,
    // Référence au tableau contenant les timer pour la fonction "verify"
    timers: [],


    /**
     * Configure quiz.
     */
    matchingConfigure: function($quiz) {
        if (!$quiz.data("engine-options") ||
                $quiz.data("engine-options").search("link") < 0) {
            matchingConfigureBase($quiz);
            return;
        }

        var prefix = $quiz.data("prefix");
        var $engine = $quiz.find("."+prefix+"Engine");
        if ($engine.data("original-state") === undefined)
            $engine.data("original-state", $engine.html());

        var quzId = $quiz.data("quiz-id");

        // On melange les items
        $.publiquiz.question.shuffleItems($quiz.find("."+prefix+"MatchingLinkItems"));

        // Configure canvas
        $.publiquiz.question.matching.configure($quiz);
    },

    /**
     * Set event click on Choice.
     *
     * @param {Object} jquery Object quiz.
     */
    matchingEnable: function($quiz) {
        if (!$quiz.data("engine-options") ||
                $quiz.data("engine-options").search("link") < 0 ) {
            matchingEnableBase($quiz);
            return;
        }
        $.publiquiz.question.matching.enableCanvasSelectionPointA($quiz);
    },

    /**
     * Remove events listener on quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    matchingDisable: function($quiz) {
        if (!$quiz.data("engine-options") ||
                $quiz.data("engine-options").search("link") < 0 ) {
            matchingDisableBase($quiz);
            return;
        }
        var quzId = $quiz.data("quiz-id");
        var $canvas = $quiz.find("#"+quzId+"_canvas");
        var evtStart = "mousedown touchstart";
        var evtMove = "mousemove touchmove";
        var evtEnd = "mouseup touchend";
        $canvas.unbind(evtStart);
        $canvas.unbind(evtMove);
        $canvas.unbind(evtEnd);
    },

    /**
     * Redo quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    matchingRedo: function($quiz) {
        if (!$quiz.data("engine-options") ||
                $quiz.data("engine-options").search("link") < 0 ) {
            matchingRedoBase($quiz);
            return;
        }

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
        if (!$quiz.data("engine-options") ||
                $quiz.data("engine-options").search("link") < 0 ) {
            matchingHelpBase($quiz);
            return;
        }
        $.publiquiz.question.displayHelp($quiz);
    },

    /**
     * Retry quiz, keep only right answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    matchingRetry: function($quiz) {
        if (!$quiz.data("engine-options") ||
                $quiz.data("engine-options").search("link") < 0 ) {
            matchingRetryBase($quiz);
            return;
        }
        
        var pqMatching = $.publiquiz.question.matching;
        var quzId = $quiz.data("quiz-id");

        pqMatching.matchingDisable($quiz);
        $quiz.removeData("quiz-result");
        pqMatching.clearVerify($quiz);

        // On selectionne uniquement les bonnes réponses
        var currAnswer = pqMatching.constructAnswerString($quiz).split("::");
        var answer = {};
        $.each($quiz.find("#"+quzId+"_correct").text().split("::"), function() {
            if ($.inArray(this, currAnswer) >= 0) {
                var key = this.substring(0, 3);
                var value = this.substring(3, this.length);
                answer[key] = value;
            }
        });
        pqMatching.drawCanvasAnswer($quiz, answer);

        // On sauvegarde l'etat du canvas
        var $canvas = $quiz.find("#"+quzId+"_canvas");
        pqMatching.canvasImg.src = $canvas[0].toDataURL();
        
        //
        $.publiquiz.context.onQuizModified($.publiquiz.question, $quiz);
    },

    /**
     * Compute score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Dictionnary}.
     */
    matchingComputeScore: function($quiz) {
        if (!$quiz.data("engine-options") ||
                $quiz.data("engine-options").search("link") < 0 )
            return matchingComputeScoreBase($quiz);

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

        result = $quiz.data("quiz-result");
        if (result !== undefined)
            return result;

        var pqMatching = $.publiquiz.question.matching;
        pqMatching.clearVerify($quiz);
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var res = $.publiquiz.question.correction($quiz.find("#"+quzId+"_correct"));

        var total = 0;
        var score = 0;
        var $leftItems = $quiz.find("#"+quzId+"_items_left").find("."+prefix+"MatchingLinkItem");
        var $rightItems = $quiz.find("#"+quzId+"_items_right").find("."+prefix+"MatchingLinkItem");

        $.each(res, function(key, value) {
            total += 1;
            var $itemLeft = $quiz.find("#"+quzId+"_"+key);
            var position = $.inArray($itemLeft[0], $leftItems);
            var index = $.inArray(position, pqMatching.canvasPointLeftSelected);
            if (index >= 0) {
                var $itemRight = $($rightItems[pqMatching.canvasPointRightSelected[index]]);
                if (value == $itemRight.data("item-value"))
                    score += 1;
            }
        });

        result = {};
        result.score = score;
        result.total = total;
        $quiz.data("quiz-result", result);
        return result;
    },

    /**
     * Display score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    matchingScore: function($quiz) {
        if (!$quiz.data("engine-options") ||
                $quiz.data("engine-options").search("link") < 0 ) {
            matchingScoreBase($quiz);
            return;
        }
    },

    /**
     * Display quiz text answer.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    matchingTextAnswer: function($quiz) {
        if (!$quiz.data("engine-options") ||
                $quiz.data("engine-options").search("link") < 0 ) {
            matchingTextAnswerBase($quiz);
            return;
        }
        $.publiquiz.question.displayTextAnswer($quiz);
    },

    /**
     * Insert user answers in html
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    matchingInsertUserAnswers: function($quiz) {
        if (!$quiz.data("engine-options") ||
                $quiz.data("engine-options").search("link") < 0 ) {
            matchingInsertUserAnswersBase($quiz);
            return;
        }

        var quzId = $quiz.data("quiz-id");
        var answer = $.publiquiz.question.matching.constructAnswerString($quiz);
        $.publiquiz.question.writeUserAnswers($quiz, quzId, answer);
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    matchingQuizAnswer: function($quiz, mode) {
        if (!$quiz.data("engine-options") ||
                $quiz.data("engine-options").search("link") < 0 ) {
            matchingQuizAnswerBase($quiz, mode);
            return;
        }

        var quzId = $quiz.data("quiz-id");
        var answers = $.publiquiz.question.correction($quiz.find("#"+quzId+mode));
        $.publiquiz.question.matching.drawCanvasAnswer($quiz, answers);
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    matchingVerifyUserAnswer: function($quiz) {
        if (!$quiz.data("engine-options") ||
                $quiz.data("engine-options").search("link") < 0 ) {
            matchingVerifyUserAnswerBase($quiz);
            return;
        }
        $.publiquiz.question.matching.verifyAnswer($quiz, "user");
    },

    /**
     * Verify right answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    matchingVerifyRightAnswer: function($quiz) {
        if (!$quiz.data("engine-options") ||
                $quiz.data("engine-options").search("link") < 0 ) {
            matchingVerifyRightAnswerBase($quiz);
            return;
        }
        $.publiquiz.question.matching.verifyAnswer($quiz, "right");
    },

    /**
     * Verify right answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    matchingVerifyFullAnswer: function($quiz) {
        if (!$quiz.data("engine-options") ||
                $quiz.data("engine-options").search("link") < 0 ) {
            matchingVerifyFullAnswerBase($quiz);
            return;
        }
        $.publiquiz.question.matching.verifyAnswer($quiz, "full");
    },

    /**
     * Modified
     */
    matchingModified: function($quiz) {
        if (!$quiz.data("engine-options") ||
                $quiz.data("engine-options").search("link") < 0 ) {
            return matchingModifiedBase($quiz);
        }
        var changes = $.publiquiz.question.matching.constructAnswerString($quiz);
        return {"data": changes, "engine": $quiz.data("engine")};
    },

    /**
     * Reload context
     */
    matchingLoadContext: function($quiz, dataClass) {
        if (!$quiz.data("engine-options") ||
                $quiz.data("engine-options").search("link") < 0 ) {
            matchingLoadContextBase($quiz, dataClass);
            return;
        }
        var quzId = $quiz.data("quiz-id");
        var $context = $quiz.find("#"+quzId+"_context");
        var $data = $context.find(dataClass);
        var values = $.publiquiz.question.correction($data);
        $.publiquiz.question.matching.drawCanvasAnswer($quiz, values);

        // On sauvegarde l'etat du canvas
        var $canvas = $quiz.find("#"+quzId+"_canvas");
        $.publiquiz.question.matching.canvasImg.src = $canvas[0].toDataURL();
    },


    /**********************************************************************
     *                          Private Library
    **********************************************************************/

    /**
     * Configure engine, after ensure all images load.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    configure: function($quiz) {
        var pqMatching = $.publiquiz.question.matching;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var $canvas = $quiz.find("#"+quzId+"_canvas");
        $canvas[0].isDrawing = false;

        // Set width/height of canvas
        var h = 0;
        var w = 0;
        $quiz.find("."+prefix+"MatchingLinkItems").each( function() {
            w = this.clientWidth;
            if (this.clientHeight > h)
                h = this.clientHeight;
        });
        $canvas[0].width = w;
        $canvas[0].height = h;

        // Clear canvas
        var context = $canvas[0].getContext("2d");
        context.clearRect(0, 0, $canvas.width(), $canvas.height());

        // Draw canvas point
        var canvasOffsetY = $canvas[0].offsetTop;

        var $left = $quiz.find("#"+quzId+"_items_left");
        $left.find("."+prefix+"MatchingLinkItem").each( function() {
            var elem = this;
            var X = pqMatching.canvasOffsetPointX;
            var Y = (elem.offsetTop - canvasOffsetY) + (elem.clientHeight/2);
            pqMatching.drawCanvasArc($canvas, X, Y);
        });

        var $right = $quiz.find("#"+quzId+"_items_right");
        $right.find("."+prefix+"MatchingLinkItem").each( function() {
            var elem = this;
            var X = $canvas.width() - pqMatching.canvasOffsetPointX;
            var Y = (elem.offsetTop - canvasOffsetY) + (elem.clientHeight/2);
            pqMatching.drawCanvasArc($canvas, X, Y);
        });

        // Save and initialise canvas state
        pqMatching.canvasPointLeftSelected = [];
        pqMatching.canvasPointRightSelected = [];
        pqMatching.canvasSelectionSide = null;
        pqMatching.canvasPointIdx = null;
        pqMatching.canvasValidLine =  {};
        pqMatching.canvasPointA = null;
        pqMatching.canvasSidePointA = null;

        pqMatching.canvasImg = new Image();
        pqMatching.canvasImgOrigin = new Image();
        pqMatching.canvasImg.src = $canvas[0].toDataURL();
        pqMatching.canvasImgOrigin.src = $canvas[0].toDataURL();
    },

    /**
     * Suppression des informations de verification du quiz
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    clearVerify: function($quiz) {
        $.each(this.timers, function() {
            clearTimeout(this);
        });

        var pqMatching = $.publiquiz.question.matching;
        var quzId = $quiz.data("quiz-id");
        var $canvas = $quiz.find("#"+quzId+"_canvas");
        pqMatching.canvasRefresh($canvas, pqMatching.canvasImg);
    },

    /**
     * Mise en place de l'event pour la selection du point A
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    enableCanvasSelectionPointA: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var $canvas = $quiz.find("#"+quzId+"_canvas");
        var evtStart = "mousedown touchstart";

        $canvas.bind(evtStart, function(ev) {
            ev.preventDefault();
            $.publiquiz.question.matching.onCanvasSelectPointA($quiz, ev);
        });
    },

    /**
     * Mise en place de l'event pour la selection du point B
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    enableCanvasSelectionPointB: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var $canvas = $quiz.find("#"+quzId+"_canvas");
        var evtMove = "mousemove touchmove";
        var evtEnd = "mouseup touchend";
        $canvas.bind(evtMove, function(ev) {
            ev.preventDefault();
            $.publiquiz.question.matching.onCanvasMouseMove($quiz, ev);
        });
        $canvas.bind(evtEnd, function(ev) {
            ev.preventDefault();
            $.publiquiz.question.matching.onCanvasSelectPointB($quiz, ev);
            $.publiquiz.context.onQuizModified($.publiquiz.question, $quiz);
        });
    },

    /**
     * Matching link helper, dessine les points du canvas
     *
     * @params {Object} $canvas : object jquery canvas.
     * @params {int} X : position X du point a dessiner.
     * @params {int} Y : position Y du point a dessiner.
     */
    drawCanvasArc: function($canvas, X, Y) {
        var context = $canvas[0].getContext("2d");
        context.beginPath();
        context.arc(
            X, Y,
            $.publiquiz.question.matching.canvasPointRadius, 0, Math.PI * 2);
        context.fill();
        context.closePath();
    },

    /**
     * Matching link helper, dessine la ligne entre un point A et B dans le canvas.
     *
     * @params {Object} $canvas : object jquery canvas.
     * @params {Array} coordinateA : position du point A.
     * @params {Array} coordinateB : position du point B.
     * @params {String} color : couleur de la ligne a dessiner.
     */
    drawCanvasLine: function($canvas, coordinateA, coordinateB, color) {
        var context = $canvas[0].getContext("2d");
        context.lineWidth = $.publiquiz.question.matching.canvasdrawLineWidth;
        context.lineCap = "round";
        context.beginPath();

        context.moveTo(coordinateA[0], coordinateA[1]);
        context.lineTo(coordinateB[0], coordinateB[1]);

        context.strokeStyle = color;
        context.stroke();
        context.closePath();
    },

    /**
     * Redraw lines for each selected points on the canvas.
     *
     * @param {jQuery} $quiz - jQuery quiz element.
     * @param {jQuery} $canvas - jQuery canvas element.
     */
    canvasRedraw: function($quiz, $canvas) {
        var pqMatching = $.publiquiz.question.matching;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var $leftItems = $quiz.find("#"+quzId+"_items_left").find("."+prefix+"MatchingLinkItem");
        var $rightItems = $quiz.find("#"+quzId+"_items_right").find("."+prefix+"MatchingLinkItem");

        // On enleve les reponses
        pqMatching.canvasRefresh($canvas, pqMatching.canvasImgOrigin);

        // On retrace les réponses sélectionnées
        $.each(pqMatching.canvasPointLeftSelected, function(idx, value) {
            var color = pqMatching.canvasLineColor;
            if (pqMatching.canvasValidLine[value] !== undefined) {
                if (pqMatching.canvasValidLine[value])
                    color = pqMatching.canvasLineColorOk;
                else
                    color = pqMatching.canvasLineColorKo;
            }

            var $itemLeft = $($leftItems[value]);
            var $itemRight = $($rightItems[pqMatching.canvasPointRightSelected[idx]]);
            pqMatching.drawCanvasItemConnection($canvas, $itemLeft, $itemRight, color);
        });

        // On sauvegarde l'etat du canvas
        pqMatching.canvasImg.src = $canvas[0].toDataURL();
    },

    /**
     * Draw line between items.
     *
     * @params {Object} $canvas : object jquery canvas.
     * @params {Object} $itemA : item A.
     * @params {Object} $itemB : item B.
     * @params {String} color : couleur de la ligne a dessiner.
     */
    drawCanvasItemConnection: function($canvas, $itemA, $itemB, color) {
        var pqMatching = $.publiquiz.question.matching;

        var coordinateA = [];
        coordinateA.push(pqMatching.canvasOffsetPointX);
        coordinateA.push(($itemA[0].offsetTop - $canvas[0].offsetTop) + ($itemA[0].clientHeight/2));

        var coordinateB = [];
        coordinateB.push($canvas.width() - pqMatching.canvasOffsetPointX );
        coordinateB.push(($itemB[0].offsetTop - $canvas[0].offsetTop) + ($itemB[0].clientHeight/2));

        pqMatching.drawCanvasLine($canvas, coordinateA, coordinateB, color);
    },

    /**
     * Draw answer on canvas.
     *
     */
    drawCanvasAnswer: function($quiz, answers) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var $canvas = $quiz.find("#"+quzId+"_canvas");
        var pqMatching = $.publiquiz.question.matching;
        
        // Reset canvas
        pqMatching.canvasRefresh($canvas, pqMatching.canvasImgOrigin);
        pqMatching.canvasPointLeftSelected = [];
        pqMatching.canvasPointRightSelected = [];
        
        // Draw
        var $leftItems = $quiz.find("#"+quzId+"_items_left").find("."+prefix+"MatchingLinkItem");
        var $rightItems = $quiz.find("#"+quzId+"_items_right").find("."+prefix+"MatchingLinkItem");
        $.each(answers, function(k, v) {
            var $itemLeft = $quiz.find("#"+quzId+"_"+k);
            var positionL = $.inArray($itemLeft[0], $leftItems);
            var $itemRight = $rightItems.filter("[data-item-value=\""+v+"\"]");
            var positionR = $.inArray($itemRight[0], $rightItems);
            pqMatching.canvasPointLeftSelected.push(positionL);
            pqMatching.canvasPointRightSelected.push(positionR);
            pqMatching.drawCanvasItemConnection($canvas, $itemLeft, $itemRight, pqMatching.canvasLineColor);
        });
    },

    /**
     * Helper, Redessine le canvas avec une image.
     *
     * @params {Object} $canvas : object jquery canvas.
     * @params {Object} image : javascript object.
     */
    canvasRefresh: function($canvas, image) {
        var context = $canvas[0].getContext("2d");
        context.clearRect(0, 0, $canvas.width(), $canvas.height());
        context.drawImage(image, 0, 0);
    },

    /**
     * Helper, Localise le point sous la souris dans le canvas.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @params {Object} ev : object event.
     * @return {Array} coordinate.
     */
    eventCoordinateInCanvas: function($quiz, ev) {
        var quzId = $quiz.data("quiz-id");
        var $canvas = $quiz.find("#"+quzId+"_canvas");
        var canvasOffset = $canvas.offset();
        var posX, posY;
        var scale = $.publiquiz.defaults.scale;

        if (ev.originalEvent.changedTouches) {
            var touch = ev.originalEvent.changedTouches[0];
            posX = touch.pageX;
            posY = touch.pageY;
        } else {
            posX = ev.pageX;
            posY = ev.pageY;
        }

        posX = (posX - canvasOffset.left) / scale.x;
        posY = (posY - canvasOffset.top) / scale.y;

        return [posX, posY];
    },

    /**
     * Helper, Détermine si les coordonnées sont sur un point.
     *
     * @params {Object} $quiz: object jquery quiz.
     * @params {Array} coordinate: coordonnée.
     * @return {Boolean}
     */
    isOnCorrectPoint: function($quiz, coordinate) {
        var pqMatching = $.publiquiz.question.matching;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var $canvas = $quiz.find("#"+quzId+"_canvas");
        var find = false;

        $quiz.find("#"+quzId+"_items_left").find("."+prefix+"MatchingLinkItem").each( function(idx) {
            var elem = this;
            if ( (coordinate[0] >= (pqMatching.canvasOffsetPointX - pqMatching.canvasMarginDetection) - pqMatching.canvasPointRadius) &&
                 (coordinate[0] <= (pqMatching.canvasOffsetPointX + pqMatching.canvasMarginDetection) + pqMatching.canvasPointRadius) &&
                 (coordinate[1] >= (elem.offsetTop - $canvas[0].offsetTop - pqMatching.canvasMarginDetection) + (elem.clientHeight/2) - pqMatching.canvasPointRadius) &&
                 (coordinate[1] <= (elem.offsetTop - $canvas[0].offsetTop + pqMatching.canvasMarginDetection) + (elem.clientHeight/2) + pqMatching.canvasPointRadius) ) {

                    find = true;
                    $.publiquiz.question.matching.canvasSelectionSide = "left";
                    $.publiquiz.question.matching.canvasPointIdx = idx;
                    return false;
            }
            return true;
        });

        if (find)
            return find;

        $quiz.find("#"+quzId+"_items_right").find("."+prefix+"MatchingLinkItem").each( function(idx) {
            var elem = this;
            if( (coordinate[0] + (pqMatching.canvasPointRadius*2) >= $canvas.width() - pqMatching.canvasOffsetPointX - pqMatching.canvasMarginDetection) &&
                (coordinate[0] - (pqMatching.canvasPointRadius*2) <= $canvas.width() - pqMatching.canvasOffsetPointX + pqMatching.canvasMarginDetection) &&
                (coordinate[1] >= (elem.offsetTop - $canvas[0].offsetTop - pqMatching.canvasMarginDetection) + (elem.clientHeight/2) - pqMatching.canvasPointRadius) &&
                (coordinate[1] <= (elem.offsetTop - $canvas[0].offsetTop + pqMatching.canvasMarginDetection) + (elem.clientHeight/2) + pqMatching.canvasPointRadius) ) {

                    find = true;
                    $.publiquiz.question.matching.canvasSelectionSide = "right";
                    $.publiquiz.question.matching.canvasPointIdx = idx;
                    return false;
            }
            return true;
        });

        return find;
    },

    /**
     * Matching link, selection du point de départ
     *
     * @params {Object} $quiz : object jquery quiz.
     * @params {Object} ev : object event.
     */
    onCanvasSelectPointA: function($quiz, ev) {
        var pqMatching = $.publiquiz.question.matching;
        pqMatching.clearVerify($quiz);

        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var $canvas = $quiz.find("#"+quzId+"_canvas");
        var coordinate = pqMatching.eventCoordinateInCanvas($quiz, ev);
        if (!pqMatching.isOnCorrectPoint($quiz, coordinate))
            return;

        // On valide que le point n'est pas encore utiliser
        // si c'est le cas on supprime le précédent tracer
        if ((pqMatching.canvasSelectionSide == "left" && $.inArray(pqMatching.canvasPointIdx, pqMatching.canvasPointLeftSelected) >= 0) ||
                (pqMatching.canvasSelectionSide == "right" && $.inArray(pqMatching.canvasPointIdx, pqMatching.canvasPointRightSelected) >= 0 )) {

            // On supprime les points correspondant dans les tableaux
            var idx = null;
            if (pqMatching.canvasSelectionSide == "left")
                idx = $.inArray(pqMatching.canvasPointIdx, pqMatching.canvasPointLeftSelected);
            else
                idx = $.inArray(pqMatching.canvasPointIdx, pqMatching.canvasPointRightSelected);
            pqMatching.canvasPointLeftSelected.splice(idx, 1);
            pqMatching.canvasPointRightSelected.splice(idx, 1);

            // On replace le canvas d'origin
            pqMatching.canvasRefresh($canvas, pqMatching.canvasImgOrigin);

            // On retrace les lignes
            $.each(pqMatching.canvasPointLeftSelected, function(pos) {
                var elemLeft = $quiz.find("#"+quzId+"_items_left").find("."+prefix+"MatchingLinkItem")[pqMatching.canvasPointLeftSelected[pos]];
                var elemRight = $quiz.find("#"+quzId+"_items_right").find("."+prefix+"MatchingLinkItem")[pqMatching.canvasPointRightSelected[pos]];
                pqMatching.drawCanvasItemConnection($canvas, $(elemLeft), $(elemRight), pqMatching.canvasLineColor);
            });
        }

        // On sauvegarde les paramètres du point selectionner
        pqMatching.canvasPointA = pqMatching.canvasPointIdx;
        pqMatching.canvasSidePointA = pqMatching.canvasSelectionSide;
        if (pqMatching.canvasSidePointA == "left")
            pqMatching.canvasPointLeftSelected.push(pqMatching.canvasPointA);
        else
            pqMatching.canvasPointRightSelected.push(pqMatching.canvasPointA);

        // On sauvegarde l'etat du canvas
        pqMatching.canvasImg.src = $canvas[0].toDataURL();

        // Events
        $canvas[0].isDrawing = true;
        pqMatching.enableCanvasSelectionPointB($quiz);
    },

    /**
     * Matching link, déplacement de la souris
     *
     * @params {Object} $quiz : object jquery quiz.
     * @params {Object} ev : object event.
     */
    onCanvasMouseMove: function($quiz, ev) {
        var pqMatching = $.publiquiz.question.matching;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var $canvas = $quiz.find("#"+quzId+"_canvas");

        if (!$canvas[0].isDrawing)
            return;

        var coordinate = pqMatching.eventCoordinateInCanvas($quiz, ev);
        pqMatching.canvasRefresh($canvas, pqMatching.canvasImg);

        var elem;
        var coordinateA = [];
        if (pqMatching.canvasSidePointA == "left") {
            elem = $quiz.find("#"+quzId+"_items_left").find("."+prefix+"MatchingLinkItem")[pqMatching.canvasPointA];
            coordinateA.push(pqMatching.canvasOffsetPointX);
            coordinateA.push((elem.offsetTop - $canvas[0].offsetTop) + (elem.clientHeight/2));
        } else {
            elem = $quiz.find("#"+quzId+"_items_right").find("."+prefix+"MatchingLinkItem")[pqMatching.canvasPointA];
            coordinateA.push($canvas.width() - pqMatching.canvasOffsetPointX);
            coordinateA.push((elem.offsetTop - $canvas[0].offsetTop) + (elem.clientHeight/2));
        }

        pqMatching.drawCanvasLine($canvas, coordinateA, coordinate, pqMatching.canvasLineColor);
    },

    /**
     * Matching link, On relanche le bouton de la souris
     *
     * @params {Object} $quiz : object jquery quiz.
     * @params {Object} ev : object event.
     */
    onCanvasSelectPointB: function($quiz, ev) {
        var pqMatching = $.publiquiz.question.matching;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var $canvas = $quiz.find("#"+quzId+"_canvas");
        $canvas[0].isDrawing = false;
        pqMatching.matchingDisable($quiz);

        var coordinate = pqMatching.eventCoordinateInCanvas($quiz, ev);
        pqMatching.canvasRefresh($canvas, pqMatching.canvasImg);

        // On valide que le point B est correct
        // et que le point B et le point A ne sont pas du même coter
        if (!pqMatching.isOnCorrectPoint($quiz, coordinate) ||
                pqMatching.canvasSelectionSide == pqMatching.canvasSidePointA) {
            if (pqMatching.canvasSelectionSide == "left")
                pqMatching.canvasPointLeftSelected.pop();
            else
                pqMatching.canvasPointRightSelected.pop();
            pqMatching.enableCanvasSelectionPointA($quiz);
            return;
        }

        // On valide que le point B n'est pas encore utiliser
        if ((pqMatching.canvasSelectionSide == "left" &&
                $.inArray(pqMatching.canvasPointIdx, pqMatching.canvasPointLeftSelected) >= 0) ||
            (pqMatching.canvasSelectionSide == "right" &&
                $.inArray(pqMatching.canvasPointIdx, pqMatching.canvasPointRightSelected) >= 0) ) {

            if (pqMatching.canvasSelectionSide == "left")
                pqMatching.canvasPointRightSelected.pop();
            else
                pqMatching.canvasPointLeftSelected.pop();

            pqMatching.enableCanvasSelectionPointA($quiz);
            return;
        }

        // On sauvegarde les paramètres du point selectionner
        if (pqMatching.canvasSelectionSide == "left")
            pqMatching.canvasPointLeftSelected.push(pqMatching.canvasPointIdx);
        else
            pqMatching.canvasPointRightSelected.push(pqMatching.canvasPointIdx);

        // On trace la ligne entre le point A et le point B
        var elemLeft = $quiz.find("#"+quzId+"_items_left").find("."+prefix+"MatchingLinkItem")[pqMatching.canvasPointLeftSelected[pqMatching.canvasPointLeftSelected.length -1]];
        var elemRight = $quiz.find("#"+quzId+"_items_right").find("."+prefix+"MatchingLinkItem")[pqMatching.canvasPointRightSelected[pqMatching.canvasPointRightSelected.length -1]];
        pqMatching.drawCanvasItemConnection($canvas, $(elemLeft), $(elemRight), pqMatching.canvasLineColor);

        // On sauvegarde l'etat du canvas
        pqMatching.canvasImg.src = $canvas[0].toDataURL();

        // Event
        pqMatching.enableCanvasSelectionPointA($quiz);
    },

    /**
     * Verify answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    verifyAnswer: function($quiz, mode) {
        var pqMatching = $.publiquiz.question.matching;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var $canvas = $quiz.find("#"+quzId+"_canvas");
        var rightAnswers = $.publiquiz.question.correction($quiz.find("#"+quzId+"_correct"));
        var userAnswers = $.publiquiz.question.correction($quiz.find("#"+quzId+"_user"));

        // On enleve les reponses pour les dessiners en couleur
        pqMatching.canvasRefresh($canvas, pqMatching.canvasImgOrigin);

        // On redessine les reponses en couleur
        var $leftItems = $quiz.find("#"+quzId+"_items_left").find("."+prefix+"MatchingLinkItem");
        var $rightItems = $quiz.find("#"+quzId+"_items_right").find("."+prefix+"MatchingLinkItem");
        $.each(rightAnswers, function(key, value) {
            var $itemLeft = $quiz.find("#"+quzId+"_"+key);
            var position = $.inArray($itemLeft[0], $leftItems);
            var index = $.inArray(position, pqMatching.canvasPointLeftSelected);
            if (index >= 0) {
                var $itemRight = $($rightItems[pqMatching.canvasPointRightSelected[index]]);
                var color = pqMatching.canvasLineColor;
                if (mode == "user") {
                    color = pqMatching.canvasLineColorKo;
                    if (value == $itemRight.data("item-value"))
                        color = pqMatching.canvasLineColorOk;
                } else if (mode == "right") {
                    if (value == $itemRight.data("item-value"))
                        color = pqMatching.canvasLineColorOk;
                } else {
                    color = pqMatching.canvasLineColorKo;
                    var userAnswer = userAnswers[key];
                    if (userAnswer &&  userAnswer == value)
                        color = pqMatching.canvasLineColorOk;
                }

                pqMatching.drawCanvasItemConnection($canvas, $itemLeft, $itemRight, color);
            }
        });
    },

    /**
     * Construct string for answer.
     *
     */
    constructAnswerString: function($quiz) {
        var answer = [];
        var pqMatching = $.publiquiz.question.matching;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var $leftItems = $quiz.find("#"+quzId+"_items_left").find("."+prefix+"MatchingLinkItem");
        var $rightItems = $quiz.find("#"+quzId+"_items_right").find("."+prefix+"MatchingLinkItem");

        $.each(pqMatching.canvasPointLeftSelected, function(idx) {
            var $itemLeft = $($leftItems[this]);
            var $itemRight = $($rightItems[pqMatching.canvasPointRightSelected[idx]]);
            var key = $itemLeft.attr("id");
            key = key.substring(key.length - 3, key.length);
            answer.push(key + $itemRight.data("item-value"));
        });

        return answer.join("::");
    }

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
