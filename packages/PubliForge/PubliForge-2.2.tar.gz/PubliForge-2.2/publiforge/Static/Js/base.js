
/*global jQuery: true */
/*global setTimeout: true */

"use strict";

jQuery(document).ready(function($) {
    // ------------------------------------------------------------------------
    // Initialization
    // ------------------------------------------------------------------------

    var shortDelay = 12000;
    var longDelay = 20000;
    var panelMinWidth = 20;
    var panelTransition = ".6s";
    var idx = {panelClosed: 0, panelWidth: 1, menuClosed: 2, tabUser: 3,
               tabGroup: 4, tabStorage: 5, tabIndexer: 6, tabProject: 7,
               tabRole: 8, tabProcessing: 9, tabTask: 10, tabPack: 11,
               tabJob: 12};
    var state = jQuery.cookie('PF_STATE');
    if (!state)
        state = '0|22|0|tab0|tab0|tab0|tab0|tab0|tab0|tab0|tab0|tab0|tab0';
    state = state.split('|');

    // ------------------------------------------------------------------------
    // Flash
    // ------------------------------------------------------------------------

    var $flash = $("#flash");
    $flash.hide().slideDown("slow").delay(shortDelay).slideUp("slow");

    // ------------------------------------------------------------------------
    // Tab set
    // ------------------------------------------------------------------------

    $(".tabs li a").click(function() {
        var $this = $(this);
        $(".tabs li").removeClass("tabCurrent");
        $this.parent().addClass("tabCurrent");
        $(".tabContent").hide();
        $("#tabContent" + $this.attr("id").replace("tab", "")).show();
        state[idx[$this.parent().parent().attr("id")]] = $this.attr("id");
        $.cookie("PF_STATE", state.join("|"), {path: "/"});
        return false;
    });

    $(".tabs").each(function() {
        var tab = window.location.hash.replace("#", "");
        if (tab.substring(0, 3) != "tab")
            tab = state[idx[$(this).attr("id")]];
        $("#" + tab).click();
    });

    // ------------------------------------------------------------------------
    // Tool tip
    // ------------------------------------------------------------------------

    $(".toolTip").removeAttr("title").click(function() { return false; });

    $("table.tableToolTip .toolTip").mouseenter(function() {
        var $icon = $(this);
        $("#toolTipContent").remove();
        $('<div id="toolTipContent">...</div>')
            .width($icon.parent().parent().width() - $icon.parent().width() - 15)
            .hide()
            .insertAfter($icon)
            .load("?" + $icon.attr("name") + ".x=10", function() {
                var $toolTip = $(this);
                if ($toolTip.text().length)
                    $toolTip.show().offset({
                        left: $icon.parents("tr").offset().left + 5,
                        top: $icon.offset().top - $toolTip.outerHeight()
                    });
            });
    });

    $("div.formItemToolTip .toolTip").mouseenter(function() {
        var $icon = $(this);
        $("#toolTipContent").remove();
        $('<div id="toolTipContent">...</div>')
            .hide()
            .insertAfter($icon)
            .load("?" + $icon.attr("name") + ".x=10", function() {
                var $toolTip = $(this);
                if ($toolTip.text().length)
                    $toolTip.show().offset({
                        left: $icon.parent().offset().left,
                        top: $icon.offset().top - $toolTip.outerHeight()
                    });
            });
    });

    $(".toolTip").mouseleave(function() {
        $("#toolTipContent").remove();
    });

    $("table.list").mouseleave(function() {
        $("#toolTipContent").remove();
    });

    // ------------------------------------------------------------------------
    // Buttons
    // ------------------------------------------------------------------------

    // Check all
    $("#check_all")
        .removeAttr("id")
        .prepend($('<input id="check_all" name="check_all" type="checkbox" value="1"/>'))
        .find("#check_all").click(function() {
            $("input.listCheck").prop("checked", $(this).prop("checked"));
        });

    // Slow button
    var slowImgUrl = "/Static/Images/wait_slow.gif";
    var $slowImg = $('<img src="' + slowImgUrl + '" alt="slow"/>');
    $("a.slow").click(function() {
        var $this = $(this);
        if ($this.children("img").length)
            $this.children("img").attr("src", slowImgUrl);
        else
            $this.append(" ").append($slowImg);
    });
    $("input.slow").click(function() {
        var $this = $(this);
        if ($this.attr("src"))
            $this.attr("src", slowImgUrl);
        else
            $this.append(" ").append($slowImg);
    });

    // ------------------------------------------------------------------------
    // Parameters for action
    // ------------------------------------------------------------------------

    $("#actionParams").hide().slideDown("slow");

    // ------------------------------------------------------------------------
    // Aside panel
    // ------------------------------------------------------------------------

    var $pfWrapper = $("#pfWrapper");
    var $asidePanel = $("#asidePanel");
    var $contentPanel = $("#contentPanel");
    var panelWidth = parseInt(state[idx["panelWidth"]]);
    if (!$("#asideClose").length) {
        $('<div id="panelResize"/>').prependTo($contentPanel);
        $('<div id="asideClose"><span>«</span></div>').prependTo($asidePanel);
        $('<div id="asideOpen"><span>»</span></div>').prependTo($contentPanel);
    }

    $asidePanel.css({width: panelWidth+"vw"});

    if (state[idx["panelClosed"]] == 1) {
        $asidePanel.hide().css({"margin-left": -$asidePanel.outerWidth(true)});
        $("#panelResize").hide();
        $("#asideOpen").show();
    }

    $("#asideClose").click(function() {
        if (state[idx["panelClosed"]] == 0) {
            $("#panelResize").hide();
            $asidePanel.animate(
                {"margin-left": -$asidePanel.outerWidth(true)},
                "slow",
                function() {
                    $asidePanel.hide();
                    $("#asideOpen").show("slow");
                });
            state[idx["panelClosed"]] = 1;
            $.cookie("PF_STATE", state.join("|"), {path: "/"});
        }
    });

    $("#asideOpen").click(function() {
        if (state[idx["panelClosed"]] == 1) {
            $("#asideOpen").hide("fast");
            $asidePanel.show().animate(
                {"margin-left": 0}, "slow",
                function() {
                    $("#panelResize").show();
                });
            state[idx["panelClosed"]] = 0;
            $.cookie("PF_STATE", state.join("|"), {path: "/"});
        }
    });

    $("#panelResize").mousedown(function(event) {
        event.preventDefault();
        $pfWrapper.mousemove(function(event) {
            panelWidth = Math.round(event.pageX / window.outerWidth * 100);
            if (panelWidth < panelMinWidth) panelWidth = panelMinWidth;
            if (panelWidth > 100 - panelMinWidth)
                panelWidth = 100 - panelMinWidth;
            $asidePanel.css({width: panelWidth+"vw"});
        });
    });

    $pfWrapper.mouseup(function() {
        if (!$._data($pfWrapper[0]).events["mousemove"])
            return;
        $pfWrapper.off("mousemove");
        state[idx["panelWidth"]] = panelWidth;
        $.cookie("PF_STATE", state.join("|"), {path: "/"});
    });

    // ------------------------------------------------------------------------
    // Selection
    // ------------------------------------------------------------------------

    var $asideContent = $("#asideContent");
    var $selection = $("#selection");
    var $menu = $("#menu");
    if ($selection.length) {
        if (state[idx["menuClosed"]] == 1) {
            $asideContent.addClass("showSelection");
            $menu.css({position: "absolute", top: 0});
        } else
            $selection.hide();

        $menu.addClass("flip")
            .children("ul").children("li").eq(0).children("ul")
            .prepend("<li><span class='selection'>"
                     + $selection.children("legend").text()
                     + " (" + $selection.find(".selectionFile").length
                     + ")</span></li>")
            .children("li").eq(0).click(function() {
                $menu.css({position: "absolute", top: 0});
                $selection.show().css("transition", panelTransition);
                $menu.css("transition", panelTransition);
                setTimeout(function() {
                    $asideContent.addClass("showSelection");
                }, 100);
                state[idx["menuClosed"]] = 1;
                $.cookie("PF_STATE", state.join("|"), {path: "/"});
            });

        $selection.addClass("flip")
            .children("legend").append("<strong/>")
            .click(function() {
                $asideContent.removeClass("showSelection");
                $selection.css("transition", panelTransition);
                $menu.css("transition", panelTransition);
                setTimeout(function() {
                    $selection.hide(); $menu.css("position", "relative");
                }, 600);
                state[idx["menuClosed"]] = 0;
                $.cookie("PF_STATE", state.join("|"), {path: "/"});
            })
            .end().find(".selectionTool").each(function () {
                var $this = $(this);
                $this.replaceWith(
                    "<span class='selectionTool'"
                        + " title='" + $this.attr("title") + "'"
                        + " data-href='" + $this.attr("href") + "'>"
                        + $this.html() + "</span>");
                $this.remove();
            })
            .end().on("click", ".selectionTool", function() {
                var $img = $(this).children("img");
                if ($img.attr("src").indexOf("remove") != -1
                    && $img.attr("src").indexOf("remove_one") != -1) {
                    $img.attr("src", $img.attr("src").replace("one", "sure"));
                    return;
                }
                $.ajax({
                    url: $(this).data("href"),
                    dataType: "json",
                    cache: false,
                    success: function(data) {
                        $("#selectionFiles").html(data);
                        var $size = $menu.find(".selection");
                        $size.text($size.text().replace(
                                /\d+/, $selection.find(".selectionFile").length));
                    }});
            }).on("click", ".selectAll", function() {
                var $this= $(this);
                $this.parent().nextAll("ul").find("input")
                    .prop("checked", $this.prop("checked"));
            });

        var toSelection = false;
        $(".selectable")
            .attr("draggable", "true")
            .on("dragstart", function(event) {
                event.originalEvent.dataTransfer.effectAllowed = "move";
                event.originalEvent.dataTransfer.setData(
                    "text", $(this).data("path"));
                toSelection = true;
            })
            .on("dragend", function() {
                $("#selectionFiles").css("background-color", "transparent");
                toSelection = false;
            });

        $("#selectionFiles")
            .on("dragover", function(event) {
                if (toSelection)
                    $(this).css("background-color", $selection.data("color"));
                event.preventDefault();
            })
            .on("dragleave", function(event) {
                $(this).css("background-color", "transparent");
            })
            .on("drop", function(event) {
                var url = "/selection/add/"
                        + event.originalEvent.dataTransfer.getData("text");
                $.ajax({
                    url: url,
                    dataType: "json",
                    cache: false,
                    success: function(data) {
                        $("#selectionFiles").html(data);
                        var $size = $menu.find(".selection");
                        $size.text($size.text().replace(
                                /\d+/, $selection.find(".selectionFile").length));
                    }});
                return false;
            })
            .on("dragstart", ".selectionFile", function(event) {
                event.originalEvent.dataTransfer.effectAllowed = "move";
                event.originalEvent.dataTransfer.setData(
                    "text", $(this).data("path"));
                toSelection = false;
            })
            .on("dragend", ".selectionFile", function() {
                $(".container").css("background-color", "transparent");
            });

        $(".container")
            .on("dragover", function(event) {
                if (!toSelection)
                    $(this).css("background-color", $selection.data("color"));
                event.preventDefault();
            })
            .on("dragleave", function(event) {
                $(this).css("background-color", "transparent");
            })
            .on("drop", function(event) {
                $(this).css("background-color", "transparent");
                var path = event.originalEvent.dataTransfer.getData("text");
                if (path.search(/(https?|file):\/\//) == 0)
                    return false;
                var qs = window.location.search;
                var url = (qs ? qs + "&" : "?") + "get!"
                    + ($(this).data("target") || '') + ".x&~" + path;
                $.getJSON(url, function() {
                    window.location = window.location.pathname;
                });
                return false;
            });
    }
});
