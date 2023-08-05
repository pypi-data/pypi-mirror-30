/**
 * @projectDescription publiquiz_wordsearch.js
 * Plugin jQuery for quiz engine "wordsearch".
 *
 * @author Sylvain GUINGOIN
 * @version 0.1
 */


/*jshint globalstrict: true*/
/*global jQuery*/

/******************************************************************************
 *
 *                                  Wordsearch
 *
 *****************************************************************************/

"use strict";

(function ($) {

    $.publiquiz.question.wordsearch = {
        /**
         * Configure the quiz.
         * @param {jQuery} $quiz - Quiz element.
         */
        wordsearchConfigure: function ($quiz) {
            var prefix = $quiz.data("prefix");
            var $engine = $quiz.find("."+prefix+"Engine");
            if ($engine.data("original-state") === undefined)
                $engine.data("original-state", $engine.html());
        },

        /**
         * Enable the quiz.
         * @param {jQuery} $quiz - Quiz element.
         */
        wordsearchEnable: function ($quiz) {
            var pqWS = $.publiquiz.question.wordsearch;
            var prefix = $quiz.data("prefix");

            // Add tools events
            var $tools = $quiz.find("."+prefix+"WordsearchTools");
            // -- Highlighter
            $tools.find("."+prefix+"WordsearchHighlighter").on("click.wordsearch", function () {
                var $this = $(this);
                var $cells = $quiz.find("."+prefix+"GridWordsearch td");

                if (!$this.hasClass("active")) {
                    $tools.children().removeClass("active");
                    $this.addClass("active");
                    $cells.off(".wordsearch");
                    pqWS.enableModeDraw($quiz, $cells);
                }
            });
            // -- Eraser
            $tools.find("."+prefix+"WordsearchEraser").on("click.wordsearch", function () {
                var $this = $(this);
                var $cells = $quiz.find("."+prefix+"GridWordsearch td");

                if (!$this.hasClass("active")) {
                    $tools.children().removeClass("active");
                    $this.addClass("active");
                    $cells.off(".wordsearch");
                    pqWS.enableModeErase($quiz, $cells);
                }
            });

            // Enable default mode: drawing
            $tools.find("."+prefix+"WordsearchHighlighter").addClass("active");
            var $cells = $quiz.find("."+prefix+"GridWordsearch td");
            pqWS.enableModeDraw($quiz, $cells);

        },

        /**
         * Disable the quiz.
         * @param {jQuery} $quiz - Quiz element.
         */
        wordsearchDisable: function ($quiz) {
            var prefix = $quiz.data("prefix");
            $quiz.find("."+prefix+"GridWordsearch td").off(".wordsearch");
            $quiz.find("."+prefix+"WordsearchTools").children()
                .off(".wordsearch").removeClass("active");
        },

        /**
         * Redo quiz.
         * @param {jQuery} $quiz - Quiz element.
         */
        wordsearchRedo: function ($quiz) {
            var prefix = $quiz.data("prefix");
            var $engine = $quiz.find("."+prefix+"Engine");
            if ($engine.data("original-state"))
                $engine.html($engine.data("original-state"));
        },

        /**
         * Display help of quiz.
         * @param {jQuery} $quiz - Quiz element.
         */
        wordsearchHelp: function ($quiz) {
            $.publiquiz.question.displayHelp($quiz);
        },

        /**
         * Retry quiz. Removes wrong answers.
         * @param {jQuery} $quiz - Quiz element.
         */
        wordsearchRetry: function ($quiz) {
            var pqWS = $.publiquiz.question.wordsearch;
            var prefix = $quiz.data("prefix");
            var quizId = $quiz.data("quiz-id");
            var options = $quiz.data("engine-options") || "";
            var strict = (options.search("strict") > -1);
            var $overlay = $quiz.find("."+prefix+"WordsearchOverlay");
            var $highlights = $overlay.children("."+prefix+"WordsearchHighlight");
            var strAnswer = $quiz.find("#"+quizId+"_correct").text();
            var answers = pqWS.strToObj(strAnswer);

            $highlights.each(function () {
                var $this = $(this);
                var highlight = $this.data(prefix+"Highlight");
                var correctHighlights =
                        answers.map(function (w) { return w.highlight; });

                if (!pqWS.isHighlightInList(highlight, correctHighlights, strict)) {
                    $this.remove();
                }
            });
        },

        /**
         * Display textAnswer of quiz.
         * @param {jQuery} $quiz - Quiz element.
         */
        wordsearchTextAnswer: function ($quiz) {
            $.publiquiz.question.displayTextAnswer($quiz);
        },

        /**
         * Insert user answers in quiz.
         * @param {jQuery} $quiz - Quiz element.
         */
        wordsearchInsertUserAnswers: function ($quiz) {
            var pqWS = $.publiquiz.question.wordsearch;
            var quzId = $quiz.data("quiz-id");
            var answer = pqWS.objToStr(pqWS.getAnswers($quiz));
            $.publiquiz.question.writeUserAnswers($quiz, quzId, answer);
        },

        /**
         * Display answers of quiz.
         * @param {jQuery} $quiz - Quiz element.
         * @param {string} mode - "_correct" to show right answers or "_user"
         * to show user answers.
         */
        wordsearchQuizAnswer: function ($quiz, mode) {
            var pqWS = $.publiquiz.question.wordsearch;
            var prefix = $quiz.data("prefix");
            var quizId = $quiz.data("quiz-id");
            var $overlay = $quiz.find("."+prefix+"WordsearchOverlay");

            // Clear highlighted answers
            $overlay.children().remove();

            var strAnswer = "";
            if (mode == "_correct") {
                strAnswer = $quiz.find("#"+quizId+"_correct").text();
            }
            else if (mode == "_user") {
                strAnswer = $quiz.find("#"+quizId+"_user").text();
            }

            var answers = pqWS.strToObj(strAnswer);
            for (var i = 0; i < answers.length; i++) {
                pqWS.drawHighlight($quiz, answers[i].highlight);
            }
        },

        /**
         * Verify user answers. Color right or wrong answers in the quiz.
         * @param {jQuery} $quiz - Quiz element.
         */
        wordsearchVerifyUserAnswer: function ($quiz) {
            $.publiquiz.question.wordsearch.verifyAnswer($quiz, "user");
        },

        /**
         * Verify right answers of quiz. Color only right answers.
         * @param {jQuery} $quiz - Quiz element.
         */
        wordsearchVerifyRightAnswer: function ($quiz) {
            $.publiquiz.question.wordsearch.verifyAnswer($quiz, "right");
        },

        /**
         * Verify all answers. Color right or wrong answers in the quiz.
         * @param {jQuery} $quiz - Quiz element.
         */
        wordsearchVerifyFullAnswer: function ($quiz) {
            $.publiquiz.question.wordsearch.verifyAnswer($quiz, "full");
        },

        /**
         * Compute score of quiz.
         * @param {jQuery} $quiz - Quiz element.
         * @return {Score} Score of the quiz.
         */
        wordsearchComputeScore: function ($quiz) {
            var noMark = false;
            if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("nomark") > -1 )
                noMark = true;

            if (noMark) {
                return {
                    score: 0,
                    total: 0
                };
            }

            var result = $quiz.data("quiz-result");
            if (result === undefined) {
                result = $.publiquiz.question.wordsearch.getScore($quiz);
                $quiz.data("quiz-result", result);
            }

            return result;
        },

        /**
         * Display score of quiz.
         * @param {jQuery} _$quiz - Quiz element.
         */
        wordsearchScore: function (_$quiz) {
        },

        /**
         * Call when quiz is modified.
         * @param {jQuery} $quiz - Quiz element.
         * @return {Object} Context data.
         */
        wordsearchModified: function ($quiz) {
            var pqWS = $.publiquiz.question.wordsearch;
            var engine = $quiz.data("engine");
            var answer = pqWS.objToStr(pqWS.getAnswers($quiz));

            return {
                data: answer,
                engine: engine
            };
        },

        /**
         * Load context of quiz.
         * @param {jQuery} $quiz - Quiz element.
         * @param {String} dataClass - class of data context element.
         */
        wordsearchLoadContext: function ($quiz, dataClass) {
            var pqWS = $.publiquiz.question.wordsearch;
            var prefix = $quiz.data("prefix");
            var quizId = $quiz.data("quiz-id");
            var $overlay = $quiz.find("."+prefix+"WordsearchOverlay");
            var $context = $quiz.find("#"+quizId+"_context");
            var $data = $context.find(dataClass);

            // Clear highlighted answers
            $overlay.children().remove();

            var answers = pqWS.strToObj($data.text());
            for (var i = 0; i < answers.length; i++) {
                pqWS.drawHighlight($quiz, answers[i].highlight);
            }
        },

        /*********************************************************************
         *                          Private Library
         *********************************************************************/

        /**
         * Check if two coordinates are aligned.
         * @param {Coords} start - First coordinates.
         * @param {Coords} end - Second coordinates.
         * @return {boolean} True when aligned, false otherwise.
         */
        areCoordsAligned: function (start, end) {
            return (start.x == end.x || // Horizontal line
                    start.y == end.y || // Vertical line
                    start.x - start.y == end.x - end.y || // Diagonal NW/SE line
                    start.x + start.y == end.x + end.y); // Diagonal SW/NE line
        },

        /**
         * Check if two coordinates are the same.
         * @param {Coords} coords1 - First coordinates.
         * @param {Coords} coords2 - Second coordinates.
         * @return {boolean} True when the coordinates are the same,
         * false otherwise.
         */
        areCoordsEquals: function (coords1, coords2) {
            return (coords1.x == coords2.x &&
                    coords1.y == coords2.y);
        },

        /**
         * Check if two coordinates are valid. They are valid when the are
         * different and aligned.
         * @param {Coords} coords1 - First coordinates.
         * @param {Coords} coords2 - Second coordinates.
         * @return {boolean} True when the coordinates are valid,
         * false otherwise.
         */
        areCoordsValid: function (coords1, coords2) {
            var pqWS = $.publiquiz.question.wordsearch;

            return (!pqWS.areCoordsEquals(coords1, coords2) &&
                pqWS.areCoordsAligned(coords1, coords2));
        },

        /**
         * Check if two highlights are the same, regardless of the
         * direction when strict is not set.
         * @param {Highlight} hl1 - First highlight.
         * @param {Highlight} hl2 - Second highlight.
         * @param {boolean} [strict] - Force direction check.
         * @return {boolean} True when the coordinates are the same,
         * false otherwise.
         */
        areHighlightsEquals: function (hl1, hl2, strict) {
            var pqWS = $.publiquiz.question.wordsearch;
            var test = false;

            if (pqWS.areCoordsEquals(hl1.start, hl2.start) &&
                pqWS.areCoordsEquals(hl1.end, hl2.end))
                test = true;

            if (!test && !strict &&
                pqWS.areCoordsEquals(hl1.start, hl2.end) &&
                pqWS.areCoordsEquals(hl1.end, hl2.start))
                test = true;

            return test;
        },

        /**
         * Draw the highlight for a word, given its starting and ending
         * coordinates.
         * @param {jQuery} $quiz - Quiz element.
         * @param {Highlight} highlight - Highlight coordinates.
         */
        drawHighlight: function ($quiz, highlight) {
            var pqWS = $.publiquiz.question.wordsearch;
            var prefix = $quiz.data("prefix");
            var $start = pqWS.getCell($quiz, highlight.start);
            var $end = pqWS.getCell($quiz, highlight.end);
            if ($start.length == 0 || $end.length == 0)
                return;

            var $highlight = pqWS.drawHighlightStart($quiz, $start);
            pqWS.drawHighlightEnd($highlight, $start, $end);
            $highlight.data(prefix+"Highlight", highlight);
            $highlight.removeClass(prefix+"WordsearchHighlightDrawing");
        },

        /**
         * Draw the highlight to the end of the word.
         * @param {jQuery} $highlight - Highlight element.
         * @param {jQuery} $start - Start cell.
         * @param {jQuery} $end - End cell.
         */
        drawHighlightEnd: function ($highlight, $start, $end) {
            var position = $end.position();
            var origPosition = $start.position();
            var cellWidth = $start.width();

            var distX = position.left - origPosition.left;
            var distY = position.top - origPosition.top;

            // Calculate width
            var deltaX = Math.abs(distX);
            var deltaY = Math.abs(distY);
            var distance = Math.sqrt(
                Math.pow(deltaX, 2) + Math.pow(deltaY, 2)) + cellWidth;
            $highlight.css("width", distance);

            // Calculate rotation
            var cos = distX / distance;
            var signY = Math.sign(distY);
            var signX = Math.sign(distX);
            var angle = Math.acos(cos)*signY;
            angle = Math.round(angle / (Math.PI / 4)) * (Math.PI / 4);
            if (angle == 0 && signX < 0)
                angle = Math.PI;

            $highlight.css("transform", "rotate("+angle+"rad)");
        },

        /**
         * Draw the beginning of a new highlight.
         * @param {jQuery} $quiz - Quiz element.
         * @param {jQuery} $start - Start cell.
         * @param {string} [type] - Suffix of an additional class.
         * @return {jQuery} Highlight element.
         */
        drawHighlightStart: function ($quiz, $start, type) {
            var prefix = $quiz.data("prefix");
            var startPosition = $start.position();
            var $overlay = $quiz.find("."+prefix+"WordsearchOverlay");
            var $highlight = $("<div/>");
            $highlight.addClass(prefix+"WordsearchHighlight");
            $highlight.addClass(prefix+"WordsearchHighlightDrawing");
            if (type)
                $highlight.addClass(prefix+"WordsearchHighlight"+type);
            $overlay.append($highlight);
            $highlight.css({
                top: startPosition.top,
                left: startPosition.left
            });

            return $highlight;
        },

        /**
         * Add events to draw highlight.
         * @param {jQuery} $quiz - Quiz element.
         * @param {jQuery} $cells - Set with cells of the table.
         */
        enableModeDraw: function ($quiz, $cells) {
            var pqWS = $.publiquiz.question.wordsearch;

            $cells.on("mousedown.wordsearch touchstart.wordsearch", function (e) {
                e.preventDefault();

                var $start = $(this);
                var $highlight = pqWS.drawHighlightStart($quiz, $start);

                $(document).on({
                    "mousemove.wordsearch touchmove.wordsearch": function (e) {
                        e.preventDefault();
                        pqWS.handleEventMove(e, $quiz, $start, $highlight);
                    },

                    "mouseup.wordsearch touchend.wordsearch": function (e) {
                        e.preventDefault();
                        if (pqWS.handleEventEnd(e, $quiz, $start, $highlight))
                            $.publiquiz.context.onQuizModified($.publiquiz.question, $quiz);
                    }
                });
            });
        },

        /**
         * Add event to remove highlight.
         * @param {jQuery} $quiz - Quiz element.
         * @param {jQuery} $cells - Set with cells of the table.
         */
        enableModeErase: function ($quiz, $cells) {
            var pqWS = $.publiquiz.question.wordsearch;

            $cells.on("click.wordsearch", function (e) {
                e.preventDefault();
                if (pqWS.handleEventErase(e, $quiz))
                    $.publiquiz.context.onQuizModified($.publiquiz.question, $quiz);
            });
        },

        /**
         * Find a highlight according to data of a word item.
         * @param {jQuery} $quiz - Quiz element.
         * @param {jQuery} $word - Word item element.
         * @return {jQuery} Highlight element matching coords.
         */
        findHighlight: function ($quiz, $word) {
            var pqWS = $.publiquiz.question.wordsearch;
            var prefix = $quiz.data("prefix");
            var wordHighlight = $word.data(prefix+"Highlight");
            var $overlay = $quiz.find("."+prefix+"WordsearchOverlay");
            var $highlights = $overlay.children("."+prefix+"WordsearchHighlight");
            var $highlight = $();

            $highlights.each(function () {
                var $this = $(this);
                var currHighlight = $this.data(prefix+"Highlight");

                if (pqWS.areHighlightsEquals(currHighlight, wordHighlight, true)) {
                    $highlight = $this;

                    return false;
                }

                return true;
            });

            return $highlight;
        },

        /**
         * Find letters selected between a pair of coordinates.
         * @param {jQuery} $quiz - Quiz element.
         * @param {Highlight} highlight - Highlight coordinates.
         * @return {string} Letters found in the highlight.
         */
        findLetters: function ($quiz, highlight) {
            var pqWS = $.publiquiz.question.wordsearch;
            var start = highlight.start;
            var end = highlight.end;
            var xDir = Math.sign(end.x - start.x);
            var yDir = Math.sign(end.y - start.y);
            var length =
                    Math.max(Math.abs(end.x - start.x), Math.abs(end.y - start.y)) + 1;
            var selection = "";

            for (var i = 0; i < length; i++) {
                var x = start.x + i * xDir;
                var y = start.y + i * yDir;
                selection += pqWS.getCell($quiz, {x: x, y: y}).text();
            }

            return selection;
        },

        /**
         * Get quiz answers from HTML.
         * @param {jQuery} $quiz - Quiz element.
         * @return {Word[]} An array with each highlight.
         */
        getAnswers: function ($quiz) {
            var prefix = $quiz.data("prefix");
            var $overlay = $quiz.find("."+prefix+"WordsearchOverlay");
            var highlights = [];

            $overlay.children().each(function () {
                highlights.push({
                    itemId: "000",
                    highlight: $(this).data(prefix+"Highlight")
                });
            });

            return highlights;
        },

        /**
         * Get the cell corresponding to table coordinates.
         * @param {jQuery} $quiz - Quiz element.
         * @param {Coords} coords - Coordinates in the table.
         * @return {jQuery} Table cell
         */
        getCell: function ($quiz, coords) {
            var prefix = $quiz.data("prefix");

            return $quiz.find("."+prefix+"GridWordsearch")
                .find("tr:eq("+coords.y+")")
                .children(":eq("+coords.x+")");
        },

        /**
         * Get the table coordinates of a cell.
         * @param {jQuery} $cell - Table cell
         * @return {Coords} Coordinates in the table.
         */
        getCoords: function ($cell) {
            return {
                x: $cell.index(),
                y: $cell.parent().index()
            };
        },

        /**
         * Get the score of the quiz.
         * @param {jQuery} $quiz - Quiz element.
         * @return {Score} Score of the quiz.
         */
        getScore: function ($quiz) {
            var pqWS = $.publiquiz.question.wordsearch;
            var prefix = $quiz.data("prefix");
            var quizId = $quiz.data("quiz-id");
            var options = $quiz.data("engine-options") || "";
            var strict = (options.search("strict") > -1);

            var $overlay = $quiz.find("."+prefix+"WordsearchOverlay");
            var $highlights = $overlay.children("."+prefix+"WordsearchHighlight");
            var strAnswer = $quiz.find("#"+quizId+"_correct").text();
            var answers = pqWS.strToObj(strAnswer);
            var score = 0;
            var total = answers.length;

            $highlights.each(function () {
                var $this = $(this);
                var currHighlight = $this.data(prefix+"Highlight");
                var correctHighlights =
                        answers.map(function (w) { return w.highlight; });

                if (pqWS.isHighlightInList(currHighlight, correctHighlights, strict))
                    score += 1;
            });

            return {score: score, total: total};
        },

        /**
         * Handle event: End. Draw the end of the highlight if the start and
         * end cells are valid.
         * @param {Event} e - End event.
         * @param {jQuery} $quiz - Quiz element.
         * @param {jQuery} $start - Start cell element.
         * @param {jQuery} $highlight - Highlight element.
         * @return {boolean} True when the highlight is valid, false otherwise.
         */
        handleEventEnd: function (e, $quiz, $start, $highlight) {
            $(document).off(".wordsearch");
            var pqWS = $.publiquiz.question.wordsearch;
            var prefix = $quiz.data("prefix");
            var $cells = $quiz.find("."+prefix+"GridWordsearch td");
            var newCoords = $.publiquiz.question.eventPosition(null, e);
            newCoords[0] -= $(document).scrollLeft();
            newCoords[1] -= $(document).scrollTop();
            var $end = $(document.elementFromPoint(newCoords[0], newCoords[1]));
            $end = $end.closest("td");
            var startCoords = pqWS.getCoords($start);
            var endCoords = pqWS.getCoords($end);

            if ($end.is($cells) && pqWS.areCoordsValid(startCoords, endCoords)) {
                pqWS.drawHighlightEnd($highlight, $start, $end);
                $highlight.data(prefix+"Highlight", {
                    start: pqWS.getCoords($start),
                    end: pqWS.getCoords($end)
                });
                $highlight.removeClass(prefix+"WordsearchHighlightDrawing");

                return true;
            }
            else {
                $highlight.remove();

                return false;
            }
        },

        /**
         * Handle event: Erase. Remove the last highlight that covers target cell.
         * @param {Event} e - Touch event.
         * @param {jQuery} $quiz - Quiz element.
         * @return {boolean} True when a highlight has been removed,
         * false otherwise.
         */
        handleEventErase: function (e, $quiz) {
            var prefix = $quiz.data("prefix");
            var newCoords = $.publiquiz.question.eventPosition(null, e);
            newCoords[0] -= $(document).scrollLeft();
            newCoords[1] -= $(document).scrollTop();

            var $overlay = $quiz.find("."+prefix+"WordsearchOverlay");
            $overlay.css("z-index", "1");
            var $target = $(document.elementFromPoint(newCoords[0], newCoords[1]));
            $overlay.css("z-index", "");

            if ($target.hasClass(prefix+"WordsearchHighlight")) {
                $target.remove();

                return true;
            }

            return false;
        },

        /**
         * Handle event: Move. Draw the highlight following the pointer.
         * @param {Event} e - Move event.
         * @param {jQuery} $cells - Set with cells of the table.
         * @param {jQuery} $start - Start cell element.
         * @param {jQuery} $highlight - Highlight element.
         */
        handleEventMove: function (e, $quiz, $start, $highlight) {
            var pqWS = $.publiquiz.question.wordsearch;
            var prefix = $quiz.data("prefix");
            var $cells = $quiz.find("."+prefix+"GridWordsearch td");
            var newCoords = $.publiquiz.question.eventPosition(null, e);
            newCoords[0] -= $(document).scrollLeft();
            newCoords[1] -= $(document).scrollTop();
            var $target = $(document.elementFromPoint(newCoords[0], newCoords[1]));
            $target = $target.closest("td");
            var startCoords = pqWS.getCoords($start);
            var endCoords = pqWS.getCoords($target);

            if ($target.is($cells) && pqWS.areCoordsAligned(startCoords, endCoords)) {
                pqWS.drawHighlightEnd($highlight, $start, $target);
                $highlight.show();
            }
            else {
                $highlight.hide();
            }
        },

        /**
         * Translate an integer to a coordinate string.
         * Ex: 1 -> "a", 6 -> "f", 55 -> "bc", 703 -> "aaa".
         * @param {int} number - Integer value.
         * @return {string} String value.
         */
        intToStr: function (number) {
            var val = "";

            var maxPow = 1;
            while (Math.pow(26, maxPow) < number) maxPow += 1;
            maxPow -= 1;

            for (var i = maxPow; i >= 0; i--) {
                var curr = Math.floor(number / Math.pow(26, i));
                val += String.fromCharCode(curr+96);
                number = number % Math.pow(26, i);
            }

            return val;
        },

        /**
         * Check if a highlight is in a list.
         * @param {Highlight} highlight - Highlight to search.
         * @param {Highlight[]} list - List of highlights.
         * @param {boolean} [strict] - Force direction check.
         * @return {boolean} True when highlight is in the list, false otherwise.
         */
        isHighlightInList: function (highlight, list, strict) {
            var pqWS = $.publiquiz.question.wordsearch;
            var valid = false;
            for (var i = 0; i < list.length; i++) {
                if (pqWS.areHighlightsEquals(highlight, list[i], strict)) {
                    valid = true;
                    break;
                }
            }

            return valid;
        },

        /**
         * Get string formatted like correction from JS Object.
         * @param {Word[]} words - An array containing coordinates for highlights.
         * @return {string} String to write in HTML.
         */
        objToStr: function (words) {
            var pqWS = $.publiquiz.question.wordsearch;
            var arr = [];
            for (var i = 0; i < words.length; i++) {
                var hl = words[i].highlight;
                var str = ""+words[i].itemId;
                str += pqWS.intToStr(hl.start.x+1) + ";" + (hl.start.y+1);
                str += "-" + pqWS.intToStr(hl.end.x+1) + ";" + (hl.end.y+1);
                arr.push(str);
            }

            return arr.join("::");
        },

        /**
         * Translate a coordinate string to integer.
         * Ex: "a" -> 1, "f" -> 6, "bc" -> 55, "aaa" -> 703.
         * @param {string} str - String value.
         * @return {number} Integer value.
         */
        strToInt: function (str) {
            var val = 0;
            var split = str.split("").reverse();
            for (var i = 0; i < split.length; i++) {
                val += Math.pow(26, i) * (split[i].charCodeAt(0) - 96);
            }

            return val;
        },

        /**
         * Get correction from string in HTML to JS Object.
         * @param {string} str - String from HTML.
         * @return {Word[]} An array of Word with coordinates for highlights.
         */
        strToObj: function (str) {
            if (str == "")
                return [];

            var pqWS = $.publiquiz.question.wordsearch;
            var allCoords = [];
            var highlights = str.split("::");
            for (var i = 0; i < highlights.length; i++) {
                var id = highlights[i].substr(0, 3);
                var split = highlights[i].substr(3).split("-");
                var start = split[0].split(";");
                var end = split[1].split(";");

                allCoords.push({
                    itemId: id,
                    highlight: {
                        start: {
                            x: pqWS.strToInt(start[0]) - 1,
                            y: start[1] - 1
                        },
                        end: {
                            x: pqWS.strToInt(end[0]) - 1,
                            y: end[1] - 1
                        }
                    }
                });
            }

            return allCoords;
        },

        /**
         * Verify answer.
         * @param {jQuery} $quiz - Quiz element.
         * @param {string} mode - Mode user/right/full.
         */
        verifyAnswer: function ($quiz, mode) {
            var pqWS = $.publiquiz.question.wordsearch;
            var prefix = $quiz.data("prefix");
            var quizId = $quiz.data("quiz-id");
            var options = $quiz.data("engine-options") || "";
            var strict = (options.search("strict") > -1);
            var $overlay = $quiz.find("."+prefix+"WordsearchOverlay");
            var $highlights = $overlay.children("."+prefix+"WordsearchHighlight");
            var strAnswer = $quiz.find("#"+quizId+"_correct").text();
            var answers = pqWS.strToObj(strAnswer);

            $highlights.each(function () {
                var $this = $(this);
                var currHighlight = $this.data(prefix+"Highlight");
                var correctHighlights =
                        answers.map(function (w) { return w.highlight; });
                var valid = pqWS.isHighlightInList(currHighlight, correctHighlights, strict);

                if (valid) {
                    $this.addClass("answerOk");
                    // TODO: find word item with itemId
                }
                else if (mode != "right") {
                    $this.addClass("answerKo");
                }
            });
        }

        /**
         * Word representation.
         * @typedef Word
         * @property {string} itemId - Item id in the list of words.
         * @property {Highlight} highlight - Highlight coordinates.
         */

        /**
         * Highlight coordinates in the table.
         * @typedef Highlight
         * @property {Coords} start - Start coordinates.
         * @property {Coords} end - End coordinates.
         */

        /**
         * Coordinate representation.
         * @typedef Coords
         * @property {number} x - X-axis value.
         * @property {number} y - Y-axis value.
         */

        /**
         * Position representation in the window.
         * @typedef Position
         * @property {number} top - Top value.
         * @property {number} left - Left value.
         */

        /**
         * Size representation of an element.
         * @typedef Size
         * @property {number} width - Width value.
         * @property {number} height - Height value.
         */

        /**
         * Score object.
         * @typedef Score
         * @property {number} score - Current user score.
         * @property {number} total - Total score for the quiz.
         */
    };

    // Register function
    $.publiquiz.question.register("wordsearch", {
        configure: $.publiquiz.question.wordsearch.wordsearchConfigure,
        enable: $.publiquiz.question.wordsearch.wordsearchEnable,
        disable: $.publiquiz.question.wordsearch.wordsearchDisable,
        redo: $.publiquiz.question.wordsearch.wordsearchRedo,
        help: $.publiquiz.question.wordsearch.wordsearchHelp,
        retry: $.publiquiz.question.wordsearch.wordsearchRetry,
        textAnswer: $.publiquiz.question.wordsearch.wordsearchTextAnswer,
        insertUserAnswers: $.publiquiz.question.wordsearch.wordsearchInsertUserAnswers,
        quizAnswer: $.publiquiz.question.wordsearch.wordsearchQuizAnswer,
        verifyUserAnswer: $.publiquiz.question.wordsearch.wordsearchVerifyUserAnswer,
        verifyRightAnswer: $.publiquiz.question.wordsearch.wordsearchVerifyRightAnswer,
        verifyFullAnswer: $.publiquiz.question.wordsearch.wordsearchVerifyFullAnswer,
        computeScore: $.publiquiz.question.wordsearch.wordsearchComputeScore,
        quizScore: $.publiquiz.question.wordsearch.wordsearchScore,
        modified: $.publiquiz.question.wordsearch.wordsearchModified,
        loadContext: $.publiquiz.question.wordsearch.wordsearchLoadContext
    });

}(jQuery));
