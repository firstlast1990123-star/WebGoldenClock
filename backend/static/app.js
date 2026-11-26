/* GoldenClok Contract Demo — dashboard renderer (vanilla JS, no build step).
   All values that originate from the API are escaped before interpolation. */

const REFRESH_MS = 15000;
const DAY_NAMES = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"];

// Contract time convention: UTC+7 wall clock for medication, epoch seconds on the wire.
const DISPLAY_TZ = "Asia/Ho_Chi_Minh";
const TZ_LABEL = "UTC+7";

const TIME_FORMAT = new Intl.DateTimeFormat("vi-VN", {
  timeZone: DISPLAY_TZ,
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
  hourCycle: "h23",
});

const el = (id) => document.getElementById(id);

function fmtTime(epochSeconds) {
  if (epochSeconds === null || epochSeconds === undefined) return "chưa có";
  return TIME_FORMAT.format(new Date(epochSeconds * 1000));
}

function fmtDuration(seconds) {
  if (seconds === null || seconds === undefined) return "—";
  if (seconds % 3600 === 0) {
    const hours = seconds / 3600;
    return `${hours} giờ`;
  }
  if (seconds % 60 === 0) return `${seconds / 60} phút`;
  return `${Math.round(seconds / 60)} phút`;
}

function fmtAgo(seconds) {
  const safe = Math.max(0, Math.floor(seconds));
  if (safe < 60) return "chưa đầy một phút trước";
  const minutes = Math.floor(safe / 60);
  if (minutes < 60) return `${minutes} phút trước`;
  const hours = Math.floor(minutes / 60);
  const restMinutes = minutes % 60;
  if (hours < 24) {
    return restMinutes ? `${hours} giờ ${restMinutes} phút trước` : `${hours} giờ trước`;
  }
  const days = Math.floor(hours / 24);
  return `${days} ngày trước`;
}

function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, (ch) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[ch]);
}

function daysLabel(days) {
  if (!Array.isArray(days) || days.length === 0) return "—";
  if (days.length === 7) return "Hằng ngày";
  return days.map((d) => DAY_NAMES[d - 1] || `?${d}`).join(", ");
}

function eventTone(type) {
  if (type === "FALL" || type === "SOS") return "danger";
  if (
    type === "FALL_CANCELLED" ||
    type === "LOW_BATTERY" ||
    type === "MED_MISSED" ||
    type === "HR_HIGH" ||
    type === "HR_LOW"
  ) {
    return "warn";
  }
  return "ok";
}

function smsLabel(value) {
  if (value === null || value === undefined) return '<span class="muted">—</span>';
  return value ? "Đã phát lệnh AT" : "Không gửi";
}

function emptyState(title, detail) {
  return `<div class="empty-state"><strong>${esc(title)}</strong>${esc(detail)}</div>`;
}

function syncNote(device, serverTime) {
  const threshold = fmtDuration(device.disconnected_after_seconds);
  if (device.last_sync_at === null || device.last_sync_at === undefined) {
    return `Chưa ghi nhận lần đồng bộ nào. Thiết bị được coi là mất kết nối cho đến khi đồng bộ trong ngưỡng ${threshold}.`;
  }
  const elapsed = Number(serverTime) - Number(device.last_sync_at);
  if (device.connected) {
    return `Đồng bộ lần cuối ${fmtAgo(elapsed)} — vẫn trong ngưỡng mất kết nối ${threshold}.`;
  }
  return `Đồng bộ lần cuối ${fmtAgo(elapsed)} — đã vượt ngưỡng mất kết nối ${threshold}.`;
}

