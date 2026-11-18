#!/bin/sh
# ==============================================================================
#  Online4Tech Super Script - All-in-One Enigma2 Manager
# ==============================================================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
WHITE='\033[1;37m'
NC='\033[0m'

REPO_BASE="https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main"

install_pkg() {
    TITLE="$1"
    URL="$2"
    echo -e "\n${CYAN}[Online4Tech] Installing: ${YELLOW}$TITLE${NC}"
    if echo "$URL" | grep -qi "\.deb$"; then
        TMP_FILE="/tmp/o4t_temp.deb"
        wget -q --no-check-certificate -O "$TMP_FILE" "$URL"
        if [ -s "$TMP_FILE" ]; then
            dpkg -i --force-overwrite "$TMP_FILE"
            apt-get update && apt-get -f install -y
            echo -e "${GREEN}[OK] $TITLE Installed!${NC}"
        else
            echo -e "${RED}[ERROR] Download failed! Check URL.${NC}"
        fi
        rm -f "$TMP_FILE"
    else
        TMP_FILE="/tmp/o4t_temp.ipk"
        wget -q --no-check-certificate -O "$TMP_FILE" "$URL"
        if [ -s "$TMP_FILE" ]; then
            opkg update >/dev/null 2>&1
            opkg install --force-overwrite --force-depends "$TMP_FILE"
            echo -e "${GREEN}[OK] $TITLE Installed!${NC}"
        else
            echo -e "${RED}[ERROR] Download failed! Check URL.${NC}"
        fi
        rm -f "$TMP_FILE"
    fi
    sleep 2
}

menu_plugins() {
    while true; do
        clear
        echo -e "${CYAN}====================================================${NC}"
        echo -e "${GREEN}         Online4Tech - Plugins Section              ${NC}"
        echo -e "${CYAN}====================================================${NC}"
        echo -e " ${YELLOW}[1]${NC} Online4Tech Panel v7.0"
        echo -e " ${YELLOW}[2]${NC} AJPanel (Latest)"
        echo -e " ${YELLOW}[3]${NC} SubsSupport"
        echo -e " ${YELLOW}[4]${NC} E2iPlayer"
        echo -e " ${YELLOW}[5]${NC} MultiStalker Pro"
        echo -e " ${RED}[0]${NC} Back to Main Menu"
        echo -e "${CYAN}====================================================${NC}"
        printf "Select Plugin: "
        read -r P_OPT
        case "$P_OPT" in
            1) install_pkg "Online4Tech Panel 7.0" "$REPO_BASE/enigma2-plugin-extensions-online4tech_7.0_all.ipk" ;;
            2) install_pkg "AJPanel" "$REPO_BASE/plugins/ajpanel.ipk" ;;
            3) install_pkg "SubsSupport" "$REPO_BASE/plugins/subssupport.ipk" ;;
            4) install_pkg "E2iPlayer" "$REPO_BASE/plugins/e2iplayer.ipk" ;;
            5) install_pkg "MultiStalker Pro" "$REPO_BASE/plugins/multistalker.ipk" ;;
            0) break ;;
            *) echo -e "${RED}Invalid option!${NC}"; sleep 1 ;;
        esac
    done
}

menu_skins() {
    while true; do
        clear
        echo -e "${CYAN}====================================================${NC}"
        echo -e "${GREEN}          Online4Tech - Skins Section               ${NC}"
        echo -e "${CYAN}====================================================${NC}"
        echo -e " ${YELLOW}[1]${NC} MetrixHD Mod"
        echo -e " ${YELLOW}[2]${NC} MadMax Impossible FHD"
        echo -e " ${YELLOW}[3]${NC} Boomerang FHD"
        echo -e " ${YELLOW}[4]${NC} Aglare FHD"
        echo -e " ${RED}[0]${NC} Back to Main Menu"
        echo -e "${CYAN}====================================================${NC}"
        printf "Select Skin: "
        read -r S_OPT
        case "$S_OPT" in
            1) install_pkg "MetrixHD Mod" "$REPO_BASE/skins/metrixhd.ipk" ;;
            2) install_pkg "MadMax FHD" "$REPO_BASE/skins/madmax.ipk" ;;
            3) install_pkg "Boomerang FHD" "$REPO_BASE/skins/boomerang.ipk" ;;
            4) install_pkg "Aglare FHD" "$REPO_BASE/skins/aglare.ipk" ;;
            0) break ;;
            *) echo -e "${RED}Invalid option!${NC}"; sleep 1 ;;
        esac
    done
}

