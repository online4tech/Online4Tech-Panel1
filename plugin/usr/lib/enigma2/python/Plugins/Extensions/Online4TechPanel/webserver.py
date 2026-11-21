# -*- coding: utf-8 -*-
"""Web control panel (default port 8080) - Twisted based, Python 2 / 3 compatible.

* Open on the local network by default; optional Basic auth (user "admin") via Tools > Web control.
* POST endpoints need the X-O4T-Request header (CSRF protection) and a matching Origin.
* The web shell is OFF until it is enabled from the receiver itself (Tools > Web control).
* Install / remove commands come only from the validated catalog (never from the client);
  the one exception is the shell, which is why it is opt-in.
"""
from __future__ import absolute_import, print_function
import collections
import hmac
import json
import os
import random
import re
import time

from twisted.internet import protocol, reactor, task, utils as tutils
from twisted.web import resource, server

from . import catalog
from .utils import (PY3, compatible, get_setting, item_key, log, parse_opkg_list,
                    read_file, set_setting, shquote, txt, urlparse)
from .version import (INSTALL_URL, MESSENGER_URL, PAGE_URL, SITE_URL, STORE_URL, VERSION,
                      WEB_PORT, WHATSAPP_NUMBER, WHATSAPP_URL)

try:
    from urllib.parse import quote
except ImportError:  # Python 2
    from urllib import quote

WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
OPKG_INSTALLED = "opkg list-installed 2>/dev/null | grep '^enigma2-plugin-'"
PLAYERS = {"xstreamity": "/etc/enigma2/xstreamity", "xklass": "/etc/enigma2/xklass"}
KINDS = ("plugin", "skin", "channels", "picons")
MAX_OUT = 300000
JOB_TIMEOUT = 1200

_state = {"port": None, "loop": None, "installed": set(), "fails": {}, "page": None}


def _b(s):
    s = txt(s)
    return s.encode("utf-8") if PY3 else s


def _eq(a, b):
    try:
        return hmac.compare_digest(_b(a), _b(b))
    except AttributeError:  # very old python
        return _b(a) == _b(b)


# ------------------------------------------------------------------ settings
def password():
    pw = get_setting("web_password", "")
    if not pw:
        rnd = random.SystemRandom()
        pw = "".join(rnd.choice("abcdefghjkmnpqrstuvwxyz23456789") for _ in range(8))
        set_setting("web_password", pw)
    return pw


def new_password():
    set_setting("web_password", "")
    return password()


# ------------------------------------------------------------------ jobs
class Job(object):
    def __init__(self, jid, title, cmd):
        self.id, self.title, self.cmd = jid, title, cmd
        self.out, self.size, self.done, self.rc = [], 0, False, None
        self.proc, self.timer = None, None

    def add(self, data):
        text = txt(data)
        self.out.append(text)
        self.size += len(text)
        while self.size > MAX_OUT and len(self.out) > 1:
            self.size -= len(self.out.pop(0))


class JobProtocol(protocol.ProcessProtocol):
    def __init__(self, job):
        self.job = job

    def outReceived(self, data):
        self.job.add(data)

    errReceived = outReceived

    def processEnded(self, reason):
        job = self.job
        job.rc = getattr(reason.value, "exitCode", None)
        job.done = True
        if job.timer and job.timer.active():
            job.timer.cancel()
        job.add("\n[exit %s]\n" % ("?" if job.rc is None else job.rc))
        log("job %s finished rc=%s" % (job.id, job.rc))
        refresh_installed()


JOBS = collections.OrderedDict()
_counter = [0]


def running_job():
    for job in JOBS.values():
        if not job.done:
            return job
    return None


