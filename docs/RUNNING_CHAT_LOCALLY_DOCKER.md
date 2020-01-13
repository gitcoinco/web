# Running Locally with Docker (Recommended)

```shell
git clone https://github.com/gitcoinco/mattermost-server.git
git clone https://github.com/gitcoinco/mattermost-client.git

```



## Mattermost Developer Setup

Follow the instructions at https://developers.mattermost.com/contribute/server/developer-setup/


You want `mattermost-server` and `mattermost-client` in the same parent directory

Server commands are scripted with a relative path to the client at ../mattermost-client

## Startup server

### Running in Detached mode

Runs the server with its dependencies on docker, conflicts with other services presently  
```shell
make run-server
```

### Developing with the command line shell

```shell
make run-cli
```

### Debugging

```shell
make debug-server
```


### Viewing Logs

Actively follow a container's log:

```shell
docker-compose logs -f mattermost # Or any other container name
```

View all container logs:

```shell
docker-compose logs
```

Navigate to `http://localhost:8065/`.


You will need to edit the `config/config.json` file with your local environment variables. Look for config items that are marked `# required`.

## Gitcoin Integration Setup (recommended)

If you plan on using the Gitcoin integration, please read this first [Django Oauth Toolkit - Register an application](https://django-oauth-toolkit.readthedocs.io/en/latest/rest-framework/getting_started.html#step-3-register-an-application). 

Create an Application on your local copy of Gitcoin and enable skip authorization.

Once you have those keys you will have to update the `GitCoinSettings` key in  `config/config.json` file with the new application keys created above.
