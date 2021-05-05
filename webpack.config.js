const path = require('path');

const webpack = require('webpack');

const FileManagerPlugin = require('filemanager-webpack-plugin');
const TerserPlugin = require('terser-webpack-plugin');
const WebpackWatchedGlobEntries = require('webpack-watched-glob-entries-plugin');

// exports webpack configuration (for js and sass)
module.exports = (_, argv) => {

  // control loading of static assets
  const static = (argv.mode === 'development' ? '/static/' : 'https://s.gitcoin.co/static/');

  // extract js bundles, minify and watch dir for changes
  const jsConfig = {
    entry: WebpackWatchedGlobEntries.getEntries(
      [ path.resolve(__dirname, 'app/assets/v2/bundles/js/*.js') ]
    ),
    devtool: false, // (argv.mode === 'development' ? 'eval-cheap-source-map' : false)
    output: {
      filename: '[name].js',
      path: path.resolve(__dirname, 'app/assets/v2/bundled/js'),
      library: {
        type: 'global'
      },
      iife: false,
      environment: {
        arrowFunction: true, // @todo - we want to set arrows to false (for IE support) but it breaks inclusions
        bigIntLiteral: false,
        const: false,
        destructuring: false,
        dynamicImport: false,
        forOf: false,
        module: false,
      },
    },
    module: {
      rules: [
        {
          test: /\.(js)$/,
          exclude: /node_modules/,
          use: [
            'babel-loader',
          ],
          parser: {
            amd: false, // disable AMD
            commonjs: false, // disable CommonJS
            system: false, // disable SystemJS
            harmony: true, // enable ES2015 Harmony import/export (import is used by bundles/*.js)
            requireInclude: false, // disable require.include
            requireEnsure: false, // disable require.ensure
            requireContext: false, // disable require.context
            browserify: false, // disable special handling of Browserify bundles
            requireJs: false, // disable requirejs.*
            node: false, // disable __dirname, __filename, module, require.extensions, require.main, etc.
            commonjsMagicComments: false // disable magic comments support for CommonJS
          }
        }
      ]
    },
    optimization: {
      minimize: (argv.mode !== 'development'),
      minimizer: [
        // use custom minimizer to avoid tree-shaking (TerserPlugin is built-in)
        new TerserPlugin({
          minify: (file, sourceMap) => {
            const options = {};

            if (sourceMap) {
              options.sourceMap = {
                content: sourceMap,
              };
            }

            return require("uglify-js").minify(file, options);
          },
        })
      ]
    },
    plugins: [
      new WebpackWatchedGlobEntries(),
      // prevent chucking of large outputs
      new webpack.optimize.LimitChunkCountPlugin({
        maxChunks: 1
      })
    ]
  };

  // extract scss bundles, compile, minify, watch and clean-up webpack artifacts
  const sassConfig = {
    entry: WebpackWatchedGlobEntries.getEntries(
      [ path.resolve(__dirname, 'app/assets/v2/bundles/scss/*.scss') ]
    ),
    devtool: false, // (argv.mode === 'development' ? 'eval-cheap-source-map' : false)
    output: {
      filename: '[name].noop.js',
      path: path.resolve(__dirname, 'app/assets/v2/bundled/css/'),
    },
    module: {
      rules: [
        {
          test: /bundles\/scss\/.*\.scss$/,
          use: [
            {
              loader: 'file-loader',
              options: {
                name: '[name].css',
              }
            },
            {
              loader: 'extract-loader',
            },
            {
              loader: 'css-loader?-url',
            },
            {
              loader: 'sass-loader',
              options: {
                additionalData: `
                  $mode: '${argv.mode}';
                  @function static($url) {
                    @if (str-slice($url, 1, 1) == '/') {
                      $url: str-slice($url, 2);
                    }
                    @return '${static}' + $url;
                  };
                  @import '${path.resolve(__dirname, 'app/assets/v2/scss/gc-mixins')}';
                `
              }
            }
          ]
        }
      ]
    },
    plugins: [
      new WebpackWatchedGlobEntries(),
      // webpack always creates a .js file for each entry - delete it
      new FileManagerPlugin({
        events: {
          onEnd: {
            delete: [path.resolve(__dirname, 'app/assets/v2/bundled/css/*.noop.*')],
          },
        },
      })
    ]
  };

  // export both configurations to webpack
  return [jsConfig, sassConfig];
};
