#!/bin/bash
##command=wget https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/packages/menusort.sh -O - | /bin/sh
######################
wget -O /var/volatile/tmp/menusort_v1.0_all.ipk "https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/packages/menusort_v1.0_all.ipk"
sleep 2
opkg install --force-overwrite /var/volatile/tmp/menusort_v1.0_all.ipk
sleep 2
rm -f /var/volatile/tmp/menusort_v1.0_all.ipk
sleep 2
exit 0
