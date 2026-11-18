#!/bin/sh
###wget --no-check-certificate -O - https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/packages/AutoSub.sh | /bin/sh
###################

echo "install shiavoice"
sleep 2

cd /tmp

curl -k -L -o /tmp/shiavoice.tar.gz "https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/packages/AutoSub.tar.gz"

sleep 1
echo "installing ...."

cd /tmp

if [ -f /tmp/AutoSub.tar.gz ]; then
    tar -xzf AutoSub.tar.gz -C /
    echo ""
    echo "OK"
else
    echo "ERROR: Download failed!"
    exit 1
fi

sleep 1
cd
rm -f /tmp/AutoSub.tar.gz

echo " UPLOADED BY EMIL_NABIL"
sleep 4
echo ""
echo ""
exit


