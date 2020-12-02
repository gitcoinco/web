/* eslint-disable no-prototype-builtins */

(function() {
  var ipfs = {};

  ipfs.localProvider = {host: '127.0.0.1', port: '5001', protocol: 'http', root: '/api/v0'};

  ipfs.setProvider = function(opts) {
    if (!opts)
      opts = this.localProvider;
    if (typeof opts === 'object' && !opts.hasOwnProperty('host')) {
      return;
    }
    ipfs.api = opts;
  };

  ipfs.api_url = function(path) {
    var api = ipfs.api;

    return api.protocol + '://' + api.host +
          (api.port ? ':' + api.port : '') +
          (api.root ? api.root : '') + path;
  };

  function ensureProvider(callback) {
    if (!ipfs.api) {
      callback(new Error('No provider set'));
      return false;
    }
    return true;
  }

  function request(opts) {
    if (!ensureProvider(opts.callback))
      return;
    var req = new XMLHttpRequest();

    req.onreadystatechange = function() {
      if (req.readyState == 4) {
        if (req.status != 200)
          opts.callback(req.responseText, null);
        else {
          var response = req.responseText;

          if (opts.transform) {
            response = opts.transform(response);
          }
          opts.callback(null, response);
        }
      }
    };
    req.open(opts.method || 'GET', ipfs.api_url(opts.uri));
    if (opts.accept) {
      req.setRequestHeader('accept', opts.accept);
    }
    if (opts.payload) {
      req.enctype = 'multipart/form-data';
      req.send(opts.payload);
    } else {
      req.send();
    }
  }

  ipfs.add = function(input, callback) {
    var form = new FormData();
    var data = (isBuffer(input) ? input.toString('binary') : input);
    var blob = new Blob([data], {});

    form.append('file', blob);
    request({
      callback: callback,
      method: 'POST',
      uri: '/add',
      payload: form,
      accept: 'application/json',
      transform: function(response) {
        return response ? JSON.parse(response)['Hash'] : null;
      }});
  };

  ipfs.catText = function(ipfsHash, callback) {
    request({callback: callback, uri: ('/cat/' + ipfsHash)});
  };

  ipfs.cat = ipfs.catText; // Alias this for now

  ipfs.addJson = function(jsonObject, callback) {
    var jsonString = JSON.stringify(jsonObject);

    ipfs.add(jsonString, callback);
  };

  ipfs.catJson = function(ipfsHash, callback) {
    ipfs.catText(ipfsHash, function(err, jsonString) {
      if (err)
        callback(err, {});
      var jsonObject = {};

      try {
        jsonObject = typeof jsonString === 'string' ? JSON.parse(jsonString) : jsonString;
      } catch (e) {
        err = e;
      }
      callback(err, jsonObject);
    });
  };

  // From https://github.com/feross/is-buffer
  function isBuffer(obj) {
    return !!(obj != null &&
    (obj._isBuffer || // For Safari 5-7 (missing Object.prototype.constructor)
      (obj.constructor &&
      typeof obj.constructor.isBuffer === 'function' &&
      obj.constructor.isBuffer(obj))
    ));
  }

  if (typeof window !== 'undefined') {
    window.ipfs = ipfs;
  }
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = ipfs;
  }
})();
