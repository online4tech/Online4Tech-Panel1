#!/bin/sh
# ONLINE4TECH SUPER SCRIPT v3.1 - Pure ASCII Engine

DB_URL="https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/o4t_database.json"
DB_FILE="/tmp/o4t_database.json"
PY_RUNNER="/tmp/o4t_menu.py"

echo "[Online4Tech] Connecting to Store Server..."
rm -f "$DB_FILE" "$PY_RUNNER"

if command -v curl >/dev/null 2>&1; then
    curl -sLk "$DB_URL" -o "$DB_FILE"
else
    wget --no-check-certificate -qO "$DB_FILE" "$DB_URL"
fi

if [ ! -s "$DB_FILE" ]; then
    echo "[ERROR] Cannot download o4t_database.json! Check internet or DNS."
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
    text = re.sub(r'\([^)]*[^\x00-\x7F]+[^)]*\)', '', text)
    text = re.sub(r'[^\x00-\x7F]+', '', text)
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
    if sys.version_info[0] >= 3:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        import io
        with io.open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

def run_command(title, cmd, is_remove=False):
    clear_screen()
    action = "UNINSTALLING" if is_remove else "INSTALLING"
    print("%s====================================================%s" % (C_CYAN, C_NC))
    print("%s[Online4Tech] %s: %s%s%s" % (C_YELLOW, action, C_WHITE, title, C_NC))
    print("%s====================================================%s\n" % (C_CYAN, C_NC))
    os.system(cmd)
    print("\n%s====================================================%s" % (C_CYAN, C_NC))
    print("%s[DONE] Operation Finished!%s" % (C_GREEN, C_NC))
    get_input("Press Enter to continue...")

def show_items_menu(data, section_key, section_title):
    items = data.get(section_key, [])
    if items and isinstance(items[0], dict) and "section" in items[0]:
        while True:
            clear_screen()
            print("%s====================================================%s" % (C_CYAN, C_NC))
            print("%s   ONLINE4TECH - %s%s" % (C_WHITE, section_title.upper(), C_NC))
            print("%s====================================================%s" % (C_CYAN, C_NC))
            for idx, sub in enumerate(items, 1):
                sub_t = clean_ascii(sub.get('title', sub.get('section')))
                print("  %s[%2d]%s %s" % (C_YELLOW, idx, C_NC, sub_t))
            print("%s----------------------------------------------------%s" % (C_CYAN, C_NC))
            print("  %s[ 0]%s Back" % (C_RED, C_NC))
            print("%s====================================================%s" % (C_CYAN, C_NC))
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
        print("%s====================================================%s" % (C_CYAN, C_NC))
        print("%s   %s (%d-%d of %d)%s" % (C_WHITE, section_title, start+1, end, total, C_NC))
        print("%s====================================================%s" % (C_CYAN, C_NC))

        for i in range(start, end):
            item = items[i]
            clean_name = clean_ascii(item.get("name", "Unknown"))
            installed = "[*]" if item.get("path") and os.path.exists(item.get("path")) else "   "
            print(" %s%s%s %s[%3d]%s %s" % (C_GREEN, installed, C_NC, C_YELLOW, i+1, C_NC, clean_name))

        print("%s----------------------------------------------------%s" % (C_CYAN, C_NC))
        nav = "  %s[0]%s Back" % (C_RED, C_NC)
        if end < total:
            nav += "  |  %s[N]%s Next Page" % (C_GREEN, C_NC)
        if page > 0:
            nav += "  |  %s[P]%s Prev Page" % (C_GREEN, C_NC)
        print(nav)
        print("%s====================================================%s" % (C_CYAN, C_NC))
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
                print("\n  %s[1]%s Install: %s" % (C_GREEN, C_NC, clean_name))
                print("  %s[2]%s Remove: %s" % (C_RED, C_NC, clean_name))
                print("  %s[0]%s Cancel" % (C_YELLOW, C_NC))
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
        print("%s====================================================%s" % (C_CYAN, C_NC))
        print("%s    ONLINE4TECH - RECEIVER SYSTEM COMMANDS          %s" % (C_YELLOW, C_NC))
        print("%s====================================================%s" % (C_CYAN, C_NC))
        print("  %s[1]%s Receiver Info (CPU Arch, Python, RAM)" % (C_YELLOW, C_NC))
        print("  %s[2]%s Clear RAM & Free Cache" % (C_YELLOW, C_NC))
        print("  %s[3]%s Update Feeds (opkg update)" % (C_YELLOW, C_NC))
        print("  %s[4]%s Clean /tmp Folder" % (C_YELLOW, C_NC))
        print("  %s[5]%s Restart Enigma2 GUI" % (C_YELLOW, C_NC))
        print("  %s[6]%s Full Receiver Reboot" % (C_YELLOW, C_NC))
        print("%s----------------------------------------------------%s" % (C_CYAN, C_NC))
        print("  %s[0]%s Back to Main Menu" % (C_RED, C_NC))
        print("%s====================================================%s" % (C_CYAN, C_NC))
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
        print("%s====================================================%s" % (C_CYAN, C_NC))
        print("%s       ONLINE4TECH SUPER SCRIPT v3.1 (350+ Store)   %s" % (C_WHITE, C_NC))
        print("%s    Vu+ & Dreambox Complete Management Center       %s" % (C_GREEN, C_NC))
        print("%s====================================================%s" % (C_CYAN, C_NC))
        for idx, sec in enumerate(sections, 1):
            clean_t = clean_ascii(sec.get("title", sec.get("section")))
            print("  %s[%2d]%s %s" % (C_YELLOW, idx, C_NC, clean_t))
        print("  %s[99]%s Receiver System Commands & Maintenance" % (C_YELLOW, C_NC))
        print("%s----------------------------------------------------%s" % (C_CYAN, C_NC))
        print("  %s[ 0]%s Exit" % (C_RED, C_NC))
        print("%s====================================================%s" % (C_CYAN, C_NC))
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