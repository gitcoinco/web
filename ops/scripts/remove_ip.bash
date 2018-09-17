#!/bin/bash

GC_SSH_PORT=$(cat app/app/.env | grep "GC_SSH_PORT" | awk -F "=" '{print $2}')
GC_SG_ID=$(cat app/app/.env | grep "GC_SG_ID" | awk -F "=" '{print $2}')

: "${GC_SSH_PORT?You need to set GC_SSH_PORT in .env}"
: "${GC_SG_ID?You need to set GC_SG_ID in .env}"

CURRENT_USER=$(whoami)
WAN_IP=$(curl v4.ifconfig.co)/32
GC_SSH_PROTO=${GC_SSH_PROTO:-'tcp'}

echo "Removing IP: $WAN_IP to AWS SG: $GC_SG_ID - Port: $GC_SSH_PORT - Protocol: $GC_SSH_PROTO"
aws ec2 revoke-security-group-ingress --group-id "$GC_SG_ID" \
    --ip-permissions='[{"IpProtocol": "'"$GC_SSH_PROTO"'", "FromPort": '"$GC_SSH_PORT"', "ToPort": '"$GC_SSH_PORT"', "IpRanges": [{"CidrIp": "'"$WAN_IP"'"}]}]'
echo "Removed!"
