#!/bin/sh
# ==============================================================================
#  ONLINE4TECH SUPER SCRIPT v2.0 - Categorized Enigma2 Manager
#  By: Ahmed Nagi Romeh (Online4Tech)
# ==============================================================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
WHITE='\033[1;37m'
MAGENTA='\033[0;35m'
NC='\033[0m'

REPO_BASE="https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main"
DB_URL="$REPO_BASE/database.txt"
DB_FILE="/tmp/o4t_db.txt"

# تحميل قاعدة البيانات عند التشغيل
fetch_db() {
    wget --no-check-certificate -qO "$DB_FILE" "$DB_URL"
    if [ ! -s "$DB_FILE" ]; then
        echo -e "${RED}[ERROR] Failed to connect to Online4Tech Server!${NC}"
        exit 1
    fi
    sed -i 's/\r$//' "$DB_FILE"
}

# دالة التثبيت الموحدة (IPK & DEB)
install_pkg() {
    TITLE="$1"
    URL="$2"
    echo -e "\n${CYAN}====================================================${NC}"
    echo -e "${YELLOW}[Online4Tech] Downloading: ${WHITE}$TITLE${NC}"
    echo -e "${CYAN}====================================================${NC}"
    
    if echo "$URL" | grep -qi "\.deb$"; then
        TMP_FILE="/tmp/o4t_pkg.deb"
        wget --no-check-certificate -q --show-progress -O "$TMP_FILE" "$URL" 2>/dev/null || wget --no-check-certificate -qO "$TMP_FILE" "$URL"
        if [ -s "$TMP_FILE" ]; then
            dpkg -i --force-overwrite "$TMP_FILE"
            apt-get update && apt-get -f install -y
            echo -e "\n${GREEN}[SUCCESS] $TITLE Installed Successfully!${NC}"
        else
            echo -e "\n${RED}[ERROR] File not found on server or download failed!${NC}"
        fi
        rm -f "$TMP_FILE"
    else
        TMP_FILE="/tmp/o4t_pkg.ipk"
        wget --no-check-certificate -q --show-progress -O "$TMP_FILE" "$URL" 2>/dev/null || wget --no-check-certificate -qO "$TMP_FILE" "$URL"
        if [ -s "$TMP_FILE" ]; then
            opkg update >/dev/null 2>&1
            opkg install --force-overwrite --force-depends "$TMP_FILE"
            echo -e "\n${GREEN}[SUCCESS] $TITLE Installed Successfully!${NC}"
        else
            echo -e "\n${RED}[ERROR] File not found on server or download failed!${NC}"
        fi
        rm -f "$TMP_FILE"
    fi
    printf "\nPress Enter to continue..."
    read -r _
}

# محرك عرض القوائم الديناميكي حسب التصنيف
show_category_menu() {
    CAT_CODE="$1"
    CAT_TITLE="$2"
    
    while true; do
        clear
        echo -e "${CYAN}====================================================${NC}"
        echo -e "${WHITE}   ONLINE4TECH - $CAT_TITLE${NC}"
        echo -e "${CYAN}====================================================${NC}"
        
        # استخراج عناصر القسم وترقيمها تلقائيا
        ITEMS=$(grep "^${CAT_CODE}|" "$DB_FILE")
        if [ -z "$ITEMS" ]; then
            echo -e " ${YELLOW}No items available in this section yet.${NC}"
            echo -e "${CYAN}====================================================${NC}"
            printf "Press Enter to go back..."
            read -r _
            break
        fi

        IDX=0
        echo "$ITEMS" | while IFS='|' read -r CAT NAME URL; do
            IDX=$((IDX + 1))
            printf "  ${YELLOW}[%2d]${NC} %s\n" "$IDX" "$NAME"
        done

        echo -e "${CYAN}----------------------------------------------------${NC}"
        echo -e "  ${RED}[ 0]${NC} Back (رجوع)"
        echo -e "${CYAN}====================================================${NC}"
        printf "Enter Number: "
        read -r CHOICE

        if [ "$CHOICE" = "0" ] || [ -z "$CHOICE" ]; then
            break
        fi

        SELECTED=$(echo "$ITEMS" | sed -n "${CHOICE}p")
        if [ -n "$SELECTED" ]; then
            SEL_NAME=$(echo "$SELECTED" | cut -d'|' -f2)
            SEL_URL=$(echo "$SELECTED" | cut -d'|' -f3)
            install_pkg "$SEL_NAME" "$SEL_URL"
        else
            echo -e "${RED}Invalid selection!${NC}"
            sleep 1
        fi
    done
}

