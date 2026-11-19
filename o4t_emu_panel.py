

<div id="o4t-v75-panel-action" style="margin:12px 0;padding:12px 16px;background:#131a29;border:1px solid rgba(245,196,66,0.45);border-radius:10px;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:10px;direction:rtl;">
  <div>
    <div style="color:#f5c442;font-weight:700;font-size:14px;">Online4Tech Store v7.5 Gold</div>
    <div style="color:#cbd5e1;font-size:12px;">تثبيت أو تحديث البلجن مباشرة على الريسيفر بضغطة واحدة</div>
  </div>
  <div style="display:flex;align-items:center;gap:8px;">
    <button id="o4tInstallV75NowBtn" type="button" onclick="o4tInstallV75Direct()" style="background:#f5c442;color:#0e131f;border:none;border-radius:8px;padding:8px 16px;font-weight:700;font-size:13px;cursor:pointer;">
      تثبيت v7.5 Gold الآن
    </button>
    <span id="o4tInstallV75Status" style="color:#38bdf8;font-size:12px;"></span>
  </div>
</div>
<script id="o4t-v75-direct-js">
function o4tInstallV75Direct() {
  var st = document.getElementById("o4tInstallV75Status");
  var btn = document.getElementById("o4tInstallV75NowBtn");
  var installCmd = 'opkg install --force-reinstall "https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/enigma2-plugin-extensions-online4tech_7.5_all.ipk"';
  if (btn) btn.disabled = true;
  if (st) st.textContent = "جاري إرسال أمر التثبيت للريسيفر...";

  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/run_cmd", true);
  xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");
  xhr.timeout = 25000;
  xhr.onload = function() {
    if (btn) btn.disabled = false;
    if (xhr.status >= 200 && xhr.status < 300) {
      if (st) st.textContent = "تم تنفيذ تثبيت v7.5 Gold بنجاح";
    } else {
      if (st) st.textContent = "تم إرسال الأمر تحقق من الريسيفر";
    }
  };
  xhr.onerror = xhr.ontimeout = function() {
    if (btn) btn.disabled = false;
    if (st) st.textContent = "تم إرسال أمر التثبيت (قد يعيد الريسيفر التشغيل)";
  };
  try {
    xhr.send("cmd=" + encodeURIComponent(installCmd));
  } catch (e) {
    if (btn) btn.disabled = false;
    if (st) st.textContent = "تعذر الإرسال المباشر";
  }
}
</script>
