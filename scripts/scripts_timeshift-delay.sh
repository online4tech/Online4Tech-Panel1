#!/bin/sh
# timeshift-delay.sh
# Auto installer for Timeshift Delay files on Enigma2 images.
# Supported folders inside package:
# openatv, openbh, openpli, openvix, pure2, egami, opendroid, openeight, openhdf, openspa, openvision, teamblue

echo "*******************************************************************"
echo "*                                                                 *"
echo "*                    Installing Timeshift Delay                   *"
echo "*                                                                 *"
echo "*                       VIP clients by mosad                      *"
echo "*                                                                 *"
echo "*                   This will take a few moments                  *"
echo "*                                                                 *"
echo "*                        Please be patient                        *"
echo "*                                                                 *"
echo "*******************************************************************"


PACKAGE_URL="${PACKAGE_URL:-https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/packages/timeshift-delay.tar.gz}"
SUPPORTED_IMAGES="openatv openbh openpli openvix pure2 egami opendroid openeight openhdf openspa openvision teamblue"
NO_RESTART="${NO_RESTART:-0}"

log() {
    echo "[timeshift-delay] $*"
}

die() {
    echo "[timeshift-delay] ERROR: $*" >&2
    exit 1
}

print_supported_images() {
    for img in $SUPPORTED_IMAGES; do
        echo "  sh /tmp/timeshift-delay.sh $img"
    done
}

usage() {
    cat <<USAGE
Usage:
  sh /tmp/timeshift-delay.sh

Manual image selection:
USAGE
    print_supported_images
    cat <<USAGE

Options by environment:
  PACKAGE_URL="https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/packages/timeshift-delay.tar.gz" sh /tmp/timeshift-delay.sh
  NO_RESTART=1 sh /tmp/timeshift-delay.sh
USAGE
}

is_supported_image() {
    img="$1"
    for x in $SUPPORTED_IMAGES; do
        [ "$img" = "$x" ] && return 0
    done
    return 1
}

lower_text() {
    echo "$1" | tr 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' 'abcdefghijklmnopqrstuvwxyz'
}

normalize_image_name() {
    # Accept friendly forms such as OpenHDF, open-hdf, open hdf and open_hdf.
    lower_text "$1" | tr -d ' _-'
}

FORCE_IMAGE=""
ARG1="$(normalize_image_name "${1:-}")"
case "$ARG1" in
    "") ;;
    h|help)
        usage
        exit 0
        ;;
    *)
        if is_supported_image "$ARG1"; then
            FORCE_IMAGE="$ARG1"
        else
            usage
            die "Unknown image name: $1"
        fi
        ;;
esac

[ "$(id -u 2>/dev/null)" = "0" ] || die "Run this script as root."
[ -d /usr/lib/enigma2/python ] || die "Enigma2 path not found: /usr/lib/enigma2/python"

if command -v mktemp >/dev/null 2>&1; then
    WORKDIR="$(mktemp -d /tmp/timeshift-delay.XXXXXX 2>/dev/null)"
fi
[ -n "${WORKDIR:-}" ] || WORKDIR="/tmp/timeshift-delay.$$"
mkdir -p "$WORKDIR" || die "Cannot create temp directory: $WORKDIR"

cleanup() {
    rm -rf "$WORKDIR" 2>/dev/null
}
trap cleanup EXIT

PKG="$WORKDIR/timeshift-delay.tar.gz"
LISTFILE="$WORKDIR/package-list.txt"

log "Downloading package..."
if command -v wget >/dev/null 2>&1; then
    wget -O "$PKG" "$PACKAGE_URL" || die "Download failed: $PACKAGE_URL"
elif command -v curl >/dev/null 2>&1; then
    curl -L -o "$PKG" "$PACKAGE_URL" || die "Download failed: $PACKAGE_URL"
else
    die "wget/curl not found. Install wget or download the package manually."
fi

[ -s "$PKG" ] || die "Downloaded package is empty."

tar -tzf "$PKG" > "$LISTFILE" 2>/dev/null || die "Invalid tar.gz package."

# Basic archive path safety check before extraction.
if grep -E '(^/|(^|/)\.\.(/|$))' "$LISTFILE" >/dev/null 2>&1; then
    die "Unsafe paths found inside archive."
fi

log "Extracting package..."
tar -xzf "$PKG" -C "$WORKDIR" || die "Extract failed."

