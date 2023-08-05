/**
 * @projectDescription Memory
 *
 * @author Tien Haï NGUYEN
 * @version 1.0
 */

/*global jQuery: true */
/*global Image: true */
/*global Audio: true */
/*global setInterval: true */
/*global clearInterval: true */
/*global setTimeout: true */
/*global clearTimeout: true */


(function ($) {

    "use strict";

    /**************************************************************************
     **************************************************************************
     *
     *                          Define namespace memory
     *
     **************************************************************************
     *************************************************************************/


    /*************************************************************************/
    /*                                memory                                 */
    /*************************************************************************/

    if (!$.memory)
        $.memory = {};


    /*************************************************************************/
    /*                           memory.defaults                             */
    /*************************************************************************/

    $.memory.defaults = {
        mainClass: "pquizQuiz",     // define class above all quiz
        prefix: "pquiz",            // Prefix des class pour le memory
        hideRightAnswer: false,     // Cache/Affiche les paires trouvées
        isReady: false,             // Indique l'état du plugin
        itemMargin: 20,             // Marge entre les paires
        currentTimerId: null,       // Identifiant du timer en cours
        currentTimer: null,         // Function timer en cours
        currentCountdownValue: 0,   // Decompte restant en cours
        currentChronoValue:  0,     // Valeur du chrono en cours
        isLoading: false,           // Indique le chargement du context
        reorganizeMethod: null,     // Methods utiliser pour reorganizer les items
        forcedColumn: 4,            // Nombre de column forcer
        isAjustBoardSize: false,    // Ajustement de la taille du board
        isResize: false,            // Resize en cours
        animEnd: "webkitTransitionEnd otransitionend oTransitionEnd msTransitionEnd transitionend", // Events end animation
        popupContentClose: true     // define where click for close dialog
    };


    /*************************************************************************/
    /*                             memory.game                               */
    /*************************************************************************/

    $.memory.game = {

        playerAudio: null,

        /**
         * Active a memory game play.
         *
         * @param {jQuery} $memory - Memory engine.
         */
        activateMemory: function($memory) {
            var prefix = $.memory.defaults.prefix;
            var $items = $memory.find("."+prefix+"MemoryItems");

            // On récupere la dimension de l'image back
            var itemWidth = $items.data("item-width") || 0;
            if (itemWidth === 0) {
                var src = $items.find("."+prefix+"MemoryItem .back img").get(0).src;
                var card = new Image();
                card.src = src;
                $(card).on("load", function() {
                    // Card height
                    $items.data("item-width", card.width);
                    $items.data("item-height", card.height);

                    // Ajust board size
                    $.memory.game.ajustBoardSize($memory);

                    var max = 5000;
                    var step = 250;
                    var count = 0;
                    var timer = setInterval(function() {
                        if ($.memory.defaults.isAjustBoardSize === false || count > max) {
                            $.memory.defaults.isAjustBoardSize = false;
                            $.memory.game.activateMemory($memory);
                            clearInterval(timer);
                        }
                        count += step;
                    }, step);

                });
                return;
            }

            $memory.data("prefix", prefix);
            $memory.data("hideRightAnswer", $.memory.defaults.hideRightAnswer);

            // Set default reorganize method
            $.memory.defaults.reorganizeMethod = $.memory.game.reorganizeItems;

            // On place les items
            $.memory.defaults.reorganizeMethod($memory);

            // Set events
            var finishResize;
            $.memory.defaults.isResize = false;
            $(window).resize(function() {
                if (!$.memory.defaults.isResize) {
                    $.publianim.addLoading($memory, $.memory.defaults.prefix);
                    $.memory.defaults.isResize = true;
                    $memory.find("."+prefix+"MemoryPick").fadeTo(250, 0);
                }
                clearTimeout(finishResize);
                finishResize = setTimeout($.memory.game.doneResizing, 250, $memory);
            });

            $memory.find("."+prefix+"MemoryAnswerBox").click(function(ev) {
                var $answer = $(this);
                $.memory.game.onCloseAnswerBox($memory, $answer);
            });

            $memory.find("."+prefix+"MemoryCongratulateBox").click(function(ev) {
                var $box = $(this);
                $box.addClass("hidden");
                $.memory.action.redo($memory);
            });

            // Set event on popups
            $.memory.game.popupEvents($memory);

            // Set button events
            $.memory.game.enableSlotButtons($memory);

            //
            $.memory.defaults.isReady = true;
        },

        /**
         * Method appeler lorsqu'on a finit de resize.
         *
         * @param {jQuery} $memory - Memory engine.
         */
        doneResizing: function($memory) {
            var prefix = $.memory.defaults.prefix;
            $.memory.defaults.isResize = false;
            $.memory.game.ajustBoardSize($memory);

            function end() {
                if ($.memory.defaults.reorganizeMethod == $.memory.game.reorganizeItems) {
                    $.memory.game.resizePickItems($memory);
                } else {
                    $.memory.game.forcedResizePickItems($memory);
                }
                $.memory.game.resizeRightAnswer($memory);
                $.memory.game.resizeCorrectItems($memory);
                $memory.find("."+prefix+"MemoryPick").fadeTo(250, 1);
                $.publianim.removeLoading($memory, $.memory.defaults.prefix);
            }

            var max = 5000;
            var step = 250;
            var count = 0;
            var timer = setInterval(function() {
                if ($.memory.defaults.isAjustBoardSize === false || count > max) {
                    end();
                    clearInterval(timer);
                }
                count += step;
            }, step);
        },

        /**
         * On n'accept pas de scroll pour cette anim.
         *
         * @param {jQuery} $memory - Memory engine.
         */
        ajustBoardSize: function($memory) {
            $.memory.defaults.isAjustBoardSize = true;
            var prefix = $.memory.defaults.prefix;
            var $board = $memory.find("."+prefix+"MemoryBoard");
            var boardHeight = $board.height();

            function hasScrollbar() {
                return (document.documentElement.scrollHeight !== document.documentElement.clientHeight);
            }

            if (hasScrollbar()) {
                boardHeight = boardHeight - (document.documentElement.scrollHeight - document.documentElement.clientHeight);
            } else {
                while (!hasScrollbar()) {
                    boardHeight += 1;
                    $board.height(boardHeight);
                }
                boardHeight -= 1;
            }

            if (boardHeight <= 480)
                boardHeight = 480;

            $board.height(boardHeight-20);
            $.memory.defaults.isAjustBoardSize = false;
        },

        /**
         * On place les items.
         *
         * @param {jQuery} $memory - Memory engine.
         */
        reorganizeItems: function($memory) {
            var prefix = $memory.data("prefix");

            // On mélange les items
            var $items = $memory.find("."+prefix+"MemoryItems");
            $.memory.game.shuffleItems($items);

            // On récupère le nombre de paire désiré
            var $board = $memory.find("."+prefix+"MemoryBoard");
            var display = $board.data("number-display");

            // On constitue les paires suivant le nombre désiré
            var itemsValue = [];
            var itemsArray = [];
            $items.find("."+prefix+"MemoryItem").each( function() {
                var $item = $(this);
                var value = $item.data("item-value");
                var order = $item.data("item-order");
                var $itemChild = $items.find("."+prefix+"MemoryItem")
                    .filter("[data-item-value=\""+value+"\"]")
                    .filter("[data-item-order!=\""+order+"\"]");

                if ($.inArray(value, itemsValue) >= 0)
                    return true;

                //
                $item = $item.clone();
                $itemChild = $itemChild.clone();
                itemsValue.push(value);
                itemsArray.push($item);
                itemsArray.push($itemChild);

                // On verifie si on a atteind le nombre de cartes désiré
                if (itemsArray.length == (display * 2))
                    return false;

                return true;
            });

            // On rempli la pioche d'items
            $.memory.game.fillPickItems($memory, $.memory.game.shuffleArray(itemsArray));
            $.memory.game.resizePickItems($memory);
        },

        /**
         * On place les items suivants le nombre de colonne désiré.
         *
         * @param {jQuery} $memory - Memory engine.
         */
        forcedReorganizeItems: function($memory) {
            var prefix = $memory.data("prefix");

            // On mélange les items
            var $items = $memory.find("."+prefix+"MemoryItems");
            $.memory.game.shuffleItems($items);

            // On récupère le nombre de colonne désiré
            var $board = $memory.find("."+prefix+"MemoryBoard");
            var display = $board.data("number-display");
            var column = $board.data("column-value");
            if (column === undefined)
                column = $.memory.defaults.forcedColumn;
            var row = parseInt((display * 2) / column, 10);
            if (((display * 2) % column) > 0)
                row += 1;

            // On constitue les paires suivant le nombre désiré
            var itemsValue = [];
            var itemsArray = [];
            $items.find("."+prefix+"MemoryItem").each( function() {
                var $item = $(this);
                var value = $item.data("item-value");
                var order = $item.data("item-order");
                var $itemChild = $items.find("."+prefix+"MemoryItem")
                    .filter("[data-item-value=\""+value+"\"]")
                    .filter("[data-item-order!=\""+order+"\"]");

                if ($.inArray(value, itemsValue) >= 0)
                    return true;

                //
                $item = $item.clone();
                $itemChild = $itemChild.clone();
                itemsValue.push(value);
                itemsArray.push($item);
                itemsArray.push($itemChild);

                // On verifie si on a atteind le nombre de cartes désiré
                if (itemsArray.length == (display*2))
                    return false;

                return true;
            });

            // On rempli la pioche d'items
            $.memory.game.forcedFillPickItems($memory, $.memory.game.shuffleArray(itemsArray));
            $.memory.game.forcedResizePickItems($memory);
        },

        /**
         * On place les items.
         *
         * @param {jQuery} $memory - Memory.
         * @param {Array} data - Tableau contenant les items a placé.
         */
        forcedFillPickItems: function($memory, data) {
            var prefix = $memory.data("prefix");
            var $board = $memory.find("."+prefix+"MemoryBoard");
            var display = $board.data("number-display");
            var column = $board.data("column-value");
            if (column === undefined)
                column = $.memory.defaults.forcedColumn;
            var $pick = $memory.find("."+prefix+"MemoryPick");

            // On vide l'ancienne pioche
            $pick.children().remove();

            // On place la nouvelle pioche
            var $rows = $("<div>").addClass("rows");
            $pick.append($rows);

            var count = 0;
            var $row = $("<div>").addClass("row");
            $rows.append($row);
            $.each(data, function() {
                count += 1;
                var $item = $(this);
                $row.append($item);
                if (count >= column) {
                    count = 0;
                    $row = $("<div>").addClass("row");
                    $rows.append($row);
                }
            });
        },

        /**
         * On ferme le dialogue affichant la bonne réponse.
         *
         * @param {jQuery} $memory - Memory engine.
         * @param {jQuery} $answer - Box answer.
         */
        onCloseAnswerBox: function($memory, $answer) {
            var prefix = $memory.data("prefix");

            // Close box answer
            $answer.addClass("hidden");
            $answer.find(".container").empty();

            // Define if game is finish
            var remaining = $memory.find("."+prefix+"MemoryPick ."+prefix+"MemoryItem").not(".correct");
            if (remaining.length > 0) {
                $.memory.action.resumeTimer($memory.data("action"));
                return;
            }

            // Display congratulation box
            var $box = $memory.find("."+prefix+"MemoryCongratulateBox");
            if ($box.length > 0) {
                $box.removeClass("hidden");
                var audio = $box.find("audio")[0];
                $.memory.game.playAudio(audio);
            }

            // Scenario finish game
            var $action = $memory.data("action");
            if ($action.scenario.onFinishGame !== undefined) {
                $.memory.context.onActionMemoryModified($action.data("memory"), "onFinishGame");
                $.memory.action.doActions($action, "onFinishGame");
            }
        },

        /**
         * Disconnect les events sur les items.
         *
         * @param {jQuery} $memory - Memory engine.
         */
        disable: function($memory) {
            var prefix = $memory.data("prefix");
            var $pick = $memory.find("."+prefix+"MemoryPick");
            $pick.find("."+prefix+"MemoryItem").off("click");
        },

        /**
         * Affiche la correction.
         *
         * @param {jQuery} $memory - Memory engine.
         */
        showCorrectAnswer: function($memory) {
            var prefix = $memory.data("prefix");
            var $correct = $memory.find("."+prefix+"MemoryCorrectAnswer");
            if ($correct.length > 0) {
                if ($correct.children().length === 0) {
                    var $items = $memory.find("."+prefix+"MemoryPick ."+prefix+"MemoryItem");
                    $items.filter("[data-item-order=\"001\"]").each( function() {
                        var $item = $(this);
                        var value = $item.data("item-value");
                        var $itemChild = $items.filter("[data-item-value=\""+value+"\"]").filter("[data-item-order=\"002\"]");
                        var $itemCorrect = $("<div>").addClass(prefix+"MemoryItemCorrect");
                        $itemCorrect.append($item.find(".front img").clone().removeAttr("style"));
                        $itemCorrect.append($itemChild.find(".front img").clone().removeAttr("style"));
                        $correct.append($itemCorrect);
                    });
                }
                $memory.find("."+prefix+"MemoryPick").addClass("hidden");
                $correct.removeClass("hidden");
                $.memory.game.resizeCorrectItems($memory);
            }
        },

        /**
         * Affiche les réponses du joueur.
         *
         * @param {jQuery} $memory - Memory engine.
         */
        showUserAnswer: function($memory) {
            var prefix = $memory.data("prefix");
            var $correct = $memory.find("."+prefix+"MemoryCorrectAnswer");
            var $pick = $memory.find("."+prefix+"MemoryPick");
            $pick.find("."+prefix+"MemoryItem").removeClass("item-visibility");
            $pick.find("."+prefix+"MemoryItem.flipped").not(".correct").removeClass("flipped first");
            $correct.addClass("hidden");
            $pick.removeClass("hidden");
        },

        /**
         * On place les items.
         *
         * @param {jQuery} $memory - Memory.
         * @param {Array} data - Tableau contenant les items a placé.
         */
        fillPickItems: function($memory, data) {
            var prefix = $memory.data("prefix");
            var $pick = $memory.find("."+prefix+"MemoryPick");

            // On vide l'ancienne pioche
            $pick.children().remove();

            // On place la nouvelle pioche
            var number = 1;
            $.each(data, function() {
                var $item = $(this);

                // Numerotation de l'item
                var $num = $("<span>").addClass(prefix+"MemoryCardNumber abs").text(number);
                $item.find(".back").append($num);
                number += 1;

                // Append item to pick
                $pick.append($item);
                $item.click( function(ev) {
                    ev.preventDefault();
                    $.memory.game.onMemoryItem($memory, $(this));
                });
            });
        },

        /**
         * This function call when click on item.
         *
         * @param {jQuery} $memory - Memory engine.
         * @param {jQuery} $item - jQuery element, card.
         */
        onMemoryItem: function($memory, $item) {
            var prefix = $memory.data("prefix");

            // Start timer
            var $action = $memory.data("action");
            if ($action.data("countdown") !== undefined)
                $.memory.action.startCountdown($action);
            if ($action.find("."+prefix+"Chrono").length > 0)
                $.memory.action.startChrono($action);

            // If the card is all ready turn, do nothing.
            if ($item.hasClass("flipped"))
                return;

            // Wait anim finish
            var anim_perform = $memory.data("anim-perform") || "";
            if (anim_perform)
                return;

            // We turn the card
            $item.addClass("flipped");

            // Play audio anim
            $.memory.game.playAudio($memory.find(".anim audio")[0]);

            // Assign card
            var first_card = $memory.find("."+prefix+"MemoryItem.first").get(0) || null;
            var $first_card = null;
            var $second_card = null;
            if (first_card === null) {
                $item.addClass("first");
            } else {
                $first_card = $(first_card);
                $second_card = $item;
            }

            // Save context
            $.memory.context.onMemoryModified($memory);

            // If the first card turn, wait player turn the second
            // If second_card turn, wait anim finish before do anything.
            if ($second_card === null) {
                return;
            } else {
                $memory.data("anim-perform", "true");
                $second_card.on($.memory.defaults.animEnd, function(e) {
                    $.memory.game.validateMemory($memory, $first_card, $second_card);
                    $(this).off($.memory.defaults.animEnd);
                });
            }
        },

        /**
         * This function call for validate card turn.
         *
         * @param {jQuery} $memory - Memory engine.
         * @param {jQuery} $first_card - Object card.
         * @param {jQuery} $second_card - Object card.
         */
        validateMemory: function($memory, $first_card, $second_card) {

            /**
             * Do at end.
             */
            function finallyValidate($memory, $fc) {
                $fc.removeClass("first");
                $memory.data("anim-perform", "");
                $.memory.context.onMemoryModified($memory);
            }

            var first_value = $first_card.data("item-value");
            first_value = first_value.substring(4, first_value.length);
            var second_value = $second_card.data("item-value");
            second_value = second_value.substring(4, second_value.length);

            if (first_value != second_value) {
                // Remove flipped class
                var delay = 500;
                var prefix = $memory.data("prefix") || "";
                var $board = $memory.find("."+prefix+"MemoryBoard");
                if ($board.data("memoryDelay"))
                    delay = parseInt($board.data("memoryDelay"), 10);
                setTimeout(function() {
                    $first_card.removeClass("flipped");
                    $second_card.removeClass("flipped");
                    finallyValidate($memory, $first_card);
                }, delay);

                // Play audio anim
                $.memory.game.playAudio($memory.find(".wrong audio")[0]);
            } else {
                $first_card.addClass("correct");
                $second_card.addClass("correct");
                $.memory.game.displayRightAnswer($memory, $first_card, $second_card);
                finallyValidate($memory, $first_card);
            }
        },

        /**
         * This function call for display right answer.
         *
         * @param {jQuery} $memory - Memory engine.
         * @param {jQuery} $first_card - Object card.
         * @param {jQuery} $second_card - Object card.
         */
        displayRightAnswer: function($memory, $first_card, $second_card) {
            var prefix = $memory.data("prefix") || "";
            var hideRightAnswer = $memory.data("hideRightAnswer") || false;

            //
            if (hideRightAnswer) {
                $first_card.addClass("item-visibility");
                $second_card.addClass("item-visibility");
            }

            //
            var $first = null;
            var $second = null;
            var audio = $memory.find(".right audio")[0];
            var $answer = $memory.find("."+prefix+"MemoryAnswerBox");
            if ($answer.length > 0) {
                var $container = $answer.find(".container");
                if ($first_card.data("item-order") > $second_card.data("item-order")) {
                    $first = $second_card.find(".front").clone();
                    $second = $first_card.find(".front").clone();
                } else {
                    $first = $first_card.find(".front").clone();
                    $second = $second_card.find(".front").clone();
                }

                $container.append($first
                        .removeClass("front abs")
                        .addClass("itemAnswer")
                        .css("position", ""));
                $container.append($second
                        .removeClass("front abs")
                        .addClass("itemAnswer")
                        .css("position", ""));
                $answer.removeClass("hidden");

                //
                $.memory.game.resizeRightAnswer($memory);

                //
                if ($first_card.find("audio").length > 0)
                    audio = $first_card.find("audio")[0];
                else if ($second_card.find("audio").length > 0)
                    audio = $second_card.find("audio")[0];

                //
                $.memory.action.stopTimer($memory);
            }
            $.memory.game.playAudio(audio);
        },

        /*                          resize function                          */
        /* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

        /**
         * On adapte la taille des images des cartes.
         *
         * @param {jQuery} $memory - Memory engine.
         */
        resizePickItems: function($memory) {
            var prefix = $memory.data("prefix");
            var $pick = $memory.find("."+prefix+"MemoryPick");

            if ($pick.hasClass("hidden"))
                return;

            var $items = $memory.find("."+prefix+"MemoryItems");
            var $board = $memory.find("."+prefix+"MemoryBoard");

            var ratio = parseInt($items.data("item-width"), 10) / parseInt($items.data("item-height"), 10);
            var bounds = {width: $board.width(), height: $board.height()};
            var count = $pick.find("."+prefix+"MemoryItem").length;
            var values = $.memory.game.getBestItemSize(count, bounds, ratio);
            $pick.find("."+prefix+"MemoryItem").css({"width": values.width, "height": values.height});
        },

        /**
         * On adapte la taille des images des cartes.
         *
         * @param {jQuery} $memory - Memory engine.
         */
        forcedResizePickItems: function($memory) {
            var prefix = $memory.data("prefix");
            var $items = $memory.find("."+prefix+"MemoryItems");
            var $pick = $memory.find("."+prefix+"MemoryPick");
            var $board = $memory.find("."+prefix+"MemoryBoard");

            // Pour calculer la largueur/hauter des cartes, on remette la boite a items en "block"
            $board.css("display", "block");

            //
            var display = $board.data("number-display");
            var column = $board.data("column-value");
            if (column === undefined)
                column = $.memory.defaults.forcedColumn;
            var row = parseInt((display*2) / column, 10);
            if (((display*2) % column) > 0)
                row += 1;

            //
            var $itm = $($pick.find("."+prefix+"MemoryItem").get(0));
            var mLeft = parseFloat($itm.css("margin-left")) || 0;
            var mRight = parseFloat($itm.css("margin-right")) || 0;
            var mTop = parseFloat($itm.css("margin-top")) || 0;
            var mBottom = parseFloat($itm.css("margin-bottom")) || 0;
            var marginLR = (mLeft + mRight) * column;
            var marginTB = (mTop + mBottom) * row;
            var pageWidth = $($memory.find(".row").get(0)).width();
            var maxWidth = (pageWidth - marginLR) / column;
            var maxHeight = ($pick.height() - marginTB) / row;
            var size = $.memory.game.calculateAspectRatioFit($items.data("item-width"), $items.data("item-height"), maxWidth, maxHeight);

            //
            $pick.find(".row ."+prefix+"MemoryItem").each( function() {
                var $item = $(this);
                $item.css({
                    "width": size.width+"px",
                    "height": size.height+"px"
                });
                $item.find(".front img").css({
                    "width": size.width+"px",
                    "height": size.height+"px"
                });
            });

            // On se replace en flex pour centrer la boite a items en vertical
            $board.css("display", "flex");
        },

        /**
         * On adapte la taille des images de la dialogue des bonne réponses.
         *
         * @param {jQuery} $memory - Memory engine.
         */
        resizeRightAnswer: function($memory) {
            var prefix = $memory.data("prefix");
            var $answer = $memory.find("."+prefix+"MemoryAnswerBox");
            if ($answer.length === 0)
                return;

            //
            var $items = $memory.find("."+prefix+"MemoryItems");
            var $itemAnswer = $($answer.find(".itemAnswer").get(0));
            var itemsPadding = parseFloat($items.css("padding")) || 0;
            var mLeft = parseFloat($itemAnswer.css("margin-left")) || 0;
            var mRight = parseFloat($itemAnswer.css("margin-right")) || 0;
            var margin = (mLeft + mRight) * 2;
            var pageWidth = $answer.width();
            var maxWidth = (pageWidth- (itemsPadding*2) - (margin*2)) / 2;
            var maxHeight = $answer.height();
            var size = $.memory.game.calculateAspectRatioFit($items.data("item-width"), $items.data("item-height"), maxWidth, maxHeight);
            $answer.find(".itemAnswer").each(function() {
                $(this).find("img").css({
                    "width": size.width+"px",
                    "height": size.height+"px"
                });
            });

            //
            $answer.find(".container").css("top", "calc(50% - "+ (size.height/2) +"px)");
        },

        /**
         * On adapte la taille des images de la correction.
         *
         * @param {jQuery} $memory - Memory engine.
         */
        resizeCorrectItems: function($memory) {
            var prefix = $memory.data("prefix");
            var $correct = $memory.find("."+prefix+"MemoryCorrectAnswer");
            if ($correct.length > 0 && !$correct.hasClass("hidden")) {
                var $board = $memory.find("."+prefix+"MemoryBoard");
                var $items = $memory.find("."+prefix+"MemoryItems");

                var ratio = (parseInt($items.data("item-width"), 10)*2) / parseInt($items.data("item-height"), 10);
                var bounds = {width: $board.width(), height: $board.height()};
                var count = $correct.find("."+prefix+"MemoryItemCorrect").length;
                var values = $.memory.game.getBestItemSize(count, bounds, ratio);
                $correct.find("."+prefix+"MemoryItemCorrect")
                    .css({"width": values.width, "height": values.height});
            }
        },

        /*                          Item size function                       */
        /* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

        /**
         * Calcule la meilleure taille pour les items.
         *
         * @param {int} count - hauteur et largeur du rectangle englobant.
         * @param {jQuery} bounds - taille du container.
         * @param {ratio} float - ratio d'un item.
         * @return {jQuery}
         */
        getBestItemSize: function(count, bounds, ratio) {
            var columns = 1;
            var totalWidth, totalHeight, elemWidth, elemHeight, rows = 0;
            var overflowing = false;
            var firstCycle = false;

            function figure() {
                var rect = {width: bounds.width / columns, height: -1};
                var itemSize = $.memory.game.getItemSizeForRect(rect, ratio);
                totalWidth = itemSize.width * columns;
                overflowing = totalWidth > bounds.width;
                if (firstCycle && overflowing) {
                    columns--;
                    return;
                }
                firstCycle = true;
                rows = Math.ceil(count / columns);
                totalHeight = itemSize.height * rows;
                elemHeight = itemSize.height-$.memory.defaults.itemMargin;
                elemWidth = itemSize.width-$.memory.defaults.itemMargin;
            }

            figure();
            while (!overflowing && rows > 1 && totalHeight > bounds.height) {
                columns++;
                figure();
            }

            return {width: elemWidth, height: elemHeight};
        },

        /**
         * Calcule la taille de l'item pour rentrer dans le "rect" en gardant le ratio.
         *
         * @param {jQuery} rect - hauteur et largeur du rectangle englobant.
         * @param {float} ratio - ratio de l'item.
         * @return {jQuery}
         */
        getItemSizeForRect: function(rect, ratio) {
            var width = rect.width;
            var height = rect.height;
            var w = width;
            var h = height;

            if (rect.width > -1)
                height = $.memory.game.getHeightForWidth(w, ratio);
            if (rect.height > -1)
                width = $.memory.game.getWidthForHeight(h, ratio);

            if (rect.width > -1 && rect.height > -1) {
                if (width < rect.width)
                    height = h;
                else
                    width = w;
            }

            return {width: Math.floor(width), height: Math.floor(height)};
        },

        /**
         * Retourne la largueur pour une hauteur donné en gardant le ratio.
         *
         * @param {int} heiht - Hauteur de l'élément.
         * @param {float} ratio - Ratio.
         * @return {int}
         */
        getWidthForHeight: function(height, ratio) {
            return Math.floor(height * ratio);
        },

        /**
         * Retourne la hauteur pour une largeur donné en gardant le ratio.
         *
         * @param {int} width - Largueur de l'élément.
         * @param {float} ratio - Ratio.
         * @return {int}
         */
        getHeightForWidth: function(width, ratio) {
            return Math.floor(width / ratio);
        },

        /*                           Audio function                          */
        /* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

        /**
         * Play an audio
         *
         * @param audio (Dom object) audio dom object.
         */
        playAudio: function(audio) {
            if (!audio) return;
            $.memory.game.stopAudio();
            this.playerAudio = new Audio();
            this.playerAudio.src = audio.currentSrc;
            this.playerAudio.play();
            $(this.playerAudio).on("ended", function() {
                this.playerAudio = null;
            });
        },

        /**
         * Stop audio playing.
         */
        stopAudio: function() {
            if (this.playerAudio !== null && this.playerAudio.paused === false) {
                this.playerAudio.pause();
                this.playerAudio = null;
            }
        },

        /*                            Misc function                          */
        /* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

        /**
         * Calcule la hauteur/largeur avec le bon ratio.
         *
         * @param scrWidth (int) largeur de l'image source.
         * @param scrHeight (int) hauteur de l'image source.
         * @param maxWidth (int) largeur maximum.
         * @param maxHeight (int) hauteur maximum.
         */
        calculateAspectRatioFit: function(srcWidth, srcHeight, maxWidth, maxHeight) {
            var ratio = Math.min(maxWidth / srcWidth, maxHeight / srcHeight);
            var rtnWidth = parseInt(srcWidth*ratio, 10);
            /*if (rtnWidth < 100)*/
            /*rtnWidth = 100;*/
            var rtnHeight = parseInt(srcHeight*ratio, 10);
            return {width: rtnWidth, height: rtnHeight};
        },

        /**
         * Shuffle items.
         *
         * @param $items (Object) jQuery element
         */
        shuffleItems: function($items) {
            for(var i = 0; i < 7 ; i++) {
                var items = $items.children();
                while (items.length) {
                    var $item = items.splice(Math.floor(Math.random() * items.length), 1)[0];
                    $items.append($item);
                }
            }
        },

        /**
         * Shuffle array.
         *
         * @param arr (Array) array to shuffle.
         */
        shuffleArray: function (arr) {
            for(var j, x, i = arr.length; i; j = parseInt(Math.random() * i, 10), x = arr[--i], arr[i] = arr[j], arr[j] = x);
            return arr;
        },

        /**
         * Enable button of memory.
         *
         * @param {Object} $memory : jQuery object memory.
         */
        enableSlotButtons: function($memory) {
            var quzId = $memory.data("quiz-id");
            var prefix = $memory.data("prefix");

            $memory.find("."+prefix+"Button").each(function() {
                var $btn = $(this);
                var id = $btn.attr("id") || "";
                if (id.substring(0, quzId.length+1) !== quzId+"_")
                    return;

                var type = "";
                if (id === quzId+"_help-link") {
                    type = "Help";
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
                    $.memory.game.displayInfo($memory, type, id.replace("link", "slot"));
                });
            });
        },

        /**
         * Disable button of memory.
         *
         * @param {Object} $memory : jQuery object memory.
         */
        disableSlotButtons: function($memory) {
            var quzId = $memory.data("quiz-id");
            var prefix = $memory.data("prefix");

            $memory.find("."+prefix+"Button").each(function() {
                var $btn = $(this);
                var id = $btn.attr("id") || "";
                if (id.substring(0, quzId.length+1) !== quzId+"_")
                    return;

                $btn.off("click");
            });
        },

        /**
         * Function call for display/hide help/explanation/script/strategy slots.
         *
         * @param {jQuery} $memory - Memory element.
         * @param {string} type - Type of the slot to display.
         * @param {string} id - Id of the slot to display.
         */
        displayInfo: function($memory, type, id) {
            var prefix = $memory.data("prefix");
            var $slot = $memory.find("#"+id);

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
         * Set events on popups to close them.
         *
         * @param {jQuery} $memory - Memory element.
         */
        popupEvents: function($memory) {
            var prefix = $memory.data("prefix");

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

            if ($.memory.defaults.popupContentClose) {
                $memory.find("."+prefix+"InstructionsPopUp,"+
                           "."+prefix+"AnswerPopUp,"+
                           "."+prefix+"HelpPopUp,"+
                           "."+prefix+"ExplanationPopUp,"+
                           "."+prefix+"ScriptPopUp,"+
                           "."+prefix+"StrategyPopUp").click(popupClose);
            }
            else {
                $memory.find(".instructionsClose,"+
                           ".answerClose,"+
                           ".helpClose,"+
                           ".explanationClose,"+
                           ".scriptClose,"+
                           ".strategyClose").click(popupClose);
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
        }
    };


    /*************************************************************************/
    /*                            memory.action                              */
    /*************************************************************************/

    $.memory.action = {

        /**
         * Init.
         *
         * @param {jQuery} $action - action with associate scenario.
         */
        initAction: function($action) {
            var prefix = $.memory.defaults.prefix;
            var $memory = $action.data("memory");

            // ----------------------------------------------------------------
            // Timer
            $.memory.action.initTimer($action, true);

            // ----------------------------------------------------------------
            // Events
            $action.find("."+prefix+"Redo").click(function() {
                $.memory.action.doActions($action, "redo");
            });
            $action.find("."+prefix+"RightAnswer").click(function() {
                $.memory.action.doActions($action, "rightAnswer");
            });
            $action.find("."+prefix+"UserAnswer").click(function() {
                $.memory.action.doActions($action, "userAnswer");
            });
        },

        /**
         * Method call when memory is modified.
         *
         * @param {Object} $action, jquery Object action.
         */
        onModified: function($action) {
            $.memory.action.doActions($action, "onModified");
        },

        /*                        Manage action function                     */
        /* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

        /**
         * Apply action form scenario.
         *
         * @param {jQuery} $action - action.
         * @param {String} scnKey - scenario key.
         */
        doActions: function($action, scnKey) {
            if ($action.scenario === undefined) {
                console.log("Defined a scenario with action '"+scnKey+"'.");
                return;
            }
            if ($action.scenario[scnKey] === undefined) {
                console.log("Must defined action '"+scnKey+"' in your scenario.");
                return;
            }

            $($action.scenario[scnKey]).each( function() {
                var actName = this.match(new RegExp("^([^(]+)"));
                if (!actName)
                    return true;
                actName = actName[0];
                var actArgs = this.replace(actName, "")
                    .replace("(", "")
                    .replace(")", "")
                    .replace(/ /g, "");
                if (actArgs)
                    actArgs = actArgs.split(",");
                else
                    actArgs = [];

                if (actName === "state") {
                    $.memory.action.actionState($action, actArgs[0]);
                } else if (actName === "disable") {
                    $.memory.action.actionDisable($action);
                } else if (actName === "redo") {
                    $.memory.action.actionRedo($action.data("memory"));
                } else if (actName === "rightAnswer") {
                    $.memory.action.actionRightAnswer($action);
                } else if (actName === "userAnswer") {
                    $.memory.action.actionUserAnswer($action);
                } else if (actName === "score") {
                    $.memory.action.actionScore($action);
                } else if (actName === "hide") {
                    $.memory.action.actionHide($action, actArgs);
                } else if (actName === "show") {
                    $.memory.action.actionShow($action, actArgs);
                } else if (actName === "stopTimer") {
                    $.memory.action.stopTimer($action.data("memory"));
                } else {
                    $.memory.action.actionCustom($action, actName, actArgs);
                }

                return true;
            });
        },

        /*                            Actions function                       */
        /* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

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
            var prefix = $.memory.defaults.prefix;
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
            if (!args)
                return;
            var prefix = $.memory.defaults.prefix;
            $.each(args, function() {
                var elemName = this;
                $action.find("."+prefix+elemName).removeClass("hidden");
            });
        },

        /**
         * Action disable
         *
         * @param {Object} $action, jquery Object action.
         */
        actionDisable: function($action) {
            $.memory.game.disable($action.data("memory"));
        },

        /**
         * Action state
         *
         * @param {Object} $action, jquery Object action.
         * @param {String} state, current State.
         */
        actionState: function($action, state) {
            var prefix = $.memory.defaults.prefix;
            var $memory = $action.data("memory");
            var $board = $memory.find("."+prefix+"MemoryBoard");
            $board.removeClass(prefix+"MemoryStateCorrected " + prefix+"MemoryStateDisabled");
            if (state !== "Enabled")
                $board.addClass(prefix+"MemoryState"+state);
        },

        /**
         * Action right answer, display right answer of quiz.
         *
         * @param {Object} $action, jquery Object action.
         */
        actionRightAnswer: function($action) {
            var prefix = $.memory.defaults.prefix;
            var $countdown = $action.find("."+prefix+"Countdown");
            if ($countdown.length > 0)
                $countdown.removeClass(prefix+"EndCountdown");
            $.memory.game.showCorrectAnswer($action.data("memory"));
            $.memory.context.onActionMemoryModified($action.data("memory"), "rightAnswer");
        },

        /**
         * Action user answer, display user answer of quiz.
         *
         * @param {Object} $action, jquery Object action.
         */
        actionUserAnswer: function($action) {
            var prefix = $.memory.defaults.prefix;
            var $countdown = $action.find("."+prefix+"Countdown");
            if ($countdown.length > 0)
                $countdown.removeClass(prefix+"EndCountdown");
            $.memory.game.showUserAnswer($action.data("memory"));
            $.memory.context.onActionMemoryModified($action.data("memory"), "userAnswer");
        },

        /**
         * Action score
         *
         * @param {Object} $action, jquery Object action.
         */
        actionScore: function($action) {
            var $memory = $action.data("memory");
            var prefix = $memory.data("prefix");
            var $board = $memory.find("."+prefix+"MemoryBoard");
            var $pick = $memory.find("."+prefix+"MemoryPick");
            var display = $board.data("number-display");

            //
            var total = parseInt(display, 10);
            var score = $pick.find(".correct").length / 2;
        
            //
            var $score = $action.find("."+prefix+"Score");
            if ($score.length === 0)
                return;

            var baseScore = -1;
            var $baseScoreElem = $action.find("."+prefix+"BaseScore");
            if ($baseScoreElem.length > 0)
                baseScore = parseInt($baseScoreElem.text(), 10);

            if (baseScore > -1) {
                score = (score * baseScore) / total.toFixed(1);
                score = Math.round(score);
                total = baseScore;
            }

            $score.text(score+" / "+total);
            $score.removeClass("hidden");
        },

        /**
         * Action redo.
         *
         * @param {jQuery} $memory - Memory engine.
         */
        actionRedo: function($memory) {
            var prefix = $memory.data("prefix") || "";
            var $action = $memory.data("action");
            var $pick = $memory.find("."+prefix+"MemoryPick");

            // Init Timer
            $.memory.action.initTimer($action, true);

            // Clear context
            $.publianim.context.clearContext($memory.data("quiz-id"));
            var $context = $memory.find("#"+$memory.data("quiz-id")+"_context");
            if ($context.length > 0)
                $context.remove();

            // Clear score
            var $score = $action.find("."+prefix+"Score");
            if ($score.length > 0) {
                $score.text("");
                $score.addClass("hidden");
            }

            // Disable
            $pick.removeClass("hidden");
            $pick.find("."+prefix+"MemoryItem").off("click");

            // Correct answer is displayed : Clear and hide answer box and reload new pick.
            var $correct = $memory.find("."+prefix+"MemoryCorrectAnswer");
            if ($correct.length > 0) {
                if ($correct.children().length > 0)
                    $correct.children().remove();

                if (!$correct.hasClass("hidden")) {
                    $correct.addClass("hidden");
                    $.memory.defaults.reorganizeMethod($memory);
                    return;
                }
            }

            // New pick
            var needWaitAnim = false;
            var $board = $memory.find("."+prefix+"MemoryBoard");
            var flipped = $memory.find("."+prefix+"MemoryItem.flipped").not(".correct");
            var items = $pick.find("."+prefix+"MemoryItem.flipped").removeClass("flipped");
            var hideRightAnswer = $memory.data("hideRightAnswer") || false;
            if (flipped.length > 0 || 
                    (!hideRightAnswer && items.length > 0) ||
                    ($board.hasClass(prefix+"MemoryStateCorrected") && items.length > 0)) {
                needWaitAnim = true;
            }

            if (needWaitAnim) {
                items.on($.memory.defaults.animEnd, function(e) {
                    $(this).off($.memory.defaults.animEnd);
                    $memory.data("anim-perform", "");
                    $.memory.defaults.reorganizeMethod($memory);
                });
            } else {
                $.memory.defaults.reorganizeMethod($memory);
            }
        },

        /*                            Timers function                        */
        /* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

        /**
         * Init timer.
         *
         * @param {jQuery} $action - action with associate scenario.
         * @param {boolean} reset - RAZ timer variable.
         */
        initTimer: function($action, reset) {
            $.memory.action.stopTimer($action);
            $.memory.defaults.currentTimer = null;
            $.memory.defaults.currentTimerId = null;
            var prefix = $.memory.defaults.prefix;

            if (reset) {
                $.memory.defaults.currentChronoValue = 0;
                $.memory.defaults.currentCountdownValue = 0;
                if ($action.data("countdown") !== undefined)
                    $.memory.defaults.currentCountdownValue = parseInt($action.data("countdown"), 10);
            }

            var $countdown = $action.find("."+prefix+"Countdown");
            if ($countdown.length > 0) {
                $countdown.removeClass(prefix+"EndCountdown");
                $countdown.text($.memory.action.formatTimer($.memory.defaults.currentCountdownValue));
            }

            var $chrono = $action.find("."+prefix+"Chrono");
            if ($chrono.length > 0)
                $chrono.text($.memory.action.formatTimer($.memory.defaults.currentChronoValue));
        },

        /**
         * Start countdown 
         *
         * @param {jQuery} $action - action.
         */
        startCountdown: function($action) {
            if ($.memory.defaults.currentTimerId !== null)
                return;
            $.memory.defaults.currentTimer = $.memory.action.countdownTimer;
            $.memory.defaults.currentTimerId = setInterval($.memory.defaults.currentTimer, 1000, $action); 
        },

        /**
         * Function for timer countdown.
         *
         * @param {jQuery} $action - action.
         */
        countdownTimer: function($action) {
            var prefix = $.memory.defaults.prefix;
            var $countdown = $action.find("."+prefix+"Countdown");
            $.memory.defaults.currentCountdownValue -= 1;

            // Counter ended
            if ($.memory.defaults.currentCountdownValue < 0) {
                clearInterval($.memory.defaults.currentTimerId);
                $.memory.defaults.currentTimerId = null;

                if ($countdown.length > 0)
                    $countdown.addClass(prefix+"EndCountdown");

                $.memory.action.doActions($action, "onEndCountdown");
                return;
            }

            // Display countdown
            if ($countdown.length > 0) {
                $countdown.data("current-value", $.memory.defaults.currentCountdownValue);
                $countdown.text($.memory.action.formatTimer($.memory.defaults.currentCountdownValue));
                $.memory.context.onMemoryModified($action.data("memory"));
            }
        },

        /**
         * Start chrono
         *
         * @param {jQuery} $action - action.
         */
        startChrono: function ($action) {
            if ($.memory.defaults.currentTimerId !== null)
                return;
            $.memory.defaults.currentTimer = $.memory.action.chronoTimer;
            $.memory.defaults.currentTimerId = setInterval($.memory.defaults.currentTimer, 1000, $action); 
        },

        /**
         * Function for timer chrono.
         *
         * @param {jQuery} $action - action.
         */
        chronoTimer: function ($action) {
            $.memory.defaults.currentChronoValue += 1;

            var prefix = $.memory.defaults.prefix;
            var $chrono = $action.find("."+prefix+"Chrono");
            if ($chrono.length > 0) {
                $chrono.data("current-value", $.memory.defaults.currentChronoValue);
                $chrono.text($.memory.action.formatTimer($.memory.defaults.currentChronoValue));
                $.memory.context.onMemoryModified($action.data("memory"));
            }
        },

        /**
         * Helper, format timer. 
         *
         * @param {Int} value - time in second.
         * @return {String} time formated.
         */
        formatTimer: function (value) {
            if (value < 0)
                value = 0;
            var minutes = Math.floor(value / 60);
            var seconds = value % 60;
            if (seconds <= 9) 
                seconds = "0" + seconds;
            return minutes+":"+seconds;
        },

        /**
         * Resume timer, continue current timer.
         *
         * @param {jQuery} $action - action.
         */
        resumeTimer: function ($action) {
            if ($.memory.defaults.currentTimer === null)
                return;
            $.memory.action.stopTimer($action);
            $.memory.defaults.currentTimerId = setInterval($.memory.defaults.currentTimer, 1000, $action); 
        },

        /**
         * Stop timer.
         *
         * @param {jQuery} $action - action.
         */
        stopTimer: function ($action) {
            if ($.memory.defaults.currentTimerId === null)
                return;
            clearInterval($.memory.defaults.currentTimerId);
            $.memory.defaults.currentTimerId = null;
        }

    };


    /*************************************************************************/
    /*                            memory.context                             */
    /*************************************************************************/

    $.memory.context = {

        /**
         * Call when click on item.
         *
         * @param {jQuery} $memory - Memory engine.
         */
        onMemoryModified: function($memory) {
            $.memory.action.onModified($memory.data("action"));

            var ttl = $memory.data("context-ttl");
            if (ttl === undefined || ttl < 0)
                return;

            if ($.memory.defaults.isLoading)
                return;

            var contextData = {};
            var prefix = $memory.data("prefix");
            var $context = $memory.find("#"+$memory.data("quiz-id")+"_context");

            // Pick
            if ($context.length > 0 && $context.find(".pick").length > 0) {
                contextData.pick = $context.find(".pick").text();
            } else {
                var pick = [];
                $memory.find("."+prefix+"MemoryPick ."+prefix+"MemoryItem").each( function() {
                    var $item = $(this);
                    pick.push($item.data("item-value") + "_" + $item.data("item-order"));
                });
                contextData.pick = JSON.stringify(pick);
            }

            // Find
            var find = [];
            $memory.find("."+prefix+"MemoryPick ."+prefix+"MemoryItem.correct").each( function() {
                var value = $(this).data("item-value");
                if ($.inArray(value, find) == -1)
                    find.push(value);
            });
            contextData.find = JSON.stringify(find);

            // Flipped
            contextData.flipped = "";
            var $flipped = $memory.find("."+prefix+"MemoryPick ."+prefix+"MemoryItem.flipped.first");
            if ($flipped.length > 0)
                contextData.flipped = $flipped.data("item-value") + "_" + $flipped.data("item-order");

            // Timer
            var $action = $memory.data("action");
            if ($action.data("countdown") !== undefined)
                contextData.countdown = $.memory.defaults.currentCountdownValue;
            if ($action.find("."+prefix+"Chrono").length > 0)
                contextData.chrono = $.memory.defaults.currentChronoValue;

            // Write DOM
            $.memory.context.writeMemoryContext($memory, contextData);

            // Save context
            var contextKey = $memory.data("context-key");
            $.publianim.context.saveContext(contextKey, ttl, $memory.data("quiz-id"), contextData);
        },

        /**
         * Call when click ona action.
         *
         * @param {jQuery} $memory - Memory engine.
         * @param {String} action - action name.
         */
        onActionMemoryModified: function($memory, action) {
            var ttl = $memory.data("context-ttl");
            if (ttl === undefined || ttl < 0)
                return;

            if ($.memory.defaults.isLoading)
                return;

            var contextData = {};
            var $data = $memory.find("#"+$memory.data("quiz-id")+"_context .action");
            var actions = [];
            if ($data.length > 0 && $data.text() !== "")
                actions = $data.text().split("::");
            if ((action === "userAnswer" && actions[actions.length-1] === "rightAnswer") ||
                    (action === "rightAnswer" && actions[actions.length-1] === "userAnswer")) {
                actions.pop();
            }
            actions.push(action);
            contextData.action = actions.join("::");

            // Write DOM
            $.memory.context.writeMemoryContext($memory, contextData);

            // Save context
            var contextKey = $memory.data("context-key");
            var $context = $memory.find("#"+$memory.data("quiz-id")+"_context");
            $context.children().each( function() {
                var $elem = $(this);
                var className = $elem[0].className;
                contextData[className] = $elem.text();
            });
            $.publianim.context.saveContext(contextKey, ttl, $memory.data("quiz-id"), contextData);
        },

        /**
         * Write context on DOM.
         *
         * @param {jQuery} $memory - Memory engine.
         * @param {Object} contextData - context.
         */
        writeMemoryContext: function($memory, contextData) {
            // Append context div
            var $context = $memory.find("#"+$memory.data("quiz-id")+"_context");
            if ($context.length === 0) {
                $context = $("<div>")
                    .attr("id", $memory.data("quiz-id")+"_context")
                    .addClass("hidden");
                $memory.append($context);
            }

            // Write changes in dom
            $.each(contextData, function(k, v) {
                var $elem = $context.find("."+k);
                if ($elem.length === 0) {
                    $elem = $("<div>").addClass(k);
                    $context.append($elem);
                }
                $elem.text(v);
            });
        },

        /**
         * Load context.
         *
         * @param {jQuery} $memory - Memory engine.
         */
        onMemoryLoadContext: function($memory) {
            var ttl = $memory.data("context-ttl");
            if (ttl === undefined || ttl < 0)
                return;

            var step = 500;
            var timer = setInterval(function() {
                if ($.memory.defaults.isReady) {
                    clearInterval(timer);
                    $.publianim.context.loadContext(
                            $memory.data("context-key"), 
                            ttl,
                            $memory.data("quiz-id"),
                            $.memory.context.setDataContext
                        );
                }
            }, step);
        },

        /**
         * Set context.
         *
         * @param {String} key - context id.
         * @param {Object} contextData - context.
         */
        setDataContext: function(key, contextData) {
            if (contextData === undefined || contextData === null || contextData === "")
                return;

            $.memory.defaults.isLoading = true;

            var prefix = $.memory.defaults.prefix;
            var $memory = $("."+prefix+"Memory").filter('[data-quiz-id="'+key+'"]');
            var $pick = $memory.find("."+prefix+"MemoryPick");
            var data = null;

            // Write DOM
            $.memory.context.writeMemoryContext($memory, contextData);

            // Pick
            if (contextData.pick !== undefined) {
                var $items = $memory.find("."+prefix+"MemoryItems");
                var pick = JSON.parse(contextData.pick);
                var itemsArray = [];
                for (var i in pick) {
                    data = pick[i].split("_");
                    var $item = $items.find("."+prefix+"MemoryItem")
                        .filter("[data-item-value=\""+data[0]+"\"]")
                        .filter("[data-item-order=\""+data[1]+"\"]");
                    $item = $item.clone();
                    itemsArray.push($item);
                }
                $.memory.game.fillPickItems($memory, itemsArray);
                $.memory.game.resizePickItems($memory);
            }

            // Find
            if (contextData.find !== undefined && contextData.find !== "") {
                var find = JSON.parse(contextData.find);
                for (var index in find) {
                    var value = find[index];
                    $pick.find("."+prefix+"MemoryItem")
                        .filter("[data-item-value=\""+value+"\"]")
                        .addClass("flipped correct item-visibility");
                }
            }

            // Flipped
            if (contextData.flipped !== undefined && contextData.flipped !== "") {
                data = contextData.flipped.split("_");
                $pick.find("."+prefix+"MemoryItem")
                    .filter("[data-item-value=\""+data[0]+"\"]")
                    .filter("[data-item-order=\""+data[1]+"\"]")
                    .addClass("flipped first");
            }

            // Timer
            if (contextData.countdown !== undefined) {
                $.memory.defaults.currentCountdownValue = parseInt(contextData.countdown, 10);
                $.memory.action.initTimer($memory.data("action"), false);
                if ($.memory.defaults.currentCountdownValue === 0)
                    $.memory.action.doActions($memory.data("action"), "onEndCountdown");
            }

            if (contextData.chrono !== undefined) {
                $.memory.defaults.currentChronoValue = parseInt(contextData.chrono,10);
                $.memory.action.initTimer($memory.data("action"), false);
            }

            // Action
            if (contextData.action !== undefined) {
                var actions = contextData.action.split("::");
                $.each(actions, function() {
                    var action = this;
                    $.memory.action.doActions($memory.data("action"), action);

                });
            }

            $.memory.action.onModified($memory.data("action"));
            $.memory.defaults.isLoading = false;
        }
    };


    /**************************************************************************
     **************************************************************************
     *
     *                      Define memoryAction plugin
     *
     **************************************************************************
     *************************************************************************/

    $.fn.memoryAction = function($memory, args) {
        var $action = $(this);
        $.each(args, function(k, v) {
            $action[k] = v; 
        });

        // Connect memory with associate action.
        // connect action with associate memory.
        $action.data("memory", $memory);
        $memory.data("action", $action);

        // Init.
        $.memory.action.initAction($action);

        return $action;
    };


    /**************************************************************************
     **************************************************************************
     *
     *                          Define memory plugin
     *
     **************************************************************************
     *************************************************************************/

    $.fn.memory = function(options, args) {

        var $this = this;

        var opts = handleOptions(options, args);
        if (opts === false)
            return $this;
        $.memory.defaults = opts;

        /**
         * Process the args that were passed to the plugin fn
         *
         * @param {jQuery} options - object can be String or {}.
         */
        function handleOptions(options, args) {
            if (options && options.constructor == String) {
                $this.each( function() {
                    var $memory = $(this);
                    switch (options) {
                        case ("loadContext"):
                            $.memory.context.onMemoryLoadContext($memory);
                            break;
                        default:
                            console.log("This option is not defined: '" + options + "'");
                    }
                });
                return false;
            }

            return $.extend({}, $.memory.defaults, options || {});
        }

        return $this.each(function() {
            var $memory = $(this);
            $.memory.game.activateMemory($memory);
        });
    };

}(jQuery));
