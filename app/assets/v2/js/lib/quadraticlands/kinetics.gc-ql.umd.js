;(function (global, factory) {
	typeof exports === 'object' && typeof module !== 'undefined' ? module.exports = factory() :
	typeof define === 'function' && define.amd ? define(factory) :
	(global = typeof globalThis !== 'undefined' ? globalThis : global || self, global.Kinetics = factory());
}(this, (function () { 'use strict';

	var isMergeableObject = function isMergeableObject(value) {
		return isNonNullObject(value)
			&& !isSpecial(value)
	};

	function isNonNullObject(value) {
		return !!value && typeof value === 'object'
	}

	function isSpecial(value) {
		var stringValue = Object.prototype.toString.call(value);

		return stringValue === '[object RegExp]'
			|| stringValue === '[object Date]'
			|| isReactElement(value)
	}

	// see https://github.com/facebook/react/blob/b5ac963fb791d1298e7f396236383bc955f916c1/src/isomorphic/classic/element/ReactElement.js#L21-L25
	var canUseSymbol = typeof Symbol === 'function' && Symbol.for;
	var REACT_ELEMENT_TYPE = canUseSymbol ? Symbol.for('react.element') : 0xeac7;

	function isReactElement(value) {
		return value.$$typeof === REACT_ELEMENT_TYPE
	}

	function emptyTarget(val) {
		return Array.isArray(val) ? [] : {}
	}

	function cloneUnlessOtherwiseSpecified(value, options) {
		return (options.clone !== false && options.isMergeableObject(value))
			? deepmerge(emptyTarget(value), value, options)
			: value
	}

	function defaultArrayMerge(target, source, options) {
		return target.concat(source).map(function(element) {
			return cloneUnlessOtherwiseSpecified(element, options)
		})
	}

	function getMergeFunction(key, options) {
		if (!options.customMerge) {
			return deepmerge
		}
		var customMerge = options.customMerge(key);
		return typeof customMerge === 'function' ? customMerge : deepmerge
	}

	function getEnumerableOwnPropertySymbols(target) {
		return Object.getOwnPropertySymbols
			? Object.getOwnPropertySymbols(target).filter(function(symbol) {
				return target.propertyIsEnumerable(symbol)
			})
			: []
	}

	function getKeys(target) {
		return Object.keys(target).concat(getEnumerableOwnPropertySymbols(target))
	}

	function propertyIsOnObject(object, property) {
		try {
			return property in object
		} catch(_) {
			return false
		}
	}

	// Protects from prototype poisoning and unexpected merging up the prototype chain.
	function propertyIsUnsafe(target, key) {
		return propertyIsOnObject(target, key) // Properties are safe to merge if they don't exist in the target yet,
			&& !(Object.hasOwnProperty.call(target, key) // unsafe if they exist up the prototype chain,
				&& Object.propertyIsEnumerable.call(target, key)) // and also unsafe if they're nonenumerable.
	}

	function mergeObject(target, source, options) {
		var destination = {};
		if (options.isMergeableObject(target)) {
			getKeys(target).forEach(function(key) {
				destination[key] = cloneUnlessOtherwiseSpecified(target[key], options);
			});
		}
		getKeys(source).forEach(function(key) {
			if (propertyIsUnsafe(target, key)) {
				return
			}

			if (propertyIsOnObject(target, key) && options.isMergeableObject(source[key])) {
				destination[key] = getMergeFunction(key, options)(target[key], source[key], options);
			} else {
				destination[key] = cloneUnlessOtherwiseSpecified(source[key], options);
			}
		});
		return destination
	}

  function isElement(source) {
    if (source && source.constructor.__proto__.prototype) {
      return ["Element", "HTMLElement"].indexOf(source.constructor.__proto__.prototype.constructor.name) !== -1
    }

    return false
  }

	function deepmerge(target, source, options) {
		options = options || {};
		options.arrayMerge = options.arrayMerge || defaultArrayMerge;
		options.isMergeableObject = options.isMergeableObject || isMergeableObject;
		// cloneUnlessOtherwiseSpecified is added to `options` so that custom arrayMerge()
		// implementations can use it. The caller may not replace it.
		options.cloneUnlessOtherwiseSpecified = cloneUnlessOtherwiseSpecified;

		var sourceIsArray = Array.isArray(source);
		var targetIsArray = Array.isArray(target);
		var sourceAndTargetTypesMatch = sourceIsArray === targetIsArray;
		if (!sourceAndTargetTypesMatch) {
			return cloneUnlessOtherwiseSpecified(source, options)
		} else if (sourceIsArray) {
			return options.arrayMerge(target, source, options)
		} else if (isElement(source)) {
      return source;
    } else {
			return mergeObject(target, source, options)
		}
	}

	deepmerge.all = function deepmergeAll(array, options) {
		if (!Array.isArray(array)) {
			throw new Error('first argument should be an array')
		}

		return array.reduce(function(prev, next) {
			return deepmerge(prev, next, options)
		}, {})
	};

	var deepmerge_1 = deepmerge;

	var cjs = deepmerge_1;

	var commonjsGlobal = typeof globalThis !== 'undefined' ? globalThis : typeof window !== 'undefined' ? window : typeof global !== 'undefined' ? global : typeof self !== 'undefined' ? self : {};

	function createCommonjsModule(fn) {
	  var module = { exports: {} };
		return fn(module, module.exports), module.exports;
	}

	var onscrolling = createCommonjsModule(function (module, exports) {
	(function (global, factory) {
	    module.exports = factory() ;
	}(commonjsGlobal, function () {
	    // Get proper requestAnimationFrame
	    var requestFrame = window.requestAnimationFrame,
	        cancelFrame  = window.cancelAnimationFrame;

	    if (!requestFrame) {
	        ['ms', 'moz', 'webkit', 'o'].every(function(prefix) {
	            requestFrame = window[prefix + 'RequestAnimationFrame'];
	            cancelFrame  = window[prefix + 'CancelAnimationFrame'] ||
	                           window[prefix + 'CancelRequestAnimationFrame'];
	            // Continue iterating only if requestFrame is still false
	            return !requestFrame;
	        });
	    }

	    // Module state
	    var isSupported   = !!requestFrame,
	        isListening   = false,
	        isQueued      = false,
	        isIdle        = true,
	        scrollY       = window.pageYOffset,
	        scrollX       = window.pageXOffset,
	        scrollYCached = scrollY,
	        scrollXCached = scrollX,
	        directionX    = ['x', 'horizontal'],
	        directionAll  = ['any'],
	        callbackQueue = {
	            x   : [],
	            y   : [],
	            any : []
	        },
	        detectIdleTimeout,
	        tickId;

	    // Main scroll handler
	    // -------------------
	    function handleScroll() {
	        var isScrollChanged = false;
	        if (callbackQueue.x.length || callbackQueue.any.length) {
	            scrollX = window.pageXOffset;
	        }
	        if (callbackQueue.y.length || callbackQueue.any.length) {
	            scrollY = window.pageYOffset;
	        }

	        if (scrollY !== scrollYCached) {
	            callbackQueue.y.forEach(triggerCallback.y);
	            scrollYCached = scrollY;
	            isScrollChanged = true;
	        }
	        if (scrollX !== scrollXCached) {
	            callbackQueue.x.forEach(triggerCallback.x);
	            scrollXCached = scrollX;
	            isScrollChanged = true;
	        }
	        if (isScrollChanged) {
	            callbackQueue.any.forEach(triggerCallback.any);
	            window.clearTimeout(detectIdleTimeout);
	            detectIdleTimeout = null;
	        }

	        isQueued = false;
	        requestTick();
	    }

	    // Utilities
	    // ---------
	    function triggerCallback(callback, scroll) {
	        callback(scroll);
	    }
	    triggerCallback.y = function(callback) {
	        triggerCallback(callback, scrollY);
	    };
	    triggerCallback.x = function(callback) {
	        triggerCallback(callback, scrollX);
	    };
	    triggerCallback.any = function(callback) {
	        triggerCallback(callback, [scrollX, scrollY]);
	    };

	    function enableScrollListener() {
	        if (isListening || isQueued) {
	            return;
	        }
	        if (isIdle) {
	            isListening = true;
	            window.addEventListener('scroll', onScrollDebouncer);
	            document.body.addEventListener('touchmove', onScrollDebouncer);
	            return;
	        }
	        requestTick();
	    }

	    function disableScrollListener() {
	        if (!isListening) {
	            return;
	        }
	        window.removeEventListener('scroll', onScrollDebouncer);
	        document.body.removeEventListener('touchmove', onScrollDebouncer);
	        isListening = false;
	    }

	    function onScrollDebouncer() {
	        isIdle = false;
	        requestTick();
	        disableScrollListener();
	    }

	    function requestTick() {
	        if (isQueued) {
	            return;
	        }
	        if (!detectIdleTimeout) {
	            // Idle is defined as 1.5 seconds without scroll change
	            detectIdleTimeout = window.setTimeout(detectIdle, 1500);
	        }
	        tickId = requestFrame(handleScroll);
	        isQueued = true;
	    }

	    function cancelTick() {
	        if (!isQueued) {
	            return;
	        }
	        cancelFrame(tickId);
	        isQueued = false;
	    }

	    function detectIdle() {
	        isIdle = true;
	        cancelTick();
	        enableScrollListener();
	    }

	    /**
	     * Attach callback to debounced scroll event
	     *
	     * Takes two forms:
	     * @param function callback  Function to attach to a vertical scroll event
	     * Or:
	     * @param string   direction Direction of scroll to attach to:
	     *                 'horizontal'/'x', 'vertical'/'y' (the default),
	     *                 or 'any' (listens to both)
	     * @param function callback  Function to attach to a scroll event in specified direction
	     */
	    function onscrolling(direction, callback) {
	        if (!isSupported) {
	            return;
	        }
	        enableScrollListener();
	        // Verify parameters
	        if (typeof direction === 'function') {
	            callback = direction;
	            callbackQueue.y.push(callback);
	            return;
	        }
	        if (typeof callback === 'function') {
	            if (~directionX.indexOf(direction)) {
	                callbackQueue.x.push(callback);
	            } else if (~directionAll.indexOf(direction)) {
	                callbackQueue.any.push(callback);
	            } else {
	                callbackQueue.y.push(callback);
	            }
	        }
	    }

	    onscrolling.remove = function(direction, fn) {
	        var queueKey = 'y',
	            queue,
	            fnIdx;

	        if (typeof direction === 'string') {
	            // If second parameter is not a function, return
	            if (typeof fn !== 'function') {
	                return;
	            }
	            if (~directionX.indexOf(direction)) {
	                queueKey = directionX[0];
	            } else if (~directionAll.indexOf(direction)) {
	                queueKey = directionAll[0];
	            }
	        } else {
	            fn = direction;
	        }
	        queue = callbackQueue[queueKey];
	        fnIdx = queue.indexOf(fn);
	        if (fnIdx > -1) {
	            queue.splice(fnIdx, 1);
	        }
	        // If there's no listeners left, disable listening
	        if (!callbackQueue.x.length && !callbackQueue.y.length && !callbackQueue.any.length) {
	            cancelTick();
	            disableScrollListener();
	        }
	    };
	    onscrolling.off = onscrolling.remove;

	    return onscrolling;

	}));
	});

	var debug = false;
	var spring = {
		tension: 8,
		friction: 10,
		randomTension: 50,
		randomFriction: -4,
		extendedRestDelay: 10
	};
	var canvas = {
		handlePosition: true,
		background: ""
	};
	var particles = {
		count: 16,
		sides: {
			min: 3,
			max: 5
		},
		sizes: {
			min: 5,
			max: 20
		},
		rotate: {
			speed: 1.5,
			direction: null
		},
		mode: {
			type: "space",
			speed: 2,
			boundery: "endless"
		},
		parallex: {
			layers: 3,
			speed: 0.15
		},
		attract: {
			chance: 0.75,
			force: 1,
			grow: 2,
			size: null,
			type: "static",
			speed: 1.5,
			direction: -1,
			radius: 1
		},
		fill: [
			"#6F3FF5",
			"#02E2AC",
			"#F35890"
		],
		toColor: "#66229933",
		opacity: "DD",
		stroke: {
			color: "",
			width: 1
		}
	};
	var config = {
		debug: debug,
		spring: spring,
		canvas: canvas,
		particles: particles
	};

	var version = "0.7.3";

	/**
	 * Cross-browser DevicePixelRatio
	 * @return {Number} DevicePixelRatio
	 */
	var dpr = (() => {
	  let dpr = 1;

	  if (typeof screen !== 'undefined' && 'deviceXDPI' in screen) {
	    dpr = screen.deviceXDPI / screen.logicalXDPI;
	  } else if (typeof window !== 'undefined' && 'devicePixelRatio' in window) {
	    dpr = window.devicePixelRatio;
	  }

	  dpr = Number(dpr.toFixed(3));
	  return dpr;
	});

	/**
	 *  Copyright (c) 2013, Facebook, Inc.
	 *  All rights reserved.
	 *
	 *  This source code is licensed under the BSD-style license found in the
	 *  LICENSE file in the root directory of this source tree. An additional grant
	 *  of patent rights can be found in the PATENTS file in the same directory.
	 */

	var rebound = createCommonjsModule(function (module, exports) {
	(function (global, factory) {
		module.exports = factory() ;
	}(commonjsGlobal, (function () {
	var _onFrame = void 0;
	if (typeof window !== 'undefined') {
	  _onFrame = window.requestAnimationFrame || window.webkitRequestAnimationFrame || window.mozRequestAnimationFrame || window.msRequestAnimationFrame || window.oRequestAnimationFrame;
	}

	if (!_onFrame && typeof process !== 'undefined' && process.title === 'node') {
	  _onFrame = setImmediate;
	}

	_onFrame = _onFrame || function (callback) {
	  window.setTimeout(callback, 1000 / 60);
	};

	var _onFrame$1 = _onFrame;

	/* eslint-disable flowtype/no-weak-types */

	var concat = Array.prototype.concat;
	var slice = Array.prototype.slice;

	// Bind a function to a context object.
	function bind(func, context) {
	  for (var _len = arguments.length, outerArgs = Array(_len > 2 ? _len - 2 : 0), _key = 2; _key < _len; _key++) {
	    outerArgs[_key - 2] = arguments[_key];
	  }

	  return function () {
	    for (var _len2 = arguments.length, innerArgs = Array(_len2), _key2 = 0; _key2 < _len2; _key2++) {
	      innerArgs[_key2] = arguments[_key2];
	    }

	    func.apply(context, concat.call(outerArgs, slice.call(innerArgs)));
	  };
	}

	// Add all the properties in the source to the target.
	function extend(target, source) {
	  for (var key in source) {
	    if (source.hasOwnProperty(key)) {
	      target[key] = source[key];
	    }
	  }
	}

	// Cross browser/node timer functions.
	function onFrame(func) {
	  return _onFrame$1(func);
	}

	// Lop off the first occurence of the reference in the Array.
	function removeFirst(array, item) {
	  var idx = array.indexOf(item);
	  idx !== -1 && array.splice(idx, 1);
	}

	var colorCache = {};
	/**
	 * Converts a hex-formatted color string to its rgb-formatted equivalent. Handy
	 * when performing color tweening animations
	 * @public
	 * @param colorString A hex-formatted color string
	 * @return An rgb-formatted color string
	 */
	function hexToRGB(colorString) {
	  if (colorCache[colorString]) {
	    return colorCache[colorString];
	  }
	  var normalizedColor = colorString.replace('#', '');
	  if (normalizedColor.length === 3) {
	    normalizedColor = normalizedColor[0] + normalizedColor[0] + normalizedColor[1] + normalizedColor[1] + normalizedColor[2] + normalizedColor[2];
	  }
	  var parts = normalizedColor.match(/.{2}/g);
	  if (!parts || parts.length < 3) {
	    throw new Error('Expected a color string of format #rrggbb');
	  }

	  var ret = {
	    r: parseInt(parts[0], 16),
	    g: parseInt(parts[1], 16),
	    b: parseInt(parts[2], 16)
	  };

	  colorCache[colorString] = ret;
	  return ret;
	}

	/**
	 * Converts a rgb-formatted color string to its hex-formatted equivalent. Handy
	 * when performing color tweening animations
	 * @public
	 * @param colorString An rgb-formatted color string
	 * @return A hex-formatted color string
	 */
	function rgbToHex(rNum, gNum, bNum) {
	  var r = rNum.toString(16);
	  var g = gNum.toString(16);
	  var b = bNum.toString(16);
	  r = r.length < 2 ? '0' + r : r;
	  g = g.length < 2 ? '0' + g : g;
	  b = b.length < 2 ? '0' + b : b;
	  return '#' + r + g + b;
	}

	var util = Object.freeze({
		bind: bind,
		extend: extend,
		onFrame: onFrame,
		removeFirst: removeFirst,
		hexToRGB: hexToRGB,
		rgbToHex: rgbToHex
	});

	/**
	 * This helper function does a linear interpolation of a value from
	 * one range to another. This can be very useful for converting the
	 * motion of a Spring to a range of UI property values. For example a
	 * spring moving from position 0 to 1 could be interpolated to move a
	 * view from pixel 300 to 350 and scale it from 0.5 to 1. The current
	 * position of the `Spring` just needs to be run through this method
	 * taking its input range in the _from_ parameters with the property
	 * animation range in the _to_ parameters.
	 * @public
	 */
	function mapValueInRange(value, fromLow, fromHigh, toLow, toHigh) {
	  var fromRangeSize = fromHigh - fromLow;
	  var toRangeSize = toHigh - toLow;
	  var valueScale = (value - fromLow) / fromRangeSize;
	  return toLow + valueScale * toRangeSize;
	}

	/**
	 * Interpolate two hex colors in a 0 - 1 range or optionally provide a
	 * custom range with fromLow,fromHight. The output will be in hex by default
	 * unless asRGB is true in which case it will be returned as an rgb string.
	 *
	 * @public
	 * @param asRGB Whether to return an rgb-style string
	 * @return A string in hex color format unless asRGB is true, in which case a string in rgb format
	 */
	function interpolateColor(val, startColorStr, endColorStr) {
	  var fromLow = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : 0;
	  var fromHigh = arguments.length > 4 && arguments[4] !== undefined ? arguments[4] : 1;
	  var asRGB = arguments[5];

	  var startColor = hexToRGB(startColorStr);
	  var endColor = hexToRGB(endColorStr);
	  var r = Math.floor(mapValueInRange(val, fromLow, fromHigh, startColor.r, endColor.r));
	  var g = Math.floor(mapValueInRange(val, fromLow, fromHigh, startColor.g, endColor.g));
	  var b = Math.floor(mapValueInRange(val, fromLow, fromHigh, startColor.b, endColor.b));
	  if (asRGB) {
	    return 'rgb(' + r + ',' + g + ',' + b + ')';
	  } else {
	    return rgbToHex(r, g, b);
	  }
	}

	function degreesToRadians(deg) {
	  return deg * Math.PI / 180;
	}

	function radiansToDegrees(rad) {
	  return rad * 180 / Math.PI;
	}

	var MathUtil = Object.freeze({
		mapValueInRange: mapValueInRange,
		interpolateColor: interpolateColor,
		degreesToRadians: degreesToRadians,
		radiansToDegrees: radiansToDegrees
	});

	// Math for converting from
	// [Origami](http://facebook.github.io/origami/) to
	// [Rebound](http://facebook.github.io/rebound).
	// You mostly don't need to worry about this, just use
	// SpringConfig.fromOrigamiTensionAndFriction(v, v);

	function tensionFromOrigamiValue(oValue) {
	  return (oValue - 30.0) * 3.62 + 194.0;
	}

	function origamiValueFromTension(tension) {
	  return (tension - 194.0) / 3.62 + 30.0;
	}

	function frictionFromOrigamiValue(oValue) {
	  return (oValue - 8.0) * 3.0 + 25.0;
	}

	function origamiFromFriction(friction) {
	  return (friction - 25.0) / 3.0 + 8.0;
	}

	var OrigamiValueConverter = Object.freeze({
		tensionFromOrigamiValue: tensionFromOrigamiValue,
		origamiValueFromTension: origamiValueFromTension,
		frictionFromOrigamiValue: frictionFromOrigamiValue,
		origamiFromFriction: origamiFromFriction
	});

	var classCallCheck = function (instance, Constructor) {
	  if (!(instance instanceof Constructor)) {
	    throw new TypeError("Cannot call a class as a function");
	  }
	};









	var _extends = Object.assign || function (target) {
	  for (var i = 1; i < arguments.length; i++) {
	    var source = arguments[i];

	    for (var key in source) {
	      if (Object.prototype.hasOwnProperty.call(source, key)) {
	        target[key] = source[key];
	      }
	    }
	  }

	  return target;
	};

	/**
	 * Plays each frame of the SpringSystem on animation
	 * timing loop. This is the default type of looper for a new spring system
	 * as it is the most common when developing UI.
	 * @public
	 */
	/**
	 *  Copyright (c) 2013, Facebook, Inc.
	 *  All rights reserved.
	 *
	 *  This source code is licensed under the BSD-style license found in the
	 *  LICENSE file in the root directory of this source tree. An additional grant
	 *  of patent rights can be found in the PATENTS file in the same directory.
	 *
	 *
	 */

	var AnimationLooper = function () {
	  function AnimationLooper() {
	    classCallCheck(this, AnimationLooper);
	    this.springSystem = null;
	  }

	  AnimationLooper.prototype.run = function run() {
	    var springSystem = getSpringSystem.call(this);

	    onFrame(function () {
	      springSystem.loop(Date.now());
	    });
	  };

	  return AnimationLooper;
	}();

	/**
	 * Resolves the SpringSystem to a resting state in a
	 * tight and blocking loop. This is useful for synchronously generating
	 * pre-recorded animations that can then be played on a timing loop later.
	 * Sometimes this lead to better performance to pre-record a single spring
	 * curve and use it to drive many animations; however, it can make dynamic
	 * response to user input a bit trickier to implement.
	 * @public
	 */
	var SimulationLooper = function () {
	  function SimulationLooper(timestep) {
	    classCallCheck(this, SimulationLooper);
	    this.springSystem = null;
	    this.time = 0;
	    this.running = false;

	    this.timestep = timestep || 16.667;
	  }

	  SimulationLooper.prototype.run = function run() {
	    var springSystem = getSpringSystem.call(this);

	    if (this.running) {
	      return;
	    }
	    this.running = true;
	    while (!springSystem.getIsIdle()) {
	      springSystem.loop(this.time += this.timestep);
	    }
	    this.running = false;
	  };

	  return SimulationLooper;
	}();

	/**
	 * Resolves the SpringSystem one step at a
	 * time controlled by an outside loop. This is useful for testing and
	 * verifying the behavior of a SpringSystem or if you want to control your own
	 * timing loop for some reason e.g. slowing down or speeding up the
	 * simulation.
	 * @public
	 */
	var SteppingSimulationLooper = function () {
	  function SteppingSimulationLooper() {
	    classCallCheck(this, SteppingSimulationLooper);
	    this.springSystem = null;
	    this.time = 0;
	    this.running = false;
	  }

	  SteppingSimulationLooper.prototype.run = function run() {}
	  // this.run is NOOP'd here to allow control from the outside using
	  // this.step.


	  // Perform one step toward resolving the SpringSystem.
	  ;

	  SteppingSimulationLooper.prototype.step = function step(timestep) {
	    var springSystem = getSpringSystem.call(this);
	    springSystem.loop(this.time += timestep);
	  };

	  return SteppingSimulationLooper;
	}();

	function getSpringSystem() {
	  if (this.springSystem == null) {
	    throw new Error('cannot run looper without a springSystem');
	  }
	  return this.springSystem;
	}



	var Loopers = Object.freeze({
		AnimationLooper: AnimationLooper,
		SimulationLooper: SimulationLooper,
		SteppingSimulationLooper: SteppingSimulationLooper
	});

	/**
	 * Provides math for converting from Origami PopAnimation
	 * config values to regular Origami tension and friction values. If you are
	 * trying to replicate prototypes made with PopAnimation patches in Origami,
	 * then you should create your springs with
	 * SpringSystem.createSpringWithBouncinessAndSpeed, which uses this Math
	 * internally to create a spring to match the provided PopAnimation
	 * configuration from Origami.
	 */
	var BouncyConversion = function () {
	  function BouncyConversion(bounciness, speed) {
	    classCallCheck(this, BouncyConversion);

	    this.bounciness = bounciness;
	    this.speed = speed;

	    var b = this.normalize(bounciness / 1.7, 0, 20.0);
	    b = this.projectNormal(b, 0.0, 0.8);
	    var s = this.normalize(speed / 1.7, 0, 20.0);

	    this.bouncyTension = this.projectNormal(s, 0.5, 200);
	    this.bouncyFriction = this.quadraticOutInterpolation(b, this.b3Nobounce(this.bouncyTension), 0.01);
	  }

	  BouncyConversion.prototype.normalize = function normalize(value, startValue, endValue) {
	    return (value - startValue) / (endValue - startValue);
	  };

	  BouncyConversion.prototype.projectNormal = function projectNormal(n, start, end) {
	    return start + n * (end - start);
	  };

	  BouncyConversion.prototype.linearInterpolation = function linearInterpolation(t, start, end) {
	    return t * end + (1.0 - t) * start;
	  };

	  BouncyConversion.prototype.quadraticOutInterpolation = function quadraticOutInterpolation(t, start, end) {
	    return this.linearInterpolation(2 * t - t * t, start, end);
	  };

	  BouncyConversion.prototype.b3Friction1 = function b3Friction1(x) {
	    return 0.0007 * Math.pow(x, 3) - 0.031 * Math.pow(x, 2) + 0.64 * x + 1.28;
	  };

	  BouncyConversion.prototype.b3Friction2 = function b3Friction2(x) {
	    return 0.000044 * Math.pow(x, 3) - 0.006 * Math.pow(x, 2) + 0.36 * x + 2;
	  };

	  BouncyConversion.prototype.b3Friction3 = function b3Friction3(x) {
	    return 0.00000045 * Math.pow(x, 3) - 0.000332 * Math.pow(x, 2) + 0.1078 * x + 5.84;
	  };

	  BouncyConversion.prototype.b3Nobounce = function b3Nobounce(tension) {
	    var friction = 0;
	    if (tension <= 18) {
	      friction = this.b3Friction1(tension);
	    } else if (tension > 18 && tension <= 44) {
	      friction = this.b3Friction2(tension);
	    } else {
	      friction = this.b3Friction3(tension);
	    }
	    return friction;
	  };

	  return BouncyConversion;
	}();

	/**
	 * Maintains a set of tension and friction constants
	 * for a Spring. You can use fromOrigamiTensionAndFriction to convert
	 * values from the [Origami](http://facebook.github.io/origami/)
	 * design tool directly to Rebound spring constants.
	 * @public
	 */

	var SpringConfig = function () {

	  /**
	   * Convert an origami Spring tension and friction to Rebound spring
	   * constants. If you are prototyping a design with Origami, this
	   * makes it easy to make your springs behave exactly the same in
	   * Rebound.
	   * @public
	   */
	  SpringConfig.fromOrigamiTensionAndFriction = function fromOrigamiTensionAndFriction(tension, friction) {
	    return new SpringConfig(tensionFromOrigamiValue(tension), frictionFromOrigamiValue(friction));
	  };

	  /**
	   * Convert an origami PopAnimation Spring bounciness and speed to Rebound
	   * spring constants. If you are using PopAnimation patches in Origami, this
	   * utility will provide springs that match your prototype.
	   * @public
	   */


	  SpringConfig.fromBouncinessAndSpeed = function fromBouncinessAndSpeed(bounciness, speed) {
	    var bouncyConversion = new BouncyConversion(bounciness, speed);
	    return SpringConfig.fromOrigamiTensionAndFriction(bouncyConversion.bouncyTension, bouncyConversion.bouncyFriction);
	  };

	  /**
	   * Create a SpringConfig with no tension or a coasting spring with some
	   * amount of Friction so that it does not coast infininitely.
	   * @public
	   */


	  SpringConfig.coastingConfigWithOrigamiFriction = function coastingConfigWithOrigamiFriction(friction) {
	    return new SpringConfig(0, frictionFromOrigamiValue(friction));
	  };

	  function SpringConfig(tension, friction) {
	    classCallCheck(this, SpringConfig);

	    this.tension = tension;
	    this.friction = friction;
	  }

	  return SpringConfig;
	}();

	SpringConfig.DEFAULT_ORIGAMI_SPRING_CONFIG = SpringConfig.fromOrigamiTensionAndFriction(40, 7);

	/**
	 * Consists of a position and velocity. A Spring uses
	 * this internally to keep track of its current and prior position and
	 * velocity values.
	 */
	var PhysicsState = function PhysicsState() {
	  classCallCheck(this, PhysicsState);
	  this.position = 0;
	  this.velocity = 0;
	};

	/**
	 * Provides a model of a classical spring acting to
	 * resolve a body to equilibrium. Springs have configurable
	 * tension which is a force multipler on the displacement of the
	 * spring from its rest point or `endValue` as defined by [Hooke's
	 * law](http://en.wikipedia.org/wiki/Hooke's_law). Springs also have
	 * configurable friction, which ensures that they do not oscillate
	 * infinitely. When a Spring is displaced by updating it's resting
	 * or `currentValue`, the SpringSystems that contain that Spring
	 * will automatically start looping to solve for equilibrium. As each
	 * timestep passes, `SpringListener` objects attached to the Spring
	 * will be notified of the updates providing a way to drive an
	 * animation off of the spring's resolution curve.
	 * @public
	 */

	var Spring = function () {
	  function Spring(springSystem) {
	    classCallCheck(this, Spring);
	    this.listeners = [];
	    this._startValue = 0;
	    this._currentState = new PhysicsState();
	    this._displacementFromRestThreshold = 0.001;
	    this._endValue = 0;
	    this._overshootClampingEnabled = false;
	    this._previousState = new PhysicsState();
	    this._restSpeedThreshold = 0.001;
	    this._tempState = new PhysicsState();
	    this._timeAccumulator = 0;
	    this._wasAtRest = true;

	    this._id = 's' + Spring._ID++;
	    this._springSystem = springSystem;
	  }

	  /**
	   * Remove a Spring from simulation and clear its listeners.
	   * @public
	   */


	  Spring.prototype.destroy = function destroy() {
	    this.listeners = [];
	    this._springSystem.deregisterSpring(this);
	  };

	  /**
	   * Get the id of the spring, which can be used to retrieve it from
	   * the SpringSystems it participates in later.
	   * @public
	   */


	  Spring.prototype.getId = function getId() {
	    return this._id;
	  };

	  /**
	   * Set the configuration values for this Spring. A SpringConfig
	   * contains the tension and friction values used to solve for the
	   * equilibrium of the Spring in the physics loop.
	   * @public
	   */


	  Spring.prototype.setSpringConfig = function setSpringConfig(springConfig) {
	    this._springConfig = springConfig;
	    return this;
	  };

	  /**
	   * Retrieve the SpringConfig used by this Spring.
	   * @public
	   */


	  Spring.prototype.getSpringConfig = function getSpringConfig() {
	    return this._springConfig;
	  };

	  /**
	   * Set the current position of this Spring. Listeners will be updated
	   * with this value immediately. If the rest or `endValue` is not
	   * updated to match this value, then the spring will be dispalced and
	   * the SpringSystem will start to loop to restore the spring to the
	   * `endValue`.
	   *
	   * A common pattern is to move a Spring around without animation by
	   * calling.
	   *
	   * ```
	   * spring.setCurrentValue(n).setAtRest();
	   * ```
	   *
	   * This moves the Spring to a new position `n`, sets the endValue
	   * to `n`, and removes any velocity from the `Spring`. By doing
	   * this you can allow the `SpringListener` to manage the position
	   * of UI elements attached to the spring even when moving without
	   * animation. For example, when dragging an element you can
	   * update the position of an attached view through a spring
	   * by calling `spring.setCurrentValue(x)`. When
	   * the gesture ends you can update the Springs
	   * velocity and endValue
	   * `spring.setVelocity(gestureEndVelocity).setEndValue(flingTarget)`
	   * to cause it to naturally animate the UI element to the resting
	   * position taking into account existing velocity. The codepaths for
	   * synchronous movement and spring driven animation can
	   * be unified using this technique.
	   * @public
	   */


	  Spring.prototype.setCurrentValue = function setCurrentValue(currentValue, skipSetAtRest) {
	    this._startValue = currentValue;
	    this._currentState.position = currentValue;
	    if (!skipSetAtRest) {
	      this.setAtRest();
	    }
	    this.notifyPositionUpdated(false, false);
	    return this;
	  };

	  /**
	   * Get the position that the most recent animation started at. This
	   * can be useful for determining the number off oscillations that
	   * have occurred.
	   * @public
	   */


	  Spring.prototype.getStartValue = function getStartValue() {
	    return this._startValue;
	  };

	  /**
	   * Retrieve the current value of the Spring.
	   * @public
	   */


	  Spring.prototype.getCurrentValue = function getCurrentValue() {
	    return this._currentState.position;
	  };

	  /**
	   * Get the absolute distance of the Spring from its resting endValue
	   * position.
	   * @public
	   */


	  Spring.prototype.getCurrentDisplacementDistance = function getCurrentDisplacementDistance() {
	    return this.getDisplacementDistanceForState(this._currentState);
	  };

	  /**
	   * Get the absolute distance of the Spring from a given state value
	   */


	  Spring.prototype.getDisplacementDistanceForState = function getDisplacementDistanceForState(state) {
	    return Math.abs(this._endValue - state.position);
	  };

	  /**
	   * Set the endValue or resting position of the spring. If this
	   * value is different than the current value, the SpringSystem will
	   * be notified and will begin running its solver loop to resolve
	   * the Spring to equilibrium. Any listeners that are registered
	   * for onSpringEndStateChange will also be notified of this update
	   * immediately.
	   * @public
	   */


	  Spring.prototype.setEndValue = function setEndValue(endValue) {
	    if (this._endValue === endValue && this.isAtRest()) {
	      return this;
	    }
	    this._startValue = this.getCurrentValue();
	    this._endValue = endValue;
	    this._springSystem.activateSpring(this.getId());
	    for (var i = 0, len = this.listeners.length; i < len; i++) {
	      var listener = this.listeners[i];
	      var onChange = listener.onSpringEndStateChange;
	      onChange && onChange(this);
	    }
	    return this;
	  };

	  /**
	   * Retrieve the endValue or resting position of this spring.
	   * @public
	   */


	  Spring.prototype.getEndValue = function getEndValue() {
	    return this._endValue;
	  };

	  /**
	   * Set the current velocity of the Spring, in pixels per second. As
	   * previously mentioned, this can be useful when you are performing
	   * a direct manipulation gesture. When a UI element is released you
	   * may call setVelocity on its animation Spring so that the Spring
	   * continues with the same velocity as the gesture ended with. The
	   * friction, tension, and displacement of the Spring will then
	   * govern its motion to return to rest on a natural feeling curve.
	   * @public
	   */


	  Spring.prototype.setVelocity = function setVelocity(velocity) {
	    if (velocity === this._currentState.velocity) {
	      return this;
	    }
	    this._currentState.velocity = velocity;
	    this._springSystem.activateSpring(this.getId());
	    return this;
	  };

	  /**
	   * Get the current velocity of the Spring, in pixels per second.
	   * @public
	   */


	  Spring.prototype.getVelocity = function getVelocity() {
	    return this._currentState.velocity;
	  };

	  /**
	   * Set a threshold value for the movement speed of the Spring below
	   * which it will be considered to be not moving or resting.
	   * @public
	   */


	  Spring.prototype.setRestSpeedThreshold = function setRestSpeedThreshold(restSpeedThreshold) {
	    this._restSpeedThreshold = restSpeedThreshold;
	    return this;
	  };

	  /**
	   * Retrieve the rest speed threshold for this Spring.
	   * @public
	   */


	  Spring.prototype.getRestSpeedThreshold = function getRestSpeedThreshold() {
	    return this._restSpeedThreshold;
	  };

	  /**
	   * Set a threshold value for displacement below which the Spring
	   * will be considered to be not displaced i.e. at its resting
	   * `endValue`.
	   * @public
	   */


	  Spring.prototype.setRestDisplacementThreshold = function setRestDisplacementThreshold(displacementFromRestThreshold) {
	    this._displacementFromRestThreshold = displacementFromRestThreshold;
	  };

	  /**
	   * Retrieve the rest displacement threshold for this spring.
	   * @public
	   */


	  Spring.prototype.getRestDisplacementThreshold = function getRestDisplacementThreshold() {
	    return this._displacementFromRestThreshold;
	  };

	  /**
	   * Enable overshoot clamping. This means that the Spring will stop
	   * immediately when it reaches its resting position regardless of
	   * any existing momentum it may have. This can be useful for certain
	   * types of animations that should not oscillate such as a scale
	   * down to 0 or alpha fade.
	   * @public
	   */


	  Spring.prototype.setOvershootClampingEnabled = function setOvershootClampingEnabled(enabled) {
	    this._overshootClampingEnabled = enabled;
	    return this;
	  };

	  /**
	   * Check if overshoot clamping is enabled for this spring.
	   * @public
	   */


	  Spring.prototype.isOvershootClampingEnabled = function isOvershootClampingEnabled() {
	    return this._overshootClampingEnabled;
	  };

	  /**
	   * Check if the Spring has gone past its end point by comparing
	   * the direction it was moving in when it started to the current
	   * position and end value.
	   * @public
	   */


	  Spring.prototype.isOvershooting = function isOvershooting() {
	    var start = this._startValue;
	    var end = this._endValue;
	    return this._springConfig.tension > 0 && (start < end && this.getCurrentValue() > end || start > end && this.getCurrentValue() < end);
	  };

	  /**
	   * The main solver method for the Spring. It takes
	   * the current time and delta since the last time step and performs
	   * an RK4 integration to get the new position and velocity state
	   * for the Spring based on the tension, friction, velocity, and
	   * displacement of the Spring.
	   * @public
	   */


	  Spring.prototype.advance = function advance(time, realDeltaTime) {
	    var isAtRest = this.isAtRest();

	    if (isAtRest && this._wasAtRest) {
	      return;
	    }

	    var adjustedDeltaTime = realDeltaTime;
	    if (realDeltaTime > Spring.MAX_DELTA_TIME_SEC) {
	      adjustedDeltaTime = Spring.MAX_DELTA_TIME_SEC;
	    }

	    this._timeAccumulator += adjustedDeltaTime;

	    var tension = this._springConfig.tension;
	    var friction = this._springConfig.friction;
	    var position = this._currentState.position;
	    var velocity = this._currentState.velocity;
	    var tempPosition = this._tempState.position;
	    var tempVelocity = this._tempState.velocity;
	    var aVelocity = void 0;
	    var aAcceleration = void 0;
	    var bVelocity = void 0;
	    var bAcceleration = void 0;
	    var cVelocity = void 0;
	    var cAcceleration = void 0;
	    var dVelocity = void 0;
	    var dAcceleration = void 0;
	    var dxdt = void 0;
	    var dvdt = void 0;

	    while (this._timeAccumulator >= Spring.SOLVER_TIMESTEP_SEC) {
	      this._timeAccumulator -= Spring.SOLVER_TIMESTEP_SEC;

	      if (this._timeAccumulator < Spring.SOLVER_TIMESTEP_SEC) {
	        this._previousState.position = position;
	        this._previousState.velocity = velocity;
	      }

	      aVelocity = velocity;
	      aAcceleration = tension * (this._endValue - tempPosition) - friction * velocity;

	      tempPosition = position + aVelocity * Spring.SOLVER_TIMESTEP_SEC * 0.5;
	      tempVelocity = velocity + aAcceleration * Spring.SOLVER_TIMESTEP_SEC * 0.5;
	      bVelocity = tempVelocity;
	      bAcceleration = tension * (this._endValue - tempPosition) - friction * tempVelocity;

	      tempPosition = position + bVelocity * Spring.SOLVER_TIMESTEP_SEC * 0.5;
	      tempVelocity = velocity + bAcceleration * Spring.SOLVER_TIMESTEP_SEC * 0.5;
	      cVelocity = tempVelocity;
	      cAcceleration = tension * (this._endValue - tempPosition) - friction * tempVelocity;

	      tempPosition = position + cVelocity * Spring.SOLVER_TIMESTEP_SEC;
	      tempVelocity = velocity + cAcceleration * Spring.SOLVER_TIMESTEP_SEC;
	      dVelocity = tempVelocity;
	      dAcceleration = tension * (this._endValue - tempPosition) - friction * tempVelocity;

	      dxdt = 1.0 / 6.0 * (aVelocity + 2.0 * (bVelocity + cVelocity) + dVelocity);
	      dvdt = 1.0 / 6.0 * (aAcceleration + 2.0 * (bAcceleration + cAcceleration) + dAcceleration);

	      position += dxdt * Spring.SOLVER_TIMESTEP_SEC;
	      velocity += dvdt * Spring.SOLVER_TIMESTEP_SEC;
	    }

	    this._tempState.position = tempPosition;
	    this._tempState.velocity = tempVelocity;

	    this._currentState.position = position;
	    this._currentState.velocity = velocity;

	    if (this._timeAccumulator > 0) {
	      this._interpolate(this._timeAccumulator / Spring.SOLVER_TIMESTEP_SEC);
	    }

	    if (this.isAtRest() || this._overshootClampingEnabled && this.isOvershooting()) {
	      if (this._springConfig.tension > 0) {
	        this._startValue = this._endValue;
	        this._currentState.position = this._endValue;
	      } else {
	        this._endValue = this._currentState.position;
	        this._startValue = this._endValue;
	      }
	      this.setVelocity(0);
	      isAtRest = true;
	    }

	    var notifyActivate = false;
	    if (this._wasAtRest) {
	      this._wasAtRest = false;
	      notifyActivate = true;
	    }

	    var notifyAtRest = false;
	    if (isAtRest) {
	      this._wasAtRest = true;
	      notifyAtRest = true;
	    }

	    this.notifyPositionUpdated(notifyActivate, notifyAtRest);
	  };

	  Spring.prototype.notifyPositionUpdated = function notifyPositionUpdated(notifyActivate, notifyAtRest) {
	    for (var i = 0, len = this.listeners.length; i < len; i++) {
	      var listener = this.listeners[i];
	      if (notifyActivate && listener.onSpringActivate) {
	        listener.onSpringActivate(this);
	      }

	      if (listener.onSpringUpdate) {
	        listener.onSpringUpdate(this);
	      }

	      if (notifyAtRest && listener.onSpringAtRest) {
	        listener.onSpringAtRest(this);
	      }
	    }
	  };

	  /**
	   * Check if the SpringSystem should advance. Springs are advanced
	   * a final frame after they reach equilibrium to ensure that the
	   * currentValue is exactly the requested endValue regardless of the
	   * displacement threshold.
	   * @public
	   */


	  Spring.prototype.systemShouldAdvance = function systemShouldAdvance() {
	    return !this.isAtRest() || !this.wasAtRest();
	  };

	  Spring.prototype.wasAtRest = function wasAtRest() {
	    return this._wasAtRest;
	  };

	  /**
	   * Check if the Spring is atRest meaning that it's currentValue and
	   * endValue are the same and that it has no velocity. The previously
	   * described thresholds for speed and displacement define the bounds
	   * of this equivalence check. If the Spring has 0 tension, then it will
	   * be considered at rest whenever its absolute velocity drops below the
	   * restSpeedThreshold.
	   * @public
	   */


	  Spring.prototype.isAtRest = function isAtRest() {
	    return Math.abs(this._currentState.velocity) < this._restSpeedThreshold && (this.getDisplacementDistanceForState(this._currentState) <= this._displacementFromRestThreshold || this._springConfig.tension === 0);
	  };

	  /**
	   * Force the spring to be at rest at its current position. As
	   * described in the documentation for setCurrentValue, this method
	   * makes it easy to do synchronous non-animated updates to ui
	   * elements that are attached to springs via SpringListeners.
	   * @public
	   */


	  Spring.prototype.setAtRest = function setAtRest() {
	    this._endValue = this._currentState.position;
	    this._tempState.position = this._currentState.position;
	    this._currentState.velocity = 0;
	    return this;
	  };

	  Spring.prototype._interpolate = function _interpolate(alpha) {
	    this._currentState.position = this._currentState.position * alpha + this._previousState.position * (1 - alpha);
	    this._currentState.velocity = this._currentState.velocity * alpha + this._previousState.velocity * (1 - alpha);
	  };

	  Spring.prototype.getListeners = function getListeners() {
	    return this.listeners;
	  };

	  Spring.prototype.addListener = function addListener(newListener) {
	    this.listeners.push(newListener);
	    return this;
	  };

	  Spring.prototype.removeListener = function removeListener(listenerToRemove) {
	    removeFirst(this.listeners, listenerToRemove);
	    return this;
	  };

	  Spring.prototype.removeAllListeners = function removeAllListeners() {
	    this.listeners = [];
	    return this;
	  };

	  Spring.prototype.currentValueIsApproximately = function currentValueIsApproximately(value) {
	    return Math.abs(this.getCurrentValue() - value) <= this.getRestDisplacementThreshold();
	  };

	  return Spring;
	}();

	Spring._ID = 0;
	Spring.MAX_DELTA_TIME_SEC = 0.064;
	Spring.SOLVER_TIMESTEP_SEC = 0.001;

	/**
	 * A set of Springs that all run on the same physics
	 * timing loop. To get started with a Rebound animation, first
	 * create a new SpringSystem and then add springs to it.
	 * @public
	 */

	var SpringSystem = function () {
	  function SpringSystem(looper) {
	    classCallCheck(this, SpringSystem);
	    this.listeners = [];
	    this._activeSprings = [];
	    this._idleSpringIndices = [];
	    this._isIdle = true;
	    this._lastTimeMillis = -1;
	    this._springRegistry = {};

	    this.looper = looper || new AnimationLooper();
	    this.looper.springSystem = this;
	  }

	  /**
	   * A SpringSystem is iterated by a looper. The looper is responsible
	   * for executing each frame as the SpringSystem is resolved to idle.
	   * There are three types of Loopers described below AnimationLooper,
	   * SimulationLooper, and SteppingSimulationLooper. AnimationLooper is
	   * the default as it is the most useful for common UI animations.
	   * @public
	   */


	  SpringSystem.prototype.setLooper = function setLooper(looper) {
	    this.looper = looper;
	    looper.springSystem = this;
	  };

	  /**
	   * Add a new spring to this SpringSystem. This Spring will now be solved for
	   * during the physics iteration loop. By default the spring will use the
	   * default Origami spring config with 40 tension and 7 friction, but you can
	   * also provide your own values here.
	   * @public
	   */


	  SpringSystem.prototype.createSpring = function createSpring(tension, friction) {
	    var springConfig = void 0;
	    if (tension === undefined || friction === undefined) {
	      springConfig = SpringConfig.DEFAULT_ORIGAMI_SPRING_CONFIG;
	    } else {
	      springConfig = SpringConfig.fromOrigamiTensionAndFriction(tension, friction);
	    }
	    return this.createSpringWithConfig(springConfig);
	  };

	  /**
	   * Add a spring with a specified bounciness and speed. To replicate Origami
	   * compositions based on PopAnimation patches, use this factory method to
	   * create matching springs.
	   * @public
	   */


	  SpringSystem.prototype.createSpringWithBouncinessAndSpeed = function createSpringWithBouncinessAndSpeed(bounciness, speed) {
	    var springConfig = void 0;
	    if (bounciness === undefined || speed === undefined) {
	      springConfig = SpringConfig.DEFAULT_ORIGAMI_SPRING_CONFIG;
	    } else {
	      springConfig = SpringConfig.fromBouncinessAndSpeed(bounciness, speed);
	    }
	    return this.createSpringWithConfig(springConfig);
	  };

	  /**
	   * Add a spring with the provided SpringConfig.
	   * @public
	   */


	  SpringSystem.prototype.createSpringWithConfig = function createSpringWithConfig(springConfig) {
	    var spring = new Spring(this);
	    this.registerSpring(spring);
	    spring.setSpringConfig(springConfig);
	    return spring;
	  };

	  /**
	   * Check if a SpringSystem is idle or active. If all of the Springs in the
	   * SpringSystem are at rest, i.e. the physics forces have reached equilibrium,
	   * then this method will return true.
	   * @public
	   */


	  SpringSystem.prototype.getIsIdle = function getIsIdle() {
	    return this._isIdle;
	  };

	  /**
	   * Retrieve a specific Spring from the SpringSystem by id. This
	   * can be useful for inspecting the state of a spring before
	   * or after an integration loop in the SpringSystem executes.
	   * @public
	   */


	  SpringSystem.prototype.getSpringById = function getSpringById(id) {
	    return this._springRegistry[id];
	  };

	  /**
	   * Get a listing of all the springs registered with this
	   * SpringSystem.
	   * @public
	   */


	  SpringSystem.prototype.getAllSprings = function getAllSprings() {
	    var vals = [];
	    for (var _id in this._springRegistry) {
	      if (this._springRegistry.hasOwnProperty(_id)) {
	        vals.push(this._springRegistry[_id]);
	      }
	    }
	    return vals;
	  };

	  /**
	   * Manually add a spring to this system. This is called automatically
	   * if a Spring is created with SpringSystem#createSpring.
	   *
	   * This method sets the spring up in the registry so that it can be solved
	   * in the solver loop.
	   * @public
	   */


	  SpringSystem.prototype.registerSpring = function registerSpring(spring) {
	    this._springRegistry[spring.getId()] = spring;
	  };

	  /**
	   * Deregister a spring with this SpringSystem. The SpringSystem will
	   * no longer consider this Spring during its integration loop once
	   * this is called. This is normally done automatically for you when
	   * you call Spring#destroy.
	   * @public
	   */


	  SpringSystem.prototype.deregisterSpring = function deregisterSpring(spring) {
	    removeFirst(this._activeSprings, spring);
	    delete this._springRegistry[spring.getId()];
	  };

	  SpringSystem.prototype.advance = function advance(time, deltaTime) {
	    while (this._idleSpringIndices.length > 0) {
	      this._idleSpringIndices.pop();
	    }
	    for (var i = 0, len = this._activeSprings.length; i < len; i++) {
	      var spring = this._activeSprings[i];
	      if (spring.systemShouldAdvance()) {
	        spring.advance(time / 1000.0, deltaTime / 1000.0);
	      } else {
	        this._idleSpringIndices.push(this._activeSprings.indexOf(spring));
	      }
	    }
	    while (this._idleSpringIndices.length > 0) {
	      var idx = this._idleSpringIndices.pop();
	      idx >= 0 && this._activeSprings.splice(idx, 1);
	    }
	  };

	  /**
	   * This is the main solver loop called to move the simulation
	   * forward through time. Before each pass in the solver loop
	   * onBeforeIntegrate is called on an any listeners that have
	   * registered themeselves with the SpringSystem. This gives you
	   * an opportunity to apply any constraints or adjustments to
	   * the springs that should be enforced before each iteration
	   * loop. Next the advance method is called to move each Spring in
	   * the systemShouldAdvance forward to the current time. After the
	   * integration step runs in advance, onAfterIntegrate is called
	   * on any listeners that have registered themselves with the
	   * SpringSystem. This gives you an opportunity to run any post
	   * integration constraints or adjustments on the Springs in the
	   * SpringSystem.
	   * @public
	   */


	  SpringSystem.prototype.loop = function loop(currentTimeMillis) {
	    var listener = void 0;
	    if (this._lastTimeMillis === -1) {
	      this._lastTimeMillis = currentTimeMillis - 1;
	    }
	    var ellapsedMillis = currentTimeMillis - this._lastTimeMillis;
	    this._lastTimeMillis = currentTimeMillis;

	    var i = 0;
	    var len = this.listeners.length;
	    for (i = 0; i < len; i++) {
	      listener = this.listeners[i];
	      listener.onBeforeIntegrate && listener.onBeforeIntegrate(this);
	    }

	    this.advance(currentTimeMillis, ellapsedMillis);
	    if (this._activeSprings.length === 0) {
	      this._isIdle = true;
	      this._lastTimeMillis = -1;
	    }

	    for (i = 0; i < len; i++) {
	      listener = this.listeners[i];
	      listener.onAfterIntegrate && listener.onAfterIntegrate(this);
	    }

	    if (!this._isIdle) {
	      this.looper.run();
	    }
	  };

	  /**
	   * Used to notify the SpringSystem that a Spring has become displaced.
	   * The system responds by starting its solver loop up if it is currently idle.
	   */


	  SpringSystem.prototype.activateSpring = function activateSpring(springId) {
	    var spring = this._springRegistry[springId];
	    if (this._activeSprings.indexOf(spring) === -1) {
	      this._activeSprings.push(spring);
	    }
	    if (this.getIsIdle()) {
	      this._isIdle = false;
	      this.looper.run();
	    }
	  };

	  /**
	   * Add a listener to the SpringSystem to receive before/after integration
	   * notifications allowing Springs to be constrained or adjusted.
	   * @public
	   */


	  SpringSystem.prototype.addListener = function addListener(listener) {
	    this.listeners.push(listener);
	  };

	  /**
	   * Remove a previously added listener on the SpringSystem.
	   * @public
	   */


	  SpringSystem.prototype.removeListener = function removeListener(listener) {
	    removeFirst(this.listeners, listener);
	  };

	  /**
	   * Remove all previously added listeners on the SpringSystem.
	   * @public
	   */


	  SpringSystem.prototype.removeAllListeners = function removeAllListeners() {
	    this.listeners = [];
	  };

	  return SpringSystem;
	}();

	var index = _extends({}, Loopers, {
	  OrigamiValueConverter: OrigamiValueConverter,
	  MathUtil: MathUtil,
	  Spring: Spring,
	  SpringConfig: SpringConfig,
	  SpringSystem: SpringSystem,
	  util: _extends({}, util, MathUtil)
	});

	return index;

	})));
	});

	class Particle {
	  // constructor(ctx, sides, canvasWidth, canvasHeight) {
	  constructor(ctx, config, springSystem) {
	    this.ctx = ctx;
	    this.config = config;
	    this.sides = this.getNumberInRange(config.particles.sides);
	    this.sidesSeeds = Array.from(Array(this.sides)).map((_, i) => Math.random()); // this.size = this.getNumberInRange(config.particles.size);
	    // this.life = 1000;  // TODO

	    this.color = Math.floor(Math.random() * config.particles.fill.length); // select initial color

	    this.springPosition = 0;
	    this.position = {
	      x: 0,
	      y: 0
	    };
	    this.attractTo = {
	      x: 0,
	      y: 0,
	      center: {
	        x: 0,
	        y: 0
	      }
	    };
	    this.attractConfig = {
	      chance: 1,
	      direction: 1,
	      force: 1,
	      grow: 1,
	      radius: 1,
	      size: null,
	      speed: 1,
	      type: ""
	    };
	    this.resetFlip();
	    this.seedX = Math.random();
	    this.seedY = Math.random(); // this.canvasWidth = 0;
	    // this.canvasHeight = 0;
	    // initialise spring

	    this.spring = springSystem.createSpring(config.spring.tension + this.seedX * config.spring.randomTension, config.spring.friction + this.seedY * config.spring.randomFriction); // this.onSpringAtRest = this.onSpringAtRest.bind(this);

	    this.onSpringUpdate = this.onSpringUpdate.bind(this);
	    this.spring.addListener({
	      onSpringUpdate: this.onSpringUpdate // onSpringAtRest: this.onSpringAtRest

	    });
	  }

	  set(config) {
	    this.config = config;
	    this.resetFlip();
	  }

	  resetFlip() {
	    this.flip = {
	      x: 1,
	      y: 1
	    };
	  }

	  getNumberInRange(range, seed) {
	    seed = seed || Math.random();
	    const {
	      min,
	      max
	    } = range;
	    return Math.round(seed * (max - min)) + min;
	  }

	  destroy() {
	    if (this.spring) this.spring.destroy();
	  }
	  /**
	   * Spring entered resting poition
	   */
	  // onSpringAtRest(spring) {
	  //   if (this.config.debug) console.log("onSpringAtRest");
	  //   // Activate re-chaos flag after some time
	  //   // if (this.onRestTimeout) clearTimeout(this.onRestTimeout);
	  //   // this.onRestTimeout = setTimeout(onExtendedRest, this.config.spring.extendedRestDelay * 1000); // when would a user normally scroll "again", while it should "feel" the same scroll?
	  // }

	  /**
	   * Spring is in extended rest  (long time)
	   */


	  onExtendedRest() {
	    if (this.config.debug) console.log("onExtendedRest"); // if (this.spring.isAtRest()) this.shouldReChaos = true;
	  }
	  /**
	   * Spring in action
	   */


	  onSpringUpdate(spring) {
	    this.springPosition = spring.getCurrentValue(); // console.log(val);
	    // this.position.y = this.position.y * val;
	    // const path = calcPath(this.srcPath, this.dstPath, val);
	    // if (this.paths.length >= this.config.path.paths) this.paths.shift();
	    // this.paths.push(path);
	    // this.resetCanvas();
	    // this.drawBackground();
	    // this.drawPaths();
	  } // attract(point, center, endval = 1, grow, mode) {


	  attract(point, center, config) {
	    this.attractTo = { ...point,
	      center
	    };
	    this.attractConfig = config;
	    this.spring.setEndValue(config.force);
	    this.isAttracted = true;
	  }

	  unattract() {
	    if (!this.isAttracted) return;
	    this.spring.setEndValue(0);
	    this.isAttracted = false;
	  } // pullSpring(pos) {
	  //   if (typeof pos === 'undefined') pos = 1;
	  //   const val = this.spring.getCurrentValue();
	  //   console.log(val, pos, val === pos);
	  //   if (val === pos) pos = Math.abs(val-pos);
	  //   this.spring.setEndValue(pos);
	  // }

	  /*
	    center(arr) {
	      const x = arr.map (xy => xy[0]);
	      const y = arr.map (xy => xy[1]);
	      const cx = (Math.min (...x) + Math.max (...x)) / 2;
	      const cy = (Math.min (...y) + Math.max (...y)) / 2;
	      return [cx, cy];
	    }
	  */


	  attractPosition() {
	    let {
	      x,
	      y
	    } = this.attractTo;

	    if (this.isAttracted || !this.spring.isAtRest()) {
	      const {
	        type,
	        speed,
	        direction,
	        radius
	      } = this.attractConfig; // TODO: these only needed on some modes
	      // const { speed, direction } = this.config.particles.attract.rotate;  // TODO: get from attractConfig

	      const angle = this.getAngle(direction, this.seedX * speed + speed);
	      const cos = Math.cos(angle);
	      const sin = Math.sin(angle);
	      const {
	        x: cx,
	        y: cy
	      } = this.attractTo.center;
	      const rx = (x - cx) * radius;
	      const ry = (y - cy) * radius; // console.log(cx, cy);

	      switch (type) {
	        case "":
	        case "static":
	          // (nothing)
	          break;

	        case "drone":
	          // x = cos * (rx) - sin * (ry) + cx;
	          // y = sin * (rx) + cos * (ry) + cy;
	          // x = cx + cos * (rx) + sin * (ry);
	          // y = cy + sin * (ry);// + cos * (ry);
	          x = cx + cos * Math.abs(rx) - sin * ry;
	          y = cy + sin * Math.abs(ry) + cos * ry;
	          break;

	        case "horz":
	          x = cos * rx + cx;
	          break;

	        case "vert":
	          y = sin * ry + cy;
	          break;

	        case "orbit":
	          x = cx + cos * Math.abs(rx) - sin * Math.abs(ry);
	          y = cy + sin * Math.abs(rx) + cos * Math.abs(ry);
	          break;

	        case "bee":
	          x = cx + Math.abs(rx) / 2 * cos * sin;
	          y = cy + Math.abs(ry) * cos;
	          break;

	        case "swing":
	          x = cx + sin * rx;
	          y = cy + sin * ry;
	          break;

	        default:
	          //
	          throw new Error("invalid type: " + type);
	      }
	    }

	    return {
	      x,
	      y
	    };
	  }

	  modulatePosition(pos, mode) {
	    // let pos = {x: 0, y: 0};
	    const {
	      type,
	      speed,
	      boundery
	    } = mode;

	    switch (type) {
	      case "wind-from-right":
	        pos.x = pos.x - (this.seedX * speed + speed) * this.flip.x; // pos.y = pos.y + (this.seedY * speed) * this.flip.y;// * Math.floor(Math.random() * 2) - 1;

	        break;

	      case "wind-from-left":
	        pos.x = pos.x + (this.seedX * speed + speed) * this.flip.x; // pos.y = pos.y + (this.seedY * speed) * this.flip.y;// * Math.floor(Math.random() * 2) - 1;

	        break;

	      case "linear":
	        pos.x = pos.x + Math.cos(Math.PI - Math.PI * this.seedX) * speed * this.flip.x;
	        pos.y = pos.y + Math.cos(Math.PI - Math.PI * this.seedY) * speed * this.flip.y;
	        break;

	      case "rain":
	        const _v = this.seedY * speed + speed;

	        pos.x = pos.x - _v / 2 * this.flip.x;
	        pos.y = pos.y + _v * this.flip.y;
	        break;
	      ///////////////

	      case "wind":
	        pos.x = pos.x - (this.seedX * speed + speed) * this.flip.x;
	        pos.y = pos.y + this.seedY * speed * this.flip.y; // * Math.floor(Math.random() * 2) - 1;

	        break;

	      case "party":
	        pos.x = pos.x + this.seedX * speed * this.flip.x;
	        pos.y = pos.y - this.seedY * speed * this.flip.y; //Math.floor(Math.random() * 2) - 1;

	        break;

	      case "space":
	        // pos.x -= speed * Math.floor(Math.random() * 2) - 1;
	        // pos.y += speed * Math.floor(Math.random() * 2) - 1;
	        break;

	      default:
	        //
	        throw new Error("invalid type: " + type);
	    }

	    pos = this.modulateBounderies(pos, boundery); // (optional) performance, less sub-pixel rendering?

	    pos.x = Math.floor(pos.x);
	    pos.y = Math.floor(pos.y);
	    return pos;
	  } // Position bounderies


	  modulateBounderies(pos, mode) {
	    let x = pos.x;
	    let y = pos.y;
	    const size = this.config.particles.sizes.max; // used to enlarge range with

	    const gap = size / 2;
	    let outside = "";
	    if (x > this.canvasWidth + gap) outside = "right";
	    if (x < -gap) outside = "left";
	    if (y > this.canvasHeight + gap) outside = "bottom";
	    if (y < -gap) outside = "top";

	    if (outside) {
	      switch (mode) {
	        case "endless":
	          switch (outside) {
	            case "left":
	              x = this.canvasWidth + gap;
	              break;

	            case "right":
	              x = -gap;
	              break;

	            case "bottom":
	              y = -gap;
	              break;

	            case "top":
	              y = this.canvasHeight + gap;
	              break;
	          }

	          break;

	        case "pong":
	          switch (outside) {
	            case "left":
	              x = -gap;
	              this.flip.x *= -1;
	              break;

	            case "right":
	              x = this.canvasWidth + gap;
	              this.flip.x *= -1;
	              break;

	            case "bottom":
	              y = this.canvasHeight + gap;
	              this.flip.y *= -1;
	              break;

	            case "top":
	              y = -gap;
	              this.flip.y *= -1;
	              break;
	          }

	          break;

	        case "emitter":
	          x = this.canvasWidth / 2;
	          y = this.canvasHeight / 2;
	          break;

	        default:
	          //
	          throw new Error("invalid mode: " + mode);
	      }
	    }

	    return {
	      x,
	      y
	    };
	  }
	  /**
	   * Generate shape
	   * @param  {number} x     center x
	   * @param  {number} y     center y
	   * @return {array}        array of vertices
	   */


	  generateVertices(x, y) {
	    // dynamically resize on attract/spring
	    const {
	      grow,
	      size
	    } = this.attractConfig;
	    let attractSizing = 1;
	    if (!size) attractSizing += this.springPosition * (grow >= 1 ? grow : grow - 1);
	    const {
	      sizes,
	      rotate: {
	        speed,
	        direction
	      }
	    } = this.config.particles;
	    const angle = this.getAngle(direction, speed);
	    return Array.from(Array(this.sides)).map((_, i) => {
	      const slice = 360 / this.sides;
	      const posAngle = (this.sidesSeeds[i] * slice + i * slice) * Math.PI / 180;
	      let length = this.getNumberInRange(sizes, this.sidesSeeds[i]);

	      if (size) {
	        // attract to fixed size?
	        const attractFixedSize = size * this.sidesSeeds[i];
	        length = (1 - this.springPosition) * length + this.springPosition * attractFixedSize; // transition between original and fixed size
	      }

	      const vx = length * Math.cos(posAngle) * attractSizing;
	      const vy = length * Math.sin(posAngle) * attractSizing;
	      return {
	        x: x + vx * Math.cos(angle) - vy * Math.sin(angle),
	        y: y + vx * Math.sin(angle) + vy * Math.cos(angle)
	      };
	    });
	  }

	  getAngle(direction, speed) {
	    const angle = this.ctx.frameCount * speed % 360 * (Number.isInteger(direction) ? direction : this.seedX > 0.5 ? 1 : -1); // if not set, randomly set rotate direction (positive/negative)

	    return angle * Math.PI / 180; // in Radians
	  }

	  getPosition() {
	    // Modulate position
	    if (!this.isAttracted) {
	      this.position = this.modulatePosition(this.position, this.config.particles.mode);
	      if (this.spring.isAtRest()) return this.position; // (optional) performance. we don't need to continue calculating...
	    } // Modulate attraction position


	    let {
	      x,
	      y
	    } = this.attractPosition();
	    x = rebound.MathUtil.mapValueInRange(this.springPosition, 0, 1, this.position.x, x);
	    y = rebound.MathUtil.mapValueInRange(this.springPosition, 0, 1, this.position.y, y);
	    return {
	      x,
	      y
	    };
	  }

	  update() {
	    // if (typeof this.canvasWidth === 'undefined') return;  // not yet initialised?
	    const {
	      x,
	      y
	    } = this.getPosition();
	    this.vertices = this.generateVertices(x, y); // this.life--;
	  }

	  draw() {
	    // if (typeof this.canvasWidth === 'undefined') return;  // not yet initialised?
	    this.ctx.beginPath(); // this.ctx.moveTo (this.vertices[0][0], this.vertices[0][1]);

	    this.vertices.forEach(p => this.ctx.lineTo(p.x, p.y));
	    this.ctx.closePath(); // ** COLOR **

	    const pos = Math.abs(Math.sin(this.ctx.frameCount * this.seedX * Math.PI / 180)); // this.color++; if (this.color >= this.config.particles.fill.length) this.color = 0;  // TODO: HACK

	    const fromColor = this.config.particles.fill[this.color];
	    const toColor = this.config.particles.toColor; //this.config.particles.fill[0];

	    const color = rebound.MathUtil.interpolateColor(pos, fromColor, toColor); // ** FILL **

	    this.ctx.fillStyle = color + this.config.particles.opacity;
	    this.ctx.fill(); // ** STROKE **

	    if (this.config.particles.stroke.color) {
	      this.ctx.strokeStyle = this.config.particles.stroke.color + this.config.particles.opacity;
	      this.ctx.lineWidth = this.config.particles.stroke.width;
	      this.ctx.stroke();
	    }
	  }

	  canvasResized(width, height) {
	    this.canvasWidth = width;
	    this.canvasHeight = height; // spread particles throughout the canvas

	    this.position = {
	      x: Math.floor(this.seedX * width),
	      y: Math.floor(this.seedY * height)
	    };
	  }

	}

	/**
	 * Finds the intersection point between
	 *     * the rectangle
	 *       with parallel sides to the x and y axes
	 *     * the half-line pointing towards (x,y)
	 *       originating from the middle of the rectangle
	 *
	 * Note: the function works given min[XY] <= max[XY],
	 *       even though minY may not be the "top" of the rectangle
	 *       because the coordinate system is flipped.
	 * Note: if the input is inside the rectangle,
	 *       the line segment wouldn't have an intersection with the rectangle,
	 *       but the projected half-line does.
	 * Warning: passing in the middle of the rectangle will return the midpoint itself
	 *          there are infinitely many half-lines projected in all directions,
	 *          so let's just shortcut to midpoint (GIGO).
	 *
	 * @param x:Number x coordinate of point to build the half-line from
	 * @param y:Number y coordinate of point to build the half-line from
	 * @param minX:Number the "left" side of the rectangle
	 * @param minY:Number the "top" side of the rectangle
	 * @param maxX:Number the "right" side of the rectangle
	 * @param maxY:Number the "bottom" side of the rectangle
	 * @param validate:boolean (optional) whether to treat point inside the rect as error
	 * @return an object with x and y members for the intersection
	 * @throws if validate == true and (x,y) is inside the rectangle
	 * @author TWiStErRob
	 * @see <a href="http://stackoverflow.com/a/31254199/253468">source</a>
	 * @see <a href="http://stackoverflow.com/a/18292964/253468">based on</a>
	 */
	var pointOnRect = ((x, y, minX, minY, maxX, maxY, validate) => {
	  //assert minX <= maxX;
	  //assert minY <= maxY;
	  if (validate && minX < x && x < maxX && minY < y && y < maxY) throw "Point " + [x, y] + "cannot be inside " + "the rectangle: " + [minX, minY] + " - " + [maxX, maxY] + ".";
	  var midX = (minX + maxX) / 2;
	  var midY = (minY + maxY) / 2; // if (midX - x == 0) -> m == Â±Inf -> minYx/maxYx == x (because value / Â±Inf = Â±0)

	  var m = (midY - y) / (midX - x);

	  if (x <= midX) {
	    // check "left" side
	    var minXy = m * (minX - x) + y;
	    if (minY <= minXy && minXy <= maxY) return {
	      x: minX,
	      y: minXy
	    };
	  }

	  if (x >= midX) {
	    // check "right" side
	    var maxXy = m * (maxX - x) + y;
	    if (minY <= maxXy && maxXy <= maxY) return {
	      x: maxX,
	      y: maxXy
	    };
	  }

	  if (y <= midY) {
	    // check "top" side
	    var minYx = (minY - y) / m + x;
	    if (minX <= minYx && minYx <= maxX) return {
	      x: minYx,
	      y: minY
	    };
	  }

	  if (y >= midY) {
	    // check "bottom" side
	    var maxYx = (maxY - y) / m + x;
	    if (minX <= maxYx && maxYx <= maxX) return {
	      x: maxYx,
	      y: maxY
	    };
	  } // edge case when finding midpoint intersection: m = 0/0 = NaN


	  if (x === midX && y === midY) return {
	    x: x,
	    y: y
	  }; // Should never happen :) If it does, please tell me!

	  throw "Cannot find intersection for " + [x, y] + " inside rectangle " + [minX, minY] + " - " + [maxX, maxY] + ".";
	});

	class Particles {
	  constructor(ctx, config, width, height) {
	    this.ctx = ctx;
	    this.width = width;
	    this.height = height;
	    const {
	      count,
	      sides
	    } = config.particles;
	    this.count = count;
	    this.sides = sides;
	    this.config = config; // const { tension, friction } = config.spring;
	    // this.tension = tension;
	    // this.friction = friction;

	    this.init();
	  }

	  init() {
	    this.particles = [];
	    this.springSystem = new rebound.SpringSystem();

	    for (let i = 0; i < this.count; i++) {
	      const particle = new Particle(this.ctx, this.config, this.springSystem);
	      this.particles.push(particle);
	    }
	  }

	  destory() {
	    if (this.springSystem) this.springSystem.destory();
	    this.particles.forEach(p => p.destory());
	  }

	  set(config) {
	    if (!config) return; // else if (typeof config === "number") {
	    //   //TODO: destory particles (and springsystem?)
	    //   this.count = config;
	    //   this.init();
	    // }
	    else {
	        this.config = config;
	        this.particles.forEach(p => p.set(config));
	      }
	  }

	  draw() {
	    this.resetCanvas();
	    this.particles.forEach(p => p.draw());
	  }

	  update() {
	    this.particles.forEach(p => p.update()); // this.particles = this.particles.filter(p => !p.isDead());
	    // if (frameCount % this.generationSpeed === 0) {
	    //   this.init();
	    // }
	  }

	  attract(area, config, kinetics, target) {
	    const {
	      chance
	    } = config;
	    const count = this.particles.length;
      const shuffled = [].concat(this.particles).sort(() => Math.random());
      // console.log(kinetics.config.container)
	    shuffled.forEach((p, i) => {
	      if (i / count < chance) {
	        const pos = p.position;
          const point = pointOnRect(pos.x, pos.y, area.left, area.top, area.right, area.bottom, false);
	        const center = {
	          x: area.left + (area.right - area.left) / 2,
	          y: area.top + (area.bottom - area.top) / 2
          };
          // hack to ensure the particles stay within a fixed el on scroll
          point.y = (kinetics.config.container && target.offsetTop > area.top ? point.y - area.top + target.offsetTop : point.y);
	        p.attract(point, center, config);
	      }
	    });
	  }
	  /*
	    pointOnRect(pos, rect) {

	      const w = rect.right - rect.left;
	      const h = rect.bottom - rect.top;
	      // const koter = (w + h) * 2;

	      const p = Math.random();
	      let x = rect.left;
	      let y = rect.top + p * h;
	      if (p>0.5) {
	        x = rect.left + p * w;
	        y = rect.top;
	      }

	      // if (pos < 0.25)https://openprocessing.org/sketch/138410

	      // else if (pos < 0.5)
	      // else if (pos < 0.75)
	      // else

	      // koter * pos

	      // if (x > rect.left + w)

	      // x += pos;
	      // y += pos;
	      // w -= pos  * 2
	      // h -= pos  * 2
	      // if (Math.random() <  w / (w + h)) { // top bottom
	      //   x = Math.random() * w + x;
	      //   y = Math.random() < 0.5 ? y : y + h -1;
	      // } else {
	      //   y = Math.random() * h + y;
	      //   x = Math.random() < 0.5 ? x: x + w -1;
	      // }
	      return {x, y};
	    }
	  */


	  unattract() {
	    this.particles.forEach(p => p.unattract());
	  }

	  bump(x, y) {
	    this.particles.forEach(p => {
	      if (p.isAttracted) {
	        // console.log(p);
	        const factor = 0.1;
	        p.attractTo.x += x * factor;
	        p.attractTo.y += y * factor; // seedX
	        // seedY
	        // size
	      }
	    });
	  } // rotate(angle) {
	  //   this.ctx.rotate(angle * Math.PI / 180);
	  // }


	  scroll(diff) {
	    this.particles.forEach((p, i) => {
	      // fix scrolling + attached chrome bug.  programatically make the y-axis follow scroll diff
	      if (p.isAttracted) p.attractTo.y -= diff; // scrolling effect
	      else p.position.y -= diff * (i % this.config.particles.parallex.layers * this.config.particles.parallex.speed);
	    });
	  }

	  resetCanvas() {
	    this.ctx.clearRect(0, 0, this.width, this.height); // this.ctx.fillStyle =
	    // this.ctx.fillRect(0, 0, this.width, this.height);
	  }

	  canvasResized(width, height) {
	    this.width = width;
	    this.height = height;
	    this.particles.forEach(p => {
	      p.canvasResized(width, height);
	    });
	  }

	}

	var interactionHook = ((kinetics, config = {}, scope = document) => {
	  // if (typeof scope === 'undefined') scope = document;
	  const defaultConfig = {
	    prefix: "kinetics",
	    attraction: {
	      keyword: "attraction"
	    },
	    intersection: {
	      threshold: 0.2,
	      keyword: "mode"
	    }
	  }; // Handle kinetics data attributes instructions, and hook events
	  // =============================================================

	  const {
	    prefix,
	    attraction,
      intersection,
    } = cjs(defaultConfig, config);
    console.log(config);
	  scope.querySelectorAll(`[data-${prefix}-${attraction.keyword}]`).forEach(element => {
	    const props = getProps(element, prefix, attraction.keyword); // const touchOptions = isPassiveSupported() ? { passive: true } : false;
	    // Hook interaction events

	    element.addEventListener("mouseenter", evt => kinetics.attract(evt.target.getBoundingClientRect(), props, evt.target), false); // element.addEventListener("touchstart", evt => kinetics.attract(evt.target.getBoundingClientRect(), props), touchOptions);

	    element.addEventListener("mouseleave", evt => kinetics.unattract(), false); // element.addEventListener("touchend",   evt => kinetics.unattract(), touchOptions);

	    element.addEventListener("mousemove", evt => kinetics.bump(evt.offsetX, evt.offsetY, evt.movementX, evt.movementY), false);
	  }); // ** KINETICS MODE **

	  if ('IntersectionObserver' in window) {
	    // incompatible browsers are out there
	    const onIntersect = entries => {
	      entries.forEach(entry => {
	        if (entry.isIntersecting) {
	          const props = getProps(entry.target, prefix, intersection.keyword); // console.log(props);

	          kinetics.set({
	            particles: {
	              mode: props
	            }
	          });
	        }
	      });
	    }; // Initialize


	    const observer = new IntersectionObserver(onIntersect, {
	      threshold: intersection.threshold
	    });
	    scope.querySelectorAll(`[data-${prefix}-${intersection.keyword}]`).forEach(element => {
	      observer.observe(element);
	    });
	  }
	});
	/**
	 * Parse element's dataset
	 * @param  {DOM Element} element
	 * @param  {String} prefix  data property prefix
	 * @param  {String} keyword data property keyword
	 * @return {Object}         Parsed properties
	 */

	function getProps(element, prefix, keyword) {
	  // -----------------------------------------
	  // Get properties from data attribute
	  let props = {};

	  try {
	    const key = prefix + keyword[0].toUpperCase() + keyword.substr(1); // camelcase

	    props = JSON.parse(element.dataset[key]);
	  } catch (e) {
	    Object.keys(element.dataset).forEach(d => {
	      let _d = d.replace(/[A-Z]/g, m => "-" + m.toLowerCase()); // camelcase back to dash


	      if (_d.startsWith(`${prefix}-`)) {
	        // is our data-prefix?
	        _d = _d.substr(prefix.length + 1); // trim prefix

	        if (_d !== keyword) {
	          // exclude top attribute ("data-kinetics-attraction")
	          let v = element.dataset[d];
	          if (!isNaN(parseFloat(v))) v = parseFloat(v);

	          const k = _d.substr(keyword.length + 1);

	          props[k] = v;
	        }
	      }
	    });
	  }

	  return props;
	}

	// import rebound from 'rebound';

	const Kinetics = function () {

	  const supports = () => {
	    return !!document.querySelector && !!window.requestAnimationFrame;
	  };

	  let _this = null; // Constructor

	  function Kinetics(options = {}) {
	    if (!supports()) return console.warn("KINETICS: FAILED FEATURE TEST"); // ERROR

	    _this = this; // console.log('CONSTRUCTOR', version, options);

	    this.destroy(); // just in case

	    this.originalConfig = cjs(config, options);
      this.config = this.originalConfig;
      console.log(this.config);
	    this.construct();
	  }
	  Kinetics.prototype.VERSION = version;

	  Kinetics.prototype.construct = function () {
	    // Destroy any existing initializations
	    this.paths = []; // init paths array
	    // // ResizeObserver (with ponyfill, if required)
	    // const RO = ('ResizeObserver' in window === false) ? Ponyfill_RO : ResizeObserver;
	    // this.resizeObserver = new RO(onResizeObserved);
	    // Intersection observer is optional, only used for "paused" (performance, stop animation when out of view)

	    if ('IntersectionObserver' in window) this.intersectionObserver = new IntersectionObserver(onIntersectionObserved);
	    this.init(); // this.setupCanvas(0,0);  // HACK: kick it once until resizeObserver is called with correct width/height

	    onResizeObserved(); // this.onScroll = this.onScroll.bind(this);
	    // this.kicker();
	  };
	  /**
	  * Destroy the current initialization.
	  * @public
	  */


	  Kinetics.prototype.destroy = function () {
	    // If plugin isn't already initialized, stop
	    if (!this.config) return;
	    if (this.config.debug) console.log("destroy"); // TODO: FIX THIS !

	    if (this.spring) this.spring.destroy();
	    if (this.canvas) this.canvas.remove(); // UNHOOK EVENTS

	    onscrolling.remove(onScroll); // if (this.resizeObserver) this.resizeObserver.disconnect();
	    // window.removeEventListener('resize', this.onResize);

	    if (this.intersectionObserver) this.intersectionObserver.disconnect();
	    if (this.config.click.shuffle) document.removeEventListener('click', onClick, true);
	    if (this.onRestTimeout) clearTimeout(this.onRestTimeout);
	    this.config = null; // Reset variables
	  };

	  Kinetics.prototype.set = function (options = {}) {
	    // if (typeof options === 'object' && options !== null) {
	    this.config = cjs(this.originalConfig, options); // important: we use originalConfig (and not config). so each call to .set() resets the config back to original.

	    this.particles.set(this.config); // }
	    // else this.particles.set(options);
	  };
	  /**
	   * Initialization method
	   */


	  Kinetics.prototype.init = function () {
	    if (this.config.debug) console.log("init", this.config); // Setup canvas element

	    this.canvas = document.createElement('canvas');

	    if (this.config.canvas.handlePosition) {
	      this.canvas.style.position = "fixed";
	      this.canvas.style.top = 0;
	      this.canvas.style.left = 0; // this.canvas.style.width = "100%";
	      // this.canvas.style.height = "100%";

	      this.canvas.style.zIndex = -1;
      }

      if (this.config.canvas.style) {
        Object.keys(this.config.canvas.style).forEach((prop) => {
          this.canvas.style[prop] = this.config.canvas.style[prop];
        })
      }

	    const elem = this.config.container || document.body;
      const target = this.config.prependTo || elem;

	    // Add canvas to element
      target.prepend(this.canvas);

	    this.ctx = this.canvas.getContext('2d', {
	      alpha: true
	    }); // Select canvas context

	    this.ctx.frameCount = 0; // initSprings();  // start spring system

	    this.particles = new Particles(this.ctx, this.config);
	    this.loop(); // ** HOOK EVENTS **

	    window.addEventListener('resize', onResizeObserved); // this.resizeObserver.observe(elem);  // Element resize observer

	    document.addEventListener('visibilitychange', onVisibilityChanged); // TODO: not this... we do't need anymore. should just test if tab in focus, else pause.  mybe not needed? if runs on GPU?

	    if (this.intersectionObserver) this.intersectionObserver.observe(elem); // Element (viewport) interaction observer
	    // if (this.config.click.shuffle) document.addEventListener('click', onClick, true); // useCapture = true important !!

      if (!this.config.container) {
        onscrolling(onScroll); // Scroll handler
      }
	  };
	  /**
	   * Setup canvas size
	   * @param  {number} width
	   * @param  {number} height
	   */


	  Kinetics.prototype.setupCanvas = function (width, height) {
	    if (this.config.debug) console.log("setupCanvas", width, height);
	    this.width = width;
	    this.height = height;

	    const _dpr = dpr();

	    this.canvas.width = width * _dpr;
	    this.canvas.height = height * _dpr;
	    this.canvas.style.width = width + "px";
	    this.canvas.style.height = height + "px";
	    if (_dpr !== 1) this.ctx.setTransform(_dpr, 0, 0, _dpr, 0, 0); // Reset context
	  }; // ========================================================================

	  /**********/

	  /* SPRING */

	  /**********/
	  // const initSprings = function() {
	  //   const springSystem = new rebound.SpringSystem();
	  //   _this.spring = springSystem.createSpring(_this.config.spring.tension, _this.config.spring.friction);
	  //   _this.spring.addListener({
	  //     onSpringUpdate: onSpringUpdate,
	  //     onSpringAtRest: onSpringAtRest
	  //   });
	  // }
	  // /**
	  //  * Spring entered resting poition
	  //  */
	  // const onSpringAtRest = function(spring) {
	  //   if (_this.config.debug) console.log("onSpringAtRest");
	  //   // Activate re-chaos flag after some time
	  //   if (_this.onRestTimeout) clearTimeout(_this.onRestTimeout);
	  //   _this.onRestTimeout = setTimeout(onExtendedRest, _this.config.spring.extendedRestDelay * 1000); // when would a user normally scroll "again", while it should "feel" the same scroll?
	  // }
	  // /**
	  //  * Spring is in extended rest  (long time)
	  //  */
	  // const onExtendedRest = function() {
	  //   if (_this.config.debug) console.log("onExtendedRest");
	  //   if (_this.spring.isAtRest()) _this.shouldReChaos = true;
	  // }
	  // /**
	  //  * Spring in action
	  //  */
	  // const onSpringUpdate = function(spring) {
	  //   const val = spring.getCurrentValue();
	  //   const path = calcPath(_this.srcPath, _this.dstPath, val);
	  //   if (_this.paths.length >= _this.config.path.paths) _this.paths.shift();
	  //   _this.paths.push(path);
	  //   // _this.resetCanvas();
	  //   // _this.drawBackground();
	  //   // _this.drawPaths();
	  // }
	  // ========================================================================
	  // ========================================================================

	  /**********/

	  /* CANVAS */

	  /**********/
	  // setTimeout(() => moo = true, 1000);


	  Kinetics.prototype.loop = function () {
	    requestAnimationFrame(_this.loop);

	    if (_this.config.unpausable || !_this.paused) {
	      _this.particles.update();

	      _this.particles.draw();

	      _this.ctx.frameCount += 1;
	    }
	  };
	  /**
	   * Clear the canvas
	   */
	  // Kinetics.prototype.resetCanvas = function() {
	  //   this.ctx.clearRect(0, 0, this.width, this.height);
	  // }

	  /**********
	  /* EVENTS *
	  /**********
	    /**
	   * Scroll event
	   * @param  {object} e event
	   */


	  const onScroll = function (e) {
	    // if (_this.config.debug) console.log("scroll");
	    if (_this.paused) return;
	    const diff = e - (_this.prevScroll || 0);
	    _this.prevScroll = e;

	    _this.particles.scroll(diff);
	  };
	  /**
	   * Element resize handler
	   */


	  const onResizeObserved = function (entries) {
	    // console.log("onResizeObserved", entries);
	    // const { width, height } = elementDimentions(entries[0]);
	    // if (!width || !height) console.warn("KINETICS: UNEXPECTED RESPONSE FROM ResizeObserver");
	    const width = (_this.config.container ? _this.config.container.clientWidth : window.innerWidth);
	    const height = (_this.config.container ? _this.config.container.clientHeight : window.innerHeight);
	    if (_this.config.debug) console.log("Resize observed: Width " + width + "px, Height " + height + "px");

	    _this.setupCanvas(width, height);

	    _this.particles.canvasResized(width, height);
	  };
	  /**
	   * Element intersection handler
	   */


	  const onIntersectionObserved = function (entries) {
	    // console.log("onIntersectionObserved");
	    _this.paused = entries[0].intersectionRatio === 0;
	    if (_this.config.debug) console.log("Paused", _this.paused);
	  };

	  const onVisibilityChanged = function () {
	    console.log("onVisibilityChanged");
	    _this.paused = document.visibilityState === 'hidden';
	    if (_this.config.debug) console.log("Paused", _this.paused);
	  };

	  Kinetics.prototype.bump = function (x, y, movementX, movementY) {
	    // if (this.config.debug) console.log("bump", x, y, movementX, movementY);
	    this.particles.bump(movementX, movementY); // this.particles.rotate((movementX - movementY) / 10);
	    // this.ctx.scale(Math.abs(movementX/10), Math.abs(movementY/10));
	    // this.particles.attract(area, force, gravity);
	  };

	  Kinetics.prototype.attract = function (area, props, target) {
	    // if (this.config.debug) console.log("attract", area, force, gravity);
	    if (this.config.debug) console.log("attract", area, props); // this.particles.attract(area, props.chance, props.force, props.grow, props.type);

	    this.particles.attract(area, cjs(config.particles.attract, props), this, target);
	  };

	  Kinetics.prototype.unattract = function () {
	    if (this.config.debug) console.log("unattract");
	    this.particles.unattract();
	  };

	  Kinetics.prototype.interactionHook = function (config, scope) {
	    interactionHook(this, config, scope);
	  };

	  return Kinetics;
	}();

	return Kinetics;

})));
