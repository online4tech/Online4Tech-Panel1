#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Online4Tech Panel 7.5 Gold IPK builder.

Builds from the authoritative installed plugin tree, not the legacy top-level
plugin/ directory. All UI icons and branding assets are included.
"""
import io
import os
import stat
import tarfile
import time

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
VERSION = "7.5"
PKG_NAME = "enigma2-plugin-extensions-online4tech"
IPK_FILENAME = "%s_%s_all.ipk" % (PKG_NAME, VERSION)
DEB_FILENAME = "%s_%s_all.deb" % (PKG_NAME, VERSION)
PLUGIN_RELATIVE_DIR = os.path.join("usr", "lib", "enigma2", "python", "Plugins", "Extensions", "Online4Tech")
PLUGIN_SOURCE_DIR = os.path.join(ROOT_DIR, PLUGIN_RELATIVE_DIR)
TARGET_PREFIX = "./" + PLUGIN_RELATIVE_DIR.replace(os.sep, "/")
REQUIRED_FILES = ("__init__.py", "plugin.py", "o4t_store.py", "plugin.png", "logo.png")


def add_tar_bytes(tar, arcname, data_bytes, mode=0o644):
    info = tarfile.TarInfo(name=arcname)
    info.size = len(data_bytes)
    info.mode = mode
    info.uid = 0
    info.gid = 0
    info.uname = "root"
    info.gname = "root"
    info.mtime = int(time.time())
    tar.addfile(info, io.BytesIO(data_bytes))


def add_source_tree(tar):
    added = []
    for current_dir, dirnames, filenames in os.walk(PLUGIN_SOURCE_DIR):
        dirnames[:] = sorted(name for name in dirnames if name != "__pycache__")
        for filename in sorted(filenames):
            if filename.endswith((".pyc", ".pyo")):
                continue
            source_path = os.path.join(current_dir, filename)
            if not os.path.isfile(source_path):
                continue
            relative = os.path.relpath(source_path, PLUGIN_SOURCE_DIR)
            archive_name = TARGET_PREFIX + "/" + relative.replace(os.sep, "/")
            with open(source_path, "rb") as handle:
                payload = handle.read()
            mode = stat.S_IMODE(os.stat(source_path).st_mode) or 0o644
            add_tar_bytes(tar, archive_name, payload, mode)
            added.append(relative)
    return added


def make_ar_member(name, data, mode=0o100644):
    timestamp = int(time.time())
    header = ("%-16s%-12d%-6d%-6d%-8s%-10d" % (
        name, timestamp, 0, 0, oct(mode)[2:], len(data)
    )).encode("ascii") + bytes([96]) + b"\n"
    result = header + data
    if len(data) % 2:
        result += b"\n"
    return result


def build():
    if not os.path.isdir(PLUGIN_SOURCE_DIR):
        raise FileNotFoundError("Missing authoritative plugin source: %s" % PLUGIN_SOURCE_DIR)
    missing = [name for name in REQUIRED_FILES
               if not os.path.isfile(os.path.join(PLUGIN_SOURCE_DIR, name))]
    if missing:
        raise FileNotFoundError("Missing required Online4Tech files: %s" % ", ".join(missing))

    control = (
        "Package: %s\nVersion: %s\n"
        "Description: Online4Tech Panel & Store - Gold Edition\n"
        "Section: extra\nPriority: optional\nMaintainer: Online4Tech\n"
        "Architecture: all\n"
        "Homepage: https://github.com/online4tech/Online4Tech-Panel1\n"
        % (PKG_NAME, VERSION)
    ).encode("utf-8")

    postinst = b"#!/bin/sh\necho \"Online4Tech Panel 7.5 Gold installed.\"\necho \"Restart Enigma2 GUI to load the updated panel.\"\nexit 0\n"
    prerm = b"#!/bin/sh\n# Keep user data and plugin files intact during package transitions.\nexit 0\n"
    postrm = b"#!/bin/sh\n# Package manager removes only files owned by this package.\n# Never recursively delete the plugin directory or unowned user files.\nexit 0\n"

    control_buffer = io.BytesIO()
    with tarfile.open(fileobj=control_buffer, mode="w:gz", format=tarfile.GNU_FORMAT) as tar:
        add_tar_bytes(tar, "./control", control, 0o644)
        add_tar_bytes(tar, "./postinst", postinst, 0o755)
        add_tar_bytes(tar, "./prerm", prerm, 0o755)
        add_tar_bytes(tar, "./postrm", postrm, 0o755)

    data_buffer = io.BytesIO()
    with tarfile.open(fileobj=data_buffer, mode="w:gz", format=tarfile.GNU_FORMAT) as tar:
        included = add_source_tree(tar)
    if len(included) < 60:
        raise RuntimeError("Only %d plugin files found; refusing to build an incomplete package." % len(included))

    package_data = bytearray(b"!<arch>\n")
    package_data.extend(make_ar_member("debian-binary", b"2.0\n"))
    package_data.extend(make_ar_member("control.tar.gz", control_buffer.getvalue()))
    package_data.extend(make_ar_member("data.tar.gz", data_buffer.getvalue()))

    output_paths = (
        os.path.join(ROOT_DIR, IPK_FILENAME),
        os.path.join(ROOT_DIR, DEB_FILENAME),
    )
    for output_path in output_paths:
        with open(output_path, "wb") as output:
            output.write(package_data)
        print("Built %s" % output_path)

    print("Version: %s | Files included: %d | Package size: %d bytes" %
          (VERSION, len(included), len(package_data)))


if __name__ == "__main__":
    build()
