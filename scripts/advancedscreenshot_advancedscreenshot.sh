#!/bin/sh
##setup command=wget https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/packages/advancedscreenshot.sh -O - | /bin/sh ###
####################################
echo "install plugin advancedscreenshot"
cd /tmp
curl  -k -Lbk -m 55532 -m 555104 "https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/packages/enigma2-plugin-extensions-advancedscreenshot_all.ipk" > /tmp/enigma2-plugin-extensions-advancedscreenshot_all.ipk
sleep 1
echo "install plugin...."
cd /tmp
opkg install /tmp/enigma2-plugin-extensions-advancedscreenshot_all.ipk
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
sleep 1
rm /tmp/enigma2-plugin-extensions-advancedscreenshot_all.ipk
sleep 2
exit
