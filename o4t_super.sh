#!/bin/sh
# ==============================================================================
#  ONLINE4TECH SUPER SCRIPT v3.0 - Full JSON Store Engine (350+ Items)
#  By: Ahmed Nagi Romeh (Online4Tech)
# ==============================================================================

DB_URL="https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/o4t_database.json"
DB_FILE="/tmp/o4t_database.json"
PY_RUNNER="/tmp/o4t_menu.py"

echo "Connecting to Online4Tech Store Server..."
wget --no-check-certificate -qO "$DB_FILE" "$DB_URL"

if [ ! -s "$DB_FILE" ]; then
    echo "[ERROR] Failed to download o4t_database.json from GitHub!"
    exit 1
fi

if command -v python3 >/dev/null 2>&1; then
    PY_BIN="python3"
else
    PY_BIN="python"
fi

cat << 'EOF' > "$PY_RUNNER"
import json, os, sys, re

DB_PATH = "/tmp/o4t_database.json"

C_CYAN   = "\033[0;36m"
C_GREEN  = "\033[0;32m"
C_YELLOW = "\033[1;33m"
C_RED    = "\033[0;31m"
C_WHITE  = "\033[1;37m"
C_NC     = "\033[0m"

def clear_screen():
    os.system("clear")

def clean_ascii(text):
    # إزالة أي نصوص عربية بين أقواس أو حروف غير لاتينية لمنع تشوه شاشة Telnet
    text = re.sub(r'\([^)]*[\u0600-\u06FF]+[^)]*\)', '', text)
    text = re.sub(r'[\u0600-\u06FF]+', '', text)
    return " ".join(text.split()).strip()

def get_input(prompt_text):
    try:
        if sys.version_info[0] >= 3:
            return input(prompt_text).strip()
        else:
            return raw_input(prompt_text).strip()
    except (EOFError, KeyboardInterrupt):
        return "0"

def load_db():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def run_command(title, cmd, is_remove=False):
    clear_screen()
    action = "UNINSTALLING" if is_remove else "INSTALLING"
    print(f"{C_CYAN}===================================================={C_NC}")
    print(f"{C_YELLOW}[Online4Tech] {action}: {C_WHITE}{title}{C_NC}")
    print(f"{C_CYAN}===================================================={C_NC}\n")
    os.system(cmd)
    print(f"\n{C_CYAN}===================================================={C_NC}")
    print(f"{C_GREEN}[DONE] Operation Finished!{C_NC}")
    get_input("Press Enter to continue...")

def show_items_menu(data, section_key, section_title):
    items = data.get(section_key, [])
    if items and isinstance(items[0], dict) and "section" in items[0]:
        while True:
            clear_screen()
            print(f"{C_CYAN}===================================================={C_NC}")
            print(f"{C_WHITE}   ONLINE4TECH - {section_title.upper()}{C_NC}")
            print(f"{C_CYAN}===================================================={C_NC}")
            for idx, sub in enumerate(items, 1):
                sub_t = clean_ascii(sub.get('title', sub.get('section')))
                print(f"  {C_YELLOW}[{idx:2d}]{C_NC} {sub_t}")
            print(f"{C_CYAN}----------------------------------------------------{C_NC}")
            print(f"  {C_RED}[ 0]{C_NC} Back")
            print(f"{C_CYAN}===================================================={C_NC}")
            choice = get_input("Select Sub-Category: ")
            if choice == "0" or not choice:
                break
            if choice.isdigit() and 1 <= int(choice) <= len(items):
                sub_item = items[int(choice) - 1]
                show_items_menu(data, sub_item["section"], clean_ascii(sub_item.get("title", sub_item["section"])))
        return

    page_size = 20
    total = len(items)
    page = 0

    while True:
        clear_screen()
        start = page * page_size
        end = min(start + page_size, total)
        print(f"{C_CYAN}===================================================={C_NC}")
        print(f"{C_WHITE}   {section_title} ({start+1}-{end} of {total}){C_NC}")
        print(f"{C_CYAN}===================================================={C_NC}")

        for i in range(start, end):
            item = items[i]
            clean_name = clean_ascii(item.get("name", "Unknown"))
            installed = "[*]" if item.get("path") and os.path.exists(item.get("path")) else "   "
            print(f" {C_GREEN}{installed}{C_NC} {C_YELLOW}[{i+1:3d}]{C_NC} {clean_name}")

        print(f"{C_CYAN}----------------------------------------------------{C_NC}")
        nav = f"  {C_RED}[0]{C_NC} Back"
        if end < total:
            nav += f"  |  {C_GREEN}[N]{C_NC} Next Page"
        if page > 0:
            nav += f"  |  {C_GREEN}[P]{C_NC} Prev Page"
        print(nav)
        print(f"{C_CYAN}===================================================={C_NC}")
        choice = get_input("Enter Number (or N/P/0): ").lower()

        if choice == "0" or not choice:
            break
        elif choice == "n" and end < total:
            page += 1
        elif choice == "p" and page > 0:
            page -= 1
        elif choice.isdigit() and 1 <= int(choice) <= total:
            sel = items[int(choice) - 1]
            clean_name = clean_ascii(sel.get("name", "Item"))
            if sel.get("remove_cmd"):
                print(f"\n  {C_GREEN}[1]{C_NC} Install: {clean_name}")
                print(f"  {C_RED}[2]{C_NC} Remove / Uninstall: {clean_name}")
                print(f"  {C_YELLOW}[0]{C_NC} Cancel")
                act = get_input("Action [1/2/0]: ")
                if act == "1":
                    run_command(clean_name, sel["cmd"], False)
                elif act == "2":
                    run_command(clean_name, sel["remove_cmd"], True)
            else:
                run_command(clean_name, sel["cmd"], False)

