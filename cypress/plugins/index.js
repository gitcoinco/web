// promisified fs module
const fs = require('fs-extra');
const path = require('path');

function getConfigurationByFile(file) {
  const pathToConfigFile = path.resolve('cypress', 'config', `${file}.json`);

  return fs.readJson(pathToConfigFile);
}


module.exports = (on, config) => {
  // `on` is used to hook into various events Cypress emits
  // `config` is the resolved Cypress config

  // accept a configFile value or use development by default
  const file = config.env.configFile || 'development';

  return getConfigurationByFile(file);
};
