(function() {
  function r(e, n, t) {
    function o(i, f) {
      if (!n[i]) {
        if (!e[i]) {
          var c = 'function' == typeof require && require;

          if (!f && c)
            return c(i, !0); if (u)
            return u(i, !0); var a = new Error("Cannot find module '" + i + "'");

          throw a.code = 'MODULE_NOT_FOUND', a;
        } var p = n[i] = {exports: {}};

        e[i][0].call(p.exports, function(r) {
          var n = e[i][1][r];

          return o(n || r);
        }, p, p.exports, r, e, n, t);
      } return n[i].exports;
    } for (var u = 'function' == typeof require && require, i = 0; i < t.length; i++)
      o(t[i]); return o;
  } return r;
})()({1: [ function(require, module, exports) {
  let extension_dapp = require('@polkadot/extension-dapp');

  window.polkadot_extension_dapp = extension_dapp;
}, {'@polkadot/extension-dapp': 4}], 2: [ function(require, module, exports) {
  function _defineProperty(obj, key, value) {
    if (key in obj) {
      Object.defineProperty(obj, key, {
        value: value,
        enumerable: true,
        configurable: true,
        writable: true
      });
    } else {
      obj[key] = value;
    }

    return obj;
  }

  module.exports = _defineProperty;
}, {}], 3: [ function(require, module, exports) {
  function _interopRequireDefault(obj) {
    return obj && obj.__esModule ? obj : {
      'default': obj
    };
  }

  module.exports = _interopRequireDefault;
}, {}], 4: [ function(require, module, exports) {
  'use strict';
  var _interopRequireDefault = require('@babel/runtime/helpers/interopRequireDefault');

  Object.defineProperty(exports, '__esModule', {
    value: true
  });
  exports.web3Enable = web3Enable;
  exports.web3Accounts = web3Accounts;
  exports.web3AccountsSubscribe = web3AccountsSubscribe;
  exports.web3FromSource = web3FromSource;
  exports.web3FromAddress = web3FromAddress;
  exports.web3ListRpcProviders = web3ListRpcProviders;
  exports.web3UseRpcProvider = web3UseRpcProvider;
  exports.web3EnablePromise = exports.isWeb3Injected = void 0;

  var _defineProperty2 = _interopRequireDefault(require('@babel/runtime/helpers/defineProperty'));

  var _util = require('./util');

  function ownKeys(object, enumerableOnly) {
    var keys = Object.keys(object);

    if (Object.getOwnPropertySymbols) {
      var symbols = Object.getOwnPropertySymbols(object);

      if (enumerableOnly)
        symbols = symbols.filter(function(sym) {
          return Object.getOwnPropertyDescriptor(object, sym).enumerable;
        }); keys.push.apply(keys, symbols);
    } return keys;
  }

  function _objectSpread(target) {
    for (var i = 1; i < arguments.length; i++) {
      var source = arguments[i] != null ? arguments[i] : {};

      if (i % 2) {
        ownKeys(Object(source), true).forEach(function(key) {
          (0, _defineProperty2.default)(target, key, source[key]);
        });
      } else if (Object.getOwnPropertyDescriptors) {
        Object.defineProperties(target, Object.getOwnPropertyDescriptors(source));
      } else {
        ownKeys(Object(source)).forEach(function(key) {
          Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key));
        });
      }
    } return target;
  }

  // just a helper (otherwise we cast all-over, so shorter and more readable)
  const win = window; // don't clobber the existing object, but ensure non-undefined

  win.injectedWeb3 = win.injectedWeb3 || {}; // true when anything has been injected and is available

  function web3IsInjected() {
    return Object.keys(win.injectedWeb3).length !== 0;
  } // helper to throw a consistent error when not enabled


  function throwError(method) {
    throw new Error(`${method}: web3Enable(originName) needs to be called before ${method}`);
  } // internal helper to map from Array<InjectedAccount> -> Array<InjectedAccountWithMeta>


  function mapAccounts(source, list) {
    return list.map(({
      address,
      genesisHash,
      name
    }) => ({
      address,
      meta: {
        genesisHash,
        name,
        source
      }
    }));
  } // have we found a properly constructed window.injectedWeb3


  let isWeb3Injected = web3IsInjected(); // we keep the last promise created around (for queries)

  exports.isWeb3Injected = isWeb3Injected;
  let web3EnablePromise = null;

  exports.web3EnablePromise = web3EnablePromise;

  // enables all the providers found on the injected window interface
  function web3Enable(originName) {
    exports.web3EnablePromise = web3EnablePromise = (0, _util.documentReadyPromise)(() => Promise.all(Object.entries(win.injectedWeb3).map(([ name, {
      enable,
      version
    }]) => {
      return Promise.all([ Promise.resolve({
        name,
        version
      }), enable(originName).catch(error => {
        console.error(`Error initializing ${name}: ${error.message}`);
      }) ]);
    })).then(values => values.filter(([ , ext ]) => !!ext).map(([ info, ext ]) => {
    // if we don't have an accounts subscriber, add a single-shot version
      if (ext && !ext.accounts.subscribe) {
        ext.accounts.subscribe = cb => {
          ext.accounts.get().then(cb).catch(console.error);
          return () => { // no ubsubscribe needed, this is a single-shot
          };
        };
      }

      const injected = _objectSpread(_objectSpread({}, info), ext);

      return injected;
    })).catch(() => []).then(values => {
      const names = values.map(({
        name,
        version
      }) => `${name}/${version}`);

      exports.isWeb3Injected = isWeb3Injected = web3IsInjected();
      console.log(`web3Enable: Enabled ${values.length} extension${values.length !== 1 ? 's' : ''}: ${names.join(', ')}`);
      return values;
    }));
    return web3EnablePromise;
  } // retrieve all the accounts accross all providers


  async function web3Accounts() {
    if (!web3EnablePromise) {
      return throwError('web3Accounts');
    }

    const accounts = [];
    const injected = await web3EnablePromise;
    const retrieved = await Promise.all(injected.map(async({
      accounts,
      name: source
    }) => {
      try {
        const list = await accounts.get();

        return mapAccounts(source, list);
      } catch (error) {
      // cannot handle this one
        return [];
      }
    }));

    retrieved.forEach(result => {
      accounts.push(...result);
    });
    const addresses = accounts.map(({
      address
    }) => address);

    console.log(`web3Accounts: Found ${accounts.length} address${accounts.length !== 1 ? 'es' : ''}: ${addresses.join(', ')}`);
    return accounts;
  }

  async function web3AccountsSubscribe(cb) {
    if (!web3EnablePromise) {
      return throwError('web3AccountsSubscribe');
    }

    const accounts = {};

    const triggerUpdate = () => cb(Object.entries(accounts).reduce((result, [ source, list ]) => {
      result.push(...mapAccounts(source, list));
      return result;
    }, []));

    const unsubs = (await web3EnablePromise).map(({
      accounts: {
        subscribe
      },
      name: source
    }) => subscribe(result => {
      accounts[source] = result; // eslint-disable-next-line @typescript-eslint/no-floating-promises

      triggerUpdate();
    }));

    return () => {
      unsubs.forEach(unsub => {
        unsub();
      });
    };
  } // find a specific provider based on the name


  async function web3FromSource(source) {
    if (!web3EnablePromise) {
      return throwError('web3FromSource');
    }

    const sources = await web3EnablePromise;
    const found = source && sources.find(({
      name
    }) => name === source);

    if (!found) {
      throw new Error(`web3FromSource: Unable to find an injected ${source}`);
    }

    return found;
  } // find a specific provider based on an address


  async function web3FromAddress(address) {
    if (!web3EnablePromise) {
      return throwError('web3FromAddress');
    }

    const accounts = await web3Accounts();
    const found = address && accounts.find(account => account.address === address);

    if (!found) {
      throw new Error(`web3FromAddress: Unable to find injected ${address}`);
    }

    return web3FromSource(found.meta.source);
  } // retrieve all providers exposed by one source


  async function web3ListRpcProviders(source) {
    const {
      provider
    } = await web3FromSource(source);

    if (!provider) {
      console.warn(`Extension ${source} does not expose any provider`);
      return null;
    }

    return provider.listProviders();
  } // retrieve all providers exposed by one source


  async function web3UseRpcProvider(source, key) {
    const {
      provider
    } = await web3FromSource(source);

    if (!provider) {
      throw new Error(`Extension ${source} does not expose any provider`);
    }

    const meta = await provider.startProvider(key);

    return {
      meta,
      provider
    };
  }
}, {'./util': 5, '@babel/runtime/helpers/defineProperty': 2, '@babel/runtime/helpers/interopRequireDefault': 3}], 5: [ function(require, module, exports) {
  'use strict';
  Object.defineProperty(exports, '__esModule', {
    value: true
  });
  exports.documentReadyPromise = documentReadyPromise;

  // Copyright 2019-2020 @polkadot/extension-dapp authors & contributors
  // This software may be modified and distributed under the terms
  // of the Apache-2.0 license. See the LICENSE file for details.
  function documentReadyPromise(creator) {
    return new Promise(resolve => {
      if ([ 'complete', 'interactive' ].includes(document.readyState)) {
        resolve(creator());
      } else {
        window.addEventListener('load', () => {
          resolve(creator());
        });
      }
    });
  }
}, {}]}, {}, [1]);
