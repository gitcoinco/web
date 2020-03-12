# Running Locally with Docker (Recommended)

Chat has been containerized and loads automatically as apart of `docker-compose up`

Chat Config overrides can be setup in `chatconfig/config.json`
- email, notifications, plugins, etc

Gitcoin Oauth Dummy Credentials are created as apart the chat/fixtures/initial.json folder.

If you want to configure a new oauth application visit: [oAuth Provider Administration](http://localhost:8000/_administrationoauth2_provider/application/) and you will have to update the `GitCoinSettings` key in  `config/config.json` file with the new application keys created above.


Visit [Chat](http://localhost:8065) to get started. 

- [ ] Login
- Setup the Platform post initialization:
  - Create Two New Teams:
    - [ ] Gitcoin - name Gitcoin, slug /gitcoin
    - [ ] Hackathons - name Hackathons, slug /hackathon
  - [ ] Access the mattermost database
  
  - [ ] extract the two team ID's for what we created above, 
and set them in `app/app/.env`
    - [ ] GITCOIN_HACK_CHAT_TEAM_ID=
    - [ ] GITCOIN_CHAT_TEAM_ID= 

Once Logged into The Gitcoin team, 
- Create a Bot Account to drive actions from Gitcoin on Chat
[Visit Gitcoin Chat Integrations](http://localhost:8065/gitcoin/integrations)
  - [ ] Create a new Bot Account and copy its access token 
  - [ ] Set CHAT_DRIVER_TOKEN= in `app/app/.env` to the access token from above 

Restart Gitcoin Web with updated env variables
