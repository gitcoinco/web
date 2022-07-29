!function() {
  'use strict'; var e = {log: 'log', debug: 'debug', info: 'info', warn: 'warn', error: 'error'}; var t = function(n) {
    for (var r = [], o = 1; o < arguments.length; o++)
      r[o - 1] = arguments[o]; Object.prototype.hasOwnProperty.call(e, n) || (n = e.log), t[n].apply(t, r);
  };

  function n(e, n) {
    return function() {
      for (var r = [], o = 0; o < arguments.length; o++)
        r[o] = arguments[o]; try {
        return e.apply(void 0, r);
      } catch (e) {
        t.error(n, e);
      }
    };
  }t.debug = console.debug.bind(console), t.log = console.log.bind(console), t.info = console.info.bind(console), t.warn = console.warn.bind(console), t.error = console.error.bind(console); var r; var o = function(e, t, n) {
    if (n || 2 === arguments.length)
      for (var r, o = 0, i = t.length; o < i; o++)
        !r && o in t || (r || (r = Array.prototype.slice.call(t, 0, o)), r[o] = t[o]); return e.concat(r || Array.prototype.slice.call(t));
  }; var i = !1;

  function s(e) {
    i = e;
  } function a(e, t, n) {
    var o = n.value;

    n.value = function() {
      for (var e = [], t = 0; t < arguments.length; t++)
        e[t] = arguments[t]; var n = r ? c(o) : o;

      return n.apply(this, e);
    };
  } function c(e) {
    return function() {
      return u(e, this, arguments);
    };
  } function u(t, n, o) {
    try {
      return t.apply(n, o);
    } catch (t) {
      if (f(e.error, t), r)
        try {
          r(t);
        } catch (t) {
          f(e.error, t);
        }
    }
  } function f(e) {
    for (var n = [], r = 1; r < arguments.length; r++)
      n[r - 1] = arguments[r]; i && t.apply(void 0, o([ e, '[MONITOR]' ], n, !1));
  } var l = 1e3; var d = 6e4;

  function v(e, t, n) {
    var r; var o; var i = !n || void 0 === n.leading || n.leading; var s = !n || void 0 === n.trailing || n.trailing; var a = !1;

    return {throttled: function() {
      for (var n = [], c = 0; c < arguments.length; c++)
        n[c] = arguments[c]; a ? r = n : (i ? e.apply(void 0, n) : r = n, a = !0, o = setTimeout((function() {
        s && r && e.apply(void 0, r), a = !1, r = void 0;
      }), t));
    }, cancel: function() {
      clearTimeout(o), a = !1, r = void 0;
    }};
  } function p(e) {
    for (var t = [], n = 1; n < arguments.length; n++)
      t[n - 1] = arguments[n]; return t.forEach((function(t) {
      for (var n in t)
        Object.prototype.hasOwnProperty.call(t, n) && (e[n] = t[n]);
    })), e;
  } function h(e) {
    return e ? (parseInt(e, 10) ^ 16 * Math.random() >> parseInt(e, 10) / 4).toString(16) : ''.concat(1e7, '-').concat(1e3, '-').concat(4e3, '-').concat(8e3, '-').concat(1e11).replace(/[018]/g, h);
  } function g(e) {
    return 0 !== e && 100 * Math.random() <= e;
  } function b() {} function m(e, t, n) {
    if (null == e)
      return JSON.stringify(e); var r = [ !1, void 0 ];

    y(e) && (r = [ !0, e.toJSON ], delete e.toJSON); var o; var i; var s = [ !1, void 0 ];

    'object' == typeof e && y(o = Object.getPrototypeOf(e)) && (s = [ !0, o.toJSON ], delete o.toJSON); try {
      i = JSON.stringify(e, t, n);
    } catch (e) {
      i = '<error: unable to serialize object>';
    } finally {
      r[0] && (e.toJSON = r[1]), s[0] && (o.toJSON = s[1]);
    } return i;
  } function y(e) {
    return 'object' == typeof e && null !== e && Object.prototype.hasOwnProperty.call(e, 'toJSON');
  } function w(e, t) {
    return -1 !== e.indexOf(t);
  } function k(e) {
    return function(e) {
      return 'number' == typeof e;
    }(e) && e >= 0 && e <= 100;
  } function x(e) {
    return Object.keys(e).map((function(t) {
      return e[t];
    }));
  } function E() {
    if ('object' == typeof globalThis)
      return globalThis; Object.defineProperty(Object.prototype, '_dd_temp_', {get: function() {
      return this;
    }, configurable: !0}); var e = _dd_temp_;

    return delete Object.prototype._dd_temp_, 'object' != typeof e && (e = 'object' == typeof self ? self : 'object' == typeof window ? window : {}), e;
  } function S(e, t, n) {
    void 0 === n && (n = ''); var r = e.charCodeAt(t - 1); var o = r >= 55296 && r <= 56319 ? t + 1 : t;

    return e.length <= o ? e : ''.concat(e.slice(0, o)).concat(n);
  } function L(e, t, n, r) {
    return C(e, [t], n, r);
  } function C(e, t, n, r) {
    var o = void 0 === r ? {} : r; var i = o.once; var s = o.capture; var a = o.passive; var u = c(i ? function(e) {
      l(), n(e);
    } : n); var f = a ? {capture: s, passive: a} : s;

    t.forEach((function(t) {
      return e.addEventListener(t, u, f);
    })); var l = function() {
      return t.forEach((function(t) {
        return e.removeEventListener(t, u, f);
      }));
    };

    return {stop: l};
  } function O(e, t, n) {
    if (void 0 === n && (n = function() {
      if ('undefined' != typeof WeakSet) {
        var e = new WeakSet;

        return {hasAlreadyBeenSeen: function(t) {
          var n = e.has(t);

          return n || e.add(t), n;
        }};
      } var t = [];

      return {hasAlreadyBeenSeen: function(e) {
        var n = t.indexOf(e) >= 0;

        return n || t.push(e), n;
      }};
    }()), void 0 === t)
      return e; if ('object' != typeof t || null === t)
      return t; if (t instanceof Date)
      return new Date(t.getTime()); if (t instanceof RegExp) {
      var r = t.flags || [ t.global ? 'g' : '', t.ignoreCase ? 'i' : '', t.multiline ? 'm' : '', t.sticky ? 'y' : '', t.unicode ? 'u' : '' ].join('');

      return new RegExp(t.source, r);
    } if (!n.hasAlreadyBeenSeen(t)) {
      if (Array.isArray(t)) {
        for (var o = Array.isArray(e) ? e : [], i = 0; i < t.length; ++i)
          o[i] = O(o[i], t[i], n); return o;
      } var s; var a = 'object' == (null === (s = e) ? 'null' : Array.isArray(s) ? 'array' : typeof s) ? e : {};

      for (var c in t)
        Object.prototype.hasOwnProperty.call(t, c) && (a[c] = O(a[c], t[c], n)); return a;
    }
  } function T(e) {
    return O(void 0, e);
  } function R() {
    for (var e, t = [], n = 0; n < arguments.length; n++)
      t[n] = arguments[n]; for (var r = 0, o = t; r < o.length; r++) {
      var i = o[r];

      null != i && (e = O(e, i));
    } return e;
  } function B() {
    var e = {};

    return {get: function() {
      return e;
    }, add: function(t, n) {
      e[t] = n;
    }, remove: function(t) {
      delete e[t];
    }, set: function(t) {
      e = t;
    }};
  } var _; var j = function() {
    function e() {
      this.buffer = [];
    } return e.prototype.add = function(e) {
      this.buffer.push(e) > 500 && this.buffer.splice(0, 1);
    }, e.prototype.drain = function() {
      this.buffer.forEach((function(e) {
        return e();
      })), this.buffer.length = 0;
    }, e;
  }();

  function M() {
    return Date.now();
  } function A() {
    return performance.now();
  } function I() {
    return {relative: A(), timeStamp: M()};
  } function U(e, t) {
    return t - e;
  } function D() {
    return void 0 === _ && (_ = performance.timing.navigationStart), _;
  } function P() {
    var e = E().DatadogEventBridge;

    if (e)
      return {getAllowedWebViewHosts: function() {
        return JSON.parse(e.getAllowedWebViewHosts());
      }, send: function(t, n) {
        e.send(JSON.stringify({eventType: t, event: n}));
      }};
  } function N(e) {
    var t;

    void 0 === e && (e = null === (t = E().location) || void 0 === t ? void 0 : t.hostname); var n = P();

    return !!n && n.getAllowedWebViewHosts().some((function(t) {
      var n = t.replace(/\./g, '\\.');

      return new RegExp('^(.+\\.)*'.concat(n, '$')).test(e);
    }));
  } var q; var F; var H;

  function J(e, t, n, r) {
    var o = new Date;

    o.setTime(o.getTime() + n); var i = 'expires='.concat(o.toUTCString()); var s = r && r.crossSite ? 'none' : 'strict'; var a = r && r.domain ? ';domain='.concat(r.domain) : ''; var c = r && r.secure ? ';secure' : '';

    document.cookie = ''.concat(e, '=').concat(t, ';').concat(i, ';path=/;samesite=').concat(s).concat(a).concat(c);
  } function z(e) {
    return function(e, t) {
      var n = new RegExp('(?:^|;)\\s*'.concat(t, '\\s*=\\s*([^;]+)')).exec(e);

      return n ? n[1] : void 0;
    }(document.cookie, e);
  } function V(e, t) {
    J(e, '', 0, t);
  } function $(e) {
    return !!F && F.has(e);
  } function W(e) {
    return G(e, function(e) {
      if (e.origin)
        return e.origin; var t = e.host.replace(/(:80|:443)$/, '');

      return ''.concat(e.protocol, '//').concat(t);
    }(window.location)).href;
  } function G(e, t) {
    if (function() {
      if (void 0 !== H)
        return H; try {
        var e = new URL('http://test/path');

        return H = 'http://test/path' === e.href;
      } catch (e) {
        H = !1;
      } return H;
    }())
      return void 0 !== t ? new URL(e, t) : new URL(e); if (void 0 === t && !(/:/).test(e))
      throw new Error("Invalid URL: '".concat(e, "'")); var n = document; var r = n.createElement('a');

    if (void 0 !== t) {
      var o = (n = document.implementation.createHTMLDocument('')).createElement('base');

      o.href = t, n.head.appendChild(o), n.body.appendChild(r);
    } return r.href = e, r;
  } var X = 'datadoghq.com'; var K = {logs: 'logs', rum: 'rum', sessionReplay: 'session-replay'}; var Q = {logs: 'logs', rum: 'rum', sessionReplay: 'replay'};

  function Y(e, t, n) {
    var r = e.site; var o = void 0 === r ? X : r; var i = e.clientToken; var s = o.split('.'); var a = s.pop(); var c = ''.concat(K[t], '.browser-intake-').concat(s.join('-'), '.').concat(a); var u = 'https://'.concat(c, '/api/v2/').concat(Q[t]); var f = e.proxyUrl && W(e.proxyUrl);

    return {build: function() {
      var e = 'ddsource=browser' + '&ddtags='.concat(encodeURIComponent(['sdk_version:'.concat('4.11.5')].concat(n).join(','))) + '&dd-api-key='.concat(i) + '&dd-evp-origin-version='.concat(encodeURIComponent('4.11.5')) + '&dd-evp-origin=browser' + '&dd-request-id='.concat(h());

      'rum' === t && (e += '&batch_time='.concat(M())); var r = ''.concat(u, '?').concat(e);

      return f ? ''.concat(f, '?ddforward=').concat(encodeURIComponent(r)) : r;
    }, buildIntakeUrl: function() {
      return f ? ''.concat(f, '?ddforward') : u;
    }, endpointType: t};
  } var Z = /[^a-z0-9_:./-]/;

  function ee(e, n) {
    var r = 200 - e.length - 1;

    (n.length > r || Z.test(n)) && t.warn(''.concat(e, " value doesn't meet tag requirements and will be sanitized")); var o = n.replace(/,/g, '_');

    return ''.concat(e, ':').concat(o);
  } function te(e) {
    var t = function(e) {
      var t = e.env; var n = e.service; var r = e.version; var o = e.datacenter; var i = [];

      return t && i.push(ee('env', t)), n && i.push(ee('service', n)), r && i.push(ee('version', r)), o && i.push(ee('datacenter', o)), i;
    }(e); var n = function(e, t) {
      return {logsEndpointBuilder: Y(e, 'logs', t), rumEndpointBuilder: Y(e, 'rum', t), sessionReplayEndpointBuilder: Y(e, 'sessionReplay', t)};
    }(e, t); var r = x(n).map((function(e) {
      return e.buildIntakeUrl();
    })); var o = function(e, t, n) {
      if (!e.replica)
        return; var r = p({}, e, {site: X, clientToken: e.replica.clientToken}); var o = {logsEndpointBuilder: Y(r, 'logs', n), rumEndpointBuilder: Y(r, 'rum', n)};

      return t.push.apply(t, x(o).map((function(e) {
        return e.buildIntakeUrl();
      }))), p({applicationId: e.replica.applicationId}, o);
    }(e, r, t);

    return p({isIntakeUrl: function(e) {
      return r.some((function(t) {
        return 0 === e.indexOf(t);
      }));
    }, replica: o, site: e.site || X}, n);
  } function ne(e) {
    var r; var o;

    if (e && e.clientToken)
      if (void 0 === e.sampleRate || k(e.sampleRate)) {
        var i;

        if (void 0 === e.telemetrySampleRate || k(e.telemetrySampleRate))
          return i = e.enableExperimentalFeatures, Array.isArray(i) && (F || (F = new Set(i)), i.filter((function(e) {
            return 'string' == typeof e;
          })).forEach((function(e) {
            F.add(e);
          }))), p({beforeSend: e.beforeSend && n(e.beforeSend, 'beforeSend threw an error:'), cookieOptions: re(e), sampleRate: null !== (r = e.sampleRate) && void 0 !== r ? r : 100, telemetrySampleRate: null !== (o = e.telemetrySampleRate) && void 0 !== o ? o : 20, service: e.service, silentMultipleInit: !!e.silentMultipleInit, batchBytesLimit: $('lower-batch-size') ? 10240 : 16384, eventRateLimiterThreshold: 3e3, maxTelemetryEventsPerPage: 15, flushTimeout: 3e4, batchMessagesLimit: 50, messageBytesLimit: 262144}, te(e)); t.error('Telemetry Sample Rate should be a number between 0 and 100');
      } else
        t.error('Sample Rate should be a number between 0 and 100'); else
      t.error('Client Token is not configured, we will not send any data.');
  } function re(e) {
    var t = {};

    return t.secure = function(e) {
      return !!e.useSecureSessionCookie || !!e.useCrossSiteSessionCookie;
    }(e), t.crossSite = !!e.useCrossSiteSessionCookie, e.trackSessionAcrossSubdomains && (t.domain = function() {
      if (void 0 === q) {
        for (var e = 'dd_site_test_'.concat(h()), t = window.location.hostname.split('.'), n = t.pop(); t.length && !z(e);)
          n = ''.concat(t.pop(), '.').concat(n), J(e, 'test', l, {domain: n}); V(e, {domain: n}), q = n;
      } return q;
    }()), t;
  } var oe = '?';

  function ie(e) {
    var t = []; var n = le(e, 'stack');

    return n && n.split('\n').forEach((function(e) {
      var n = function(e) {
        var t = se.exec(e);

        if (!t)
          return; var n = t[2] && 0 === t[2].indexOf('native'); var r = t[2] && 0 === t[2].indexOf('eval'); var o = ae.exec(t[2]);

        r && o && (t[2] = o[1], t[3] = o[2], t[4] = o[3]); return {args: n ? [t[2]] : [], column: t[4] ? +t[4] : void 0, func: t[1] || oe, line: t[3] ? +t[3] : void 0, url: n ? void 0 : t[2]};
      }(e) || function(e) {
        var t = ce.exec(e);

        if (!t)
          return; return {args: [], column: t[4] ? +t[4] : void 0, func: t[1] || oe, line: +t[3], url: t[2]};
      }(e) || function(e) {
        var t = ue.exec(e);

        if (!t)
          return; var n = t[3] && t[3].indexOf(' > eval') > -1; var r = fe.exec(t[3]);

        n && r && (t[3] = r[1], t[4] = r[2], t[5] = void 0); return {args: t[2] ? t[2].split(',') : [], column: t[5] ? +t[5] : void 0, func: t[1] || oe, line: t[4] ? +t[4] : void 0, url: t[3]};
      }(e);

      n && (!n.func && n.line && (n.func = oe), t.push(n));
    })), {message: le(e, 'message'), name: le(e, 'name'), stack: t};
  } var se = /^\s*at (.*?) ?\(((?:file|https?|blob|chrome-extension|native|eval|webpack|<anonymous>|\/).*?)(?::(\d+))?(?::(\d+))?\)?\s*$/i; var ae = /\((\S*)(?::(\d+))(?::(\d+))\)/; var ce = /^\s*at (?:((?:\[object object\])?.+) )?\(?((?:file|ms-appx|https?|webpack|blob):.*?):(\d+)(?::(\d+))?\)?\s*$/i; var ue = /^\s*(.*?)(?:\((.*?)\))?(?:^|@)((?:file|https?|blob|chrome|webpack|resource|capacitor|\[native).*?|[^@]*bundle)(?::(\d+))?(?::(\d+))?\s*$/i; var fe = /(\S+) line (\d+)(?: > eval line \d+)* > eval/i;

  function le(e, t) {
    if ('object' == typeof e && e && t in e) {
      var n = e[t];

      return 'string' == typeof n ? n : void 0;
    }
  } var de = 'agent'; var ve = 'console'; var pe = 'logger'; var he = 'network'; var ge = 'source'; var be = 'report';

  function me(e) {
    var t = ye(e);

    return e.stack.forEach((function(e) {
      var n = '?' === e.func ? '<anonymous>' : e.func; var r = e.args && e.args.length > 0 ? '('.concat(e.args.join(', '), ')') : ''; var o = e.line ? ':'.concat(e.line) : ''; var i = e.line && e.column ? ':'.concat(e.column) : '';

      t += '\n  at '.concat(n).concat(r, ' @ ').concat(e.url).concat(o).concat(i);
    })), t;
  } function ye(e) {
    return ''.concat(e.name || 'Error', ': ').concat(e.message);
  } function we() {
    var e; var t = new Error;

    if (!t.stack)
      try {
        throw t;
      } catch (e) {} return u((function() {
      var n = ie(t);

      n.stack = n.stack.slice(2), e = me(n);
    })), e;
  } var ke = function() {
    function e(e) {
      this.onFirstSubscribe = e, this.observers = [];
    } return e.prototype.subscribe = function(e) {
      var t = this;

      return !this.observers.length && this.onFirstSubscribe && (this.onLastUnsubscribe = this.onFirstSubscribe() || void 0), this.observers.push(e), {unsubscribe: function() {
        t.observers = t.observers.filter((function(t) {
          return e !== t;
        })), !t.observers.length && t.onLastUnsubscribe && t.onLastUnsubscribe();
      }};
    }, e.prototype.notify = function(e) {
      this.observers.forEach((function(t) {
        return t(e);
      }));
    }, e;
  }();

  function xe() {
    for (var e = [], t = 0; t < arguments.length; t++)
      e[t] = arguments[t]; var n = new ke((function() {
      var t = e.map((function(e) {
        return e.subscribe((function(e) {
          return n.notify(e);
        }));
      }));

      return function() {
        return t.forEach((function(e) {
          return e.unsubscribe();
        }));
      };
    }));

    return n;
  } var Ee = {intervention: 'intervention', deprecation: 'deprecation', cspViolation: 'csp_violation'};

  function Se(e) {
    var t; var n = [];

    w(e, Ee.cspViolation) && n.push(t = new ke((function() {
      var e = c((function(e) {
        t.notify(function(e) {
          var t = Ee.cspViolation; var n = "'".concat(e.blockedURI, "' blocked by '").concat(e.effectiveDirective, "' directive");

          return {type: Ee.cspViolation, subtype: e.effectiveDirective, message: ''.concat(t, ': ').concat(n), stack: Le(e.effectiveDirective, ''.concat(n, ' of the policy "').concat(S(e.originalPolicy, 100, '...'), '"'), e.sourceFile, e.lineNumber, e.columnNumber)};
        }(e));
      }));

      return L(document, 'securitypolicyviolation', e).stop;
    }))); var r = e.filter((function(e) {
      return e !== Ee.cspViolation;
    }));

    return r.length && n.push(function(e) {
      var t = new ke((function() {
        if (window.ReportingObserver) {
          var n = c((function(e) {
            return e.forEach((function(e) {
              t.notify(function(e) {
                var t = e.type; var n = e.body;

                return {type: t, subtype: n.id, message: ''.concat(t, ': ').concat(n.message), stack: Le(n.id, n.message, n.sourceFile, n.lineNumber, n.columnNumber)};
              }(e));
            }));
          })); var r = new window.ReportingObserver(n, {types: e, buffered: !0});

          return r.observe(), function() {
            r.disconnect();
          };
        }
      }));

      return t;
    }(r)), xe.apply(void 0, n);
  } function Le(e, t, n, r, o) {
    return n && me({name: e, message: t, stack: [{func: '?', url: n, line: r, column: o}]});
  } function Ce(e, n, r) {
    return void 0 === e ? [] : 'all' === e || Array.isArray(e) && e.every((function(e) {
      return w(n, e);
    })) ? 'all' === e ? n : (o = e, i = new Set, o.forEach((function(e) {
        return i.add(e);
      })), function(e) {
        var t = [];

        return e.forEach((function(e) {
          return t.push(e);
        })), t;
      }(i)) : void t.error(''.concat(r, ' should be "all" or an array with allowed values "').concat(n.join('", "'), '"')); var o; var i;
  } var Oe = function(e, t, n, r) {
    var o; var i = arguments.length; var s = i < 3 ? t : null === r ? r = Object.getOwnPropertyDescriptor(t, n) : r;

    if ('object' == typeof Reflect && 'function' == typeof Reflect.decorate)
      s = Reflect.decorate(e, t, n, r); else
      for (var a = e.length - 1; a >= 0; a--)
        (o = e[a]) && (s = (i < 3 ? o(s) : i > 3 ? o(t, n, s) : o(t, n)) || s); return i > 3 && s && Object.defineProperty(t, n, s), s;
  }; var Te = {debug: 'debug', error: 'error', info: 'info', warn: 'warn'}; var Re = 'console'; var Be = 'http'; var _e = Object.keys(Te); var je = function() {
    function e(e, t, n, r, o) {
      void 0 === n && (n = Be), void 0 === r && (r = Te.debug), void 0 === o && (o = {}), this.handleLogStrategy = e, this.handlerType = n, this.level = r, this.contextManager = B(), this.contextManager.set(p({}, o, t ? {logger: {name: t}} : void 0));
    } return e.prototype.log = function(e, t, n) {
      void 0 === n && (n = Te.info), this.handleLogStrategy({message: e, context: T(t), status: n}, this);
    }, e.prototype.debug = function(e, t) {
      this.log(e, t, Te.debug);
    }, e.prototype.info = function(e, t) {
      this.log(e, t, Te.info);
    }, e.prototype.warn = function(e, t) {
      this.log(e, t, Te.warn);
    }, e.prototype.error = function(e, t) {
      var n = {error: {origin: pe}};

      this.log(e, R(n, t), Te.error);
    }, e.prototype.setContext = function(e) {
      this.contextManager.set(e);
    }, e.prototype.getContext = function() {
      return this.contextManager.get();
    }, e.prototype.addContext = function(e, t) {
      this.contextManager.add(e, t);
    }, e.prototype.removeContext = function(e) {
      this.contextManager.remove(e);
    }, e.prototype.setHandler = function(e) {
      this.handlerType = e;
    }, e.prototype.getHandler = function() {
      return this.handlerType;
    }, e.prototype.setLevel = function(e) {
      this.level = e;
    }, e.prototype.getLevel = function() {
      return this.level;
    }, Oe([a], e.prototype, 'log', null), e;
  }(); var Me; var Ae = [ 'https://www.datadoghq-browser-agent.com', 'https://www.datad0g-browser-agent.com', 'http://localhost', '<anonymous>' ]; var Ie = ['ddog-gov.com']; var Ue = {maxEventsPerPage: 0, sentEventCount: 0, telemetryEnabled: !1};

  function De(e) {
    var t; var n = new ke;

    return Ue.telemetryEnabled = g(e.telemetrySampleRate), Me = function(r) {
      !w(Ie, e.site) && Ue.telemetryEnabled && n.notify(function(e) {
        return R({type: 'telemetry', date: M(), service: 'browser-sdk', version: '4.11.5', source: 'browser', _dd: {format_version: 2}, telemetry: e}, void 0 !== t ? t() : {});
      }(r));
    }, r = Pe, p(Ue, {maxEventsPerPage: e.maxTelemetryEventsPerPage, sentEventCount: 0}), {setContextProvider: function(e) {
      t = e;
    }, observable: n};
  } function Pe(e) {
    Ne(p({status: 'error'}, function(e) {
      if (e instanceof Error) {
        var t = ie(e);

        return {error: {kind: t.name, stack: me(qe(t))}, message: t.message};
      } return {error: {stack: 'Not an instance of error'}, message: 'Uncaught '.concat(m(e))};
    }(e)));
  } function Ne(e) {
    Me && Ue.sentEventCount < Ue.maxEventsPerPage && (Ue.sentEventCount += 1, Me(e));
  } function qe(e) {
    return e.stack = e.stack.filter((function(e) {
      return !e.url || Ae.some((function(t) {
        return n = e.url, r = t, n.slice(0, r.length) === r; var n; var r;
      }));
    })), e;
  } var Fe = /[^\u0000-\u007F]/; var He = function() {
    function e(e, t, n, r, o, i) {
      void 0 === i && (i = b), this.request = e, this.batchMessagesLimit = t, this.batchBytesLimit = n, this.messageBytesLimit = r, this.flushTimeout = o, this.beforeUnloadCallback = i, this.pushOnlyBuffer = [], this.upsertBuffer = {}, this.bufferBytesCount = 0, this.bufferMessagesCount = 0, this.flushOnVisibilityHidden(), this.flushPeriodically();
    } return e.prototype.add = function(e) {
      this.addOrUpdate(e);
    }, e.prototype.upsert = function(e, t) {
      this.addOrUpdate(e, t);
    }, e.prototype.flush = function(e) {
      if (0 !== this.bufferMessagesCount) {
        var t = this.pushOnlyBuffer.concat(x(this.upsertBuffer));

        this.request.send(t.join('\n'), this.bufferBytesCount, e), this.pushOnlyBuffer = [], this.upsertBuffer = {}, this.bufferBytesCount = 0, this.bufferMessagesCount = 0;
      }
    }, e.prototype.computeBytesCount = function(e) {
      return Fe.test(e) ? void 0 !== window.TextEncoder ? (new TextEncoder).encode(e).length : new Blob([e]).size : e.length;
    }, e.prototype.addOrUpdate = function(e, n) {
      var r = this.process(e); var o = r.processedMessage; var i = r.messageBytesCount;

      i >= this.messageBytesLimit ? t.warn('Discarded a message whose size was bigger than the maximum allowed size '.concat(this.messageBytesLimit, 'KB.')) : (this.hasMessageFor(n) && this.remove(n), this.willReachedBytesLimitWith(i) && this.flush('batch_bytes_limit'), this.push(o, i, n), this.isFull() && this.flush('batch_messages_limit'));
    }, e.prototype.process = function(e) {
      var t = m(e);

      return {processedMessage: t, messageBytesCount: this.computeBytesCount(t)};
    }, e.prototype.push = function(e, t, n) {
      this.bufferMessagesCount > 0 && (this.bufferBytesCount += 1), void 0 !== n ? this.upsertBuffer[n] = e : this.pushOnlyBuffer.push(e), this.bufferBytesCount += t, this.bufferMessagesCount += 1;
    }, e.prototype.remove = function(e) {
      var t = this.upsertBuffer[e];

      delete this.upsertBuffer[e]; var n = this.computeBytesCount(t);

      this.bufferBytesCount -= n, this.bufferMessagesCount -= 1, this.bufferMessagesCount > 0 && (this.bufferBytesCount -= 1);
    }, e.prototype.hasMessageFor = function(e) {
      return void 0 !== e && void 0 !== this.upsertBuffer[e];
    }, e.prototype.willReachedBytesLimitWith = function(e) {
      return this.bufferBytesCount + e + 1 >= this.batchBytesLimit;
    }, e.prototype.isFull = function() {
      return this.bufferMessagesCount === this.batchMessagesLimit || this.bufferBytesCount >= this.batchBytesLimit;
    }, e.prototype.flushPeriodically = function() {
      var e = this;

      setTimeout(c((function() {
        e.flush('batch_flush_timeout'), e.flushPeriodically();
      })), this.flushTimeout);
    }, e.prototype.flushOnVisibilityHidden = function() {
      var e = this;

      navigator.sendBeacon && (L(window, 'beforeunload', this.beforeUnloadCallback), L(document, 'visibilitychange', (function() {
        'hidden' === document.visibilityState && e.flush('visibility_hidden');
      })), L(window, 'beforeunload', (function() {
        return e.flush('before_unload');
      })));
    }, e;
  }(); var Je = 'datadog-browser-sdk-failed-send-beacon';

  function ze(t, n, r) {
    if ($('failed-sendbeacon')) {
      var o; var i; var s = {reason: r, endpointType: t, version: '4.11.5', connection: navigator.connection ? navigator.connection.effectiveType : void 0, onLine: navigator.onLine, size: n};

      'before_unload' === r || 'visibility_hidden' === r ? window.localStorage.setItem(''.concat(Je, '-').concat(h()), JSON.stringify(s)) : (f(e.debug, o = 'failed sendBeacon', i = s), Ne(p({message: o, status: 'debug'}, i)));
    }
  } var Ve = function() {
    function e(e, t) {
      this.endpointBuilder = e, this.bytesLimit = t;
    } return e.prototype.send = function(e, t, n) {
      var r = this.endpointBuilder.build();

      if (!!navigator.sendBeacon && t < this.bytesLimit)
        try {
          if (navigator.sendBeacon(r, e))
            return; ze(this.endpointBuilder.endpointType, t, n);
        } catch (e) {
          !function(e) {
            $e || ($e = !0, Pe(e));
          }(e);
        } var o = new XMLHttpRequest;

      o.open('POST', r, !0), o.send(e);
    }, e;
  }(); var $e = !1;

  function We(e, t, n) {
    var r; var o = i(t);

    function i(t) {
      return new He(new Ve(t, e.batchBytesLimit), e.batchMessagesLimit, e.batchBytesLimit, e.messageBytesLimit, e.flushTimeout);
    } return n && (r = i(n)), {add: function(e, t) {
      void 0 === t && (t = !0), o.add(e), r && t && r.add(e);
    }};
  } var Ge = 1 / 0; var Xe = function() {
    function e(e) {
      var t = this;

      this.expireDelay = e, this.entries = [], this.clearOldContextsInterval = setInterval((function() {
        return t.clearOldContexts();
      }), 6e4);
    } return e.prototype.add = function(e, t) {
      var n = this; var r = {context: e, startTime: t, endTime: Ge, remove: function() {
        var e = n.entries.indexOf(r);

        e >= 0 && n.entries.splice(e, 1);
      }, close: function(e) {
        r.endTime = e;
      }};

      return this.entries.unshift(r), r;
    }, e.prototype.find = function(e) {
      void 0 === e && (e = Ge); for (var t = 0, n = this.entries; t < n.length; t++) {
        var r = n[t];

        if (r.startTime <= e) {
          if (e <= r.endTime)
            return r.context; break;
        }
      }
    }, e.prototype.closeActive = function(e) {
      var t = this.entries[0];

      t && t.endTime === Ge && t.close(e);
    }, e.prototype.findAll = function(e) {
      return void 0 === e && (e = Ge), this.entries.filter((function(t) {
        return t.startTime <= e && e <= t.endTime;
      })).map((function(e) {
        return e.context;
      }));
    }, e.prototype.reset = function() {
      this.entries = [];
    }, e.prototype.stop = function() {
      clearInterval(this.clearOldContextsInterval);
    }, e.prototype.clearOldContexts = function() {
      for (var e = A() - this.expireDelay; this.entries.length > 0 && this.entries[this.entries.length - 1].endTime < e;)
        this.entries.pop();
    }, e;
  }(); var Ke; var Qe = 144e5; var Ye = 9e5; var Ze = /^([a-z]+)=([a-z0-9-]+)$/; var et = '&'; var tt = '_dd_s'; var nt = [];

  function rt(e, t) {
    var n;

    if (void 0 === t && (t = 0), Ke || (Ke = e), e === Ke)
      if (t >= 100)
        st(); else {
        var r; var o = ut();

        if (ot()) {
          if (o.lock)
            return void it(e, t); if (r = h(), o.lock = r, ct(o, e.options), (o = ut()).lock !== r)
            return void it(e, t);
        } var i = e.process(o);

        if (ot() && (o = ut()).lock !== r)
          it(e, t); else {
          if (i && at(i, e.options), ot() && (!i || !ft(i))) {
            if ((o = ut()).lock !== r)
              return void it(e, t); delete o.lock, ct(o, e.options), i = o;
          }null === (n = e.after) || void 0 === n || n.call(e, i || o), st();
        }
      } else
      nt.push(e);
  } function ot() {
    return !!window.chrome || (/HeadlessChrome/).test(window.navigator.userAgent);
  } function it(e, t) {
    setTimeout(c((function() {
      rt(e, t + 1);
    })), 10);
  } function st() {
    Ke = void 0; var e = nt.shift();

    e && rt(e);
  } function at(e, t) {
    ft(e) ? function(e) {
      J(tt, '', 0, e);
    }(t) : (e.expire = String(Date.now() + Ye), ct(e, t));
  } function ct(e, t) {
    J(tt, function(e) {
      return (t = e, Object.keys(t).map((function(e) {
        return [ e, t[e] ];
      }))).map((function(e) {
        var t = e[0]; var n = e[1];

        return ''.concat(t, '=').concat(n);
      })).join(et); var t;
    }(e), Ye, t);
  } function ut() {
    var e = z(tt); var t = {};

    return function(e) {
      return void 0 !== e && (-1 !== e.indexOf(et) || Ze.test(e));
    }(e) && e.split(et).forEach((function(e) {
      var n = Ze.exec(e);

      if (null !== n) {
        var r = n[1]; var o = n[2];

        t[r] = o;
      }
    })), t;
  } function ft(e) {
    return t = e, 0 === Object.keys(t).length; var t;
  } function lt(e, t, n) {
    var r = new ke; var o = new ke; var i = setInterval(c((function() {
      rt({options: e, process: function(e) {
        return f(e) ? void 0 : {};
      }, after: a});
    })), 1e3); var s = function() {
      var e = ut();

      if (f(e))
        return e; return {};
    }();

    function a(e) {
      return f(e) || (e = {}), u() && (!function(e) {
        return s.id !== e.id || s[t] !== e[t];
      }(e) ? s = e : (s = {}, o.notify())), e;
    } function u() {
      return void 0 !== s[t];
    } function f(e) {
      return (void 0 === e.created || Date.now() - Number(e.created) < Qe) && (void 0 === e.expire || Date.now() < Number(e.expire));
    } return {expandOrRenewSession: v(c((function() {
      var o;

      rt({options: e, process: function(e) {
        var r = a(e);

        return o = function(e) {
          var r = n(e[t]); var o = r.trackingType; var i = r.isTracked;

          e[t] = o, i && !e.id && (e.id = h(), e.created = String(Date.now())); return i;
        }(r), r;
      }, after: function(e) {
        o && !u() && function(e) {
          s = e, r.notify();
        }(e), s = e;
      }});
    })), 1e3).throttled, expandSession: function() {
      rt({options: e, process: function(e) {
        return u() ? a(e) : void 0;
      }});
    }, getSession: function() {
      return s;
    }, renewObservable: r, expireObservable: o, stop: function() {
      clearInterval(i);
    }};
  } var dt = [];

  function vt(e, t, n) {
    !function(e) {
      var t = z(tt); var n = z('_dd'); var r = z('_dd_r'); var o = z('_dd_l');

      if (!t) {
        var i = {};

        n && (i.id = n), o && (/^[01]$/).test(o) && (i.logs = o), r && (/^[012]$/).test(r) && (i.rum = r), at(i, e);
      }
    }(e); var r = lt(e, t, n);

    dt.push((function() {
      return r.stop();
    })); var o; var i = new Xe(144e5);

    function s() {
      return {id: r.getSession().id, trackingType: r.getSession()[t]};
    } return dt.push((function() {
      return i.stop();
    })), r.renewObservable.subscribe((function() {
      i.add(s(), A());
    })), r.expireObservable.subscribe((function() {
      i.closeActive(A());
    })), r.expandOrRenewSession(), i.add(s(), [ 0, D() ][0]), o = C(window, [ 'click', 'touchstart', 'keydown', 'scroll' ], (function() {
      return r.expandOrRenewSession();
    }), {capture: !0, passive: !0}).stop, dt.push(o), function(e) {
      var t = c((function() {
        'visible' === document.visibilityState && e();
      })); var n = L(document, 'visibilitychange', t).stop;

      dt.push(n); var r = setInterval(t, 6e4);

      dt.push((function() {
        clearInterval(r);
      }));
    }((function() {
      return r.expandSession();
    })), {findActiveSession: function(e) {
      return i.find(e);
    }, renewObservable: r.renewObservable, expireObservable: r.expireObservable};
  } var pt;

  function ht(e) {
    var t = vt(e.cookieOptions, 'logs', (function(t) {
      return function(e, t) {
        var n = function(e) {
          return '0' === e || '1' === e;
        }(t) ? t : gt(e);

        return {trackingType: n, isTracked: '1' === n};
      }(e, t);
    }));

    return {findTrackedSession: function(e) {
      var n = t.findActiveSession(e);

      return n && '1' === n.trackingType ? {id: n.id} : void 0;
    }};
  } function gt(e) {
    return g(e.sampleRate) ? '1' : '0';
  } var bt = ((pt = {})[Te.debug] = 0, pt[Te.info] = 1, pt[Te.warn] = 2, pt[Te.error] = 3, pt);

  function mt(e, t, n) {
    var r = n.getHandler(); var o = Array.isArray(r) ? r : [r];

    return bt[e] >= bt[n.getLevel()] && w(o, t);
  } function yt(e, t, n, r, o) {
    var i = _e.concat(['custom']); var s = {};

    i.forEach((function(e) {
      var r; var o; var i; var a; var c;

      s[e] = (r = e, o = t.eventRateLimiterThreshold, i = function(e) {
        return function(e, t) {
          t.notify(0, {rawLogsEvent: {message: e.message, date: e.startClocks.timeStamp, error: {origin: de}, origin: de, status: Te.error}});
        }(e, n);
      }, a = 0, c = !1, {isLimitReached: function() {
        if (0 === a && setTimeout((function() {
          a = 0;
        }), d), (a += 1) <= o || c)
          return c = !1, !1; if (a === o + 1) {
          c = !0; try {
            i({message: 'Reached max number of '.concat(r, 's by minute: ').concat(o), source: de, startClocks: I()});
          } finally {
            c = !1;
          }
        } return !0;
      }});
    })), n.subscribe(0, (function(i) {
      var a; var c; var u; var f = i.rawLogsEvent; var l = i.messageContext; var d = void 0 === l ? void 0 : l; var v = i.savedCommonContext; var p = void 0 === v ? void 0 : v; var h = i.logger; var g = void 0 === h ? o : h; var b = f.date - D(); var m = e.findTrackedSession(b);

      if (m) {
        var y = p || r(); var w = R({service: t.service, session_id: m.id, view: y.view}, y.context, wt(b), f, g.getContext(), d);

        !mt(f.status, Be, g) || !1 === (null === (a = t.beforeSend) || void 0 === a ? void 0 : a.call(t, w)) || (null === (c = w.error) || void 0 === c ? void 0 : c.origin) !== de && (null !== (u = s[w.status]) && void 0 !== u ? u : s.custom).isLimitReached() || n.notify(1, w);
      }
    }));
  } function wt(e) {
    var t = window.DD_RUM;

    return t && t.getInternalContext ? t.getInternalContext(e) : void 0;
  } var kt; var xt = {};

  function Et(e) {
    var t = e.map((function(e) {
      return xt[e] || (xt[e] = function(e) {
        var t = new ke((function() {
          var n = console[e];

          return console[e] = function() {
            for (var r = [], o = 0; o < arguments.length; o++)
              r[o] = arguments[o]; n.apply(console, r); var i = we();

            u((function() {
              t.notify(St(r, e, i));
            }));
          }, function() {
            console[e] = n;
          };
        }));

        return t;
      }(e)), xt[e];
    }));

    return xe.apply(void 0, t);
  } function St(t, n, r) {
    var o; var i = t.map((function(e) {
      return function(e) {
        if ('string' == typeof e)
          return e; if (e instanceof Error)
          return ye(ie(e)); return m(e, void 0, 2);
      }(e);
    })).join(' ');

    if (n === e.error) {
      var s = function(e, t) {
        for (var n = 0; n < e.length; n += 1) {
          var r = e[n];

          if (t(r, n, e))
            return r;
        }
      }(t, (function(e) {
        return e instanceof Error;
      }));

      o = s ? me(ie(s)) : void 0, i = 'console error: '.concat(i);
    } return {api: n, message: i, stack: o, handlingStack: r};
  } var Lt; var Ct = ((kt = {})[e.log] = Te.info, kt[e.debug] = Te.debug, kt[e.info] = Te.info, kt[e.warn] = Te.warn, kt[e.error] = Te.error, kt); var Ot; var Tt = ((Lt = {})[Ee.cspViolation] = Te.error, Lt[Ee.intervention] = Te.error, Lt[Ee.deprecation] = Te.warn, Lt);

  function Rt(e, t, n) {
    var r = e[t]; var o = n(r); var i = function() {
      return o.apply(this, arguments);
    };

    return e[t] = i, {stop: function() {
      e[t] === i ? e[t] = r : o = r;
    }};
  } function Bt(e, t, n) {
    var r = n.before; var o = n.after;

    return Rt(e, t, (function(e) {
      return function() {
        var t; var n = arguments;

        return r && u(r, this, n), 'function' == typeof e && (t = e.apply(this, n)), o && u(o, this, n), t;
      };
    }));
  } var _t; var jt = new WeakMap;

  function Mt() {
    var e;

    return Ot || (e = new ke((function() {
      var t = Bt(XMLHttpRequest.prototype, 'open', {before: At}).stop; var n = Bt(XMLHttpRequest.prototype, 'send', {before: function() {
        It.call(this, e);
      }}).stop; var r = Bt(XMLHttpRequest.prototype, 'abort', {before: Ut}).stop;

      return function() {
        t(), n(), r();
      };
    })), Ot = e), Ot;
  } function At(e, t) {
    jt.set(this, {state: 'open', method: e, url: W(t.toString())});
  } function It(e) {
    var t = this; var n = jt.get(this);

    if (n) {
      var r = n;

      r.state = 'start', r.startTime = A(), r.startClocks = I(), r.isAborted = !1, r.xhr = this; var o = !1; var i = Bt(this, 'onreadystatechange', {before: function() {
        this.readyState === XMLHttpRequest.DONE && s();
      }}).stop; var s = c((function() {
        if (t.removeEventListener('loadend', s), i(), !o) {
          o = !0; var a = n;

          a.state = 'complete', a.duration = U(r.startClocks.timeStamp, M()), a.status = t.status, e.notify(p({}, a));
        }
      }));

      this.addEventListener('loadend', s), e.notify(r);
    }
  } function Ut() {
    var e = jt.get(this);

    e && (e.isAborted = !0);
  } function Dt() {
    var e;

    return _t || (e = new ke((function() {
      if (window.fetch)
        return Rt(window, 'fetch', (function(t) {
          return function(n, r) {
            var o; var i = u(Pt, null, [ e, n, r ]);

            return i ? (o = t.call(this, i.input, i.init), u(Nt, null, [ e, o, i ])) : o = t.call(this, n, r), o;
          };
        })).stop;
    })), _t = e), _t;
  } function Pt(e, t, n) {
    var r = n && n.method || 'object' == typeof t && t.method || 'GET'; var o = W('object' == typeof t && t.url || t); var i = {state: 'start', init: n, input: t, method: r, startClocks: I(), url: o};

    return e.notify(i), i;
  } function Nt(e, t, n) {
    var r = function(t) {
      var r = n;

      r.state = 'complete', r.duration = U(r.startClocks.timeStamp, M()), 'stack' in t || t instanceof Error ? (r.status = 0, r.isAborted = t instanceof DOMException && t.code === DOMException.ABORT_ERR, r.error = t, e.notify(r)) : 'status' in t && (r.response = t, r.responseType = t.type, r.status = t.status, r.isAborted = !1, e.notify(r));
    };

    t.then(c(r), c(r));
  } function qt(e, t) {
    if (!e.forwardErrorsToLogs)
      return {stop: b}; var n = Mt().subscribe((function(e) {
      'complete' === e.state && o('xhr', e);
    })); var r = Dt().subscribe((function(e) {
      'complete' === e.state && o('fetch', e);
    }));

    function o(n, r) {
      function o(e) {
        t.notify(0, {rawLogsEvent: {message: ''.concat(Ht(n), ' error ').concat(r.method, ' ').concat(r.url), date: r.startClocks.timeStamp, error: {origin: he, stack: e || 'Failed to load'}, http: {method: r.method, status_code: r.status, url: r.url}, status: Te.error, origin: he}});
      }e.isIntakeUrl(r.url) || !function(e) {
        return 0 === e.status && 'opaque' !== e.responseType;
      }(r) && !function(e) {
        return e.status >= 500;
      }(r) || ('xhr' in r ? function(e, t, n) {
        'string' == typeof e.response ? n(Ft(e.response, t)) : n(e.response);
      }(r.xhr, e, o) : r.response ? function(e, t, n) {
        window.TextDecoder ? e.body ? function(e, t, n) {
          !function(e, t, n) {
            var r = e.getReader(); var o = []; var i = 0;

            function s() {
              r.read().then(c((function(e) {
                e.done ? a() : (o.push(e.value), (i += e.value.length) > t ? a() : s());
              })), c((function(e) {
                return n(e);
              })));
            } function a() {
              var e;

              if (r.cancel().catch(b), 1 === o.length)
                e = o[0]; else {
                e = new Uint8Array(i); var s = 0;

                o.forEach((function(t) {
                  e.set(t, s), s += t.length;
                }));
              }n(void 0, e.slice(0, t), e.length > t);
            }s();
          }(e, t, (function(e, t, r) {
            if (e)
              n(e); else {
              var o = (new TextDecoder).decode(t);

              r && (o += '...'), n(void 0, o);
            }
          }));
        }(e.clone().body, t.requestErrorResponseLengthLimit, (function(e, t) {
          n(e ? 'Unable to retrieve response: '.concat(e) : t);
        })) : n() : e.clone().text().then(c((function(e) {
          return n(Ft(e, t));
        })), c((function(e) {
          return n('Unable to retrieve response: '.concat(e));
        })));
      }(r.response, e, o) : r.error && function(e, t, n) {
        n(Ft(me(ie(e)), t));
      }(r.error, e, o));
    } return {stop: function() {
      n.unsubscribe(), r.unsubscribe();
    }};
  } function Ft(e, t) {
    return e.length > t.requestErrorResponseLengthLimit ? ''.concat(e.substring(0, t.requestErrorResponseLengthLimit), '...') : e;
  } function Ht(e) {
    return 'xhr' === e ? 'XHR' : 'Fetch';
  } var Jt = /^(?:[Uu]ncaught (?:exception: )?)?(?:((?:Eval|Internal|Range|Reference|Syntax|Type|URI|)Error): )?(.*)$/;

  function zt(e) {
    var t = function(e) {
      return Bt(window, 'onerror', {before: function(t, n, r, o, i) {
        var s;

        if (i)
          s = ie(i), e(s, i); else {
          var a; var c = {url: n, column: o, line: r}; var u = t;

          if ('[object String]' === {}.toString.call(t)) {
            var f = Jt.exec(u);

            f && (a = f[1], u = f[2]);
          }e(s = {name: a, message: 'string' == typeof u ? u : void 0, stack: [c]}, t);
        }
      }});
    }(e).stop; var n = function(e) {
      return Bt(window, 'onunhandledrejection', {before: function(t) {
        var n = t.reason || 'Empty reason'; var r = ie(n);

        e(r, n);
      }});
    }(e).stop;

    return {stop: function() {
      t(), n();
    }};
  } function Vt(e) {
    return zt((function(t, n) {
      var r = function(e, t, n, r) {
        return e && (void 0 !== e.message || t instanceof Error) ? {message: e.message || 'Empty message', stack: me(e), handlingStack: r, type: e.name} : {message: ''.concat(n, ' ').concat(m(t)), stack: 'No stack, consider using an instance of Error', handlingStack: r, type: e && e.name};
      }(t, n, 'Uncaught'); var o = r.stack; var i = r.message; var s = r.type;

      e.notify({message: i, stack: o, type: s, source: ge, startClocks: I(), originalError: n, handling: 'unhandled'});
    }));
  } var $t = function() {
    function e() {
      this.callbacks = {};
    } return e.prototype.notify = function(e, t) {
      var n = this.callbacks[e];

      n && n.forEach((function(e) {
        return e(t);
      }));
    }, e.prototype.subscribe = function(e, t) {
      var n = this;

      return this.callbacks[e] || (this.callbacks[e] = []), this.callbacks[e].push(t), {unsubscribe: function() {
        n.callbacks[e] = n.callbacks[e].filter((function(e) {
          return t !== e;
        }));
      }};
    }, e;
  }(); var Wt; var Gt; var Xt; var Kt; var Qt = function(n) {
    var r; var o; var i = !1; var a = B(); var u = {}; var f = new j; var l = function(e, t, n, r) {
      void 0 === n && (n = T(h())), void 0 === r && (r = M()), f.add((function() {
        return l(e, t, n, r);
      }));
    }; var d = function() {}; var v = new je((function() {
      for (var e = [], t = 0; t < arguments.length; t++)
        e[t] = arguments[t]; return l.apply(void 0, e);
    }));

    function h() {
      return {view: {referrer: document.referrer, url: window.location.href}, context: a.get()};
    } return r = {logger: v, init: c((function(r) {
      if (N() && (r = function(e) {
        return p({}, e, {clientToken: 'empty'});
      }(r)), function(e) {
        return !i || (e.silentMultipleInit || t.error('DD_LOGS is already initialized.'), !1);
      }(r)) {
        var o = function(t) {
          var n = ne(t); var r = Ce(t.forwardConsoleLogs, x(e), 'Forward Console Logs'); var o = Ce(t.forwardReports, x(Ee), 'Forward Reports');

          if (n && r && o)
            return t.forwardErrorsToLogs && !w(r, e.error) && r.push(e.error), p({forwardErrorsToLogs: !1 !== t.forwardErrorsToLogs, forwardConsoleLogs: r, forwardReports: o, requestErrorResponseLengthLimit: 32768}, n);
        }(r);

        o && (l = n(o, h, v).handleLog, d = function() {
          return T(r);
        }, f.drain(), i = !0);
      }
    })), getLoggerGlobalContext: c(a.get), setLoggerGlobalContext: c(a.set), addLoggerGlobalContext: c(a.add), removeLoggerGlobalContext: c(a.remove), createLogger: c((function(e, t) {
      return void 0 === t && (t = {}), u[e] = new je((function() {
        for (var e = [], t = 0; t < arguments.length; t++)
          e[t] = arguments[t]; return l.apply(void 0, e);
      }), e, t.handler, t.level, t.context), u[e];
    })), getLogger: c((function(e) {
      return u[e];
    })), getInitConfiguration: c((function() {
      return d();
    }))}, o = p({version: '4.11.5', onReady: function(e) {
      e();
    }}, r), Object.defineProperty(o, '_setDebug', {get: function() {
      return s;
    }, enumerable: !1}), o;
  }((function(n, r, o) {
    var i = new $t;

    (function(e) {
      var t; var n = De(e);

      if (N()) {
        var r = P();

        n.observable.subscribe((function(e) {
          return r.send('internal_telemetry', e);
        }));
      } else {
        var o = We(e, e.rumEndpointBuilder, null === (t = e.replica) || void 0 === t ? void 0 : t.rumEndpointBuilder);

        n.observable.subscribe((function(t) {
          return o.add(t, function(e) {
            return 'datad0g.com' === e.site;
          }(e));
        }));
      } return n;
    })(n).setContextProvider((function() {
      var e; var t; var n; var r; var o; var i;

      return {application: {id: null === (e = wt()) || void 0 === e ? void 0 : e.application_id}, session: {id: null === (t = a.findTrackedSession()) || void 0 === t ? void 0 : t.id}, view: {id: null === (r = null === (n = wt()) || void 0 === n ? void 0 : n.view) || void 0 === r ? void 0 : r.id}, action: {id: null === (i = null === (o = wt()) || void 0 === o ? void 0 : o.user_action) || void 0 === i ? void 0 : i.id}};
    })), qt(n, i), function(e, t) {
      if (!e.forwardErrorsToLogs)
        return {stop: b}; var n = new ke; var r = Vt(n).stop; var o = n.subscribe((function(e) {
        t.notify(0, {rawLogsEvent: {message: e.message, date: e.startClocks.timeStamp, error: {kind: e.type, origin: ge, stack: e.stack}, origin: ge, status: Te.error}});
      }));
    }(n, i), function(t, n) {
      var r = Et(t.forwardConsoleLogs).subscribe((function(t) {
        n.notify(0, {rawLogsEvent: {date: M(), message: t.message, origin: ve, error: t.api === e.error ? {origin: ve, stack: t.stack} : void 0, status: Ct[t.api]}});
      }));
    }(n, i), function(e, t) {
      var n = Se(e.forwardReports).subscribe((function(e) {
        var n; var r = e.message; var o = Tt[e.type];

        o === Te.error ? n = {kind: e.subtype, origin: be, stack: e.stack} : e.stack && (r += ' Found in '.concat(function(e) {
          var t;

          return null === (t = (/@ (.+)/).exec(e)) || void 0 === t ? void 0 : t[1];
        }(e.stack))), t.notify(0, {rawLogsEvent: {date: M(), message: r, origin: be, error: n, status: o}});
      }));
    }(n, i); var s = function(e) {
      return {handleLog: function(n, r, o, i) {
        var s = n.context;

        mt(n.status, Re, r) && t(n.status, n.message, R(r.getContext(), s)), e.notify(0, {rawLogsEvent: {date: i || M(), message: n.message, status: n.status, origin: pe}, messageContext: s, savedCommonContext: o, logger: r});
      }};
    }(i).handleLog; var a = function(e) {
      if (void 0 === document.cookie || null === document.cookie)
        return !1; try {
        var n = 'dd_cookie_test_'.concat(h()); var r = 'test';

        J(n, r, l, e); var o = z(n) === r;

        return V(n, e), o;
      } catch (e) {
        return t.error(e), !1;
      }
    }(n.cookieOptions) && !N() ? ht(n) : function(e) {
        var t = '1' === gt(e) ? {} : void 0;

        return {findTrackedSession: function() {
          return t;
        }};
      }(n);

    return yt(a, n, i, r, o), N() ? function(e) {
      var t = P();

      e.subscribe(1, (function(e) {
        t.send('log', e);
      }));
    }(i) : function(e, t) {
      var n; var r = We(e, e.logsEndpointBuilder, null === (n = e.replica) || void 0 === n ? void 0 : n.logsEndpointBuilder);

      t.subscribe(1, (function(e) {
        r.add(e);
      }));
    }(n, i), {handleLog: s};
  }));

  Wt = E(), Xt = Qt, Kt = Wt[Gt = 'DD_LOGS'], Wt[Gt] = Xt, Kt && Kt.q && Kt.q.forEach((function(e) {
    return n(e, 'onReady callback threw an error:')();
  }));
}();