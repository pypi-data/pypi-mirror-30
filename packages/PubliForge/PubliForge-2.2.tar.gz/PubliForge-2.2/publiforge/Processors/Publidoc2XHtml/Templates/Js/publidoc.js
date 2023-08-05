// Publidoc

/*global jQuery: true */

jQuery(document).ready(function($) {
    // ------------------------------------------------------------------------
    // Hotspots
    var prefix = "pdoc";
    if ($.publidoc && $.publidoc.defaults && $.publidoc.defaults.prefix)
        prefix = $.publidoc.defaults.prefix;

    var delay = 5000;
    $('.'+prefix+'Hotspot').each(function() {
        var $hotspot = $(this);
        var $spot = $('#' + $hotspot.attr('id') + 's');
        var $audio = $spot.find("audio");
        var scenario = $hotspot.children('span').length;
        if ($spot.length && scenario) {
            $spot.css('opacity', 0);
            $hotspot.click(function() {
                if ($spot.css('opacity') == 0) {
                    $hotspot.addClass(prefix+"Hotspot-active");
                    $spot.removeClass("hidden");
                    $spot.css("opacity", 0)
                        .animate({opacity: 1})
                        .delay(delay)
                        .animate({opacity: 0}, function() {
                            $hotspot.removeClass(prefix+"Hotspot-active");
                            $spot.addClass("hidden");
                        });
                    if (!$hotspot.hasClass(prefix+"Hotspot-text")) {
                        $hotspot.animate({opacity: 0})
                            .delay(delay)
                            .animate({opacity: 1});
                    }
                    if ($audio.length > 0) {
                        $audio.get(0).play();
                    }
                } else {
                    $spot.click();
                }
            });

            $spot.click(function() {
                $hotspot.removeClass(prefix+"Hotspot-active");
                $spot.stop().animate({opacity: 0}, function() {
                    $spot.addClass("hidden");
                });
                if (!$hotspot.hasClass(prefix+"Hotspot-text")) {
                    $hotspot.stop().animate({opacity: 1});
                }
                if ($audio.length > 0) {
                    var audio = $audio.get(0);
                    audio.pause();
                    audio.currentTime = 0;
                }
            });
        }
    });

    // ------------------------------------------------------------------------
    // Audio player
    if ($.fn.player) {
        $(".pdocAudioPlayer").player();
    }

    // ------------------------------------------------------------------------
    // Abs
    $("<style>").text(".abs { position: absolute; }").appendTo("head");
});
