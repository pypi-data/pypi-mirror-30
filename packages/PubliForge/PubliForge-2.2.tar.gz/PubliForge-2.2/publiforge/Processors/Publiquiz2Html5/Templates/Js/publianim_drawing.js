/**
 * @projectDescription PubliAnim Drawing
 *
 * @author Tien Haï NGUYEN
 * @version 0.1
 */

/*jshint globalstrict: true*/
/*global jQuery: true*/
/*global document: true */
/*global window: true */
/*global setInterval: true */
/*global clearInterval: true */
/*global Image: true*/

"use strict";

(function ($) {

    if (!$.publianim) {
        $.publianim = {};
    }

    /*************************
     *
     *        Drawing
     *
     *************************/

    /**
     * Constructor for the drawing effect.
     * @param {jQuery} $drawingElem - Main element.
     * @param {Object} options - Specific parameters.
     */
    $.publianim.Drawing = function($drawingElem, options) {
        this.options = $.extend({}, this.defaults, options);
        this._$drawingCanvas = $drawingElem;
        this._pixelsZone = [];
        this._zonesPixel = {};
        this._zonesColor = {};

        this._ready = {};
        this.initColors();
        this.initTools();
        this.initDrawingCanvas();
        this.initMaskCanvas();
    };
    $.publianim.Drawing.animName = "Drawing";

    /**
     * Object implements PubliAnimInterface.
     */
    var Drawing = $.publianim.Drawing;
    $.extend(Drawing.prototype, new $.publianim.PubliAnimInterface());

    /**
     * Define functions included in object.
     */
    $.extend(Drawing.prototype, {

        /*-------------
         Public members
         -------------*/
        defaults: {
            /**
             * jQuery colors elements.
             * @type {jQuery}
             */
            $colors: null,

            context: null,

            defaultBackgroundColor: "#ffffff",
            defaultColor: "#000000",
            defaultTool: "bucket",

            /**
             * Image path for the drawing's mask. Allows zone painting.
             * @type {String}
             */
            mask: null,

            /**
             * Hexadecimal value of a color to ignore on the mask. Prevents
             * this area from being painted.
             * @type {String}
             */
            maskIgnoreColor: null,

            /**
             * Image path for the drawing's outline.
             * @type {String}
             */
            outline: null,

            /**
             * jQuery tools elements.
             * @type {jQuery}
             */
            $tools: null,

            /**
             * jQuery tool size element.
             * @type {jQuery}
             */
            $toolSize: null
        },
        options: null,

        /*--------------
         Private members
         --------------*/
        /**
         * Main element.
         * @type {jQuery}
         */
        _$drawingCanvas: null,

        /**
         * Currently selected color in hex format (ex: #000000).
         * @type {String}
         */
        _activeColor: null,

        /**
         * Currently selected tool.
         * @type {String}
         */
        _activeTool: null,

        /**
         * Canvas HTML.
         * @type {HTMLCanvasElement}
         */
        _canvas: null,

        /**
         * Context of the drawing canvas.
         * @type {CanvasRenderingContext2D}
         */
        _context: null,

        /**
         * Current drawing state.
         * @type {boolean}
         */
        _drawingState: false,

        /**
         * Image data of the context of the drawing canvas.
         * @type {ImageData}
         */
        _imageData: null,

        /**
         * @type {String}
         */
        _lastImageURL: null,

        /**
         * Default lineWidth to draw.
         * @type {Number}
         */
        _lineWidth: 10,

        /**
         * @type {Image}
         */
        _outline: null,

        /**
         * List of the pixels of the canvas associated with their corresponding zone.
         * @type {Array}
         */
        _pixelsZone: null,

        /**
         * Ready states. Check current value with {@link Drawing._isReady}.
         * @type {Object}
         */
        _ready: null,

        /**
         * List of zones with a list of their respective pixels.
         * @type {Object}
         */
        _zonesPixel: null,

        /**
         * List of zones with their respective color when drawn.
         * @type {Object}
         */
        _zonesColor: null,

        /**
         * Suffix used for save context
         * @type {String}
         */
        _cntSuffix: "_drawing_context",
        /**
         * Save current highlighter point in array.
         */
        _currentHighlighterPoints: [],

        /*-------------
         Public methods
         -------------*/

        enable: function () {
            this.disable();

            var _that = this;
            var offset = this._$drawingCanvas.get(0).getBoundingClientRect();
            var border = {
                top: parseInt(this._$drawingCanvas.css("borderTopWidth"), 10),
                left: parseInt(this._$drawingCanvas.css("borderLeftWidth"), 10)
            };
            var padding = {
                top: parseInt(this._$drawingCanvas.css("paddingTop"), 10),
                left: parseInt(this._$drawingCanvas.css("paddingLeft"), 10)
            };
            offset = {
                top: offset.top - (border.top + padding.top),
                left: offset.left - (border.left + padding.left)
            };
            var cssRatio = {
                height: _that._$drawingCanvas.attr("height") / _that._$drawingCanvas.height(),
                width: _that._$drawingCanvas.attr("width") / _that._$drawingCanvas.width()
            };

            var touchOrig = {x:0, y:0};

            this._$drawingCanvas.on("mousedown.drawing", function (e) {
                e.preventDefault();
                offset = _that._$drawingCanvas.get(0).getBoundingClientRect();
                offset = {
                    top: offset.top + border.top + padding.top,
                    left: offset.left + border.left + padding.left
                };
                cssRatio = {
                    height: _that._$drawingCanvas.attr("height") / _that._$drawingCanvas.height(),
                    width: _that._$drawingCanvas.attr("width") / _that._$drawingCanvas.width()
                };
                touchOrig = {
                    x: Math.floor((e.clientX - offset.left) * cssRatio.width),
                    y: Math.floor((e.clientY - offset.top) * cssRatio.height)
                };

                $(document).off(".drawing");
                $(document).on("mousemove.drawing", function (e) {
                    e.preventDefault();

                    if (_that._drawingState) {
                        var pos = {
                            x: Math.floor((e.clientX - offset.left) * cssRatio.width),
                            y: Math.floor((e.clientY - offset.top) * cssRatio.height)
                        };

                        _that._eventMove(touchOrig, pos);
                        touchOrig = pos;
                    }
                });
                $(document).on("mouseup.drawing", function (e) {
                    e.preventDefault();

                    $(document).off(".drawing");
                    _that._eventEnd(touchOrig);
                });

                _that._eventStart(touchOrig);
            });

            this._$drawingCanvas.on("touchstart.drawing", function (e) {
                e.preventDefault();
                offset = _that._$drawingCanvas.get(0).getBoundingClientRect();
                offset = {
                    top: offset.top + border.top + padding.top,
                    left: offset.left + border.left + padding.left
                };
                cssRatio = {
                    height: _that._$drawingCanvas.attr("height") / _that._$drawingCanvas.height(),
                    width: _that._$drawingCanvas.attr("width") / _that._$drawingCanvas.width()
                };

                var touch = e.originalEvent.changedTouches[0];
                touchOrig = {
                    x: Math.floor((touch.clientX - offset.left) * cssRatio.width),
                    y: Math.floor((touch.clientY - offset.top) * cssRatio.height)
                };

                _that._eventStart(touchOrig);
            });

            this._$drawingCanvas.on("touchmove.drawing", function (e) {
                e.preventDefault();

                if (_that._drawingState) {
                    var touch = e.originalEvent.changedTouches[0];
                    var pos = {
                        x: Math.floor((touch.clientX - offset.left) * cssRatio.width),
                        y: Math.floor((touch.clientY - offset.top) * cssRatio.height)
                    };

                    _that._eventMove(touchOrig, pos);
                    touchOrig = pos;
                }
            });

            this._$drawingCanvas.on("touchend.drawing", function (e) {
                e.preventDefault();
                _that._eventEnd(touchOrig);
            });

            if (this.options.buttons && this.options.buttons.$clear) {
                this.options.buttons.$clear.on("click", function() {
                    _that.clear();
                });
            }
        },

        disable: function () {
            this._$drawingCanvas.off(".drawing");
            $(document).off(".drawing");
        },

        modified: function () {
            // Trigger an event for save context when use in quiz or use only animation
            this._$drawingCanvas.trigger("drawingModified");

            // Trigger an event when animation has modified
            $(document).trigger("animationModified");
        },

        save: function () {
            if (!this.options.context || this.options.context.ttl < 0)
                return null;

            var data = this._zonesColor;
            if (this._lastImageURL) {
                data = this._lastImageURL;
            }

            return data;
        },

        saveContext: function () {
            var data = this.save();
            if (data === null)
                return;
            $.publianim.context.saveContext(
                this.options.context.ttl, this.options.context.ttl,
                this.options.context.id+this._cntSuffix, data);
        },

        loadContext: function() {
            if (!this.options.context || this.options.context.ttl < 0)
                return;

            var step = 500;
            var _that = this;
            _that._ready.context = false;
            var timer = setInterval(function() {
                if (_that._ready.canvas) {
                    clearInterval(timer);
                    $.publianim.context.loadContext(
                        _that.options.context.ttl, _that.options.context.ttl,
                        _that.options.context.id+_that._cntSuffix,
                        function (id, data) {
                            if (data) {
                                _that.load(data);
                            }
                            _that._ready.context = true;
                        }
                    );
                }
            }, step);
        },

        load: function (data) {
            var _that = this;
            this._ready.load = false;
            var timer = window.setInterval(function () {
                if (_that._ready.canvas) {
                    if (typeof data === "string") {
                        var image = new Image();
                        image.onload = function () {
                            _that._context.clearRect(0, 0, _that._canvas.width, _that._canvas.height);
                            _that._context.drawImage(image, 0, 0);
                            _that._imageData = _that._context.getImageData(0, 0, _that._canvas.width, _that._canvas.height);
                            _that._ready.load = true;
                        };

                        image.src = data;
                    }
                    else {
                        _that._repaintZones(data);
                        _that._ready.load = true;
                    }

                    window.clearInterval(timer);
                }
            }, 100);
        },

        clear: function () {
            this._clearCanvas();

            if (this.options.context) {
                $.publianim.context.clearContext(this.options.context.id+this._cntSuffix);
            }
        },

        isReady: function () {
            for (var i in this._ready) {
                if (!this._ready[i]) {
                    return false;
                }
            }

            return true;
        },

        /*--------------
         Private methods
         --------------*/

        /**
         * Find and add a listener on the colors.
         */
        initColors: function () {
            if (this.options.$colors) {
                this._enableColors();

                var $defaultColor = this.options.$colors.filter(".selected");
                if ($defaultColor.length > 0) {
                    $defaultColor.click();
                }
            }
            else {
                this._activeColor = this.options.defaultColor;
            }

        },

        /**
         * Find and add a listener on the tools.
         */
        initTools: function () {
            var _that = this;

            if (this.options.$tools) {
                this.options.$tools.on("touch click", function (e) {
                    e.preventDefault();
                    var $this = $(this);

                    // When previously selected tools disabled colors, enables them.
                    if (_that._activeTool === "eraser") {
                        _that._enableColors();
                    }

                    _that.options.$tools.removeClass("selected");
                    $this.addClass("selected");
                    _that._activeTool = $this.data("drawingTool");

                    // When selected tools doesn't need colors, disables them.
                    if (_that._activeTool === "eraser") {
                        _that._disableColors();
                    }
                });
                var $defaultTool = this.options.$tools.filter(".selected");
                if ($defaultTool.length > 0) {
                    $defaultTool.click();
                }
            }
            else {
                this._activeTool = this.options.defaultTool;
            }

        },

        initDrawingCanvas: function () {
            var _that = this;
            this._canvas = this._$drawingCanvas.get(0);
            this._context = this._canvas.getContext("2d");
            var width = this._canvas.width;
            var height = this._canvas.height;

            // Fix canvas dimensions
            var bgWidth = this._$drawingCanvas.width();
            var bgHeight = this._$drawingCanvas.height();
            var ratio = Math.max(bgWidth, bgHeight) / Math.min(bgWidth, bgHeight);
            if (bgWidth > bgHeight) {
                this._$drawingCanvas.attr("height", height / ratio);
            }
            else if (bgWidth < bgHeight) {
                this._$drawingCanvas.attr("width", width / ratio);
            }

            this._imageData = this._context.getImageData(0, 0, width, height);

            if (this.options.outline) {
                this._ready.canvas = false;

                this._outline = new Image();
                this._outline.onload = function () {
                    _that._loadImageCanvas(_that._canvas, _that._outline);

                    var width = _that._canvas.width;
                    var height = _that._canvas.height;
                    _that._imageData = _that._context.getImageData(0, 0, width, height);

                    _that._ready.canvas = true;
                };
                this._outline.src = this.options.outline;
            } else {
                _that._ready.canvas = true;
            }

        },

        initMaskCanvas: function () {
            var _that = this;

            if (this.options.mask) {
                var backColor = this._$drawingCanvas.css("background-color");

                if (!(backColor.startsWith("rgba") && backColor.endsWith("0)") || backColor === "transparent")) {
                    var result = /^rgba?\((\d+), (\d+), (\d+)/i.exec(backColor);
                    this.options.defaultBackgroundColor = this._rgbToHex({
                        r: parseInt(result[1], 10),
                        g: parseInt(result[2], 10),
                        b: parseInt(result[3], 10)
                    });
                }

                var canvas = document.createElement("canvas");
                this._ready.mask = false;
                var mask = new Image();
                mask.onload = function () {
                    _that._loadImageCanvas(canvas, mask);
                    _that._discoverZones(canvas);

                    _that._ready.mask = true;
                };
                mask.src = this.options.mask;
            }
            else {
                // When no mask, can't use bucket to paint zones.
                var $selected = this.options.$tools.filter(".selected");
                if ($selected.length > 0)
                    this._activeTool = $selected.data("drawingTool");
                else
                    this._activeTool = "brush";
            }

        },

        _enableColors: function () {
            if (this.options.$colors) {
                var _that = this;
                this.options.$colors.on("touch.drawingColor click.drawingColor", function (e) {
                    e.preventDefault();
                    var $this = $(this);
                    _that.options.$colors.removeClass("selected");
                    $this.addClass("selected");
                    _that._activeColor = $this.data("drawingColor");
                });

                if (_that._activeColor) {
                    var $color = this.options.$colors.filter(function () {
                        if ($(this).data("drawingColor") === _that._activeColor)
                            return true;

                        return false;
                    });
                    $color.click();
                }
            }
        },

        _disableColors: function () {
            if (this.options.$colors) {
                this.options.$colors.off(".drawingColor").removeClass("selected");
            }
        },

        /**
         * Start event to draw. Set context configuration according to current
         * tool and color.
         * @param {Object} origPos - Coordinates of the event.
         */
        _eventStart: function (origPos) {
            if (this.options.$toolSize && this.options.$toolSize.length > 0) {
                this._lineWidth = this.options.$toolSize.text();
            }

            if ((this._activeTool === "brush" && this._activeColor) ||
                    this._activeTool === "eraser") {
                this._drawingState = true;

                this._context.lineCap = "round";
                this._context.lineJoin = "round";
                this._context.lineWidth = this._lineWidth;
                this._context.globalAlpha = 1.0;
                this._context.beginPath();
                this._context.moveTo(origPos.x, origPos.y);
                this._context.closePath();
                this._context.shadowBlur = 0;

                if (this._activeTool === "eraser") {
                    this._context.globalCompositeOperation = "destination-out";
                }
                else {
                    this._context.globalCompositeOperation = "source-over";
                    this._context.strokeStyle = this._activeColor;
                    this._context.fillStyle = this._activeColor;
                }
            }
            else if (this._activeTool === "highlighter" && this._activeColor) {
                this._drawingState = true;

                this._currentHighlighterPoints = [];

                this._lastImageURL = this._canvas.toDataURL();
                this._context.lineCap = "round";
                this._context.lineJoin = "round";
                this._context.lineWidth = this._lineWidth;
                this._context.globalAlpha = 0.35;
                this._context.globalCompositeOperation = "xor";
                this._context.beginPath();
                this._context.moveTo(origPos.x, origPos.y);
                this._context.closePath();
                this._context.shadowBlur = 0;
                this._context.strokeStyle = this._activeColor;
                this._context.fillStyle = this._activeColor;
            }
        },

        /**
         * Move event during drawing.
         * @param {Object} prevPos - Previous position.
         * @param {Object} currPos - Current position.
         */
        _eventMove: function (prevPos, currPos) {
            if (this._activeTool === "highlighter" && this._activeColor) {
                this._currentHighlighterPoints.push(currPos);
                var _that = this;
                var img = new Image();

                img.onload = function () {
                    _that._context.clearRect(0, 0, _that._canvas.width, _that._canvas.height);
                    _that._context.beginPath();
                    _that._context.globalAlpha = 0.35;
                    _that._context.globalCompositeOperation = "xor";
                    for (var i = 0; i < _that._currentHighlighterPoints.length; i++) {
                        if (_that._currentHighlighterPoints[i] && i) {
                            _that._context.moveTo(_that._currentHighlighterPoints[i-1].x, _that._currentHighlighterPoints[i-1].y);
                        }
                        else {
                            _that._context.moveTo(_that._currentHighlighterPoints[i].x, _that._currentHighlighterPoints[i].y);
                        }
                        _that._context.lineTo(_that._currentHighlighterPoints[i].x, _that._currentHighlighterPoints[i].y);
                        _that._context.stroke();
                    }
                    _that._context.globalAlpha = 1.0;
                    _that._context.globalCompositeOperation = "destination-over";
                    _that._context.drawImage(img, 0, 0, _that._canvas.width, _that._canvas.height);
                    _that._context.closePath();
                };

                img.src = this._lastImageURL;
            }
            else {
                this._context.beginPath();
                this._context.moveTo(prevPos.x, prevPos.y);
                this._context.lineTo(currPos.x, currPos.y);
                this._context.stroke();
                this._context.closePath();

                this._redrawOutline();
            }
        },

        /**
         * End event of drawing. Redraw outline and save state.
         * @param {Object} lastPos - Last position.
         */
        _eventEnd: function (lastPos) {

            if ((this._activeTool === "brush" && this._activeColor) ||
                    this._activeTool === "eraser") {
                this._context.beginPath();
                this._context.arc(lastPos.x, lastPos.y, this._lineWidth/2, 0, 2*Math.PI);
                this._context.fill();
                this._context.closePath();

                this._redrawOutline();
                this._imageData = this._context.getImageData(0, 0, this._canvas.width, this._canvas.height);
                this._lastImageURL = this._canvas.toDataURL();
                this._drawingState = false;

            }
            else if (this._activeTool === "bucket") {
                var pixel = lastPos.y * this._canvas.width + lastPos.x;
                var zone = this._pixelsZone[pixel];

                if (!this._zonesPixel[zone] || !this._activeColor)
                    return;

                this._context.globalCompositeOperation = "source-over";

                this._paintZone(zone);
                this._redrawOutline();
                this._imageData = this._context.getImageData(0, 0, this._canvas.width, this._canvas.height);

                if (this._lastImageURL) {
                    this._lastImageURL = this._canvas.toDataURL();
                }

            }
            else if (this._activeTool === "highlighter" && this._activeColor) {
                this._redrawOutline();
                this._imageData = this._context.getImageData(0, 0, this._canvas.width, this._canvas.height);
                this._lastImageURL = this._canvas.toDataURL();
                this._drawingState = false;
                this._context.globalAlpha = 1.0;
            }

            this.modified();
        },

        /**
         * Redraw a zone with a new color
         * @param {String} zone - Reference to the zone to paint.
         * @param {String} [color] - Color to paint.
         */
        _paintZone: function (zone, color) {
            if (!color) {
                color = this._activeColor;
            }

            var newColor = this._hexToRgb(color);
            var pixels = this._zonesPixel[zone];

            for (var i = 0; i < pixels.length; i++) {
                this._setPixelColor(pixels[i]*4, newColor);
            }

            this._context.putImageData(this._imageData, 0, 0);
            this._context.drawImage(this._outline, 0, 0, this._canvas.width, this._canvas.height);

            this._zonesColor[zone] = color;
        },

        /**
         * Converts an hexadecimal color to an object with r, g and b values.
         * @param {string} hex - The hexadecimal color.
         * @return {Object} RGB color.
         */
        _hexToRgb: function (hex) {
            var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);

            return result ? {
                r: parseInt(result[1], 16),
                g: parseInt(result[2], 16),
                b: parseInt(result[3], 16)
            } : null;
        },

        /**
         * Converts an object with r, g and b values to an hexadecimal string.
         * @param {Object} rgb - RGB color.
         * @return {string} - The hexadecimal color.
         */
        _rgbToHex: function (rgb) {
            var toTwoDigits = function (s) {
                return (s.length > 1 ?"":"0") + s;
            };

            return "#" + toTwoDigits(rgb.r.toString(16)) +
                toTwoDigits(rgb.g.toString(16)) + toTwoDigits(rgb.b.toString(16));
        },

        /**
         * Get an object with r, g and b values of a pixel on an image_data of a canvas.
         * @param {Object} imageData - Image data from a canvas' context.
         * @param {number} pixelPos - Position to get.
         * @return {Object} RGB color of the pixel.
         */
        _getPixelColor: function (imageData, pixelPos) {
            return {
                r: imageData.data[pixelPos],
                g: imageData.data[pixelPos + 1],
                b: imageData.data[pixelPos + 2]
            };
        },

        /**
         * Set color of a pixel from an object with r, g and b values on an image_data of a canvas.
         * @param {number} pixelPos - Index of the pixel to set.
         * @param {Object} color - RGB color.
         */
        _setPixelColor: function (pixelPos, color) {
            this._imageData.data[pixelPos] = color.r;
            this._imageData.data[pixelPos + 1] = color.g;
            this._imageData.data[pixelPos + 2] = color.b;
            this._imageData.data[pixelPos + 3] = 255;
        },

        /**
         * Load an image in a canvas. Shrinks the canvas to fit the image, keeping proportions.
         * @param {HTMLCanvasElement} canvas - HTML Canvas.
         * @param {Image} img - Image to draw.
         */
        _loadImageCanvas: function (canvas, img) {
            canvas.width = img.width;
            canvas.height = img.height;

            canvas.getContext("2d").drawImage(img, 0, 0, canvas.width, canvas.height);
        },

        /**
         * Find the colors of each pixels of the canvas.
         * @param {HTMLCanvasElement} mask - Canvas with mask drawn.
         */
        _discoverZones: function (mask) {
            var width = mask.width;
            var height = mask.height;
            var maskData = mask.getContext("2d").getImageData(0, 0, width, height);
            this._pixelsZone = [];
            for (var i = 0; i < maskData.data.length/4; i++) {
                var rgb = {r: 0, g: 0, b: 0};
                rgb.r = maskData.data[i*4];
                rgb.g = maskData.data[i*4+1];
                rgb.b = maskData.data[i*4+2];
                var hex = this._rgbToHex(rgb);

                if (hex !== this.options.maskIgnoreColor) {
                    this._pixelsZone[i] = hex;
                    if (this._zonesPixel[hex]) {
                        this._zonesPixel[hex].push(i);
                    }
                    else {
                        this._zonesPixel[hex] = [i];
                        this._zonesColor[hex] = this.options.defaultBackgroundColor;
                    }
                }
            }

        },

        _redrawOutline: function () {
            if (this._activeColor !== "transparent") {
                if (this._outline) {
                    var operation = this._context.globalCompositeOperation;
                    this._context.globalCompositeOperation = "source-over";
                    this._context.drawImage(this._outline, 0, 0, this._canvas.width, this._canvas.height);
                    this._context.globalCompositeOperation = operation;
                }
            }
        },

        /**
         * Repaint multiple zones with an associated color.
         * @param {Object} zonesColor - Associations between a zone and a color.
         */
        _repaintZones: function (zonesColor) {
            for (var z in zonesColor) {
                if (this._zonesPixel[z]) {
                    this._paintZone(z, zonesColor[z]);
                }
            }
        },

        _clearCanvas: function () {
            var width = this._canvas.width;
            var height = this._canvas.height;
            this._context.globalCompositeOperation = "source-over";
            this._context.clearRect(0, 0, width, height);
            if (this._outline)
                this._context.drawImage(this._outline, 0, 0, width, height);
            this._imageData = this._context.getImageData(0, 0, width, height);

            this._zonesColor = {};
            for (var z in this._zonesPixel) {
                this._zonesColor[z] = this.options.defaultBackgroundColor;
            }

        }

    });
}(jQuery));

