# Running Gitcoin remotely

We'll be using DigitalOcean which is a nice VPS service pretty customizable, easy to use and cheap. You need to create an account and pay for a droplet using any of the payment methods available.

There will be kind of a high memory load, so we gonna need the second best droplet which offers 2GB/1CPU (costs $10).

#### Create a droplet with the following settings:

Distribution: Ubuntu 18.04.3 LTS X64
Plan: Starter $10 2GB/1CPU
Block storage: not necessary.
Data center: choose the one closest to you.
Authentication: SSH Keys (highly recommended)
Hostname: identify your droplet with a name you easily remember.
Backups: not necessary (up to you).

* Note: you will need to generate SSH keys if you don't already have them. DO provides you a guide to do this on both Linux and Windows. It's required you copy your public key into DO, as this will be used to connect to your droplet.

## Connecting to the droplet and setting it up.

Once the droplet has been created, you need to connect to it.  I will be using PuTTY to connect to the droplet. DO has a convenient guide to setup PuTTY [here.](https://www.digitalocean.com/docs/droplets/how-to/connect-with-ssh/)

You will know you've successfully connected to the droplet after your SSH client terminal welcomes you like this:

![screenshot1](https://github.com/gitcoinco/web/raw/master/docs/imgs/rr1.png)

It's recommended you create a new user as using root is dangerous.

```shell
# adduser newuser
```

You will be prompted to enter a password, and some personal data (this is optional).

Sudo priviledges are required, to grant priviledges type:

```shell
# usermod -aG sudo newuser
```

Login as the new user you created:

```shell
# su - newuser
```

![screenshot2](https://github.com/gitcoinco/web/raw/master/docs/imgs/rr2.png)

Now we can start having fun, it's time to install Docker:

```shell
$ sudo apt update
$ sudo apt install apt-transport-https ca-certificates curl software-properties-common
$ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
$ sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
$ sudo apt update
$ sudo apt install docker-ce
```

Docker should be installed and configured to start on boot. You can check if Docker is running:

```shell
$ sudo systemctl status docker
```

Add your user into the docker group:

```shell
$ sudo usermod -aG docker ${USER}
```

To apply the changes you need to login again:

```shell
$ su - ${USER}
```

Time to install Docker Compose:

```shell
$ sudo curl -L "https://github.com/docker/compose/releases/download/1.25.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
$ sudo chmod +x /usr/local/bin/docker-compose
```

Test that Docker Compose was successfully installed:

```shell
$ docker-compose --version
docker-compose version 1.25.4, build 1110ad01
```

![screenshot3](https://github.com/gitcoinco/web/raw/master/docs/imgs/rr3.png)

Great! Now we need to download the Gitcoin repo:

```shell
$ git clone https://github.com/gitcoinco/web.git
$ cd web
$ cp app/app/local.env app/app/.env
```

We're ready to run the container, you have two options to do this:

- Running the container in detached mode (recommended):

```shell
$ docker-compose up -d --build
```

- Running the container in the foreground:

```shell
$ docker-compose up --build
```

Your screen will look like this after docker finishes the setup:

![screenshot4](https://github.com/gitcoinco/web/raw/master/docs/imgs/rr4.png)

We're halfway there as we still need a desktop environment and a VNC server. Let's install Xfce:

```shell
$ sudo apt install xfce4 xfce4-goodies
```

Once Xfce gets installed, install TightVNC server:

```shell
$ sudo apt install tightvncserver
```

Run the command 'vncserver' to set up a secure password and create the initial configuration files:

```shell
$ vncserver
```

You’ll be prompted to enter and verify a password to access your machine remotely. The password must be between six and eight characters long. 

Once you verify the password, you’ll have the option to create a a view-only password. This is not required and for our purposes, not necessary.

The VNC server needs to know which commands to execute when it starts up. Specifically, VNC needs to know which graphical desktop it should connect to.

These commands are located in a configuration file called xstartup in the .vnc folder under your home directory. The startup script was created when you ran the vncserver in the previous step, but we’ll create our own to launch the Xfce desktop.

First, stop the VNC server:

```shell
$ vncserver -kill :1
```

Before modifying the configuration file, it's recommended to make a backup:

```shell
$ mv ~/.vnc/xstartup ~/.vnc/xstartup.bak
```

Create a new file and open it:

```shell
$ nano ~/.vnc/xstartup
```

Commands in this file are executed automatically whenever you start or restart the VNC server. We need VNC to start our desktop environment if it’s not already started.

Add these commands to the file:

```shell
#!/bin/bash
xrdb $HOME/.Xresources
startxfce4 &
```

Save the changes made to the file (press Ctrl-O), hit Enter to confirm and then close the editor (press Ctrl-X).

To ensure that the VNC server will be able to use this new startup file properly, we’ll need to make it executable.

```shell
$ sudo chmod +x ~/.vnc/xstartup
```

Restart the VNC server:

```shell
$ vncserver
```

Connect to the VNC server using any VNC client you like, I'll use RealVNC Viewer.

Add a new connection, use the droplet IP with port 5901. You'll be prompted for a password, use the one you input after starting vncserver for the first time.

![screenshot5](https://github.com/gitcoinco/web/raw/master/docs/imgs/rr5.png)

Inmediately after connecting you should see the desktop environment. There's no web browser installed, let's install Firefox:

```shell
$ sudo apt install firefox
```

It's time to finally see how all of this hard work looks like, in the browser enter the following address:

```shell
https://localhost:8000/
```

And..

![screenshot6](https://github.com/gitcoinco/web/raw/master/docs/imgs/rr6.png)

We made it! You're now ready to work remotely!