image_signature_exists() {
    pattern="$1"
    grep -Eisq "$pattern" $CHECK_FILES /etc/opkg/* 2>/dev/null
}

detect_image() {
    [ -n "$FORCE_IMAGE" ] && echo "$FORCE_IMAGE" && return 0

    CHECK_FILES="/etc/image-version /etc/issue /etc/issue.net /etc/motd /etc/hostname"

    if image_signature_exists 'openatv'; then
        echo "openatv"; return 0
    fi
    if image_signature_exists 'openbh|open bh|blackhole|black hole'; then
        echo "openbh"; return 0
    fi
    if image_signature_exists 'openpli|open pli'; then
        echo "openpli"; return 0
    fi
    if image_signature_exists 'openvix|open vix'; then
        echo "openvix"; return 0
    fi
    if image_signature_exists 'pure2'; then
        echo "pure2"; return 0
    fi
    if image_signature_exists 'egami'; then
        echo "egami"; return 0
    fi
    if image_signature_exists 'opendroid|open droid|open-droid'; then
        echo "opendroid"; return 0
    fi
    if image_signature_exists 'openeight|open eight|open-eight'; then
        echo "openeight"; return 0
    fi
    if image_signature_exists 'openhdf|open hdf|open-hdf|hdfreaks|hdfreak'; then
        echo "openhdf"; return 0
    fi
    if image_signature_exists 'openspa|open spa|open-spa'; then
        echo "openspa"; return 0
    fi
    if image_signature_exists 'openvision|open vision|open-vision'; then
        echo "openvision"; return 0
    fi
    if image_signature_exists 'teamblue|team blue|team-blue|team_blue'; then
        echo "teamblue"; return 0
    fi

    return 1
}

IMAGE_NAME="$(detect_image)" || IMAGE_NAME=""

if [ -z "$IMAGE_NAME" ]; then
    cat <<MSG
[timeshift-delay] Could not detect your image automatically.
[timeshift-delay] Run manually with one of these names:
MSG
    print_supported_images | sed 's/^/[timeshift-delay] /'
    exit 1
fi

is_supported_image "$IMAGE_NAME" || die "Unsupported image detected: $IMAGE_NAME"
SRC_DIR="$WORKDIR/$IMAGE_NAME"
[ -d "$SRC_DIR/usr" ] || die "Package folder not found for image: $IMAGE_NAME"

log "Detected/selected image: $IMAGE_NAME"

BACKUP_DIR="/tmp/timeshift-delay-backup-$(date +%Y%m%d-%H%M%S 2>/dev/null || echo now)"
mkdir -p "$BACKUP_DIR" || die "Cannot create backup directory: $BACKUP_DIR"

log "Backing up old files to: $BACKUP_DIR"
find "$SRC_DIR/usr" -type f | while IFS= read -r srcfile; do
    rel="${srcfile#$SRC_DIR/}"
    dest="/$rel"
    if [ -e "$dest" ] || [ -L "$dest" ]; then
        mkdir -p "$BACKUP_DIR/$(dirname "$rel")" 2>/dev/null
        cp -a "$dest" "$BACKUP_DIR/$rel" 2>/dev/null || cp "$dest" "$BACKUP_DIR/$rel" 2>/dev/null
    fi
done

log "Installing new files..."
cp -af "$SRC_DIR/usr/." /usr/ 2>/dev/null || cp -rf "$SRC_DIR/usr/." /usr/ || die "Copy failed."

# Safe permissions for Python files.
chmod 644 /usr/lib/enigma2/python/Screens/AudioSelection.py 2>/dev/null
chmod 644 /usr/lib/enigma2/python/Screens/AudioSelection.pyc 2>/dev/null
chmod 644 /usr/lib/enigma2/python/Components/Converter/ServicePosition.py 2>/dev/null
chmod 644 /usr/lib/enigma2/python/Components/Converter/ServicePosition.pyc 2>/dev/null

# Remove Python 3 cached versions so Enigma2 recompiles from the installed .py files.
rm -f /usr/lib/enigma2/python/Screens/__pycache__/AudioSelection*.pyc 2>/dev/null
rm -f /usr/lib/enigma2/python/Components/Converter/__pycache__/ServicePosition*.pyc 2>/dev/null

# Patch only the TimeshiftState screen in skin.xml files to enable half-second Remaining output.
patch_skin_remaining_halfsec() {
    SKIN_ROOT="/usr/share/enigma2"
    OLD_CONVERT='<convert type="ServicePosition">Remaining</convert>'
    NEW_CONVERT='<convert type="ServicePosition">Remaining,HalfSec</convert>'

    if [ ! -d "$SKIN_ROOT" ]; then
        log "Skin path not found, skipping skin.xml patch: $SKIN_ROOT"
        return 0
    fi

    command -v awk >/dev/null 2>&1 || die "awk not found. Cannot safely patch skin.xml files."

    SKIN_LIST="$WORKDIR/skinxml-list.txt"
    AWK_SCRIPT="$WORKDIR/patch-timeshiftstate.awk"
    : > "$SKIN_LIST" || die "Cannot create skin list: $SKIN_LIST"

    cat > "$AWK_SCRIPT" <<'AWK'
BEGIN {
    in_target = 0
    found_target = 0
    patched = 0
    already = 0
}

function is_target_screen(s) {
    return (s ~ /<screen[[:space:]][^>]*name[[:space:]]*=[[:space:]]*["\047]TimeshiftState["\047]/)
}

function is_screen_end(s) {
    return (s ~ /<\/screen>/)
}

{
    line = $0

    if (is_target_screen(line)) {
        in_target = 1
        found_target = 1
    }

    if (in_target) {
        if (index(line, new_convert) > 0) {
            already = 1
        }
        if (index(line, old_convert) > 0) {
            gsub(old_convert, new_convert, line)
            patched++
        }
    }

    print line

    if (in_target && is_screen_end($0)) {
        in_target = 0
    }
}

END {
    if (patched > 0) {
        print "patched" > status_file
    } else if (already > 0) {
        print "already" > status_file
    } else if (found_target > 0) {
        print "target_without_convert" > status_file
    } else {
        print "no_target_screen" > status_file
    }
}
AWK

    find "$SKIN_ROOT" -type f -name skin.xml > "$SKIN_LIST" 2>/dev/null

    FOUND_COUNT=0
    PATCHED_COUNT=0
    ALREADY_COUNT=0
    NO_TARGET_COUNT=0
    NO_CONVERT_COUNT=0
    ERROR_COUNT=0

    while IFS= read -r skinfile; do
        [ -n "$skinfile" ] || continue
        FOUND_COUNT=$((FOUND_COUNT + 1))

        tmpfile="$WORKDIR/skinxml.$FOUND_COUNT.tmp"
        statusfile="$WORKDIR/skinxml.$FOUND_COUNT.status"
        rm -f "$tmpfile" "$statusfile" 2>/dev/null

        if ! awk \
            -v old_convert="$OLD_CONVERT" \
            -v new_convert="$NEW_CONVERT" \
            -v status_file="$statusfile" \
            -f "$AWK_SCRIPT" \
            "$skinfile" > "$tmpfile"; then
            rm -f "$tmpfile" "$statusfile" 2>/dev/null
            ERROR_COUNT=$((ERROR_COUNT + 1))
            die "Cannot parse skin file: $skinfile"
        fi

        STATUS="$(cat "$statusfile" 2>/dev/null || echo error)"

        case "$STATUS" in
            patched)
                if cmp -s "$skinfile" "$tmpfile" 2>/dev/null; then
                    rm -f "$tmpfile" "$statusfile" 2>/dev/null
                    NO_CONVERT_COUNT=$((NO_CONVERT_COUNT + 1))
                    continue
                fi

                rel="${skinfile#/}"
                mkdir -p "$BACKUP_DIR/$(dirname "$rel")" 2>/dev/null
                cp -a "$skinfile" "$BACKUP_DIR/$rel" 2>/dev/null || cp "$skinfile" "$BACKUP_DIR/$rel" 2>/dev/null || \
                    die "Cannot backup skin file: $skinfile"

                # Preserve the original file permissions/ownership as much as BusyBox allows.
                cp -p "$skinfile" "$tmpfile.perm" 2>/dev/null || true
                if [ -e "$tmpfile.perm" ]; then
                    cat "$tmpfile" > "$tmpfile.perm" || die "Cannot prepare patched skin file: $skinfile"
                    mv -f "$tmpfile.perm" "$skinfile" || die "Cannot write patched skin file: $skinfile"
                    rm -f "$tmpfile" 2>/dev/null
                else
                    mv -f "$tmpfile" "$skinfile" || die "Cannot write patched skin file: $skinfile"
                    chmod 644 "$skinfile" 2>/dev/null
                fi

                PATCHED_COUNT=$((PATCHED_COUNT + 1))
                log "Patched TimeshiftState Remaining converter: $skinfile"
                ;;
            already)
                ALREADY_COUNT=$((ALREADY_COUNT + 1))
                rm -f "$tmpfile" 2>/dev/null
                ;;
            target_without_convert)
                NO_CONVERT_COUNT=$((NO_CONVERT_COUNT + 1))
                rm -f "$tmpfile" 2>/dev/null
                ;;
            no_target_screen)
                NO_TARGET_COUNT=$((NO_TARGET_COUNT + 1))
                rm -f "$tmpfile" 2>/dev/null
                ;;
            *)
                ERROR_COUNT=$((ERROR_COUNT + 1))
                rm -f "$tmpfile" 2>/dev/null
                die "Unknown patch status for skin file: $skinfile"
                ;;
        esac

        rm -f "$statusfile" 2>/dev/null
    done < "$SKIN_LIST"

    log "skin.xml scan completed: found=$FOUND_COUNT patched=$PATCHED_COUNT already=$ALREADY_COUNT no_TimeshiftState=$NO_TARGET_COUNT TimeshiftState_without_target_line=$NO_CONVERT_COUNT errors=$ERROR_COUNT"
}

patch_skin_remaining_halfsec

sync
log "Installation completed."
log "Backup saved in: $BACKUP_DIR"

restart_enigma2() {
    [ "$NO_RESTART" = "1" ] && { log "NO_RESTART=1, Enigma2 restart skipped."; return 0; }

    log "Restarting Enigma2..."
    if command -v systemctl >/dev/null 2>&1; then
        systemctl restart enigma2 2>/dev/null && return 0
        systemctl restart enigma2.service 2>/dev/null && return 0
    fi

    if command -v init >/dev/null 2>&1; then
        init 4 2>/dev/null
        sleep 2
        init 3 2>/dev/null
        return 0
    fi

    killall -9 enigma2 2>/dev/null || true
}

restart_enigma2
exit 0