# 1. قائمة أقسام البلجنات
menu_plugins_categories() {
    while true; do
        clear
        echo -e "${CYAN}====================================================${NC}"
        echo -e "${GREEN}      ONLINE4TECH - PLUGINS CATEGORIES (البلجنات)    ${NC}"
        echo -e "${CYAN}====================================================${NC}"
        echo -e "  ${YELLOW}[1]${NC} Panels & Feeds (لوحات التحكم والـ Feeds)"
        echo -e "  ${YELLOW}[2]${NC} IPTV & Media Players (مشغلات IPTV والميديا)"
        echo -e "  ${YELLOW}[3]${NC} Subtitles, EPG & Picons (الترجمة والبيكونات)"
        echo -e "  ${YELLOW}[4]${NC} System, Backup & Tools (أدوات النظام والباك أب)"
        echo -e "${CYAN}----------------------------------------------------${NC}"
        echo -e "  ${RED}[0]${NC} Back to Main Menu (رجوع)"
        echo -e "${CYAN}====================================================${NC}"
        printf "Select Category [0-4]: "
        read -r P_CAT
        case "$P_CAT" in
            1) show_category_menu "P_PANEL" "PANELS & FEEDS" ;;
            2) show_category_menu "P_IPTV" "IPTV & MEDIA PLAYERS" ;;
            3) show_category_menu "P_SUB_EPG" "SUBTITLES, EPG & PICONS" ;;
            4) show_category_menu "P_SYS" "SYSTEM & BACKUP TOOLS" ;;
            0) break ;;
            *) echo -e "${RED}Invalid choice!${NC}"; sleep 1 ;;
        esac
    done
}

# 2. قائمة أقسام السكينات
menu_skins_categories() {
    while true; do
        clear
        echo -e "${CYAN}====================================================${NC}"
        echo -e "${MAGENTA}       ONLINE4TECH - SKINS CATEGORIES (السكينات)     ${NC}"
        echo -e "${CYAN}====================================================${NC}"
        echo -e "  ${YELLOW}[1]${NC} OpenATV / OpenPLi / Egami Skins (.ipk)"
        echo -e "  ${YELLOW}[2]${NC} DreamOS OE2.5 / OE2.6 Skins (.deb)"
        echo -e "${CYAN}----------------------------------------------------${NC}"
        echo -e "  ${RED}[0]${NC} Back to Main Menu (رجوع)"
        echo -e "${CYAN}====================================================${NC}"
        printf "Select Skin Type [0-2]: "
        read -r S_CAT
        case "$S_CAT" in
            1) show_category_menu "S_OPEN" "OPEN IMAGES SKINS (IPK)" ;;
            2) show_category_menu "S_DREAM" "DREAMOS SKINS (DEB)" ;;
            0) break ;;
            *) echo -e "${RED}Invalid choice!${NC}"; sleep 1 ;;
        esac
    done
}

