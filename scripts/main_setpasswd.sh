#!/bin/sh
##command=wget -q "--no-check-certificate" https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/packages/setpasswd.sh -O - | /bin/sh
#########################################
echo "install plugin"
cd /tmp
if command -v wget >/dev/null 2>&1; then
    wget -q --no-check-certificate -O setpasswd.tar.gz "https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/packages/setpasswd.tar.gz"
else
    curl -k -L -o setpasswd.tar.gz "https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/packages/setpasswd.tar.gz"
fi
sleep 1
echo "install plugin...."
cd /tmp
tar -xzf setpasswd.tar.gz -C /
sleep 2
rm -f setpasswd.tar.gz
sleep 2
exit
