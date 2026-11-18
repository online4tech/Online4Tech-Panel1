#!/bin/sh
#
echo " INSALLER Plugin SKIN TeamNitro "
 MY_URL="https://gitlab.com/emilnabil1/teamnitro/-/raw/main" MY_EM='=============================================================' 
echo $MY_EM 
echo '' 
cd /tmp 
set -e 
wget "https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/packages/TeamNitro.tar.gz" 
echo "=================================" 
set +e 
cd .. 
wait 
rm -rf /usr/lib/enigma2/python/Plugins/Extensions/TeamNitro  echo ''
echo $MY_EM 
echo 'Extracting ...' 
echo '' 
tar -xvf /tmp/TeamNitro.tar.gz -C / 
sleep 2; 
rm -f /tmp/TeamNitro.tar.gz echo '' 
echo '' 
echo "#####################################################################" 
echo "# >>>>>>>>> UPLODED BY EMIL_NABIL   #" 
sleep 4; 
echo "#####################################################################" 
echo "#  PLEASE RESTART  Your Device Now #" 
exit
