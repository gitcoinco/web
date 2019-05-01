// you can use this file to add your custom webpack plugins, loaders and anything you like.
// This is just the basic way to add additional webpack configurations.
// For more information refer the docs: https://storybook.js.org/configurations/custom-webpack-config

// IMPORTANT
// When you add this file, we won't add the default configurations which is similar
// to "React Create App". This only has babel loader to load JavaScript.
const paths = require('../config/paths');

// https://storybook.js.org/docs/configurations/custom-webpack-config/#using-your-existing-config

module.exports = {
  plugins: [
    // your custom plugins
  ],
  module: {
    rules: [
      {
        test: /\.scss$/,
        include: paths.appSrc,
        loaders: [
          require.resolve('style-loader'),
          require.resolve('css-loader'),
          require.resolve('sass-loader')
        ]
      },
      {
        test: /\.css$/,
        loaders: [
          require.resolve('style-loader'),
          require.resolve('css-loader')
        ]
      },
    ]
  },
};
