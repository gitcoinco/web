const path = require('path');

const webpack = require('webpack');

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


  // export configuration to webpack
  return jsConfig;
};