# 3. قائمة الإيموهات وملفات القنوات
menu_cams_channels() {
    while true; do
        clear
        echo -e "${CYAN}====================================================${NC}"
        echo -e "${GREEN}   ONLINE4TECH - SOFTCAMS, KEYS & CHANNEL LISTS     ${NC}"
        echo -e "${CYAN}====================================================${NC}"
        echo -e "  ${YELLOW}[1]${NC} Install Softcams (NCam / OSCam)"
        echo -e "  ${YELLOW}[2]${NC} Update Latest SoftCam.Key (تحديث الشفرات)"
        echo -e "  ${YELLOW}[3]${NC} Update Motor Channels (قنوات المتحرك)"
        echo -e "  ${YELLOW}[4]${NC} Update Nilesat Channels (قنوات نايل سات)"
        echo -e "${CYAN}----------------------------------------------------${NC}"
        echo -e "  ${RED}[0]${NC} Back to Main Menu (رجوع)"
        echo -e "${CYAN}====================================================${NC}"
        printf "Select Option [0-4]: "
        read -r C_OPT
        case "$C_OPT" in
            1) show_category_menu "CAM" "SOFTCAMS (NCAM / OSCAM)" ;;
            2)
               echo -e "\n${CYAN}Updating SoftCam.Key...${NC}"
               mkdir -p /etc/tuxbox/config
               wget --no-check-certificate -qO /etc/tuxbox/config/SoftCam.Key "https://raw.githubusercontent.com/online4tech/Chanal-List/main/SoftCam.Key"
               echo -e "${GREEN}[SUCCESS] SoftCam.Key Updated!${NC}"; sleep 2 ;;
            3)
               echo -e "\n${CYAN}Downloading Motor Channels...${NC}"
               wget --no-check-certificate -qO /tmp/motor.tar.gz "https://raw.githubusercontent.com/online4tech/Chanal-List/main/motor_channels.tar.gz"
               if [ -s /tmp/motor.tar.gz ]; then
                   tar -xzf /tmp/motor.tar.gz -C /
                   wget -qO - "http://127.0.0.1/web/servicelistreload?mode=0" >/dev/null 2>&1
                   rm -f /tmp/motor.tar.gz
                   echo -e "${GREEN}[SUCCESS] Motor Channels Installed & Reloaded!${NC}"
               else
                   echo -e "${RED}[ERROR] Motor Channels archive not found!${NC}"
               fi
               sleep 2 ;;
            4)
               echo -e "\n${CYAN}Downloading Nilesat Channels...${NC}"
               wget --no-check-certificate -qO /tmp/nilesat.tar.gz "https://raw.githubusercontent.com/online4tech/Chanal-List/main/nilesat_channels.tar.gz"
               if [ -s /tmp/nilesat.tar.gz ]; then
                   tar -xzf /tmp/nilesat.tar.gz -C /
                   wget -qO - "http://127.0.0.1/web/servicelistreload?mode=0" >/dev/null 2>&1
                   rm -f /tmp/nilesat.tar.gz
                   echo -e "${GREEN}[SUCCESS] Nilesat Channels Installed & Reloaded!${NC}"
               else
                   echo -e "${RED}[ERROR] Nilesat Channels archive not found!${NC}"
               fi
               sleep 2 ;;
            0) break ;;
            *) echo -e "${RED}Invalid choice!${NC}"; sleep 1 ;;
        esac
    done
}

