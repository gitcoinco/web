# Running Locally with Docker (Recommended)

Chat has been containerized and loads automatically as apart of `docker-compose up`

Chat Config overrides can be setup in `chatconfig/config.json`
- email, notifications, plugins, etc

Gitcoin Oauth Dummy Credentials are created when you boot up the app the first time and the fixtures run.
The fixtures can be found over at `app/fixtures/oauth_application`

*NOTE*

*If you need to configure a new oauth application visit: [oAuth Provider Administration](http://localhost:8000/_administrationoauth2_provider/application/) an you will have to update the `GitCoinSettings` key in `config/config.json` file with the new application keys created above.*


1. [Login into chat](http://localhost:8065) 

2. Create two new teams:
    - name `Gitcoin`, slug `/gitcoin`
    - name `Hackathons`, slug `/hackathon`

3. Connect to mattermost database and extract the id and set them in `app/app/.env` them 
```
GITCOIN_HACK_CHAT_TEAM_ID=
GITCOIN_CHAT_TEAM_ID= 
```

4. Create a new Bot Account [via here](http://localhost:8065/gitcoin/integrations)
   Ensure the bot account has role `SYSTEM ADMIN`

5. Copy the token and and update `app/app/.env`
```
CHAT_DRIVER_TOKEN=
```

Restart Gitcoin Web with updated env variables