def system_tools_menu():
    while True:
        clear_screen()
        print(f"{C_CYAN}===================================================={C_NC}")
        print(f"{C_YELLOW}    ONLINE4TECH - RECEIVER SYSTEM COMMANDS          {C_NC}")
        print(f"{C_CYAN}===================================================={C_NC}")
        print(f"  {C_YELLOW}[1]{C_NC} Receiver Info (CPU Arch, Python, RAM)")
        print(f"  {C_YELLOW}[2]{C_NC} Clear RAM & Free Cache")
        print(f"  {C_YELLOW}[3]{C_NC} Update Feeds (opkg update)")
        print(f"  {C_YELLOW}[4]{C_NC} Clean /tmp Folder")
        print(f"  {C_YELLOW}[5]{C_NC} Restart Enigma2 GUI")
        print(f"  {C_YELLOW}[6]{C_NC} Full Receiver Reboot")
        print(f"{C_CYAN}----------------------------------------------------{C_NC}")
        print(f"  {C_RED}[0]{C_NC} Back to Main Menu")
        print(f"{C_CYAN}===================================================={C_NC}")
        c = get_input("Select Command: ")
        if c == "0" or not c: break
        elif c == "1": run_command("System Info", "uname -a && python3 --version 2>&1 && free -h 2>/dev/null || free && df -h")
        elif c == "2": run_command("Clear RAM", "sync && echo 3 > /proc/sys/vm/drop_caches")
        elif c == "3": run_command("Update Feeds", "opkg update")
        elif c == "4": run_command("Clean /tmp", "rm -rf /tmp/*.ipk /tmp/*.deb /tmp/*.tar.gz /tmp/*.zip")
        elif c == "5": os.system("killall -9 enigma2")
        elif c == "6": os.system("reboot")

def main():
    data = load_db()
    sections = data.get("main", [])
    while True:
        clear_screen()
        print(f"{C_CYAN}===================================================={C_NC}")
        print(f"{C_WHITE}       ONLINE4TECH SUPER SCRIPT v3.0 (350+ Store)   {C_NC}")
        print(f"{C_GREEN}    Vu+ & Dreambox Complete Management Center       {C_NC}")
        print(f"{C_CYAN}===================================================={C_NC}")
        for idx, sec in enumerate(sections, 1):
            clean_t = clean_ascii(sec.get("title", sec.get("section")))
            print(f"  {C_YELLOW}[{idx:2d}]{C_NC} {clean_t}")
        print(f"  {C_YELLOW}[99]{C_NC} Receiver System Commands & Maintenance")
        print(f"{C_CYAN}----------------------------------------------------{C_NC}")
        print(f"  {C_RED}[ 0]{C_NC} Exit")
        print(f"{C_CYAN}===================================================={C_NC}")
        choice = get_input("Enter Section Number: ")

        if choice == "0" or not choice:
            break
        elif choice == "99":
            system_tools_menu()
        elif choice.isdigit() and 1 <= int(choice) <= len(sections):
            sec = sections[int(choice) - 1]
            clean_t = clean_ascii(sec.get("title", sec.get("section")))
            show_items_menu(data, sec["section"], clean_t)

if __name__ == "__main__":
    main()
EOF

"$PY_BIN" "$PY_RUNNER"
rm -f "$DB_FILE" "$PY_RUNNER" /tmp/o4t_super.sh
echo "Goodbye from Online4Tech!"