def start_job(title, cmd):
    if running_job():
        return None
    _counter[0] += 1
    job = Job("j%d" % _counter[0], title, cmd)
    JOBS[job.id] = job
    while len(JOBS) > 8:
        JOBS.popitem(last=False)
    log("job %s start: %s | %s" % (job.id, title, cmd[:300]))
    job.add("$ %s\n" % title)
    try:
        job.proc = reactor.spawnProcess(JobProtocol(job), "/bin/sh", ["/bin/sh", "-c", cmd],
                                        env=dict(os.environ, TERM="dumb"))
    except Exception as exc:
        job.add("failed to start: %s\n" % exc)
        job.done, job.rc = True, -1
        return job

    def kill():
        try:
            job.add("\n[timeout - killed]\n")
            job.proc.signalProcess("KILL")
        except Exception:
            pass
    job.timer = reactor.callLater(JOB_TIMEOUT, kill)
    return job


# ------------------------------------------------------------------ system info
def refresh_installed():
    def ok(out):
        _state["installed"] = set(p["pkg"] for p in parse_opkg_list(txt(out)))

    d = tutils.getProcessOutput("/bin/sh", ["-c", OPKG_INSTALLED], errortoo=False)
    d.addCallbacks(ok, lambda failure: None)


def _temp():
    for path, div in (("/proc/stb/fp/temp_sensor_avs", 1.0), ("/proc/stb/fp/temp_sensor", 1.0),
                      ("/sys/class/thermal/thermal_zone0/temp", 1000.0),
                      ("/proc/stb/sensors/temp0/value", 1.0)):
        try:
            t = float(read_file(path).strip()) / div
            if 0 < t < 150:
                return int(round(t))
        except Exception:
            continue
    return None


VU = {"duo4k": "Duo 4K", "duo4kse": "Duo 4K SE", "uno4k": "Uno 4K", "uno4kse": "Uno 4K SE",
      "ultimo4k": "Ultimo 4K", "solo4k": "Solo 4K", "zero4k": "Zero 4K", "duo2": "Duo2",
      "solo2": "Solo2", "solose": "Solo SE", "solose v2": "Solo SE V2", "ultimo": "Ultimo",
      "uno": "Uno", "zero": "Zero", "duo": "Duo", "solo": "Solo"}
OTHER = {"dm900": "Dreambox DM900", "dm920": "Dreambox DM920", "dreamone": "Dreambox One",
         "dreamtwo": "Dreambox Two", "dm525": "Dreambox DM525", "hd51": "AX HD51",
         "h7": "Zgemma H7", "h9": "Zgemma H9", "gbquad4k": "GigaBlue Quad 4K",
         "gbue4k": "GigaBlue UE 4K", "osmio4k": "Edision OSmio4K", "osmio4kplus": "Edision OSmio4K Plus"}


def device_name():
    """Human readable receiver name, e.g. 'Vu+ Duo 4K' (best effort)."""
    def first(*paths):
        for path in paths:
            val = read_file(path).strip()
            if val:
                return val
        return ""
    vu = first("/proc/stb/info/vumodel").lower()
    raw = first("/proc/stb/info/boxtype", "/proc/stb/info/model", "/proc/stb/info/hwmodel")
    host = read_file("/etc/hostname").strip().lower()
    for key in (vu, raw.lower(), host):
        k = key.replace("vu+", "").replace("vu", "", 1) if key.startswith("vu") else key
        if key.startswith("vu") and k in VU:
            return "Vu+ " + VU[k]
        if key in VU and (vu or host.startswith("vu")):
            return "Vu+ " + VU[key]
        if key in OTHER:
            return OTHER[key]
    return (first("/proc/stb/info/model") or raw or host or "-").upper() if (raw or host) else "-"


