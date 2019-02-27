const path = require('path');
const webpack = require('webpack');
const BundleTracker = require('webpack-bundle-tracker');
const styleLintPlugin = require('stylelint-webpack-plugin');


module.exports = {
  devtool: 'inline-source-map',
  output: {
    path: path.resolve(__dirname, 'app/static/bundles'),
    filename: '[name]-[hash].js',

    // Tell django to use this URL to load packages and not use STATIC_URL + bundle_name
    publicPath: 'http://localhost:3000/static/bundles/'
  },
  module: {
    rules: [{
      test: /\.js$/,
      enforce: 'pre',
      exclude: /node_modules/,
      use: [{
        loader: 'eslint-loader',
        options: {
          failOnError: true,
          outputReport: {
            filePath: 'checkstyle.xml',
            formatter: require('eslint-friendly-formatter')
          }
        }
      }]
    }, {
      test: /\.js?$/,
      exclude: /node_modules/,
      use: [{
        loader: 'babel-loader',
        options: {
          presets: ['env']
        }
      }]
    }]
  },
  plugins: [
    new webpack.HotModuleReplacementPlugin(),

    // don't reload if there is an error
    new webpack.NoEmitOnErrorsPlugin(),
    new BundleTracker({
      filename: './webpack-stats.json'
    }),
    new styleLintPlugin({
      configFile: '.stylelintrc',
      context: 'app/assets/',
      files: '**/**/*.*css',
      failOnError: false,
      quiet: false
    })
  ],
  resolve: {
    alias: {
      modulesDirectories: path.resolve(__dirname, 'node_modules')
    },
    extensions: ['.js']
  }
};


if (process.env.NODE_ENV === 'production') {
  module.exports.plugins = [
    new webpack.DefinePlugin({
      'process.env': {
        NODE_ENV: '"production"'
      }
    }),
    new webpack.optimize.UglifyJsPlugin({
      compress: {
        warnings: false
      }
    }),
    new webpack.optimize.OccurenceOrderPlugin()
  ];
} else {
  module.exports.devtool = '#source-map';
}
