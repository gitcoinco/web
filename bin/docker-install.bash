#!/usr/local/bin/dumb-init /bin/bash

# ==================================================
# Install docker
# ==================================================

# add repo
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update

# use docker-ce over default
apt-cache policy docker-ce

# install from docker-ce
sudo apt-get install -y docker-ce

# add current user to dockers usergroup
sudo usermod -aG docker ${USER}
