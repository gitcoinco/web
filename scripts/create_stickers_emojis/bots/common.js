const fs = require('fs');
const readline = require('readline');
const sharp = require('sharp');
// import the colors
const colors = require('../colors');

const askQuestion = (query) => {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
    });

    return new Promise(resolve => rl.question(query, ans => {
        rl.close();
        resolve(ans);
    }))
};

// These are the common script functions used by both bots
const readImagesPath =  (svgImagesPath) => {
  return new Promise( (resolve, reject) => {
      fs.readdir(svgImagesPath, function(err, items) {
        
        if(err) {
           reject(err);
        } else{
           resolve(items);
        }
      }); 
  });
};

const createTempFolder = (dir) => {
	if (!fs.existsSync(dir)){
	    fs.mkdirSync(dir);
	}
};

const convertAndResizeSvg = async (width, height, inputSvg, outputPng) => {
    try {
      await sharp(inputSvg, { density: 300 })
            .resize(width, height, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
            .png()
            .toFile(outputPng);
    } catch (err) {
      const fileName = inputSvg.split('/').pop();
      console.error(colors.FgRed, err, 'for image: ' + fileName, colors.Reset);
    } 
};

const deleteTempFolderRecursive = (dir) => {

  if (fs.existsSync(dir)) {

    fs.readdirSync(dir).forEach(function(file, index){

      var curPath = dir + "/" + file;
      if (fs.lstatSync(curPath).isDirectory()) { // recurse
        deleteFolderRecursive(curPath);
      } else { // delete file
        fs.unlinkSync(curPath);
      }
    });

    fs.rmdirSync(dir);
  }
};

module.exports = { readImagesPath, createTempFolder, convertAndResizeSvg, deleteTempFolderRecursive, askQuestion };