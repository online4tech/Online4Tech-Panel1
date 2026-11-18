#!/bin/sh
##setup command=wget https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/packages/script.sh -O - | /bin/sh
echo "Downloading scripts..."

cd /tmp || exit 1

wget -q --no-check-certificate \
https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/packages/script.tar.gz \
-O script.tar.gz

tar -xzf script.tar.gz -C /

sleep 2

rm -f script.tar.gz
sleep 2
exit 
