/*
* Script used to create emojis/stickers in both discord and telegram
*/
const sharp = require('sharp');
const fs = require('fs');

// import the bots functions
const { setupDiscord } = require('./bots/discord');

// import the colors
const colors = require('./colors');

// the args
let platform = process.argv[2];
const imagesPath = process.argv[3];


// first of all check if the platform arg is legit
if (!platform) { 
   console.log(colors.FgRed, "Please enter a valid platform i.e. Telegram or Discord ", colors.Reset);
   process.exit(1);
} 
else {
	platform = String(platform).trim();

	if (platform.toLowerCase() !== "telegram" && platform.toLowerCase() !== "discord") {
      console.log(colors.FgRed, "Please enter a valid platform  i.e. telegram or discord ", colors.Reset);
   	  process.exit(1);
	}
	else if (!fs.existsSync(imagesPath)) { // check if the image path has been entered too
	   console.log(colors.FgRed, "Please enter a valid path to the images folder i.e. /Users/gitcoin/images", colors.Reset);
	   process.exit(1);
	}
	else {
		platform = platform.toLowerCase();

		if (platform === "discord") {
			setupDiscord(imagesPath);
		}
	}
}
