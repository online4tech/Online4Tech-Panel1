#!/bin/sh
##Install (wget https://ia803104.us.archive.org/0/items/freecccamserver/installer.sh -O - | /bin/sh)

version=8.3.8

# check depends packges
if [ -f /var/lib/dpkg/status ]; then
   STATUS=/var/lib/dpkg/status
   OSTYPE=DreamOs
   ext=deb
else
   STATUS=/var/lib/opkg/status
   OSTYPE=Dream
   ext=ipk
fi

if [ $OSTYPE = "DreamOs" ]; then
    apt-get update
else
    opkg update
fi

if python --version 2>&1 | grep -q '^Python 3\.'; then
    echo "You have Python3 image"
    PYTHON=PY3
    Packagerequests=python3-requests
    Packagepillow=python3-pillow
else
    echo "You have Python2 image"
    PYTHON=PY2
    Packagerequests=python-requests
    Packagepillow=python-pillow
fi

if grep -qs "Package: $Packagerequests" cat $STATUS ; then
    echo ""
else
    echo "Need to install $Packagerequests"
    echo ""
    if [ $OSTYPE = "DreamOs" ]; then
        apt-get update && apt-get install $Packagerequests -y
    else
        opkg update && opkg install $Packagerequests
    fi
fi
if grep -qs "Package: $Packagepillow" cat $STATUS ; then
    echo ""
else
    echo "Need to install $Packagepillow"
    echo ""
    if [ $OSTYPE = "DreamOs" ]; then
        apt-get update && apt-get install $Packagepillow -y
    else
        opkg update && opkg install $Packagepillow
    fi
fi
echo ""
if grep -qs "Package: wget" cat $STATUS ; then
    echo ""
else
    echo "Need to install wget"
    echo ""
    if [ $OSTYPE = "DreamOs" ]; then
        apt-get update && apt-get install wget
    else
        opkg update && opkg install wget
    fi
fi
echo ""
if grep -qs "Package: coreutils" cat $STATUS ; then
    echo ""
else
    echo "Need to install coreutils"
    echo ""
    if [ $OSTYPE = "DreamOs" ]; then
        apt-get update && apt-get install coreutils
    else
        opkg update && opkg install coreutils
    fi
fi
echo ""
if grep -qs "Package: curl" cat $STATUS ; then
    echo ""
else
    echo "Need to install curl"
    echo ""
    if [ $OSTYPE = "DreamOs" ]; then
        apt-get update && apt-get install curl
    else
        opkg update && opkg install curl
    fi
fi
echo ""
if grep -qs "Package: coreutils-truefalse" cat $STATUS ; then
    echo ""
else
    echo "Need to install coreutils-truefalse"
    echo ""
    if [ $OSTYPE = "DreamOs" ]; then
        apt-get update && apt-get install coreutils-truefalse
    else
        opkg update && opkg install coreutils-truefalse
    fi
fi

cd /tmp
rm -f *enigma2-plugin-extensions-freeserver*
# Download new version
wget "https://ia903104.us.archive.org/0/items/freecccamserver/enigma2-plugin-extensions-freeserver_"$version"_all.$ext"

# remove old version
if [ -f /tmp/enigma2-plugin-extensions-freeserver_"$version"_all.$ext ]; then
    if [ -f /var/lib/dpkg/status ]; then
           apt-get -r enigma2-plugin-extensions-freeserver
    else
           opkg remove enigma2-plugin-extensions-freeserver
    fi
fi

# Install new version
echo "****** Install New version ******"
if [ $OSTYPE = "DreamOs" ]; then
    dpkg -i enigma2-plugin-extensions-freeserver_"$version"_all.deb && apt-get install -f
else
    opkg install enigma2-plugin-extensions-freeserver_"$version"_all.ipk
fi
# Update Server
#echo "****** Update Servers ******"
#wget https://ia803104.us.archive.org/0/items/freecccamserver/FreeServer.sh -O - | /bin/sh
#
set +e
rm -f *enigma2-plugin-extensions-freeserver*
cd ..

sync
echo "#########################################################"
echo "#      freecccamserver INSTALLED SUCCESSFULLY           #"
echo "#########################################################"
echo "#           your Device will RESTART Now                #"
echo "#########################################################"
sleep 3
killall -9 enigma2
exit 0