def system_status():
    mem = {}
    for line in read_file("/proc/meminfo").splitlines():
        p = line.replace(":", " ").split()
        if len(p) >= 2:
            mem[p[0]] = int(p[1]) if p[1].isdigit() else 0
    total = mem.get("MemTotal", 0) // 1024
    free = mem.get("MemAvailable", mem.get("MemFree", 0)) // 1024
    try:
        up = int(float(read_file("/proc/uptime").split()[0]))
    except Exception:
        up = 0
    try:
        st = os.statvfs("/")
        fl_total = st.f_blocks * st.f_frsize / 1073741824.0
        fl_free = st.f_bavail * st.f_frsize / 1073741824.0
    except Exception:
        fl_total = fl_free = 0
    image = [l for l in read_file("/etc/image-version").splitlines() if l.strip()][:1]
    return {
        "ram_total": total, "ram_used": max(0, total - free), "uptime": up,
        "flash_total": round(fl_total, 1), "flash_free": round(fl_free, 1),
        "temp": _temp(), "model": device_name(),
        "image": image[0] if image else "-", "version": VERSION,
        "shell": bool(get_setting("web_shell", False)), "auth": bool(get_setting("web_auth", False)), "busy": running_job() is not None,
        "links": {"whatsapp": WHATSAPP_URL, "messenger": MESSENGER_URL, "page": PAGE_URL,
                  "store": STORE_URL, "site": SITE_URL},
        "phone": WHATSAPP_NUMBER,
    }


# ------------------------------------------------------------------ catalog api
def items_for(kind):
    if kind == "picons":
        return [i for i in catalog.items("skin") if i["category"] == "Picons"]
    if kind == "skin":
        return [i for i in catalog.items("skin") if i["category"] != "Picons"]
    return catalog.items(kind)


def find_item(item_id):
    for kind in ("plugin", "skin", "channels"):
        for it in catalog.items(kind):
            if it["id"] == item_id:
                return it
    return None


def is_installed(it):
    return (bool(it.get("pkg")) and it["pkg"] in _state["installed"]) or \
        (bool(it.get("path")) and os.path.exists(it["path"]))


def catalog_view(kind, cat, query, show_all, limit=400):
    items = items_for(kind)
    cats = catalog.categories(kind if kind != "picons" else "skin", items)
    if not show_all:
        items = [i for i in items if compatible(i)]
    q = (query or "").lower()
    out = []
    for it in items:
        if cat and it["category"] != cat:
            continue
        if q and q not in it["name"].lower() and q not in it.get("desc", "").lower():
            continue
        out.append({"id": it["id"], "name": it["name"], "cat": it["category"],
                    "desc": it.get("desc", ""), "installed": is_installed(it),
                    "compat": compatible(it), "removable": bool(catalog.remove_cmd(it))})
    return {"cats": [{"name": c, "count": n} for c, n in cats], "items": out[:limit],
            "total": len(out)}


# ------------------------------------------------------------------ IPTV playlists
_HOST_RE = re.compile(r"^(https?://)?[A-Za-z0-9.-]+$")
_SAFE_RE = re.compile(r"^[^\s'\"`\\<>|;&]{1,128}$")


def add_playlist(data):
    player = txt(data.get("player", ""))
    base = PLAYERS.get(player)
    if not base:
        return False, "unknown player"
    m3u = txt(data.get("m3u", "")).strip()
    if m3u:
        if not re.match(r"^https?://[^\s'\"`\\<>|;&]+$", m3u) or len(m3u) > 500:
            return False, "invalid M3U URL"
        line = m3u
    else:
        host = txt(data.get("host", "")).strip().rstrip("/")
        port = txt(data.get("port", "")).strip()
        user, pwd = txt(data.get("user", "")), txt(data.get("pass", ""))
        if not _HOST_RE.match(host) or (port and not port.isdigit()):
            return False, "invalid host/port"
        if not _SAFE_RE.match(user) or not _SAFE_RE.match(pwd):
            return False, "invalid username/password"
        if not host.startswith("http"):
            host = "http://" + host
        line = "%s%s/get.php?username=%s&password=%s&type=m3u_plus&output=ts" % (
            host, ":" + port if port else "", quote(user, safe=""), quote(pwd, safe=""))
    if not os.path.isdir(base):
        return False, "player not found - install it first and open it once"
    path = os.path.join(base, "playlists.txt")
    existing = read_file(path)
    if line in existing.splitlines():
        return True, "already in the list"
    try:
        if existing:
            with open(path + ".bak", "w") as fh:
                fh.write(existing)
        with open(path, "a") as fh:
            fh.write(("" if not existing or existing.endswith("\n") else "\n") + line + "\n")
    except Exception as exc:
        return False, "write failed: %s" % exc
    log("playlist added to %s" % player)  # never log the credentials
    return True, "playlist saved - reopen the player"


