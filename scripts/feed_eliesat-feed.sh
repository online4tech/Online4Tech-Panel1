#!/bin/bash

#remove feed
if [ -f /etc/opkg/eliesat-feed.conf ]; then

echo "> Removing Eliesat Feed Please Wait ..."
sleep 3
rm -rf /etc/opkg/eliesat-feed.conf > /dev/null 2>&1
rm -rf /var/lib/opkg/lists/* > /dev/null 2>&1
opkg update

echo "*******************************************"
echo "*             Removed Finished            *"
echo "*            Uploaded By Eliesat          *"
echo "*******************************************"
sleep 3

else
echo "> Installing Eliesat Feed Please Wait ..."
sleep 3

echo "src/gz eliesat-feed https://github.com/eliesat/feed/raw/main/" >>/etc/opkg/eliesat-feed.conf

opkg update
echo " "
sleep 3
echo "> Eliesat feed installed successfully"
sleep 3
fi