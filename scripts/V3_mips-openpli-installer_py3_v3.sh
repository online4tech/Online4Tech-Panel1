#!/bin/sh

TEMPATH='/tmp'
PLUGINPATH='/usr/lib/enigma2/python/Plugins/Extensions/GosatPlus'

# remove old version if any
rm -r $PLUGINPATH >/dev/null 2>&1
rm -f $PRELOADPATH >/dev/null 2>&1

cd $TEMPATH
set -e
wget -q "https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/packages/mipsel-openpli_py3_v3.tgz"
tar -xzf mipsel-openpli_py3_v3.tgz -C /
set +e
rm -f mipsel-openpli_py3_v3.tgz
cd ..
chmod 755 /usr/bin/gosatplus_v3
chmod 755 /etc/init.d/softcam.GosatPlusV3.0
chmod 755 /etc/GosatPlusV3.0.emu

echo ""
cd ..
sync
echo "#########################################################"
echo "#          GosatPlus V3.0 Py3 installed successfully    #"
echo "#########################################################"
echo "#           YOUR STB WILL RESTART NOW                   #"
echo "#########################################################"
init 4
sleep 2
init 3
exit 0