menu_cams_channels() {
    while true; do
        clear
        echo -e "${CYAN}====================================================${NC}"
        echo -e "${GREEN}      Online4Tech - Softcams & Channel Lists        ${NC}"
        echo -e "${CYAN}====================================================${NC}"
        echo -e " ${YELLOW}[1]${NC} NCam Official"
        echo -e " ${YELLOW}[2]${NC} OSCam Emu"
        echo -e " ${YELLOW}[3]${NC} Update Motor Channels List"
        echo -e " ${YELLOW}[4]${NC} Update Nilesat Channels List"
        echo -e " ${RED}[0]${NC} Back to Main Menu"
        echo -e "${CYAN}====================================================${NC}"
        printf "Select Option: "
        read -r C_OPT
        case "$C_OPT" in
            1) install_pkg "NCam" "$REPO_BASE/cams/ncam.ipk" ;;
            2) install_pkg "OSCam" "$REPO_BASE/cams/oscam.ipk" ;;
            3) 
               echo -e "${CYAN}Updating Motor Channels...${NC}"
               wget -qO /tmp/channels.tar.gz "https://raw.githubusercontent.com/online4tech/Chanal-List/main/motor_channels.tar.gz"
               tar -xzf /tmp/channels.tar.gz -C /
               wget -qO - "http://127.0.0.1/web/servicelistreload?mode=0" >/dev/null 2>&1
               rm -f /tmp/channels.tar.gz
               echo -e "${GREEN}[OK] Channels Reloaded!${NC}"; sleep 2 ;;
            4)
               echo -e "${CYAN}Updating Nilesat Channels...${NC}"
               wget -qO /tmp/nilesat.tar.gz "https://raw.githubusercontent.com/online4tech/Chanal-List/main/nilesat_channels.tar.gz"
               tar -xzf /tmp/nilesat.tar.gz -C /
               wget -qO - "http://127.0.0.1/web/servicelistreload?mode=0" >/dev/null 2>&1
               rm -f /tmp/nilesat.tar.gz
               echo -e "${GREEN}[OK] Nilesat Reloaded!${NC}"; sleep 2 ;;
            0) break ;;
            *) echo -e "${RED}Invalid option!${NC}"; sleep 1 ;;
        esac
    done
}

menu_tools() {
    while true; do
        clear
        echo -e "${CYAN}====================================================${NC}"
        echo -e "${GREEN}        Online4Tech - System & Maintenance          ${NC}"
        echo -e "${CYAN}====================================================${NC}"
        echo -e " ${YELLOW}[1]${NC} Clear RAM & Cache"
        echo -e " ${YELLOW}[2]${NC} Check Disk Space"
        echo -e " ${YELLOW}[3]${NC} Restart Enigma2 GUI"
        echo -e " ${YELLOW}[4]${NC} Full Receiver Reboot"
        echo -e " ${RED}[0]${NC} Back to Main Menu"
        echo -e "${CYAN}====================================================${NC}"
        printf "Select Tool: "
        read -r T_OPT
        case "$T_OPT" in
            1) sync; echo 3 > /proc/sys/vm/drop_caches; echo -e "${GREEN}[OK] RAM Cleared!${NC}"; sleep 2 ;;
            2) df -h | grep -E "Filesystem|/dev/root|/media/hdd|/media/usb"; printf "\nPress Enter..."; read -r _ ;;
            3) echo -e "${YELLOW}Restarting GUI...${NC}"; killall -9 enigma2 ;;
            4) echo -e "${RED}Rebooting...${NC}"; reboot ;;
            0) break ;;
            *) echo -e "${RED}Invalid option!${NC}"; sleep 1 ;;
        esac
    done
}

while true; do
    clear
    echo -e "${CYAN}====================================================${NC}"
    echo -e "${WHITE}         ONLINE4TECH SUPER SCRIPT (v1.0)            ${NC}"
    echo -e "${GREEN}      All-in-One Control for Vu+ & Dreambox         ${NC}"
    echo -e "${CYAN}====================================================${NC}"
    echo -e "  ${YELLOW}[1]${NC} Plugins (البلجنات)"
    echo -e "  ${YELLOW}[2]${NC} Skins (السكينات)"
    echo -e "  ${YELLOW}[3]${NC} Softcams & Channels (الإيموهات والقنوات)"
    echo -e "  ${YELLOW}[4]${NC} System Tools (أدوات الصيانة)"
    echo -e "  ${RED}[0]${NC} Exit (خروج)"
    echo -e "${CYAN}====================================================${NC}"
    printf "Enter Choice [0-4]: "
    read -r MAIN_OPT

    case "$MAIN_OPT" in
        1) menu_plugins ;;
        2) menu_skins ;;
        3) menu_cams_channels ;;
        4) menu_tools ;;
        0) rm -f /tmp/o4t_super.sh; echo -e "${GREEN}Goodbye from Online4Tech!${NC}"; exit 0 ;;
        *) echo -e "${RED}Wrong choice!${NC}"; sleep 1 ;;
    esac
done