/*
* Script used to create emojis/stickers in both discord and telegram
*/
const sharp = require('sharp');
const fs = require('fs');
const colors = require('./colors');

// api tokens
const telegramBotToken = "";
const discordBotToken = "";

// the args
let platform = process.argv[2];
const svgImagesPath = process.argv[3];

// The Script Functions
const readFolderContents = async () => {
	fs.readdir(svgImagesPath, function(err, items) {
	    console.log(items);
	 
	    for (var i=0; i<items.length; i++) {
	        console.log(items[i]);
	    }
	});	
};

const createTempFolder = () => {
	var dir = './tmp';
	if (!fs.existsSync(dir)){
	    fs.mkdirSync(dir);
	}
};

const deleteTempFolderRecursive = () => {
  const dir = './tmp';

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

// The Script Steps
// first of all check if the platform name is legit
if (!platform) { 
   console.log(colors.FgRed, "Please enter a valid platform i.e. Telegram or Discord ", colors.Reset);
   process.exit(1);
} 
else {
	platform = String(platform).trim();

	if (platform.toLowerCase() !== "telegram" && platform.toLowerCase() !== "discord") {
      console.log(colors.FgRed, "Please enter a valid platform i.e. Telegram or Discord ", colors.Reset);
   	  process.exit(1);
	} 
	else {
		platform = platform.toLowerCase();
	}
}

// secondly check if the images path is legit
if (!fs.existsSync(svgImagesPath)) { 
   console.log(colors.FgRed, "Please enter a valid path to the images folder i.e. /Users/gitcoin/images", colors.Reset);
   process.exit(1);
}


