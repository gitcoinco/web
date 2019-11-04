const fs = require('fs');
const { askQuestion, readImagesPath, createTempFolder, convertAndResizeSvg, deleteTempFolderRecursive } = require('./common');
const open = require('open');
const readline = require('readline');
const { discordBotToken, discordBotClientId, discordServerId } = require('../config');
const https = require('https');

// import the colors
const colors = require('../colors');

// Script Vars
const DISCORD_EMOJI_SIZE = 128;
const DISCORD_TEMP_FOLDER = __dirname + '/discord_images';

// upload the converted PNG's to discord via the bot
const uploadEmojisToDiscord = async() => {
  try {

    const emojis = await readImagesPath(DISCORD_TEMP_FOLDER);
    console.log(emojis);

    if (emojis.length > 0) {

      for (var i = 0; i < 2; i++) {

        const emojiPath = DISCORD_TEMP_FOLDER + '/' + emojis[i];
        const emojiBase64 = fs.readFileSync(emojiPath, 'base64');
        const emojiData = JSON.stringify({
                        name: emojis[i].split('.').slice(0, -1).join('.'),
                        image: `data:image/png;base64,${emojiBase64}`,
                      });

      

        const options = {
            hostname: 'discordapp.com',
            port: 443,
            path: `/api/guilds/${discordServerId}/emojis`,
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Content-Length': data.length,
              'Authorization': `Bot ${discordBotToken}` 
            }
        };

        const req = https.request(options, res => {
          console.log(`statusCode: ${res.statusCode}`)

          res.on('data', d => {
            process.stdout.write(d)
          });

        });

        req.on('error', error => {
          console.error(error)
        });

        req.write(data);
        req.end();

      }

    }

  } 
  catch(error) {

  }

};

const createEmoji = async (imagesPath) => {

  try {

    const images = await readImagesPath(imagesPath);

    if (images.length > 0) {
      console.log("");
      console.log(colors.FgYellow, "Please note discord only accepts a maximum of 50 emoji's for each server, so only the first 50 images will be used to create emoji's!!", colors.Reset);
      console.log("");

      // delete the old temp folder if it exists
      deleteTempFolderRecursive(DISCORD_TEMP_FOLDER);

      // then create a new temp folder to store the images being converted
      createTempFolder(DISCORD_TEMP_FOLDER);

      // the convert the first 50 images
      for (var i = 0; i < images.length; i++) {

        const currImagePath = imagesPath + '/' + images[i];
        const newImageName = images[i].toLowerCase().split('.').slice(0, -1).join('.').replace(/ /g,"_").replace(/-/g,"_")+'.png';
        const newImagePath = DISCORD_TEMP_FOLDER + '/' + newImageName;

        await convertAndResizeSvg(DISCORD_EMOJI_SIZE, DISCORD_EMOJI_SIZE, currImagePath, newImagePath);

        // exit the loop if we have converted 50 images to png
        if (i >= 50) { break; }
      }

      // finally upload the emoji's to discord
      uploadEmojisToDiscord();

    }

  }
  catch (error) {
     console.log(error);
  }

};

// function that setups discord by asking the user to allow the bot to manage/create emojis in the server
const setupDiscord = async (imagesPath) => {
  console.log("");
  const ans1 = await askQuestion(colors.FgGreen + "You now need to kindly authorize the discord bot to manage emoji's in your server. Is this ok? (Y/n) " + colors.Reset);

  if (ans1.trim().toLowerCase() === 'y' || ans1.trim().toLowerCase() === '') {

    const authLink = `https://discordapp.com/oauth2/authorize?client_id=${discordBotClientId}&scope=bot&permissions=1073741824`;

   	await open(authLink);

    console.log("");
   	const ans2 = await askQuestion(colors.FgGreen + "Awesome! we can now continue if you have enabled the bot to have emoji permissions in our discord server. Continue? (Y/n) " + colors.Reset);

   	if (ans2.trim().toLowerCase() === 'y' || ans2.trim().toLowerCase() === '') {
      // if everything checks out, then create the emoji's
   		createEmoji(imagesPath);
   	} else {
   		console.log("");
   		console.log(colors.FgGreen, "No worries, you can always re-do this steps later.", colors.Reset);
      console.log("");
    	process.exit(1);
   	}

  } else {
    console.log("");
  	console.log(colors.FgRed, "Sorry, but you'll need to authorise the discord bot to manage the emoji's before continuing!", colors.Reset);
    console.log("");
  	process.exit(1);
  }
  
};
	
module.exports = { setupDiscord };
