/**
 * @projectDescription Make a object dragAndPath
 *
 * @author Tien Haï NGUYEN
 * @version 0.1
 */


/*jshint globalstrict: true*/
/*global document*/
/*global jQuery*/
/*global localStorage*/
/*global sessionStorage*/


"use strict";


(function ($) {

    if (!$.publianim) {
        $.publianim = {};
    }

    /**
     * Array contain all animations instanciate by loader.
     */
    $.publianim.animRegister = [];


    /*************************************************************************
     *
     *                          PubliAnimInterface
     *
     ************************************************************************/

    /**
     * Constructor for publianim interface.
     * All animations have to implement this interface.
     */
    function PubliAnimInterface() {}
    $.publianim.PubliAnimInterface = PubliAnimInterface;

    /**
     * Define functions included in object.
     * All animation have to implement these functions.
     */
    PubliAnimInterface.prototype = {

        /***
         * Define object class name.
         */
        className: function() {
            throw new Error('className method must be implemented.');
        },

        /**
         * Function used clear animation.
         */
        clear: function() {
            throw new Error('clear method must be implemented.');
        },

        /**
         * Function used for load context.
         */
        loadContext: function() {
            throw new Error('loadContext method must be implemented.');
        },

        /**
         * Function used for save context.
         */
        saveContext: function() {
            throw new Error('saveContext method must be implemented.');
        },

        /**
         * Function used for know state.
         */
        isReady: function() {
            throw new Error('isReady method must be implemented.');
        }

    };


    /*************************************************************************
     *
     *                      Function $.publianim.initEffect
     *
     ************************************************************************/

    /**
     * Function init effect.
     *
     * arguments - specific variable contains all arguments.
     * passed to the function. The first argument is the effect class.
     * and following are the parameters to instanciate class.
     *
     * @param {Class} effect - class effect.
     * @return {Object} Instance of effect.
     */
    $.publianim.initEffect = function(effect) {
        var $mainElement = arguments[1];

        if ($mainElement.data("init"+effect.animName)) {
            return $mainElement.data("init"+effect.animName);
        }
        else {
            var args = Array.prototype.slice.call(arguments, 1);
            var effectInstance = Object.create(effect.prototype);
            effect.apply(effectInstance, args);
            $mainElement.data("init"+effect.animName, effectInstance);
            return effectInstance;
        }
    };


    /*************************************************************************
     *
     *                          $.publianim.defaults
     *
     ************************************************************************/

    /**
     *
     */
    $.publianim.defaults = {
        /**
         * define class above effect
         */
        mainClass: "body",
        /**
         * Define prefix of anim element class
         */
        prefix: "pdoc"
    };


    /*************************************************************************
     *
     *                          $.publianim.context
     *
     ************************************************************************/

    /**
     *
     */
    $.publianim.context = {
        defaults: {
            timeout: 2000
        },

        /**
         * @param {String} contextKey - Context key to validate data.
         * @param {number} ttl - TTL of the context.
         * @param {String} key - Key to retrieve data later.
         * @param {Object} contextData - Data to save. Can be anything that can be
         * passed to JSON.stringify() method.
         */
        saveContext: function (contextKey, ttl, key, contextData) {
            var data = {
                contextKey: contextKey,
                date: new Date(),
                context: contextData
            };

            if ($.publianim.context.isLocalStorageEnable()) {
                if (ttl > 0)
                    localStorage.setItem(key, JSON.stringify(data));
                else
                    sessionStorage.setItem(key, JSON.stringify(data));
            } else {
                $.publianim.context.writeCookie(key, JSON.stringify(data), null);
            }
        },

        /**
         * @param {String} key - Key to remove.
         */
        clearContext: function (key) {
            if ($.publianim.context.isLocalStorageEnable()) {
                localStorage.removeItem(key);
            } else {
                var day = 3600 * 24; // one day
                var date = new Date(new Date() - day);
                $.publianim.context.writeCookie(key, null, date);
            }
        },

        /**
         * @param {String} contextKey - Context key to validate data.
         * @param {number} ttl - TTL of the context.
         * @param {String} key - Key to retrieve data later.
         * @param {Object} callback - Function called after data loaded.
         */
        loadContext: function (contextKey, ttl, key, callback) {
            var res = null;
            var loadedData;

            if ($.publianim.context.isLocalStorageEnable()) {
                if (ttl > 0)
                    res = localStorage.getItem(key);
                else
                    res = sessionStorage.getItem(key);
            } else {
                res = $.publianim.context.readCookie(key);
            }

            if (res !== undefined && res !== null) {
                var data = JSON.parse(res);
                if (data.contextKey === contextKey && !$.publianim.context.isContextExpired(data.date, ttl))
                    loadedData = data.context;
            }

            callback(key, loadedData);
        },

        /**
         *
         */
        isLocalStorageEnable: function () {
            if (typeof localStorage !== "undefined" && localStorage !== null)
                return true;

            return false;
        },

        /**
         * Write a cookie
         *
         * @param {String} name - Data name.
         * @param {String} value - Data value.
         * @param {Date} dt - Date value.
         */
        writeCookie: function (name, value, dt) {
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
         * @param {String} name - Data name.
         * @return {String} Data
         */
        readCookie: function (name) {
            var nameEQ = name + "=";
            var ca = document.cookie.split(";");
            for(var i=0;i < ca.length;i++) {
                var c = ca[i];
                while (c.charAt(0)===" ") c = c.substring(1,c.length);
                if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length,c.length);
            }

            return null;
        },

        /**
         * Verify date of context.
         * @param {String} date - Context date.
         * @param {number} ttl - Context life duration.
         * @return {Boolean} True when context is no longer valid, false otherwise.
         */
        isContextExpired: function (date, ttl) {
            if (ttl > 0 && date !== undefined) {
                var days = (ttl / 3600) / 24;
                var dt = new Date(date);
                dt.setHours(0,0,0,0);
                var expire = new Date(new Date() - days);
                expire.setHours(0,0,0,0);
                if (expire > dt)
                    return true;
            }

            return false;
        }

    };


    /*************************************************************************
     *
     *                      $.publianim: Loading
     *
     ************************************************************************/

    /**
     *
     */
    $.publianim.addLoading = function ($elem, prefix) {
        $elem.addClass(prefix+"StateLoading");

        var $div = $("<div><span class='abs'></span></div>");
        $div.addClass(prefix+"Loading abs");

        $elem.append($div);
    };

    /**
     *
     */
    $.publianim.removeLoading = function ($elem, prefix) {
        $elem.removeClass(prefix+"StateLoading");
        $elem.find("."+prefix+"Loading").remove();
    };


    /*************************************************************************
     *
     *                  CSS Transform Matrix to Object
     *
     ************************************************************************/

    /**
     * Convert a transform matrix into an object.
     *
     * @return {Object} Transform object.
     */
    $.fn.getTransformObj = function () {
        var obj = {
            rotate: 0,
            scale: {x: 1, y: 1},
            translate: {x: 0, y: 0}
        };
        var transform = this.css("transform");
        if (transform !== "none") {
            var matrix = transform.match(/([-+]?[\d\.]+)/g);

            obj.translate.x = matrix[4];
            obj.translate.y = matrix[5];

            obj.rotate = Math.round(Math.atan2(parseFloat(matrix[1]), parseFloat(matrix[0])) * (180/Math.PI));

            obj.scale.x = Math.sqrt(matrix[0]*matrix[0] + matrix[1]*matrix[1]);
            obj.scale.y = Math.sqrt(matrix[2]*matrix[2] + matrix[3]*matrix[3]);
        }

        obj.toString = function () {
            return "transform: translate("+obj.translate.x+"px,"+obj.translate.y+"px) rotate("+obj.rotate+"deg) scale("+obj.scale.x+","+obj.scale.y+");";
        };

        return obj;
    };


    /*************************************************************************
     *
     *                          Missing functions
     *
     ************************************************************************/

    // MSIE
    /**
     *
     */
    if (!String.prototype.startsWith) {
        String.prototype.startsWith = function (searchString, position) {
            position = position || 0;

            return this.substr(position, searchString.length) === searchString;
        };
    }

    // MSIE
    /**
     *
     */
    if (!String.prototype.endsWith) {
        String.prototype.endsWith = function (searchString, position) {
            var subjectString = this.toString();
            if (typeof position !== "number" || !isFinite(position) || Math.floor(position) !== position || position > subjectString.length) {
                position = subjectString.length;
            }
            position -= searchString.length;
            var lastIndex = subjectString.lastIndexOf(searchString, position);

            return lastIndex !== -1 && lastIndex === position;
        };
    }

    // MSIE
    /**
     *
     */
    if (!Number.parseInt) {
        Number.parseInt = parseInt;
    }

}(jQuery));
