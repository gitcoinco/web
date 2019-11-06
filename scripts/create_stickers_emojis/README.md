# Requirements

To run the script, please make sure yyou have the following softwares installed locally.

1. [Node.JS](https://nodejs.org/en/)
2. [ImageMagick](https://imagemagick.org/script/download.php)

# Dependencies

The script has only 2 dev depencencies to help with the creation of the discord and telegram emojis/stickers and they are,

1. [open](https://www.npmjs.com/package/open) - To help in opening url's for manual authorization, where required.
2. [sharp](https://www.npmjs.com/package/sharp) - To help in converting the svg images to the required formats by both discord and telegram.

# Installation

Run the command, `npm i` to install the above dev dependencies, before running the script.

# Setup

After installing the dev dependencies, you need to setup the necessary environment variables in the [config.js](/scripts/create_stickers_emojis/config.js) file, as follows.

## Discord

1. [Create a discord application](https://github.com/SinisterRectus/Discordia/wiki/Setting-up-a-Discord-application#creating-discord-applications), copy it's `CLIENT ID` and paste it in the `discordBotClientId` env var.
2. [Create a discord bot](https://github.com/SinisterRectus/Discordia/wiki/Setting-up-a-Discord-application#creating-the-bot), copy it's `TOKEN` and paste it in the `discordBotToken` env var.
3. Finally right click on your discord server, in the discord app, and select the last option `Copy ID` and paste it into the `discordServerId` env var.

Make sure to reset these config vars after creating the emoji's to prevent them from being used to compromise your discord server in case they fall into the wrong hands.

# Usage

Using the script is very simple, you simply need to run the script via the cli using node.js and specify the necessary flags as follows
```sh
node scripts/create_stickers_emojis/ PLATFORM PATH_TO_SVG_IMAGES
```
where `PLATFORM` is the platform you are targeting i.e. `discord` or `telegram` and `PLATFORM PATH_TO_SVG_IMAGES` is the path to svg images you want to create emojis/stickers from i.e. `/home/ubuntu/gitcoin/images`

And so for example for discord emoji's the cli command would be something like,
```sh
node scripts/create_stickers_emojis/ discord /home/ubuntu/gitcoin/images
``` 
# Caveats

The script has the following limitations for both of the platforms

## Discord

- Due to discord restrictions, you can only upload **50 emojis** and so regardless of the number of images in your path, the script will only use the first 50 images to create the emoji's
- Due to discord api [rate limiting](https://discordapp.com/developers/docs/topics/rate-limits), the script may at time's give the error `You are being rate limited`. If this occur's kindly wait a few minutes before trying to create the discord emoji's and it will work.