# ------------------------------------------------------------------ HTTP
def _quit(mode):
    try:
        from enigma import quitMainloop
        quitMainloop(mode)
    except Exception as exc:
        log("quitMainloop failed: %s" % exc)


class Root(resource.Resource):
    isLeaf = True

    # -- helpers
    def _send(self, request, obj, code=200):
        request.setResponseCode(code)
        request.setHeader(b"Content-Type", b"application/json; charset=utf-8")
        return json.dumps(obj).encode("utf-8")

    def _headers(self, request):
        for k, v in ((b"Cache-Control", b"no-store"), (b"X-Content-Type-Options", b"nosniff"),
                     (b"X-Frame-Options", b"DENY"), (b"Referrer-Policy", b"no-referrer"),
                     (b"Content-Security-Policy",
                      b"default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'")):
            request.setHeader(k, v)

    def _auth(self, request):
        if not get_setting("web_auth", False):   # open access by default (LAN use)
            return 200
        ip = txt(request.getClientIP())
        fails = _state["fails"].get(ip)
        now = time.time()
        if fails and fails[0] >= 5 and now - fails[1] < 60:
            return 429
        ok = _eq(request.getUser(), "admin") and _eq(request.getPassword(), password())
        if ok:
            _state["fails"].pop(ip, None)
            return 200
        cnt = (fails[0] + 1) if fails and now - fails[1] < 60 else 1
        _state["fails"][ip] = (cnt, now)
        return 401

    def _body(self, request):
        try:
            request.content.seek(0)
            raw = request.content.read(20000)
            data = json.loads(txt(raw) or "{}")
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _arg(self, request, name, default=""):
        vals = request.args.get(_b(name))
        return txt(vals[0]) if vals else default

    # -- dispatch
    def render(self, request):
        self._headers(request)
        try:
            code = self._auth(request)
            if code != 200:
                request.setResponseCode(code)
                if code == 401:
                    request.setHeader(b"WWW-Authenticate", b'Basic realm="Online4Tech Panel"')
                request.setHeader(b"Content-Type", b"text/plain; charset=utf-8")
                return b"Too many attempts, wait a minute" if code == 429 else b"Authentication required"
            method, path = txt(request.method), txt(request.path)
            if method == "POST":
                host = txt(request.getHeader("host") or "")
                origin = txt(request.getHeader("origin") or "")
                if request.getHeader("x-o4t-request") != "1" or \
                        (origin and urlparse(origin).netloc != host):
                    return self._send(request, {"error": "forbidden"}, 403)
                return self.post(request, path)
            if method == "GET":
                return self.get(request, path)
            return self._send(request, {"error": "method"}, 405)
        except Exception:
            import traceback
            log("web error:\n" + traceback.format_exc())
            return self._send(request, {"error": "internal error"}, 500)

    def get(self, request, path):
        if path in ("/", "/index.html"):
            if _state["page"] is None:
                with open(os.path.join(WEB_DIR, "index.html"), "rb") as fh:
                    _state["page"] = fh.read()
            request.setHeader(b"Content-Type", b"text/html; charset=utf-8")
            return _state["page"]
        if path == "/api/status":
            return self._send(request, system_status())
        if path == "/api/catalog":
            kind = self._arg(request, "kind", "plugin")
            if kind not in KINDS:
                return self._send(request, {"error": "kind"}, 400)
            return self._send(request, catalog_view(
                kind, self._arg(request, "cat"), self._arg(request, "q"),
                self._arg(request, "all") == "1"))
        if path == "/api/job":
            job = JOBS.get(self._arg(request, "id"))
            if not job:
                return self._send(request, {"error": "no such job"}, 404)
            start = int(self._arg(request, "from", "0") or 0)
            text = "".join(job.out)
            return self._send(request, {"out": text[start:], "next": len(text),
                                        "done": job.done, "rc": job.rc})
        return self._send(request, {"error": "not found"}, 404)

    def post(self, request, path):
        data = self._body(request)
        if path in ("/api/install", "/api/remove"):
            it = find_item(txt(data.get("id", "")))
            if not it:
                return self._send(request, {"error": "unknown item"}, 404)
            cmd = catalog.install_cmd(it) if path == "/api/install" else catalog.remove_cmd(it)
            if not cmd:
                return self._send(request, {"error": "not supported for this item"}, 400)
            return self._job(request, ("%s %s" % ("install" if path == "/api/install" else "remove",
                                                  it["name"])), cmd)
        if path == "/api/action":
            return self.action(request, txt(data.get("name", "")))
        if path == "/api/shell":
            if not get_setting("web_shell", False):
                return self._send(request, {"error": "web shell is disabled - enable it on the "
                                                     "receiver: Tools > Web control"}, 403)
            cmd = txt(data.get("cmd", "")).strip()
            if not cmd or len(cmd) > 4000:
                return self._send(request, {"error": "empty or too long"}, 400)
            return self._job(request, cmd.splitlines()[0][:80], cmd)
        if path == "/api/iptv":
            ok, msg = add_playlist(data)
            return self._send(request, {"ok": ok, "message": msg}, 200 if ok else 400)
        return self._send(request, {"error": "not found"}, 404)

    def _job(self, request, title, cmd):
        job = start_job(title, cmd)
        if job is None:
            return self._send(request, {"error": "another operation is running"}, 409)
        return self._send(request, {"job": job.id})

    def action(self, request, name):
        if name in ("restart_gui", "reboot", "standby"):
            mode = {"restart_gui": 3, "reboot": 2, "standby": 1}[name]
            log("action %s" % name)
            reactor.callLater(1.5, _quit, mode)
            return self._send(request, {"ok": True})
        shell = {"clear_ram": "sync; echo 3 > /proc/sys/vm/drop_caches && echo done",
                 "clean_tmp": "rm -f /tmp/*.ipk /tmp/*.tar.gz /tmp/o4t_pkg* && echo done",
                 "update_feed": "opkg update",
                 "self_update": "wget -q --no-check-certificate -O - %s | O4T_NO_RESTART=1 /bin/sh"
                                % shquote(INSTALL_URL),
                 "sync_catalog": "echo 'use the panel on the receiver to sync'"}.get(name)
        if name == "sync_catalog":
            def done(ok):
                pass
            from .version import CATALOG_URL, TMP_CATALOG
            shell = ("wget -q -T 15 -t 1 --no-check-certificate -O %s.part %s && mv -f %s.part %s "
                     "&& echo catalog synced" % (TMP_CATALOG, shquote(CATALOG_URL), TMP_CATALOG,
                                                 TMP_CATALOG))
        if not shell:
            return self._send(request, {"error": "unknown action"}, 400)
        return self._job(request, name, shell)


# ------------------------------------------------------------------ lifecycle
def start():
    """Start listening (idempotent). Called at session start."""
    if _state["port"] is not None or not get_setting("web_enabled", True):
        return False
    password()
    port = int(get_setting("web_port", WEB_PORT))
    site = server.Site(Root())
    site.displayTracebacks = False
    try:
        _state["port"] = reactor.listenTCP(port, site)
    except Exception as exc:
        log("web server cannot listen on %s: %s" % (port, exc))
        return False
    refresh_installed()
    loop = task.LoopingCall(refresh_installed)
    loop.start(180, now=False)
    _state["loop"] = loop
    log("web control listening on port %s" % port)
    return True


def stop():
    if _state["loop"] is not None:
        try:
            _state["loop"].stop()
        except Exception:
            pass
        _state["loop"] = None
    port, _state["port"] = _state["port"], None
    if port is not None:
        try:
            return port.stopListening()
        except Exception:
            pass


def restart():
    d = stop()
    if d is not None and hasattr(d, "addBoth"):
        d.addBoth(lambda *a: start())
    else:
        start()


def is_running():
    return _state["port"] is not None
