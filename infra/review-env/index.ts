import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import * as awsx from "@pulumi/awsx";


//////////////////////////////////////////////////////////////
// Set up VPC
//////////////////////////////////////////////////////////////

const vpc = new awsx.ec2.Vpc("gitcoin", {
    subnets: [
        { type: "public", },
        { type: "private", mapPublicIpOnLaunch: true },
    ],
});


export const vpcID = vpc.id;
export const vpcPrivateSubnetIds = vpc.privateSubnetIds;
export const vpcPublicSubnetIds = vpc.publicSubnetIds;
export const vpcPrivateSubnetId1 = vpcPrivateSubnetIds.then(values => values[0]);
export const vpcPublicSubnetId1 = vpcPublicSubnetIds.then(values => values[0]);
export const vpcPrivateSubnetId2 = vpcPrivateSubnetIds.then(values => values[1]);
export const vpcPublicSubnetId2 = vpcPublicSubnetIds.then(values => values[1]);


//////////////////////////////////////////////////////////////
// Set up EC2 instance 
//      - it is intended to be used for troubleshooting
//////////////////////////////////////////////////////////////

// Create a new security group that permits SSH and web access.
const secgrp = new aws.ec2.SecurityGroup("secgrp", {
    description: "gitcoin",
    vpcId: vpc.id,
    ingress: [
        { protocol: "tcp", fromPort: 22, toPort: 22, cidrBlocks: ["0.0.0.0/0"] },
        { protocol: "tcp", fromPort: 80, toPort: 80, cidrBlocks: ["0.0.0.0/0"] },
    ],
    egress: [{
        protocol: "-1",
        fromPort: 0,
        toPort: 0,
        cidrBlocks: ["0.0.0.0/0"],
    }],
});

export const securityGroupsForEc2 = secgrp.id;

const ubuntu = aws.ec2.getAmi({
    mostRecent: true,
    filters: [
        {
            name: "name",
            values: ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"],
        },
        {
            name: "virtualization-type",
            values: ["hvm"],
        },
    ],
    owners: ["099720109477"],
});

// Script to install docker in ec2 instance
const ec2InitScript = `#!/bin/bash

# Installing docker in ubuntu
# Instructions taken from here: https://docs.docker.com/engine/install/ubuntu/

mkdir /var/log/gitcoin
echo $(date) "Starting installation of docker" >> /var/log/gitcoin/init.log
apt-get remove docker docker-engine docker.io containerd runc

apt-get update

apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
    
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
  
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io
mkdir /var/log/gitcoin
echo $(date) "Finished installation of docker" >> /var/log/gitcoin/init.log

`

const web = new aws.ec2.Instance("Web", {
    ami: ubuntu.then(ubuntu => ubuntu.id),
    associatePublicIpAddress: true,
    instanceType: "t3.micro",
    subnetId: vpcPublicSubnetId1.then(),

    vpcSecurityGroupIds: [secgrp.id],
    rootBlockDevice: {
        volumeSize: 50
    },
    tags: {
        Name: "Troubleshooting instance",
    },
    userData: ec2InitScript,
});

export const ec2PublicIp = web.publicIp;