function renderDevice(data) {
  const d = data.device;
  const tone = d.connected ? "ok" : "danger";
  const label = d.connected ? "ĐÃ KẾT NỐI" : "MẤT KẾT NỐI";
  el("device-card").dataset.status = tone;

  el("device-body").innerHTML = `
    <div class="status-hero">
      <div class="status-identity">
        <span class="status-dot" aria-hidden="true"></span>
        <div>
          <p class="status-label ${tone}">${label}</p>
          <p class="status-name">${esc(d.name)}</p>
          <p class="status-id">Mã thiết bị <code>${esc(d.id)}</code></p>
        </div>
      </div>
      <p class="status-note">${esc(syncNote(d, data.server_time))}</p>
    </div>
    <dl class="stat-grid">
      <div class="stat"><dt>Đồng bộ lần cuối (${TZ_LABEL})</dt><dd>${esc(fmtTime(d.last_sync_at))}</dd></div>
      <div class="stat"><dt>Ngưỡng mất kết nối</dt><dd>${esc(fmtDuration(d.disconnected_after_seconds))} không đồng bộ</dd></div>
      <div class="stat"><dt>Phiên bản cấu hình</dt><dd>${esc(d.config_version)}</dd></div>
      <div class="stat"><dt>Dải cảnh báo nhịp tim</dt><dd>${esc(d.hr_low)}–${esc(d.hr_high)} nhịp/phút</dd></div>
    </dl>`;
}

function renderWearer(data) {
  const w = data.wearer;
  const note = w.notes ? `<p class="profile-note">${esc(w.notes)}</p>` : "";
  el("wearer-body").innerHTML = `
    <dl class="stat-grid">
      <div class="stat"><dt>Mã người đeo</dt><dd><code>${esc(w.id ?? "—")}</code></dd></div>
      <div class="stat"><dt>Họ tên</dt><dd>${esc(w.name || "—")}</dd></div>
      <div class="stat"><dt>Số điện thoại người giám hộ</dt><dd><code>${esc(w.guardian_phone || "—")}</code></dd></div>
    </dl>
    ${note}`;
}

function renderSchedules(data) {
  if (!data.schedules.length) {
    el("schedule-body").innerHTML = emptyState(
      "Chưa có lịch uống thuốc.",
      "Hãy nạp dữ liệu mẫu cho cơ sở dữ liệu demo để hiển thị lịch uống thuốc."
    );
    return;
  }
  const rows = data.schedules
    .map(
      (s) => `<tr>
        <td>${esc(s.schedule_id)}</td>
        <td>${esc(s.name)}</td>
        <td>${esc(s.time)} <span class="tz">${TZ_LABEL}</span></td>
        <td>${esc(daysLabel(s.days))}</td>
        <td>${esc(s.start_date)}</td>
        <td>${esc(s.end_date ?? "—")}</td>
      </tr>`
    )
    .join("");
  el("schedule-body").innerHTML = `
    <div class="table-wrap">
      <table>
        <caption class="sr-only">Lịch uống thuốc đã lưu cho người đeo trong bản demo.</caption>
        <thead>
          <tr><th scope="col">Ca</th><th scope="col">Tên thuốc</th><th scope="col">Giờ</th><th scope="col">Ngày</th><th scope="col">Bắt đầu</th><th scope="col">Kết thúc</th></tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>`;
}

function renderEvents(data) {
  if (!data.events.length) {
    el("events-body").innerHTML = emptyState(
      "Chưa có sự kiện nào.",
      "Sự kiện sẽ xuất hiện sau khi thiết bị đồng bộ."
    );
    return;
  }
  const rows = data.events
    .map(
      (e) => `<tr>
        <td><span class="badge ${eventTone(e.event_type)}">${esc(e.event_type)}</span></td>
        <td>${esc(fmtTime(e.occurred_at))}</td>
        <td>${smsLabel(e.sms_sent)}</td>
        <td><code>${esc(e.record_id)}</code></td>
      </tr>`
    )
    .join("");
  el("events-body").innerHTML = `
    <div class="table-wrap">
      <table>
        <caption class="sr-only">Các sự kiện gần đây của thiết bị, mới nhất trước.</caption>
        <thead>
          <tr><th scope="col">Loại sự kiện</th><th scope="col">Thời điểm (${TZ_LABEL})</th><th scope="col">SMS</th><th scope="col">Mã bản ghi</th></tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>`;
}

