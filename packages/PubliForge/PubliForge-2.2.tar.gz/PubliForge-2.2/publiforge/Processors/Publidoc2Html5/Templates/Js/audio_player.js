/**
 * @projectDescription audio_player.js
 * Plugin for custom player audio.
 *
 * @author prismallia.fr
 * @version 0.1
 */

/**
 *
 * Copyright (C) Prismallia, Paris, 2015. All rights reserved.
 *
 * This program is free software. You can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation.
 *
 * This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
 * WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
 *
 */

/*jshint globalstrict: true*/
/*global jQuery: true */


(function ($) {

"use strict";

$.fn.player = function(options, args) {

    var defaults = {
        durationFormat: "m:ss / m:ss"
    };

    var $this = this;
    var opts = $.extend( {}, defaults, options);


    /**********************************************************************
     *                          Library function
     *********************************************************************/

    /**
     * Read audio metadata
     *
     * @param {Object} $player, object jquery playerAudio.
     */
    function audioMetaData($player) {
        var $source = $player.find("audio");
        var $playerInfo = $player.children().filter("[data-player=\"player-info\"]");
        var $playerDuration = $playerInfo.children().filter("[data-player=\"duration\"]");

        $source.off("loadedmetadata.audioPlayer canplaythrough.audioPlayer");

        var duration = $source[0].duration;
        var minutes = Math.floor(duration / 60);
        var seconds = Math.round(duration - minutes * 60);
        seconds = ("0" + seconds).slice(-2);

        if (opts.durationFormat == "m:ss / m:ss")
            $playerDuration.text("0:00 / "+minutes+":"+seconds);
        if (opts.durationFormat == "m:ss")
            $playerDuration.text("0:00");
    }

    /**
     * Event timeupdate, update cursor position and duration info.
     *
     * @param {Object} $player, object jquery playerAudio.
     * @param {int} timelineWidth, player timeline width.
     */
    function onTimerUpdate($player, timelineWidth) {
        var $source = $player.find("audio");
        var $playerInfo = $player.children().filter("[data-player=\"player-info\"]");
        var $playerDuration = $playerInfo.children().filter("[data-player=\"duration\"]");
        var $playerTimeLine = $playerInfo.children().filter("[data-player=\"timeline\"]");
        var $playerCursor = $playerTimeLine.children().filter("[data-player=\"cursor\"]");

        // Source duration
        var duration = $source[0].duration;
        var minutes = Math.floor(duration / 60);
        var seconds = Math.round(duration - minutes * 60);
        seconds = ("0" + seconds).slice(-2);

        // Update duration
        var time = $source[0].currentTime;
        var m = Math.floor(time / 60);
        var s = Math.round(time - m * 60);
        s = ("0" + s).slice(-2);
        if (opts.durationFormat == "m:ss / m:ss")
            $playerDuration.text(m+":"+s+" / "+minutes+":"+seconds);
        if (opts.durationFormat == "m:ss")
            $playerDuration.text(m+":"+s);

        // Update player cursor position
        var position = timelineWidth * (time / duration);
        $playerCursor.css("margin-left", position + "px");
    }

    /**
     * Get click position in player time line
     *
     * @params {Object} ev: Event object.
     * @param {Object} $player, object jquery playerAudio.
     * @param {int} timelineWidth, player timeline width.
     * @return {int} position.
     */
    function clickPercent(ev, $player, timelineWidth) {
        var $playerInfo = $player.children().filter("[data-player=\"player-info\"]");
        var $playerTimeLine = $playerInfo.children().filter("[data-player=\"timeline\"]");
        var $playerCursor = $playerTimeLine.children().filter("[data-player=\"cursor\"]");
        var posX = null;

        if (ev.originalEvent.changedTouches) {
            var touch = ev.originalEvent.changedTouches[0];
            posX = touch.pageX;
        } else {
            posX = ev.pageX;
        }

        return ((posX - $playerTimeLine.offset().left - ($playerCursor.width()/2)) * 100) / timelineWidth;
    }

    /**
     * Event click on audio button for play and pause.
     *
     * @param {Object} $player, object jquery playerAudio.
     */
    function playAudio($player) {
        var source = $player.find("audio").get(0);
        if (source.paused) {
            var classList = $player.attr("class").split(/\s+/);
            $("."+classList[0]).each( function() {
                var $_player = $(this);
                var _source = $_player.find("audio").get(0);
                _source.pause();
            });
            source.play();
        } else {
            source.pause();
        }
    }

    /**
     * Event click on audio button for stop.
     *
     * @param {Object} $player, object jquery playerAudio.
     */
    function stopAudio($player) {
        var source = $player.find("audio").get(0);
        source.pause();
        source.currentTime = 0;
    }

    /**
     * Event when mouse down on player cursor.
     *
     * @param {Object} $player, object jquery playerAudio.
     * @param {int} timelineWidth, player timeline width.
     */
    function onPlayerCursorMouseDown($player, timelineWidth) {
        var $source = $player.find("audio");

        // unbind
        var moveCursor = true;
        $source.off("timeupdate.audioPlayer");

        // events
        var evtMove = "mousemove.audioPlayer touchmove.audioPlayer";
        var evtEnd = "mouseup.audioPlayer touchend.audioPlayer";
        $player.on(evtMove, function(ev) {
            ev.preventDefault();
            movePlayerCursor(ev, $player, timelineWidth);
        });
        $player.on(evtEnd, function(ev) {
            ev.preventDefault();
            if (moveCursor) {
                $player.off(evtMove);
                movePlayerCursor(ev, $player, timelineWidth);
                $source.on({
                    "timeupdate.audioPlayer": function() {
                        onTimerUpdate($player, timelineWidth);
                    }
                });
            }
            moveCursor = false;
        });
    }

    /**
     * Move player cursor, when mouse down.
     *
     * @params {Object} ev: Event object.
     * @param {Object} $player, object jquery playerAudio.
     * @param {int} timelineWidth, player timeline width.
     */
    function movePlayerCursor(ev, $player, timelineWidth) {
        var $source = $player.find("audio");
        var $playerInfo = $player.children().filter("[data-player=\"player-info\"]");
        var $playerTimeLine = $playerInfo.children().filter("[data-player=\"timeline\"]");
        var $playerCursor = $playerTimeLine.children().filter("[data-player=\"cursor\"]");
        var duration = $source[0].duration;
        var posX = null;

        if (ev.originalEvent.changedTouches) {
            var touch = ev.originalEvent.changedTouches[0];
            posX = touch.pageX;
        } else {
            posX = ev.pageX;
        }

        var newMargLeft = posX - $playerTimeLine.offset().left - ($playerCursor.width()/2);
        if (newMargLeft >= 0 && newMargLeft <= timelineWidth) {
            $playerCursor.css("margin-left", newMargLeft + "px");
            $source[0].currentTime = (duration * clickPercent(ev, $player, timelineWidth)) / 100;
            onTimerUpdate($player, timelineWidth);
        } else if (newMargLeft < 0) {
            $playerCursor.css("margin-left", "0px");
        } else {
            $playerCursor.css("margin-left", timelineWidth + "px");
        }
    }

    /**
     * Change button to "play" or "pause".
     *
     * @param {string} type - "play" or "pause".
     */
    function changeButton($button, type) {
        var inverseType = type=="pause"?"play":"pause";
        $button.removeClass(inverseType);
        $button.addClass(type);
    }


    /**********************************************************************
     *                          Plug-in main function
     *********************************************************************/

    return $this.each( function() {
        var $player = $(this);
        var hasPlayOneOnce = false;
        var $source = $player.find("audio");

        // Can play type
        var canPlayType = false;
        $source.find("source").each( function() {
            var ext = this.src.split(".").pop();
            var type = "";
            switch (ext) {
                case "mp3":
                    type = "audio/mpeg";
                    break;
                case "ogg":
                    type = "audio/ogg";
                    break;
                case "m4a":
                case "aac":
                    type = "audio/aac";
                    break;
                case "wav":
                    type = "audio/wav";
                    break;
                case "webm":
                    type = "audio/webm";
                    break;
            }
            if ($source[0].canPlayType(type) !== "") {
                canPlayType = true;
                return false;
            }
            return true;
        });
        if (!canPlayType) {
            $source.parent().children().each(function() {
                var $this = $(this);
                $this.addClass("hidden");
                $this.children().addClass("hidden");
            });
            $source.parent().text("(Audio format not supported)");
            return;
        }


        /**********************************************************************
         *                              Events
         *********************************************************************/

        var $playerButtonPlay = $player.children().filter("[data-player=\"button-play\"]");
        var $playerButtonStop = $player.children().filter("[data-player=\"button-stop\"]");
        var $playerInfo = $player.children().filter("[data-player=\"player-info\"]");
        var $playerDuration = $playerInfo.children().filter("[data-player=\"duration\"]");
        var $playerTimeLine = $playerInfo.children().filter("[data-player=\"timeline\"]");
        var $playerCursor = $playerTimeLine.children().filter("[data-player=\"cursor\"]");

        var cursorWidth = parseFloat($playerCursor.css("width")) || 0;
        var timelineWidth = parseFloat($playerTimeLine.css("width")) || 0;
        timelineWidth -= cursorWidth;

        // Source event
        $source.off(".audioPlayer");
        $source.on({
            "canplaythrough.audioPlayer": function() {
                audioMetaData($player);
            },
            "loadedmetadata.audioPlayer": function() {
                audioMetaData($player);
            },
            "ended.audioPlayer pause.audioPlayer": function() {
                changeButton($playerButtonPlay, "play");
            },
            "play.audioPlayer": function() {
                changeButton($playerButtonPlay, "pause");
            },
            "timeupdate.audioPlayer": function() {
                onTimerUpdate($player, timelineWidth);
            }
        });

        // Timeline event
        $playerTimeLine.off("click.audioPlayer");
        $playerTimeLine.on("click.audioPlayer", function(ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var duration = $source[0].duration;
            $source[0].currentTime = (duration * clickPercent(ev, $player, timelineWidth)) / 100;
        });

        // Player buttons click event
        $playerButtonPlay.off("click.audioPlayer");
        $playerButtonPlay.on("click.audioPlayer", function(ev) {
            ev.preventDefault();
            ev.stopPropagation();
            hasPlayOneOnce = true;
            playAudio($player);
        });
        if ($playerButtonStop) {
            $playerButtonStop.off("click.audioPlayer");
            $playerButtonStop.on("click.audioPlayer", function(ev) {
                ev.preventDefault();
                ev.stopPropagation();
                stopAudio($player);
            });
        }

        // PLayer cursor event
        var evtStart = "mousedown.audioPlayer touchstart.audioPlayer";
        $playerCursor.off(evtStart);
        $playerCursor.on(evtStart, function(ev) {
            if (hasPlayOneOnce)
                onPlayerCursorMouseDown($player, timelineWidth);
        });
    });
};

}(jQuery));
