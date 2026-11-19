#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import base64
import io
import os
import subprocess
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = 2020
LOGO_PATHS = [
    "/usr/lib/enigma2/python/Plugins/Extensions/Online4Tech/plugin.png",
    "/usr/lib/enigma2/python/Plugins/Extensions/Online4TechWeb/assets/o4t_icon.png",
    "/usr/lib/enigma2/python/Plugins/Extensions/Online4TechWeb/assets/o4t_banner.png",
]


def get_logo_data_uri():
    for p in LOGO_PATHS:
        if os.path.exists(p) and os.path.getsize(p) > 0:
            try:
                with open(p, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("ascii")
                return "data:image/png;base64," + b64
            except Exception:
                pass
    return ""


def get_sys_stats():
    ram_txt = "N/A"
    flash_txt = "N/A"
    temp_txt = "N/A"
    try:
        with open("/proc/meminfo", "r", encoding="utf-8", errors="ignore") as f:
            lines = dict(
                (parts[0].rstrip(":"), int(parts[1]))
                for line in f
                if len(line.split()) >= 2
                for parts in [line.split()]
            )
        total_mb = lines.get("MemTotal", 0) // 1024
        avail_mb = lines.get("MemAvailable", lines.get("MemFree", 0)) // 1024
        used_mb = max(0, total_mb - avail_mb)
        pct = int((used_mb * 100) / total_mb) if total_mb else 0
        ram_txt = f"{pct}% ({used_mb}/{total_mb}MB)"
    except Exception:
        pass

    try:
        st = os.statvfs("/")
        free_gb = (st.f_bavail * st.f_frsize) / (1024 ** 3)
        total_gb = (st.f_blocks * st.f_frsize) / (1024 ** 3)
        used_pct = int(((total_gb - free_gb) * 100) / total_gb) if total_gb else 0
        flash_txt = f"{used_pct}% ({free_gb:.1f}G free)"
    except Exception:
        pass

    for tp in ("/proc/stb/fp/temp_sensor", "/sys/class/thermal/thermal_zone0/temp"):
        if os.path.exists(tp):
            try:
                with open(tp, "r", encoding="utf-8", errors="ignore") as tf:
                    raw = tf.read().strip()
                val = int(float(raw))
                if val > 1000:
                    val = val // 1000
                temp_txt = f"{val}\u00b0C"
                break
            except Exception:
                pass

    return ram_txt, flash_txt, temp_txt


def build_html(message=""):
    logo_uri = get_logo_data_uri()
    ram_txt, flash_txt, temp_txt = get_sys_stats()
    logo_html = (
        f'<img src="{logo_uri}" alt="Online4Tech" width="96" height="38" '
        f'loading="eager" decoding="async" '
        f'style="height:38px;width:auto;border-radius:8px;object-fit:contain;display:inline-block;vertical-align:middle;" />'
        if logo_uri
        else ""
    )
    msg_banner = (
        f'<div style="margin:10px 0;padding:10px 14px;border-radius:8px;background:#162636;color:#7dd3fc;border:1px solid rgba(125,211,252,0.35);font-size:13px;">{message}</div>'
        if message
        else ""
    )
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Online4Tech Web Panel • Port {PORT}</title>
  <style>
    body {{ margin:0; padding:16px; background:#0b0f17; color:#f8fafc; font-family:Tahoma,Arial,sans-serif; }}
    .wrap {{ max-width:980px; margin:0 auto; }}
    .hdr {{ display:flex; align-items:center; justify-content:space-between; gap:12px; padding:12px 16px; background:#121826; border:1px solid rgba(245,196,66,0.35); border-radius:12px; }}
    .hdr-brand {{ display:flex; align-items:center; gap:10px; }}
    .hdr-title {{ margin:0; font-size:18px; color:#f5c442; font-weight:700; }}
    .hdr-sub {{ font-size:12px; color:#94a3b8; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:10px; margin:14px 0; }}
    .card {{ background:#121826; border:1px solid rgba(148,163,184,0.18); border-radius:10px; padding:12px; }}
    .card-k {{ font-size:12px; color:#94a3b8; }}
    .card-v {{ font-size:16px; font-weight:700; color:#f5c442; margin-top:4px; }}
    .box {{ background:#121826; border:1px solid rgba(148,163,184,0.18); border-radius:12px; padding:14px; margin:12px 0; }}
    .btn {{ border:none; border-radius:8px; padding:9px 14px; font-weight:700; font-size:13px; cursor:pointer; }}
    .btn-gold {{ background:#f5c442; color:#0b0f17; }}
    .btn-blue {{ background:#0284c7; color:#ffffff; }}
    .btn-red {{ background:#be123c; color:#ffffff; }}
    .btn-green {{ background:#059669; color:#ffffff; }}
    .row {{ display:flex; flex-wrap:wrap; gap:8px; align-items:center; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hdr">
      <div class="hdr-brand">
        {logo_html}
        <div>
          <h1 class="hdr-title">Online4Tech</h1>
          <div class="hdr-sub">لوحة التحكم المتكاملة لأجهزة Enigma2 • Port {PORT}</div>
        </div>
      </div>
      <div class="hdr-sub">v7.5 Gold</div>
    </div>

    {msg_banner}

    <div class="grid">
      <div class="card"><div class="card-k">الذاكرة (RAM)</div><div class="card-v">{ram_txt}</div></div>
      <div class="card"><div class="card-k">المساحة (Flash)</div><div class="card-v">{flash_txt}</div></div>
      <div class="card"><div class="card-k">حرارة المعالج</div><div class="card-v">{temp_txt}</div></div>
    </div>

    <div class="box">
      <div style="font-weight:700;margin-bottom:10px;color:#f5c442;">التحكم السريع وتثبيت Online4Tech Store v7.5 Gold</div>
      <div class="row">
        <button id="o4tInstallV75NowBtn" type="button" class="btn btn-gold" onclick="o4tInstallV75Direct()">تثبيت v7.5 Gold الآن</button>
        <button type="button" class="btn btn-blue" onclick="o4tSendAction('restart_gui')">ريستارت الواجهة</button>
        <button type="button" class="btn btn-red" onclick="o4tSendAction('reboot')">ريستارت الريسيفر</button>
        <button type="button" class="btn btn-green" onclick="location.reload()">تحديث اللوحة</button>
        <span id="o4tInstallV75Status" style="color:#38bdf8;font-size:12px;"></span>
      </div>
    </div>
  </div>

  <script>
    function o4tSetStatus(txt) {{
      var el = document.getElementById("o4tInstallV75Status");
      if (el) el.textContent = txt;
    }}
    function o4tInstallV75Direct() {{
      var cmd = 'opkg install --force-reinstall "https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/enigma2-plugin-extensions-online4tech_7.5_all.ipk"';
      o4tSetStatus("جاري إرسال أمر تثبيت v7.5 Gold...");
      var xhr = new XMLHttpRequest();
      xhr.open("POST", "/run_cmd", true);
      xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");
      xhr.onload = function() {{
        o4tSetStatus(xhr.status >= 200 && xhr.status < 300 ? "تم تنفيذ أمر التثبيت v7.5 Gold" : "تم إرسال الأمر");
      }};
      xhr.onerror = function() {{
        o4tSetStatus("تم إرسال أمر التثبيت");
      }};
      xhr.send("cmd=" + encodeURIComponent(cmd));
    }}
    function o4tSendAction(act) {{
      o4tSetStatus("جاري تنفيذ الأمر...");
      var xhr = new XMLHttpRequest();
      xhr.open("POST", "/action", true);
      xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");
      xhr.onload = function() {{ o4tSetStatus("تم إرسال الأمر بنجاح"); }};
      xhr.onerror = function() {{ o4tSetStatus("تم إرسال الأمر"); }};
      xhr.send("act=" + encodeURIComponent(act));
    }}
  </script>
</body>
</html>"""


class O4THandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def _send_html(self, html_str, status=200):
        raw = html_str.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        self._send_html(build_html())

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(length).decode("utf-8", errors="ignore")
        params = urllib.parse.parse_qs(body)
        if self.path == "/run_cmd":
            cmd = params.get("cmd", [""])[0]
            if cmd:
                subprocess.Popen(["/bin/sh", "-c", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._send_html("OK")
            return
        if self.path == "/action":
            act = params.get("act", [""])[0]
            if act == "restart_gui":
                subprocess.Popen(["/bin/sh", "-c", "killall -9 enigma2 >/dev/null 2>&1 || true"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif act == "reboot":
                subprocess.Popen(["/bin/sh", "-c", "reboot >/dev/null 2>&1 || true"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._send_html("OK")
            return
        self._send_html("NOT_FOUND", status=404)


def main():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), O4THandler)
    server.serve_forever()


if __name__ == "__main__":
    main()