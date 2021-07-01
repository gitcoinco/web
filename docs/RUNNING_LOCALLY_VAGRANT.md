# Running locally with Vagrant

Testing an alternative approach to running Gitcoin web locally by provisioning vms with vagrant to more closely match the production environment, test configuring with ansible, and find a common way to list and install packages across deployments types.

#### Disclaimer
This is still a work in progress as a python package mismatch may be causing the virtualenv to be configured incorrectly.

## How to use

### Requirements
* [Virtualbox](https://www.virtualbox.org/wiki/Downloads)
* [Vagrant](https://www.vagrantup.com/downloads)
* [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/index.html)
* Add Ansible community collections:
    ```shell
    ansible-galaxy collection install community.general
    ```

### Instructions
First, we provision the db and web vms with vagrant and check the Ansible connection to the newly created vms:
```shell
~/$ vagrant up
```

Next, we configure the PostgreSQL database on the db vm:
```shell
~/$ ansible-playbook ansible/config-db.yml
```

For the webserver we configure packages, clone latest from gitcoin web, run through the python requirements, and startup the django server.
```shell
~/$ ansible-playbook ansible/config-web.yml
```

Once the configuration of the db and web servers is successful gitcoin web should be running locally at `http://localhost:8000/`.