function renderMeasurements(data) {
  if (!data.measurements.length) {
    el("measure-body").innerHTML = emptyState(
      "Chưa nhận được dữ liệu đo.",
      "Dữ liệu nhịp tim sẽ xuất hiện sau khi thiết bị đồng bộ."
    );
    return;
  }
  const rows = data.measurements
    .map(
      (m) => `<tr>
        <td class="num">${esc(m.heart_rate)} nhịp/phút</td>
        <td>${esc(fmtTime(m.measured_at))}</td>
        <td><code>${esc(m.record_id)}</code></td>
      </tr>`
    )
    .join("");
  el("measure-body").innerHTML = `
    <div class="table-wrap">
      <table>
        <caption class="sr-only">Các kết quả đo nhịp tim gần đây, mới nhất trước.</caption>
        <thead>
          <tr><th scope="col">Nhịp tim</th><th scope="col">Thời điểm đo (${TZ_LABEL})</th><th scope="col">Mã bản ghi</th></tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>`;
}

function renderNotSeeded() {
  const detail = "Hãy chạy lệnh python3 backend/seed.py từ thư mục gốc của repository rồi làm mới.";
  el("device-card").dataset.status = "neutral";
  el("device-body").innerHTML = emptyState("Cơ sở dữ liệu demo chưa được nạp dữ liệu.", detail);
  for (const id of ["wearer-body", "schedule-body", "events-body", "measure-body"]) {
    el(id).innerHTML = emptyState("Chưa có dữ liệu mô phỏng.", detail);
  }
}

function renderUnavailable() {
  el("device-card").dataset.status = "neutral";
  const detail = "Hãy khởi động máy chủ demo cục bộ rồi chọn Làm mới.";
  el("device-body").innerHTML = emptyState("Không thể tải bảng điều khiển.", detail);
  for (const id of ["wearer-body", "schedule-body", "events-body", "measure-body"]) {
    el(id).innerHTML = emptyState("Chưa tải được dữ liệu.", detail);
  }
}

let inFlight = false;
let hasLoaded = false;

async function load() {
  if (inFlight) return;
  inFlight = true;

  const state = el("refresh-state");
  const button = el("refresh");
  const alertBox = el("api-alert");

  button.disabled = true;
  button.setAttribute("aria-busy", "true");
  state.textContent = "Đang làm mới…";
  state.className = "refresh-time";

  try {
    const res = await fetch("/api/dashboard", {
      cache: "no-store",
      headers: { Accept: "application/json" },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    if (!data.seeded) {
      renderNotSeeded();
    } else {
      renderDevice(data);
      renderWearer(data);
      renderSchedules(data);
      renderEvents(data);
      renderMeasurements(data);
    }

    const stamp =
      data.server_time === null || data.server_time === undefined
        ? "vừa xong"
        : fmtTime(data.server_time);
    state.textContent = `Cập nhật lần cuối: ${stamp} ${TZ_LABEL}`;
    state.className = "refresh-time";
    hasLoaded = true;
    alertBox.hidden = true;
    alertBox.textContent = "";
  } catch (err) {
    if (!hasLoaded) renderUnavailable();
    state.textContent = "Cập nhật thất bại";
    state.className = "refresh-time is-error";
    alertBox.textContent = hasLoaded
      ? `Không thể kết nối API bảng điều khiển (${err.message}). Đang hiển thị dữ liệu tải thành công gần nhất.`
      : `Không thể kết nối API bảng điều khiển (${err.message}). Hãy khởi động máy chủ demo cục bộ rồi làm mới.`;
    alertBox.hidden = false;
  } finally {
    inFlight = false;
    button.disabled = false;
    button.removeAttribute("aria-busy");
  }
}

el("refresh").addEventListener("click", load);
load();
setInterval(load, REFRESH_MS);