# 4. قائمة الأوامر المتقدمة وصيانة الرسيفر
menu_commands() {
    while true; do
        clear
        echo -e "${CYAN}====================================================${NC}"
        echo -e "${YELLOW}    ONLINE4TECH - RECEIVER COMMANDS & MAINTENANCE   ${NC}"
        echo -e "${CYAN}====================================================${NC}"
        echo -e "  ${YELLOW}[1]${NC} Receiver Info (CPU Arch, Python, Image, RAM)"
        echo -e "  ${YELLOW}[2]${NC} Clear RAM & Free Cache (تنظيف الرامات)"
        echo -e "  ${YELLOW}[3]${NC} Check Flash & HDD/USB Space (فحص المساحة)"
        echo -e "  ${YELLOW}[4]${NC} Update Image Feeds (opkg update)"
        echo -e "  ${YELLOW}[5]${NC} Fix Broken Packages (إصلاح الحزم المعلقة)"
        echo -e "  ${YELLOW}[6]${NC} Clean /tmp Folder (تنظيف الملفات المؤقتة)"
        echo -e "  ${YELLOW}[7]${NC} Restart Enigma2 GUI (ريستارت الواجهة)"
        echo -e "  ${YELLOW}[8]${NC} Full Receiver Reboot (إعادة تشغيل كاملة)"
        echo -e "${CYAN}----------------------------------------------------${NC}"
        echo -e "  ${RED}[0]${NC} Back to Main Menu (رجوع)"
        echo -e "${CYAN}====================================================${NC}"
        printf "Select Command [0-8]: "
        read -r CMD_OPT
        case "$CMD_OPT" in
            1)
               echo -e "\n${CYAN}--- System Information ---${NC}"
               echo -e "${GREEN}Architecture:${NC} $(uname -m)"
               echo -e "${GREEN}Kernel:${NC} $(uname -r)"
               echo -e "${GREEN}Python:${NC} $(python3 --version 2>&1 || python --version 2>&1)"
               echo -e "${GREEN}Memory:${NC}"
               free -h 2>/dev/null || free
               printf "\nPress Enter..."
               read -r _ ;;
            2)
               sync; echo 3 > /proc/sys/vm/drop_caches
               echo -e "\n${GREEN}[SUCCESS] RAM & Cache Cleared!${NC}"; sleep 2 ;;
            3)
               echo -e "\n${CYAN}--- Storage Status ---${NC}"
               df -h | grep -E "Filesystem|/dev/root|/media/hdd|/media/usb"
               printf "\nPress Enter..."
               read -r _ ;;
            4)
               echo -e "\n${CYAN}Updating Feeds...${NC}"
               opkg update
               printf "\nPress Enter..."
               read -r _ ;;
            5)
               echo -e "\n${CYAN}Fixing Broken Packages...${NC}"
               opkg configure
               echo -e "${GREEN}[DONE]${NC}"; sleep 2 ;;
            6)
               rm -rf /tmp/*.ipk /tmp/*.deb /tmp/*.tar.gz /tmp/*.zip
               echo -e "\n${GREEN}[SUCCESS] /tmp Cleaned!${NC}"; sleep 2 ;;
            7)
               echo -e "\n${YELLOW}Restarting Enigma2 GUI...${NC}"
               killall -9 enigma2 ;;
            8)
               echo -e "\n${RED}Rebooting Receiver Now...${NC}"
               reboot ;;
            0) break ;;
            *) echo -e "${RED}Invalid choice!${NC}"; sleep 1 ;;
        esac
    done
}

# ------------------------------------------------------------------------------
# تشغيل السكربت وجلب قاعدة البيانات
# ------------------------------------------------------------------------------
fetch_db

while true; do
    clear
    echo -e "${CYAN}====================================================${NC}"
    echo -e "${WHITE}         ONLINE4TECH SUPER SCRIPT (v2.0)            ${NC}"
    echo -e "${GREEN}    All-in-One Control Center for Vu+ & Dreambox    ${NC}"
    echo -e "${CYAN}====================================================${NC}"
    echo -e "  ${YELLOW}[1]${NC} Plugins Categories (أقسام البلجنات)"
    echo -e "  ${YELLOW}[2]${NC} Skins Categories   (أقسام السكينات)"
    echo -e "  ${YELLOW}[3]${NC} Softcams & Channels (الإيموهات والقنوات)"
    echo -e "  ${YELLOW}[4]${NC} System Commands    (أوامر الصيانة والتحكم)"
    echo -e "  ${YELLOW}[5]${NC} Refresh Database   (تحديث قائمة السيرفر)"
    echo -e "${CYAN}----------------------------------------------------${NC}"
    echo -e "  ${RED}[0]${NC} Exit (خروج)"
    echo -e "${CYAN}====================================================${NC}"
    printf "Enter Choice [0-5]: "
    read -r MAIN_OPT

    case "$MAIN_OPT" in
        1) menu_plugins_categories ;;
        2) menu_skins_categories ;;
        3) menu_cams_channels ;;
        4) menu_commands ;;
        5) fetch_db; echo -e "${GREEN}[OK] Database Refreshed!${NC}"; sleep 1 ;;
        0) rm -f /tmp/o4t_super.sh "$DB_FILE"; echo -e "${GREEN}Goodbye from Online4Tech!${NC}"; exit 0 ;;
        *) echo -e "${RED}Wrong choice!${NC}"; sleep 1 ;;
    esac
done