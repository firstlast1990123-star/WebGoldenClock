# NHẬT KÝ TIẾN ĐỘ DỰ ÁN GOLDENCLOK (PROJECT PROGRESS LOG)

Tài liệu theo dõi tiến độ, quyết định kỹ thuật và các hạng mục triển khai cho nền tảng Web GoldenClok.
Quy tắc quản lý: Cập nhật sau mỗi task/phase, ghi nhận đúng thực tế, phân định rõ trạng thái quyết định và tuyệt đối không lưu trữ thông tin nhạy cảm.

---

## TỔNG QUAN HIỆN TRẠNG DỰ ÁN (CURRENT STATUS)

- **Giai đoạn hiện tại:** Phase 2.8.4 — Đối soát tài liệu sau baseline: **Contract Demo thu gọn** đã kiểm chứng bằng 47 test tự động, SĐT giả lập chuẩn `+84000000000`, `.gitignore` được tăng cường, tài liệu kiến trúc/lộ trình được đối soát (Phase 2.2 → 2.8.1) và **baseline Git đã được commit cục bộ + push thành công lên GitHub** (Phase 2.8.2/2.8.3). Commit baseline `ebc288281a8dfc4b9f644cfe2d63ac04ba0c5843` — `chore: establish GoldenClok Contract Demo baseline` — gồm **33 tệp đã kiểm duyệt**; GitHub `main` trỏ đúng commit này. **Option D Hybrid đã được phê duyệt là kiến trúc sản xuất mục tiêu tại Phase 1.7.2.** Việc triển khai sản xuất **chưa bắt đầu** và vẫn phụ thuộc vào mức độ sẵn sàng bảo mật, các quyết định chưa chốt và một lần phê duyệt triển khai riêng. Tech Stack vẫn `PROVISIONAL`; production Phase 2 vẫn **blocked**.
- **Tài liệu kiểm toán:** Đã lưu tại `docs/Architecture/Phase 1.6 - Architecture Readiness Audit.md`.
- **Phạm vi Contract Demo:** `docs/Decisions/Phase 2 Contract Demo Scope.md` (FastAPI + SQLite + HTML/JS thuần, chỉ chạy `127.0.0.1`).
- **SĐT giả lập chuẩn (Phase 2.7.2, xác nhận lại Phase 2.7.3):** `+84000000000` — quyết định của Project Owner; đã áp dụng trong `backend/seed.py`, các test, `README.md`, decision record và `backend/demo.db`.
- **Trạng thái mã nguồn:** Đã có `backend/` (endpoint `POST /api/device/sync`, dashboard demo, seed dữ liệu giả lập, **47 test tự động**: 41 test contract/persistence + 6 test HTTP integration). Lớp HTTP đã được kiểm chứng tự động: `/health` 200, dashboard 200, sync 200/ACK 4 ID, replay không trùng, token sai/thiếu 401, JSON hỏng và lỗi cấu trúc 400, mixed record 200 với `rejected`, config-version handshake. Dashboard đã được tinh chỉnh UI/UX, Việt hóa và **được Project Owner phê duyệt thị giác** (Phase 2.6; kiểm chứng headless Firefox ở 1920, 1440, 1280, 1024 và 360 px; **chưa** kiểm thử tương tác). **Chưa có** migration Supabase, chưa có xác thực guardian, chưa triển khai mô hình bảo mật Option D.
- **Môi trường phát triển:** Linux Mint (4 Cores, ~3.3 GB RAM, áp lực bộ nhớ cao, Python 3.12 & SQLite có sẵn; chưa cài Node.js). `.venv/` trong repo đã có FastAPI 0.165.0 và Uvicorn 0.54.0 (đã nằm trong `.gitignore`); interpreter hệ thống vẫn ở chế độ PEP 668, không có FastAPI/Uvicorn và không cài đặt hệ thống. Test HTTP dùng `.venv/bin/python -m uvicorn` + thư viện chuẩn `urllib`, không cài thêm gói.
- **Trạng thái baseline Git:** **đã hoàn tất.** Phase 2.8.2 tạo commit cục bộ `ebc288281a8dfc4b9f644cfe2d63ac04ba0c5843` (message `chore: establish GoldenClok Contract Demo baseline`, parent `e0d4d066d558ca5a76d21d01e27248ffc551f493`, **33 tệp** đã kiểm duyệt); Phase 2.8.3 push thành công lên GitHub `main` ngày **2026-11-27**. GitHub `main` đã được xác minh độc lập là trỏ đúng commit baseline.
- **Bước tiếp theo:** (1) Phase 2.8.5 — đánh giá/tích hợp công cụ workflow; (2) Phase 2.9 — đánh giá mức độ sẵn sàng kiến trúc và bảo mật; (3) chỉ bắt đầu Phase 2 — Project Scaffolding sau khi các quyết định bắt buộc được chốt và có uỷ quyền triển khai riêng (Task `GC-T003`, `GC-T004`).
- **Giới hạn vẫn còn:** chưa thử nghiệm ESP32/phần cứng thật; request envelope vẫn `INTERIM`; các mục firmware `OPEN` vẫn `OPEN`; dashboard chưa có xác thực; chưa có Supabase project hay CSDL sản xuất; demo **không** bảo mật sản xuất; chưa kiểm thử tương tác/đa trình duyệt; Superpowers, Spec Kit và Browser MCP chưa được tích hợp.

---

## LỊCH SỬ TIẾN ĐỘ THEO GIAI ĐOẠN

### [2026-11-20] — Phase 1: Project Discovery (Khảo sát ban đầu)
- **Mục tiêu:** Khảo sát repository, phân tích hợp đồng giao tiếp Firmware ↔ Web, đánh giá môi trường máy chủ cục bộ và lập báo cáo kỹ thuật ban đầu.
- **Công việc đã hoàn thành:**
  - Khảo sát mã nguồn repository: Xác nhận branch `main`, 1 commit ban đầu, chưa có code ứng dụng.
  - Kiểm tra tài nguyên máy tính phát triển: 4 cores, RAM vật lý ~3.3 GB (khả dụng ~380 MB, Swap sử dụng ~2.3 GB), phát hiện áp lực bộ nhớ nghiêm trọng.
  - Phân tích hợp đồng giao tiếp giữa nhóm Firmware (ESP32-32D, A7680C) và Web Platform.
  - Đề xuất sơ bộ Tech Stack và lập Báo cáo Khảo sát kỹ thuật.
- **Tập tin tạo/sửa đổi:** Không (tuân thủ nghiêm ngặt chế độ Read-Only).
- **Kiểm tra/Xác minh đã thực hiện:**
  - Lệnh kiểm tra hệ thống: `git status`, `git log`, `free -m`, `python3 --version`, `which node/npm`.
- **Hạn chế/Rủi ro ghi nhận:** Báo cáo ban đầu có một số giả định chưa chuẩn xác về định dạng ACK, khoảng thời gian sync và quy trình bootstrap thiết bị.

---

### [2026-11-20] — Phase 1.5: Architecture Refinement & Contract Correction (Hiệu đính & Tinh chỉnh kiến trúc)
- **Mục tiêu:** Hiệu đính toàn bộ các sai lệch trong báo cáo Phase 1 theo chỉ đạo của Project Owner; tích hợp các quyết định công nghệ đã phê duyệt (Supabase PostgreSQL, Supabase Auth); thiết kế chi tiết kiến trúc kết nối và mô hình dữ liệu chuẩn hóa.
- **Công việc đã hoàn thành:**
  - **Sửa đổi các sai sót kỹ thuật:**
    1. *ACK Response Format:* Đính chính định dạng `ack` bắt buộc là mảng phẳng chứa ID các bản ghi (`["GC-001", "GC-002"]`), tuyệt đối không nhóm theo loại (`hr`, `med`, `events`).
    2. *Device Bootstrap:* Hủy bỏ endpoint chưa duyệt `POST /api/device/bootstrap`; phân loại quy thức cấp token ban đầu là OPEN; đánh giá các phương án thay thế.
    3. *Tần suất đồng bộ:* Xác nhận đã chốt (CONFIRMED): Khi có WiFi đồng bộ ngay; duy trì WiFi đồng bộ ~15 phút/lần; sau SMS khẩn cấp thử đồng bộ ngay; trước hạn lịch thuốc 1 ngày đồng bộ kiểm tra gia hạn. V1 không sync qua 4G.
    4. *Cấu hình JSON phản hồi:* Xác nhận cấu hình trả về đã được chốt cấu trúc chuẩn (`version`, `wearer_name`, `guardian_phone`, `hr_high`, `hr_low`, `schedule` với `id`, `name`, `time`, `days`, `start_date`, `end_date`).
    5. *Thông số ghép nối & Cảnh báo ngã:* Đính chính các thông số TTL, số lần khóa lockout và độ trễ thông báo ngã 15–30s chỉ là đề xuất thảo luận, phân loại là OPEN.
    6. *Định danh thiết bị:* Không mặc định `device_id` là MAC address; phân loại là OPEN.
  - **Thiết kế phân hệ Supabase:**
    - Supabase PostgreSQL: Phân tích Direct Connection vs Session Pooler vs Transaction Pooler (Supavisor port 6543 vs 5432) cho backend FastAPI kết nối dài hạn và Alembic migrations.
    - Supabase Auth: Tách biệt hoàn toàn xác thực Người giám hộ (Supabase Auth JWT) và xác thực Thiết bị đeo (Opaque Token băm SHA-256).
    - Phân định rõ 3 chức năng điện thoại/SMS: Đăng nhập Người giám hộ, Xác thực SĐT khẩn cấp qua OTP Web, và SMS khẩn cấp phát từ mô-đun A7680C.
  - **Chuẩn hóa Mô hình Dữ liệu (Schema Refinement):**
    - Xác định 10 thực thể: `guardians`, `wearers`, `devices`, `device_tokens`, `pairing_codes`, `medication_schedules`, `medication_records`, `health_measurements`, `events`, `sync_logs`.
    - Ràng buộc toàn vẹn: Unique `(device_id, schedule_id)` với `schedule_id` 0–255; tính Idempotency qua `(device_id, record_id)`; chính sách lưu trữ 7 ngày (HR, Med) và 30 ngày (Events).
- **Bảng trạng thái quyết định kỹ thuật:**
  - `CONFIRMED`:
    - Cơ sở dữ liệu: Supabase PostgreSQL.
    - Xác thực Người giám hộ: Supabase Auth.
    - Quản lý tài liệu: Sử dụng GitHub Documentation / `project.md` (hoãn Obsidian).
    - Hợp đồng Firmware: Endpoint `POST /api/device/sync`, ACK mảng phẳng, cấu trúc JSON cấu hình trả về, chu kỳ sync (~15m, có WiFi sync ngay, sau SMS khẩn cấp sync ngay, trước 1 ngày hết hạn lịch thuốc sync kiểm tra).
    - Chính sách thiết bị khi `unpaired`: Xóa dữ liệu/cấu hình, ngừng đo, ngừng nhắc thuốc, ngừng SMS.
    - Chính sách lưu trữ: HR 7 ngày, Med 7 ngày, Events 30 ngày, Schedules không tự động xóa.
    - Trạng thái hiển thị V1: Thời gian sync cuối, mất kết nối sau ~1 giờ; không hiển thị % pin, không tracking thời gian thực.
  - `PROVISIONAL` (Được chọn để đánh giá, chưa phê duyệt chính thức):
    - Backend: Python 3.12 + FastAPI + SQLAlchemy 2.0 Async + Alembic.
    - Frontend: React + Vite + TypeScript + Tailwind CSS.
  - `PROPOSED` (Đề xuất kỹ thuật đang chờ xem xét):
    - Phương thức đăng nhập Guardian: Email & Password cho V1 (tiết kiệm chi phí SMS).
    - Phương án cấp bootstrap token: Factory-provisioned Pre-shared Secret hoặc QR Code kích hoạt một lần.
    - Giới hạn payload: Tạm đề xuất tối đa 200 bản ghi/lần sync.
    - Kết nối DB: Dùng Session Pooler (port 5432) cho FastAPI backend và Direct connection cho Alembic.
    - Hiển thị sự kiện ngã: Lưu ngay lập tức khi nhận; nếu có `FALL_CANCELLED` đến sau thì cập nhật trạng thái hiển thị của vụ việc nhưng vẫn giữ nguyên cả 2 bản ghi lịch sử.
  - `OPEN` (Đang chờ quyết định):
    - Cơ chế cấp bootstrap token lần đầu cho thiết bị ESP32 chưa có token.
    - Định dạng và phương thức nạp `device_id` phần cứng.
    - Ngưỡng thời gian và chính sách thông báo sự kiện `FALL` / `FALL_CANCELLED` trên giao diện người giám hộ.
    - Chi tiết ngữ nghĩa lịch thuốc (`end_date` có thể null cho thuốc dùng vô thời hạn không; nhiều khung giờ trong ngày biểu diễn bằng nhiều schedule_id hay mảng).
- **Tập tin tạo/sửa đổi:**
  - Tạo mới: `project.md` (tập tin duy nhất được phép tạo/sửa đổi trong pha này).
- **Kiểm tra/Xác minh đã thực hiện:**
  - Kiểm tra trạng thái git: `git status` xác nhận working tree sạch trước khi tạo file.
  - Đối soát tài liệu: Đọc và rà soát từng điều khoản trong yêu cầu của Project Owner và Addendum.
- **Kế hoạch tiếp theo:**
  - Chờ Project Owner phê duyệt Báo cáo Tinh chỉnh Kiến trúc.
  - Chuẩn bị bước vào Phase 2: Thiết lập khung dự án FastAPI + React, cấu hình kết nối Supabase, thiết lập Alembic migrations và test suite.

---

### [2026-11-20] — Thiết lập Quy chế Hoạt động Workspace (Workspace Governance & AGENTS.md Setup)
- **Mục tiêu:** Thiết lập quy tắc hoạt động bền vững và quy chế quản trị dự án cho AI Agent và nhà phát triển tại workspace nhằm ngăn ngừa lệch phạm vi (scope drift), quên quyết định kiến trúc, sửa đổi mã tùy tiện và bỏ sót cập nhật tiến độ.
- **Bản chất công việc:** Đây là thay đổi cấu hình và quy chế quản trị workspace, **không phải là triển khai mã nguồn ứng dụng**.
- **Công việc đã hoàn thành:**
  - Khảo sát hiện trạng workspace: Kiểm tra `git status`, các tệp tin hiện hữu, xác nhận `AGENTS.md` chưa tồn tại và `project.md` đang theo dõi tiến độ chuẩn xác.
  - Khởi tạo tập tin `AGENTS.md` tại thư mục gốc với 8 nguyên tắc cốt lõi:
    1. *Nhận diện dự án & Phân định trách nhiệm:* Web Platform toàn diện; tuyệt đối không viết firmware nhúng; tích hợp qua hợp đồng đã duyệt.
    2. *Nắm bắt ngữ cảnh trước khi làm:* Đọc `AGENTS.md`, `project.md`, inspect mã nguồn và kiểm tra Git trước mọi task.
    3. *Kiểm soát phạm vi nhiệm vụ:* Làm đúng acceptance criteria, không thêm tính năng thừa, không refactor tùy tiện.
    4. *Bảo vệ hợp đồng Firmware bất biến:* Tuyệt đối không tự ý đổi tên trường, kiểu dữ liệu, định dạng ACK phẳng, mã lỗi HTTP, enum sự kiện và chu kỳ sync.
    5. *Kỷ luật lập trình:* Mặc định Single Agent, tiết kiệm tài nguyên trên máy Linux Mint RAM ~3.3 GB, ưu tiên test tập trung.
    6. *An toàn bảo mật trên GitHub công khai:* Chặn commit secrets, không lộ Service-Role key, dùng dữ liệu giả lập.
    7. *Quy tắc bắt buộc với project.md:* Đọc đầu phiên, cập nhật cuối phiên, nối tiếp lịch sử, không xóa vết quá khứ.
    8. *Quy trình nghiệm thu hoàn thành task:* Rà soát diff, kiểm tra kết quả, cập nhật log, dừng lại và không tự tiện commit/push.
  - Cập nhật nhật ký tiến độ `project.md` theo quy định.
- **Tập tin tạo/sửa đổi:**
  - Tạo mới: `AGENTS.md`
  - Sửa đổi: `project.md` (cập nhật tóm tắt hiện trạng và thêm mục lịch sử tiến độ).
- **Quyết định kỹ thuật & Phân loại trạng thái:**
  - `CONFIRMED`: Thiết lập `AGENTS.md` làm luật hoạt động thường trực bắt buộc cho mọi Agent trong workspace.
- **Kiểm tra/Xác minh đã thực hiện:**
  - Kiểm tra sự tồn tại của `AGENTS.md` tại gốc repo: Đã tạo thành công.
  - Kiểm tra nội dung `AGENTS.md`: Ngắn gọn, rõ ràng, không trùng lặp toàn bộ global rules nhưng bao quát đầy đủ 8 yêu cầu quản trị.
  - Kiểm tra `git status` và `git diff`: Xác nhận chỉ có `AGENTS.md` và `project.md` bị tác động, không ảnh hưởng đến bất kỳ tệp tin nào khác.
- **Hạn chế/Vấn đề chưa xác minh:** Quy chế quản trị đã sẵn sàng nhưng chưa áp dụng vào việc viết code vì dự án vẫn đang ở giai đoạn chuẩn bị.
- **Kế hoạch tiếp theo:** Chờ Project Owner phê duyệt báo cáo kiến trúc và cho phép bắt đầu Phase 2.

---

### [2026-11-21] — Thiết lập Obsidian Knowledge Workspace (Dashboard, Roadmap & Task Board)

- **Mục tiêu:** Tạo lớp điều hướng và quản lý công việc trực quan trong Obsidian ngay trên repository `WebGoldenClock`, không tạo bản sao Vault tách rời.
- **Quyết định & nguyên tắc:**
  - `CONFIRMED`: Obsidian được sử dụng làm lớp quản lý trực quan cho Dashboard, Roadmap, Decision Register và Task Board.
  - `CONFIRMED`: `project.md` tiếp tục là nhật ký tiến độ chính thức và duy nhất; Dashboard/Roadmap/Tasks không thay thế lịch sử này.
  - `CONFIRMED`: Sử dụng Obsidian Bases (core plugin) cho Task Board; không cần community plugin Kanban riêng.
- **Tập tin tạo mới:**
  - `docs/Home.md`: Project Dashboard và liên kết nhanh.
  - `docs/Roadmap.md`: Các giai đoạn, điều kiện hoàn thành và cổng phê duyệt.
  - `docs/Decisions/Open Decisions.md`: Sổ quyết định CONFIRMED/PROVISIONAL/PROPOSED/OPEN.
  - `docs/Tasks/Task Board.base`: Bases với Kanban và Table views.
  - `docs/Tasks/README.md`, `docs/Tasks/Task Template.md` và các task `GC-T001` đến `GC-T008`.
- **Trạng thái task ban đầu:**
  - `GC-T001` — xác minh Dashboard/Bases trong Obsidian: `Done` (Project Owner đã xác nhận Dashboard và Task Board hiển thị chính xác; Roadmap chưa được xác minh riêng biệt).
  - `GC-T002` — chạy Phase 1.6 audit: `Todo`; prompt đã chuẩn bị nhưng chưa gửi.
  - `GC-T003` và `GC-T004`: `Blocked` cho đến khi audit và phê duyệt hoàn tất.
  - Các quyết định Guardian login, device bootstrap/device_id, schedule semantics và fall notifications được theo dõi riêng; không tự coi là đã chốt.
- **Kiểm tra/Xác minh:** Project Owner đã xác nhận Dashboard và Task Board hiển thị chính xác trong Obsidian. Roadmap chưa có xác minh riêng biệt.
- **Phạm vi không thực hiện:** Không sửa `AGENTS.md`, không thay đổi hợp đồng Firmware ↔ Web, không tạo mã nguồn ứng dụng, migration hoặc Supabase project; không commit/push.
- **Bước tiếp theo:** Sau khi Project Owner xác nhận Dashboard/Task Board, thực hiện Phase 1.6 audit.

---

### [2026-11-21] — Phase 1.6: Architecture Finalization & Documentation Reconciliation (Kiểm toán kiến trúc & Hiệu đính tài liệu)

- **Mục tiêu:** Rà soát và đánh giá mức độ sẵn sàng kiến trúc trước khi triển khai; hiệu đính toàn bộ các sai lệch thông tin trong báo cáo sơ bộ; phân định rõ giữa số liệu đo thực tế, ước tính tham khảo và nhận định; bổ sung quy tắc bảo mật vào `.gitignore`; đồng bộ hệ thống tài liệu Obsidian.
- **Bản chất công việc:** Khảo sát chỉ đọc (read-only audit), hiệu đính báo cáo và chuẩn hóa tài liệu quản trị; **tuyệt đối không viết mã nguồn ứng dụng, không cài đặt runtime/package, không tạo migration**.
- **Công việc đã hoàn thành:**
  - **Hiệu đính các sai lệch thông tin:**
    1. *Git & Bảo mật:* Đính chính sự thật rằng `.gitignore` trước đó chỉ có `/.obsidian/`. Đã bổ sung đầy đủ quy tắc chặn `.env`, `.env.*` (ngoại trừ `!.env.example`), `*.key`, `*.pem`, `*.sqlite`, `*.db`, `.venv/`, `node_modules/`, `dist/`. Đã kiểm chứng thực tế bằng `git check-ignore`.
    2. *Tài nguyên máy tính:* Phân loại rạch ròi: Đo thực tế (RAM tổng 3287 MB, available 459 MB, swap used 2706 MB; 4 cores; 47 GB disk; Python 3.12.3 & SQLite 3.45.1) đối chiếu với Ước tính tham khảo (FastAPI ~45–70 MB, Vite ~80–120 MB, Browser ~200–300 MB). Bác bỏ kết luận "hoàn toàn an toàn" suy diễn thiếu căn cứ benchmark; khẳng định máy phát triển đang chịu áp lực RAM đáng kể và cần kiến trúc tối giản.
    3. *Chu kỳ phát hành Node.js:* Rà soát lịch phát hành chính thức (nodejs.org): Node.js 26 là Active LTS; Node.js 24 là Maintenance LTS; Node.js 22 là Maintenance LTS (dự kiến EOL 2027-04-30). Không mô tả Node.js 22 là Active LTS. Node.js 20 đã EOL từ tháng 4/2026. Phân định rõ giữa các phiên bản được hỗ trợ và phiên bản đề xuất cho dự án; việc lựa chọn phiên bản runtime tiếp tục chờ Project Owner xem xét. Không tự phê duyệt runtime version, không cài đặt Node.js.
    4. *SQLite vs PostgreSQL:* Làm rõ SQLite WAL không tương đương 100% với PostgreSQL (khác biệt về mảng `integer[]`, UUID native, JSONB, concurrency, locking và migrations). Phân định rõ: SQLite chỉ dùng cho Unit Test độc lập; Supabase Cloud PostgreSQL là môi trường Integration Test và Production duy nhất có thẩm quyền.
    5. *Supabase Connection:* Phân biệt rõ ràng Direct Connection (Port 5432, direct hostname `db.<ref>.supabase.co`, dùng cho Alembic DDL locks) và Session Pooler (Port 5432 qua Supavisor hostname, dùng cho FastAPI persistent backend). Giữ phương án kết nối ở mức `PROPOSED`.
    6. *JWT & API Keys:* Làm rõ JWKS chỉ dùng cho asymmetric signing keys (RS256/ES256); nếu Supabase dùng symmetric HS256 thì phải dùng secret key. Cập nhật thuật ngữ Supabase Publishable Key vs Secret Key.
    7. *Hợp đồng vi điều khiển:* Khẳng định tính bất biến của ACK mảng phẳng, HTTP 400/200, `sms_sent`, `FALL_CANCELLED` lưu độc lập, `unpaired` dừng hoạt động. ĐẶC BIỆT: Ghi nhận ngữ nghĩa phản hồi `config` khi phiên bản không đổi (`config: null`, `{}` hay omit) là `OPEN`, không tự suy diễn.
    8. *Hiệu đính kết luận Readiness:* Xóa bỏ tuyên bố "100% readiness triệt tiêu rủi ro". Thay bằng đánh giá 4 chiều: Documentation Readiness (Đạt), Architecture Proposal Readiness (Đạt), Owner Approval Status (Chờ Owner duyệt), Implementation Readiness (Bị chặn/Chưa được phép).
  - **Tạo và đồng bộ tài liệu:**
    - Tạo tập tin báo cáo hiệu đính chính thức tại: `docs/Architecture/Phase 1.6 - Architecture Readiness Audit.md`.
    - Đồng bộ `docs/Home.md`, `docs/Roadmap.md`, `docs/Decisions/Open Decisions.md`.
    - Cập nhật task: `GC-T001` (Done — Project Owner đã xác nhận Dashboard và Task Board; Roadmap chưa xác minh riêng), `GC-T002` (Done), `GC-T003` (Todo — sẵn sàng cho Owner review), `GC-T004` (Blocked).
- **Tập tin tạo/sửa đổi:**
  - Tạo mới: `docs/Architecture/Phase 1.6 - Architecture Readiness Audit.md`
  - Sửa đổi: `.gitignore`, `docs/Home.md`, `docs/Roadmap.md`, `docs/Decisions/Open Decisions.md`, `docs/Tasks/GC-T001 ...`, `docs/Tasks/GC-T002 ...`, `docs/Tasks/GC-T003 ...`, `project.md`.
- **Bảng trạng thái quyết định kỹ thuật:**
  - `CONFIRMED`: Supabase PostgreSQL, Supabase Auth, GitHub Docs/project.md, Hợp đồng Firmware (ACK mảng phẳng, HTTP 400/200, chu kỳ sync ~15m, thời gian UTC/UTC+7, retention 7/30 ngày, unpaired policy).
  - `PROVISIONAL`: Backend Python 3.12/FastAPI/SQLAlchemy 2.0 Async/Alembic; Frontend React/Vite/TypeScript/Tailwind CSS.
  - `PROPOSED`: Email/Password cho Guardian login; Factory pre-shared secret cho bootstrap; Giới hạn payload 200 bản ghi; Chế độ kết nối DB Session Pooler/Direct; Mô hình 10 entities; Xử lý sự kiện ngã lưu tức thì kèm Incident badge.
  - `OPEN`: Bootstrap token protocol; Định dạng `device_id`; Ngữ nghĩa chi tiết lịch thuốc; Ngữ nghĩa phản hồi config khi không đổi; Chính sách thông báo Web Push.
- **Kiểm tra/Xác minh thực tế đã thực hiện:**
  - `git check-ignore`: Xác nhận `.obsidian/`, `.env`, `.env.local`, `*.key`, `*.sqlite`, `*.db` bị ignore chính xác; `.env.example` KHÔNG bị ignore.
  - `free -m`, `nproc`, `df -h`: Đo lường chính xác tài nguyên hệ thống thực tế.
  - `git status --short`: Kiểm tra working tree, đảm bảo không có file code hay artifact rác nào được tạo.
- **Những nội dung CHƯA ĐƯỢC XÁC MINH:**
  - Chưa đo benchmark thực tế mức RAM tiêu thụ của FastAPI và Vite trên máy phát triển này (mới chỉ dựa trên ước tính tham khảo).
  - Chưa kiểm tra kết nối mạng thực tế tới Supabase (chưa có Supabase project).
  - Roadmap (`docs/Roadmap.md`) chưa được xác minh hiển thị riêng biệt trong Obsidian (Dashboard và Task Board đã được Project Owner xác nhận).
- **Bước tiếp theo:**
  - Project Owner xem xét báo cáo `docs/Architecture/Phase 1.6 - Architecture Readiness Audit.md` (Task `GC-T003`).
  - Project Owner đưa ra quyết định phê duyệt Tech Stack và cho phép tạo Supabase Project (Task `GC-T004`) để mở khóa Phase 2.


---

### [2026-11-23] — Phase 2 (thu gọn): Contract Demo — Vertical Slice chạy cục bộ

- **Mục tiêu:** Xây dựng một lát cắt dọc (vertical slice) tối giản của Web Platform để có sản phẩm trình diễn trước hạn nộp 2026-11-26, **chỉ triển khai các ngữ nghĩa hợp đồng đã CONFIRMED**, không suy diễn các mục còn `OPEN`.
- **Bản chất công việc:** Viết mã ứng dụng demo (lần đầu tiên trong repository). **Không** triển khai kiến trúc sản xuất Option D, **không** tạo Supabase project, **không** viết migration, **không** đụng tới firmware.
- **Căn cứ thẩm quyền:** Project Owner cho phép triển khai song song với tài liệu nộp bài (2026-11-23); Lead Architect chọn phạm vi Contract Demo thu gọn. Ghi nhận chính thức tại `docs/Decisions/Phase 2 Contract Demo Scope.md`.
- **Stack đã khóa cho demo:** Python 3.12 + FastAPI + Uvicorn + `sqlite3` stdlib + HTML/CSS/JS thuần (không build step).
- **Công việc đã hoàn thành:**
  - `backend/contract.py`: Toàn bộ quy tắc hợp đồng chỉ dùng thư viện chuẩn — parse payload, ACK mảng phẳng, validate theo từng bản ghi, dựng `config` đúng bộ khóa đã chốt, handshake `config_version`.
  - `backend/db.py`: Schema SQLite demo (wearers, devices, device_tokens, medication_schedules, health_measurements, medication_records, events, sync_logs), idempotency theo `(device_id, record_id)`, projection cho dashboard, quy tắc hiển thị ngắt kết nối sau ~1 giờ.
  - `backend/app.py`: `GET /health`, `POST /api/device/sync`, `GET /api/dashboard` (chỉ phục vụ UI, **không** thuộc hợp đồng), mount static; tắt `docs_url`/`redoc_url`.
  - `backend/seed.py`: Sinh dữ liệu giả lập tất định (1 wearer, 1 device, 3 lịch thuốc, 1 sự kiện); token demo cố định, **không phải credential**.
  - `backend/static/`: Dashboard responsive duy nhất (trạng thái thiết bị/lần sync, hồ sơ wearer, lịch thuốc, sự kiện gần đây, nhịp tim gần đây) với nhãn **DEMO / SIMULATED DATA** trên mọi khối.
  - `backend/examples/sync-request.json`: Payload mẫu, ghi rõ đây là **envelope tạm thời**.
  - `backend/tests/`: 31 unit test `unittest` (contract + persistence), không cần FastAPI.
  - `README.md`: Hướng dẫn cài đặt/chạy demo, lệnh `curl`, các ca lỗi hợp đồng, ghi chú bảo mật.
  - `.gitignore`: Bổ sung additive `*.db-journal`, `*.db-wal`, `*.db-shm`.
  - `docs/Decisions/Phase 2 Contract Demo Scope.md`: Ghi nhận phạm vi, 6 giả định INTERIM, các sai lệch so với Option D và tiêu chí nghiệm thu.
- **Tập tin tạo/sửa đổi:**
  - Tạo mới: `backend/app.py`, `backend/contract.py`, `backend/db.py`, `backend/seed.py`, `backend/requirements.txt`, `backend/examples/sync-request.json`, `backend/static/index.html`, `backend/static/styles.css`, `backend/static/app.js`, `backend/tests/test_contract.py`, `backend/tests/test_db.py`, `docs/Decisions/Phase 2 Contract Demo Scope.md`.
  - Sửa đổi: `README.md`, `.gitignore`, `project.md`.
- **Quyết định kỹ thuật quan trọng:**
  - Tách `contract.py` khỏi FastAPI để kiểm thử được bằng thư viện chuẩn (do môi trường chưa có dependency).
  - Mọi giả định chưa được chốt được cô lập thành hằng số `INTERIM_*` trong `contract.py` để có thể đổi bằng một dòng khi có quyết định chính thức.
  - Bản ghi bị từ chối vẫn được ACK (chống lặp vô hạn ở firmware), `rejected` là trường tùy chọn.
  - `TAKEN`/`MISSED` do firmware quyết định; Web không ghi đè.
  - `FALL` và `FALL_CANCELLED` lưu thành hai bản ghi độc lập.
  - `sms_sent` chỉ hiển thị là "AT command issued", không phải xác nhận đã gửi SMS.
- **Kiểm tra/Xác minh thực tế đã thực hiện:**
  - `python3 -m compileall -q backend`: **Đạt**.
  - `python3 -m unittest discover -s backend/tests`: **31 test, 0 lỗi** (0.325s).
  - `python3 backend/seed.py --db /tmp/opencode/gc-demo.db --reset`: **Đạt**.
  - Mô phỏng pipeline không qua HTTP (auth → parse → validate → persist → ACK → config → replay): **Đạt** — 4/4 bản ghi được ACK, replay ghi 0 dòng trùng, payload hỏng trả `PayloadError` (ánh xạ HTTP 400).
- **Những nội dung CHƯA ĐƯỢC XÁC MINH (trung thực):**
  - **Chưa chạy được server Uvicorn** và **chưa gọi thử HTTP bằng `curl`**: `python3 -m pip` và `python3 -m ensurepip` không tồn tại, interpreter ở chế độ PEP 668 `EXTERNALLY-MANAGED`, và không được phép dùng `sudo`. Vì vậy FastAPI/Uvicorn chưa được cài.
  - **Không có test ở tầng HTTP** (TestClient) vì lý do trên. Mã trạng thái 400/200/401 mới chỉ được suy ra từ thiết kế và kiểm thử lớp contract, chưa được chứng minh bằng request thật.
  - Chưa kiểm thử giao diện dashboard trên trình duyệt (mới chỉ kiểm tra cú pháp và luồng dữ liệu qua `db.dashboard_snapshot`).
- **Rủi ro tồn đọng:**
  - Hình dạng **request body** của `/api/device/sync` chưa có trong bất kỳ tài liệu nào — đang dùng giả định INTERIM (I-1). Nếu firmware thật khác đi thì phải sửa `parse_payload`/`collect_records`, phần còn lại giữ nguyên.
  - Dashboard không có xác thực — chỉ chấp nhận được vì chạy cục bộ với dữ liệu giả lập.
  - Chưa có bất kỳ bảo đảm bảo mật sản xuất nào (RLS, guardian JWT, phân tách role đều chưa có).
- **Bước tiếp theo:**
  1. Cài FastAPI/Uvicorn (cần quyết định của Owner về cách cài: `apt` với sudo, hoặc `pip install --user --break-system-packages`) rồi chạy lại kiểm thử HTTP end-to-end bằng `curl`.
  2. Chụp ảnh/log dashboard làm minh chứng nộp bài.
  3. Trình bày các mục `OPEN` và giả định INTERIM với đội Firmware để chốt hình dạng request thật.
  4. Hoàn tất `GC-T003`/`GC-T004` trước khi bắt đầu Phase 2 sản xuất.

---

### [2026-11-23] — Phase 2.2: Contract Demo Critical Corrections (Khắc phục sau rà soát độc lập)

- **Mục tiêu:** Áp dụng các chỉnh sửa tối thiểu, đúng phạm vi cho Contract Demo dựa trên kết quả rà soát độc lập Phase 2.1; không mở rộng sang kiến trúc sản xuất.
- **Bản chất công việc:** Sửa lỗi hướng dẫn chạy, tính toàn vẹn dữ liệu, tính rõ ràng của bộ đếm, ghi nhận giả định INTERIM và an toàn khi reset SQLite. **Không** thêm dependency, không cài gói, không chạy server.
- **Công việc đã hoàn thành:**
  - **H-1/H-2 — Hướng dẫn chạy:** Chuẩn hóa toàn bộ lệnh về thư mục gốc repository. Seed: `python3 backend/seed.py --reset`. Server: `python3 -m uvicorn app:app --app-dir backend --host 127.0.0.1 --port 8000`. Dashboard: `http://127.0.0.1:8000/`. Curl chạy ở **terminal thứ hai**, cùng thư mục gốc, dùng `--data @backend/examples/sync-request.json`. Loại bỏ khuyến nghị `--break-system-packages`; ghi trung thực việc thiếu `python3-venv`/wheel của `ensurepip` và chế độ PEP 668.
  - **M-1 — Toàn vẹn CSDL:** `db.insert_record` chuyển sang `INSERT ... ON CONFLICT(device_id, record_id) DO NOTHING` và kiểm tra `cursor.rowcount`; bỏ hoàn toàn việc nuốt mọi `IntegrityError`. Lỗi khóa ngoại/NOT NULL giờ lan truyền thay vì bị ACK như bản ghi trùng.
  - **M-2 — Bộ đếm:** `accepted` chỉ tăng khi thực sự ghi dòng mới; thêm bộ đếm `duplicates`. `sync_logs` có 3 bộ đếm tách bạch: `accepted`, `duplicates`, `rejected` (tổng là `total_records`).
  - **M-3/M-4/M-7/H-3 — Giả định INTERIM:** Thêm các hằng số có tên trong `contract.py`: `INTERIM_UNKNOWN_GROUP_POLICY`, `INTERIM_INVALID_RECORD_STRUCTURE_POLICY`, `INTERIM_MISSING_RECORD_ID_POLICY` (đều `fail_closed_400`), `INTERIM_SCHEDULE_DAYS_CONVENTION` (1=Thứ Hai…7=Chủ Nhật), `INTERIM_SCHEDULE_TIME_FORMAT` (HH:MM UTC+7), `INTERIM_SCHEDULE_END_DATE_NULLABLE`. Ghi thành I-7…I-12 trong decision record, kèm cảnh báo firmware thật có thể nhận HTTP 400 và lặp vô hạn; cấm ghép firmware thật trước khi chốt schema với đội Firmware.
  - **M-5 — Truy vết bản ghi bị từ chối:** Thêm bảng `sync_rejections` chỉ lưu metadata an toàn (device_id, record_id, record_group, reason, received_at); **không** lưu payload thô. API dashboard trả thêm danh sách `rejections`.
  - **M-8 — Reset an toàn:** `seed.py --reset` xóa DB và các sidecar `-wal`, `-shm`, `-journal`; từ chối đường dẫn không kết thúc bằng `.db`; cảnh báo phải dừng server trước khi reset.
  - **Khác:** `openapi_url=None`; dashboard hiển thị ngưỡng offline 1 giờ; mọi mốc thời gian hiển thị theo `Asia/Ho_Chi_Minh` (UTC+7); README hiển thị đúng 3 lịch thuốc trong response mẫu; bỏ import `field` và hàm `fmtClock` không dùng.
  - **Migration additive:** `init_schema` tự thêm cột `duplicates` cho CSDL demo tạo trước Phase 2.2 (đã kiểm chứng, giữ nguyên dữ liệu cũ).
- **Tập tin sửa đổi:** `backend/contract.py`, `backend/db.py`, `backend/app.py`, `backend/seed.py`, `backend/static/app.js`, `backend/static/index.html`, `backend/tests/test_contract.py`, `backend/tests/test_db.py`, `README.md`, `docs/Decisions/Phase 2 Contract Demo Scope.md`, `project.md`.
- **Kiểm tra/Xác minh thực tế đã chạy:**
  - `python3 -m compileall -q backend` → **Đạt**.
  - `python3 -m unittest discover -s backend/tests` → **40 test, 0 lỗi** (0.492s).
  - `seed.py --reset` chạy 2 lần với sidecar `-wal`/`-shm` giả lập → sidecar bị xóa đúng; guard từ chối đường dẫn không phải `.db`.
  - Migration trên bảng `sync_logs` kiểu cũ → thêm cột `duplicates`, dữ liệu cũ nguyên vẹn.
  - Mô phỏng pipeline không HTTP: lần đầu 4 accepted/0 duplicate; replay 0 accepted/4 duplicate; ACK phẳng 4 ID; config 3 lịch; unknown group vẫn fail-closed.
- **CHƯA ĐƯỢC XÁC MINH:** server Uvicorn, request HTTP thật, `curl`, và hiển thị dashboard trên trình duyệt — FastAPI/Uvicorn vẫn chưa có trong môi trường này. Không có test tầng HTTP.
- **Rủi ro tồn đọng:** request envelope vẫn là giả định INTERIM; firmware thật dùng hình dạng khác sẽ nhận 400 và giữ buffer vô hạn. Dashboard không có xác thực (chỉ chấp nhận được vì local). Không có bảo đảm bảo mật sản xuất.
- **Bước tiếp theo:** cài FastAPI/Uvicorn trong virtual environment hợp lệ, chạy `curl` end-to-end và chụp minh chứng; chốt request schema với đội Firmware trước khi tích hợp thiết bị thật.

---

### [2026-11-23] — Phase 2.3: Hoàn thiện Contract Demo — Hiệu chỉnh, kiểm chứng HTTP và nhất quán dữ liệu giả lập

- **Mục tiêu:** Tổng hợp và ghi nhận trung thực chuỗi triển khai/kiểm chứng Phase 2.2 → 2.3.2 của Contract Demo trước hạn nộp 2026-11-26; **không** mở rộng sang kiến trúc sản xuất.
- **Bản chất công việc:** Cập nhật nhật ký tiến độ và tóm tắt hiện trạng. Phiên cập nhật nhật ký này **không** sửa mã nguồn ứng dụng, tài liệu kiến trúc hay hợp đồng Firmware, **không** commit/push.

**Các milestone đã hoàn thành:**
1. **Phase 2.2 — Critical corrections:** Đã hoàn thành (chi tiết tại mục nhật ký Phase 2.2 ngay trước đó): sửa lệnh chạy về thư mục gốc, `ON CONFLICT ... DO NOTHING`, bộ đếm `accepted`/`duplicates`/`rejected` tách bạch, bảng `sync_rejections`, reset an toàn sidecar SQLite, các hằng số `INTERIM_*` và I-7…I-12, `openapi_url=None`, mốc thời gian UTC+7.
2. **Phase 2.3.1 — Guardian phone consistency audit (read-only):** Đã hoàn thành. Kết luận: dashboard và `POST /api/device/sync` **cùng đọc một cột** `wearers.guardian_phone` (`db.py:25`, `db.py:151-154`, `db.py:323`, `db.py:404-408`, `contract.py:305`, `app.js:78`). Không có giá trị `+84900000000` nào trong repository. Nguyên nhân sai lệch từng thấy là **trạng thái runtime cũ** (tab dashboard cũ trước khi reseed, hoặc DB khác), không phải lỗi projection. Điểm yếu góp phần: `INSERT OR IGNORE` khiến seed thường không sửa được dòng đã lệch. Giá trị giả lập chuẩn duy nhất: **`+840000000000`** (`seed.py`, `README.md`, decision record, cả hai file test).
3. **Phase 2.3.2 — Seed UPSERT correction:** Đã hoàn thành. Trong `backend/seed.py`, câu lệnh `INSERT OR IGNORE INTO wearers (...)` được thay bằng `INSERT ... ON CONFLICT(id) DO UPDATE SET name, guardian_phone, notes = excluded.*`; các fixture khác (token, device, 3 lịch, 1 sự kiện, giá trị `+840000000000`) giữ nguyên. Thêm một test tập trung trong `backend/tests/test_db.py`: seed → đổi SĐT giả lập → seed lại **không dùng `--reset`** → kiểm tra giá trị chuẩn được khôi phục và các bảng không bị nhân bản (`wearers=1`, `devices=1`, `device_tokens=1`, `medication_schedules=3`, `events=1`).

**Kiểm tra/Xác minh thực tế:**
- Phiên cập nhật nhật ký này tự chạy lại: `python3 -m compileall -q backend` → **Đạt**; `python3 -m unittest discover -s backend/tests` → **41 test, 0 lỗi** (0.599s).
- Các kết quả HTTP dưới đây do **Project Owner thực hiện và báo cáo** trong phiên chạy demo cục bộ; phiên cập nhật nhật ký này **không gửi lại request HTTP** để tránh ghi thêm dữ liệu vào `backend/demo.db`. Bằng chứng đối chiếu có trong workspace: `.venv/` chứa FastAPI 0.165.0 và Uvicorn 0.54.0; `backend/demo.db` có các dòng `sync_logs` phản ánh đúng luồng sync/replay.
  - FastAPI khởi động bằng Uvicorn thành công trong môi trường cục bộ; `GET /health` → **HTTP 200**.
  - `POST /api/device/sync` → **HTTP 200**, ACK là **mảng phẳng 4 record ID** theo đúng hợp đồng.
  - Replay cùng payload → **HTTP 200**, **không tạo bản ghi nghiệp vụ trùng** (`health_measurements`, `medication_records`, `events`).
  - Token thiết bị sai → **HTTP 401**; JSON hỏng → **HTTP 400**.
  - Sau các request lỗi, số dòng trong các bảng nghiệp vụ, `sync_logs` và `sync_rejections` **không tăng** (không có sync log hay rejection row mới do request lỗi tạo ra).
  - Dashboard hiển thị dữ liệu giả lập đã seed và cập nhật sau sync thành công.
- Theo báo cáo kiểm toán idempotency, tại thời điểm đó có **2 dòng `sync_logs`** — dòng 1 `accepted=4, duplicates=0`, dòng 2 `accepted=0, duplicates=4`. Truy vấn SQLite chỉ đọc (`mode=ro`) trong phiên này xác nhận **hiện tại CSDL có 3 dòng** do một lần replay bổ sung sau đó (dòng 3 cũng `duplicates=4`). `sync_rejections` hiện **0 dòng**. Số dòng nghiệp vụ hiện tại: `wearers=1`, `devices=1`, `device_tokens=1`, `medication_schedules=3`, `health_measurements=1`, `medication_records=1`, `events=3`.
- Dashboard API và config đồng bộ trả **cùng một** SĐT giả lập `+840000000000` (đã đối chiếu trực tiếp trên `backend/demo.db` trong phiên này).
- Chạy seed thường (không `--reset`) khôi phục đúng dòng wearer về fixture chuẩn: được kiểm chứng bằng test mới trên CSDL tạm; **`backend/demo.db` không bị ghi bởi phiên kiểm chứng này**.
- **Bằng chứng hình ảnh:** Project Owner đã chụp ảnh màn hình Dashboard làm minh chứng (trong `~/Pictures` có 2 tệp PNG 1920×1080, chụp 2026-11-23 lúc 23:04–23:05 theo giờ UTC+7). **Không có tệp ảnh nào trong repository**; ảnh không được copy vào repo và không được commit.

**Giới hạn phải luôn nêu rõ:**
- **Chưa thử nghiệm ESP32 hoặc bất kỳ phần cứng thật nào.** Mọi request là mô phỏng cục bộ bằng payload giả lập.
- **Request envelope vẫn là `INTERIM`** (I-1); firmware dùng hình dạng khác sẽ nhận HTTP 400 và có thể retry vô hạn.
- Các mục firmware **`OPEN` vẫn `OPEN`**: bootstrap token, định dạng `device_id`, thông báo `FALL`/`FALL_CANCELLED`, hình dạng `unpaired`, ngữ nghĩa `end_date` và nhiều khung giờ/ngày.
- **Dashboard chưa có xác thực** (chỉ chấp nhận được vì chạy local với dữ liệu giả lập).
- **Chưa tạo Supabase project hay CSDL sản xuất nào.** Contract Demo **không** bảo mật theo chuẩn sản xuất (không RLS, không guardian JWT, không tách role theo Option D).
- **Superpowers, Spec Kit và Browser MCP chưa được tích hợp.**

**Bước tiếp theo:** Chốt request envelope với đội Firmware; Project Owner phê duyệt Tech Stack và đóng các task `GC-T003`/`GC-T004`; chỉ bắt đầu Phase 2 sản xuất sau khi có phê duyệt rõ ràng.

---

### [2026-11-24] — Phase 2.5: Dashboard UI/UX Quality Pass (Tinh chỉnh giao diện trình diễn)

- **Mục tiêu:** Nâng cấp giao diện Contract Demo thành dashboard giám sát sức khỏe/IoT gọn gàng, chuyên nghiệp, phù hợp trình bày dự án khoa học – kỹ thuật; **chỉ frontend**, giữ nguyên toàn bộ hành vi đã hoạt động.
- **Bản chất công việc:** Viết lại ba tệp tĩnh (`index.html`, `styles.css`, `app.js`) theo hướng dẫn thiết kế mới. **Không** sửa backend, CSDL, hợp đồng Firmware, tài liệu kiến trúc hay dependencies; không commit/push.
- **Tập tin sửa đổi:** `backend/static/index.html`, `backend/static/styles.css`, `backend/static/app.js`, `project.md`.
- **Cải thiện UI/UX đã thực hiện:**
  - **Nhận diện:** nền sáng trung tính, cấu trúc navy, hành động xanh dương, điểm nhấn teal; logo đồng hồ vẽ bằng SVG nội tuyến (không icon/font/CDN bên ngoài). Banner DEMO màu hổ phách, gọn nhưng nổi bật.
  - **Bố cục:** header thấp, có tên GoldenClok, nhãn “Contract demo”, thời điểm cập nhật, chu kỳ tự làm mới và nút Refresh. Thẻ trạng thái thiết bị chiếm toàn chiều rộng với trạng thái CONNECTED/DISCONNECTED, lý do thời gian, ngưỡng offline 1 giờ, phiên bản cấu hình và dải cảnh báo nhịp tim.
  - **Thẻ dữ liệu:** wearer (ID, tên, SĐT giả lập, ghi chú), lịch thuốc 6 cột, sự kiện gần đây có badge phân loại (critical/warning/ok), nhịp tim gần đây. Bảng có header rõ, hàng xen kẽ, hover nhẹ, wrapper cuộn ngang.
  - **Trạng thái:** loading ban đầu, empty state cho từng khu vực, lỗi API có banner `role="alert"` + “Update failed”; lần tải đầu thất bại hiển thị “Dashboard unavailable” thay vì treo “Loading…”. Nếu đã có dữ liệu, lỗi làm mới giữ nguyên dữ liệu cũ và nói rõ điều đó.
  - **Footer:** thay câu quá mức “Firmware contract implemented” bằng “Confirmed contract behaviors implemented in this local demo”; tách rõ ba nhóm: hành vi hợp đồng đã xác nhận, giả định INTERIM, và phần chưa triển khai (ESP32/firmware thật, xác thực guardian, CSDL/bảo mật sản xuất).
- **Hành vi được giữ nguyên:** nút Refresh gọi `load()`; tự làm mới mỗi 15 giây; trạng thái kết nối tính ở server theo ngưỡng 1 giờ; timestamp hiển thị `Asia/Ho_Chi_Minh (UTC+7)` qua `Intl.DateTimeFormat`; mọi giá trị động đi qua `esc()` trước khi chèn HTML; empty state cho lịch/sự kiện/nhịp tim; không thêm thư viện hay build step.
- **Cải thiện responsive & accessibility:**
  - Breakpoint 1024/820/640/420 px; grid chuyển 2 cột → 1 cột; stat grid 4 → 2 → 1 cột; bảng cuộn trong `.table-wrap` nên không đẩy tràn trang; đã render thử ở 1440 px và 360 px.
  - Skip link tới `#app`; bảng có `<caption class="sr-only">` và `<th scope="col">`; `aria-live="polite"` cho thời điểm cập nhật; `aria-labelledby` cho từng thẻ; nút Refresh có `aria-label`; `:focus-visible` tương phản; tôn trọng `prefers-reduced-motion`.
- **Kiểm tra/Xác minh thực tế đã chạy:**
  - Kiểm tra tĩnh bằng script: mọi ID do JS tham chiếu đều tồn tại trong HTML; không có `aria-labelledby` gãy; không có class dùng mà thiếu định nghĩa CSS; ngoặc CSS cân bằng; bộ quét dấu phân cách JS (có xử lý template literal/regex) báo cân bằng; không còn chuỗi “Firmware contract implemented”, không còn `toLocaleString()`/`toLocaleTimeString()` thiếu timezone.
  - Smoke test server bằng `.venv` hiện có, trỏ `GOLDENCLOK_DEMO_DB` vào **bản sao tạm** của `backend/demo.db`: `/health` 200; `/`, `/styles.css`, `/app.js` đều 200 đúng content-type; `/api/dashboard` trả 3 lịch, 3 sự kiện, 1 đo nhịp tim, SĐT `+840000000000`, ngưỡng 3600 giây.
  - **Render thật bằng Firefox headless** (Firefox có sẵn trên máy): ảnh 1440×1400 cho trạng thái CONNECTED; ảnh 1440×1400 cho trạng thái DISCONNECTED (dữ liệu gốc đã cũ hơn 1 giờ); ảnh 360×2600 cho mobile; ảnh 1440×1300 cho lỗi API HTTP 503 qua mock server tạm. Ảnh nằm trong `/tmp/opencode/ui-check`, **không** copy vào repository.
  - **Chưa kiểm thử tương tác:** không mô phỏng click Refresh, chờ chu kỳ 15 giây, điều hướng bàn phím, hay cuộn bảng bằng thiết bị cảm ứng thật. Không có Node.js/JS engine để chạy `node --check`; đã dùng kiểm tra tĩnh và render headless thay thế. Không kiểm thử đa trình duyệt.
- **Bảo toàn dữ liệu và phạm vi:**
  - `backend/demo.db` **không bị sửa**: mtime vẫn `2026-11-23 23:53:16`, SHA-256 `f586c8bd59af86671c50e50b79099d4889dea1bf695e96246f008ce60eac4a75`; mọi lần chạy server dùng bản sao trong `/tmp/opencode`.
  - Không thay đổi `backend/app.py`, `db.py`, `contract.py`, `seed.py`, `tests`, schema, `requirements.txt`, tài liệu kiến trúc hay mã firmware.
- **Giới hạn còn lại:** giao diện mới được xác minh bằng render headless, **chưa** có phê duyệt hoặc nghiệm thu thị giác từ Project Owner; chưa kiểm thử tương tác/đa trình duyệt; dashboard vẫn không có xác thực và chỉ dành cho demo cục bộ với dữ liệu giả lập.
- **Bước tiếp theo:** Project Owner xem trực tiếp dashboard trong trình duyệt, xác nhận bố cục và mức độ dễ đọc; sau đó mới coi phần trình diễn giao diện là được nghiệm thu.

---

### [2026-11-24] — Phase 2.6: Vietnamese Localization (Việt hóa bảng điều khiển)

- **Mục tiêu:** Việt hóa toàn bộ giao diện Contract Demo thành tiếng Việt tự nhiên, rõ ràng, phù hợp người dùng Việt Nam, giáo viên và giám khảo khoa học – kỹ thuật; **chỉ thay đổi ngôn ngữ**, giữ nguyên thiết kế, bố cục, hành vi và phong cách Phase 2.5.
- **Tập tin sửa đổi:** `backend/static/index.html`, `backend/static/app.js`, `project.md`. `backend/static/styles.css` **không sửa** vì không cần điều chỉnh bố cục cho văn bản tiếng Việt.
- **Nội dung đã Việt hóa:**
  - Thuộc tính `lang="vi"`, tiêu đề trang, skip link, banner cảnh báo dữ liệu mô phỏng, tên thương hiệu/phụ đề, nhãn “Bản demo”, thông báo tự làm mới và nút “Làm mới”.
  - Tiêu đề thẻ và nhãn phân loại: Vận hành, Hồ sơ, Lịch thuốc, Hoạt động, Sinh hiệu; trạng thái ĐÃ KẾT NỐI / MẤT KẾT NỐI; các nhãn thống kê (Đồng bộ lần cuối, Ngưỡng mất kết nối, Phiên bản cấu hình, Dải cảnh báo nhịp tim).
  - Bảng: Ca, Tên thuốc, Giờ, Ngày, Bắt đầu, Kết thúc; Loại sự kiện, Thời điểm, SMS, Mã bản ghi; Nhịp tim, Thời điểm đo, Mã bản ghi. Caption ẩn cho trình đọc màn hình cũng được Việt hóa.
  - Trạng thái tải, rỗng, chưa nạp dữ liệu, không thể tải bảng điều khiển, cập nhật thất bại; thông báo lỗi API; nhãn thời gian tương đối (phút/giờ/ngày trước).
  - Chân trang: phân định rõ hành vi hợp đồng đã xác nhận, giả định INTERIM (tạm thời, chưa chốt), và các phần chưa triển khai (ESP32/firmware thật, kiểm thử phần cứng thật, xác thực người giám hộ, CSDL/bảo mật sản xuất). Bổ sung giải thích tiếng Việt cho ACK, HTTP 400/200, SHA-256 và `sync request envelope`.
- **Thuật ngữ kỹ thuật giữ nguyên:** API, HTTP, ACK, Bearer, SHA-256, INTERIM, ESP32/firmware, SMS, AT, `sms_sent`, các loại sự kiện FALL / FALL_CANCELLED / SOS / HR_HIGH / HR_LOW / MED_MISSED / LOW_BATTERY, UTC+7, Asia/Ho_Chi_Minh, mã bản ghi, tên trường JSON, DOM ID và định danh JavaScript. Các giá trị dữ liệu động lấy từ CSDL (tên thiết bị/người đeo/thuốc, ghi chú, mã bản ghi) **không bị thay đổi**; chỉ nhãn giao diện được Việt hóa.
- **Hành vi được giữ nguyên:** nút Làm mới gọi cùng luồng `load()`; tự làm mới mỗi 15 giây; thời điểm cập nhật lần cuối; tính trạng thái kết nối theo ngưỡng 1 giờ; trạng thái lỗi API; trạng thái tải/rỗng; định dạng thời gian theo `Asia/Ho_Chi_Minh`; mọi giá trị động đi qua `esc()` trước khi chèn HTML; focus bàn phím và bố cục responsive. Bộ định dạng ngày đổi sang locale `vi-VN` nhưng vẫn giữ timezone `Asia/Ho_Chi_Minh` và `hourCycle: "h23"`.
- **Kiểm tra/Xác minh thực tế đã chạy:**
  - Kiểm tra tĩnh bằng script: cả ba tệp tĩnh hợp lệ UTF-8; mọi ID do JS tham chiếu đều tồn tại trong HTML; không có `aria-labelledby` gãy; không có class dùng mà thiếu định nghĩa CSS; ngoặc CSS cân bằng; bộ quét dấu phân cách JS cân bằng; `lang="vi"`; `REFRESH_MS = 15000`; nút Làm mới và `setInterval(load, REFRESH_MS)` vẫn được nối; `DISPLAY_TZ = "Asia/Ho_Chi_Minh"`; `esc()` vẫn hiện diện và được gọi cho dữ liệu động.
  - **Render thật bằng Firefox headless** với bản sao CSDL tạm trong `/tmp/opencode/l10n-check`: 1920×1400, 1440×1500, 1280×1500, 1024×1800 và 360×2800; trạng thái ĐÃ KẾT NỐI và MẤT KẾT NỐI; trạng thái rỗng (xóa lịch/sự kiện/đo nhịp tim trên bản sao); trạng thái chưa nạp dữ liệu (xóa thiết bị trên bản sao); lỗi API HTTP 503 qua mock server tạm. Ảnh chỉ nằm trong `/tmp/opencode`, **không** copy vào repository.
  - **Chưa kiểm thử tương tác:** chưa mô phỏng click nút Làm mới, chưa chờ chu kỳ 15 giây thực tế, chưa kiểm tra điều hướng bàn phím hoặc cuộn bảng bằng thiết bị cảm ứng; chưa kiểm thử đa trình duyệt. Không có Node.js/JS engine để chạy `node --check`; đã dùng kiểm tra tĩnh và render headless thay thế.
  - **Chưa có phê duyệt thị giác của Project Owner** cho bản Việt hóa; cần Project Owner xem trực tiếp và góp ý từ ngữ.
  - **41 unit test backend vẫn đạt** (`python3 -m unittest discover -s backend/tests`: Ran 41 tests, OK).
- **Bảo toàn dữ liệu và phạm vi:** `backend/demo.db` **không bị sửa** (mtime `2026-11-23 23:53:16`, SHA-256 `f586c8bd59af86671c50e50b79099d4889dea1bf695e96246f008ce60eac4a75`); mọi lần chạy server dùng bản sao trong `/tmp/opencode/l10n-check`. Không thay đổi `backend/app.py`, `db.py`, `contract.py`, `seed.py`, `backend/tests`, `requirements.txt`, schema, tài liệu kiến trúc hay mã firmware. Không commit/push.
- **Giới hạn còn lại:** bản Việt hóa mới được xác minh bằng render headless; một số giá trị dữ liệu mẫu vẫn là tiếng Anh vì thuộc CSDL/dynamic data và không được phép sửa trong phạm vi nhiệm vụ; chưa có xác thực, chưa dùng dữ liệu thật, chưa phải bản sản xuất.
- **Bước tiếp theo:** Project Owner xem trực tiếp dashboard tiếng Việt, xác nhận thuật ngữ và mức độ dễ đọc; nếu cần, điều chỉnh từ ngữ trong một phase riêng.

---

### [2026-11-25] — Phase 2.7.1: Automated HTTP Contract Tests & Verification-Record Reconciliation (Kiểm thử HTTP tự động & Đối soát hồ sơ kiểm chứng)

- **Mục tiêu:** Bổ sung kiểm thử tích hợp HTTP tự động cho Contract Demo bằng Uvicorn hiện có trong `.venv` và thư viện chuẩn `urllib`; đối soát các tài liệu kiểm chứng còn ghi sai trạng thái. **Không** thay đổi hợp đồng Firmware ↔ Web, schema, giao diện, dependency hay kiến trúc sản xuất.
- **Bản chất công việc:** Thêm một tệp test HTTP; cập nhật `README.md`, `docs/Decisions/Phase 2 Contract Demo Scope.md`, `docs/Home.md`, `docs/Roadmap.md` và `project.md`. Không sửa mã backend, seed, static, requirements hay `backend/demo.db`.
- **Căn cứ:** Phase 2.7.0 read-only audit; cơ chế chọn CSDL qua biến môi trường `GOLDENCLOK_DEMO_DB` đã có sẵn trong `backend/app.py` (không cần thêm cơ chế mới).
- **Tập tin tạo/sửa đổi:**
  - Tạo mới: `backend/tests/test_http_contract.py`.
  - Sửa đổi: `README.md`, `docs/Decisions/Phase 2 Contract Demo Scope.md`, `docs/Home.md`, `docs/Roadmap.md`, `project.md`.
  - Không sửa: `backend/app.py`, `backend/contract.py`, `backend/db.py`, `backend/seed.py`, `backend/static/*`, `backend/requirements.txt`, `backend/demo.db`, tài liệu kiến trúc và tài liệu nộp bài.
- **Thiết kế test harness:**
  - Chỉ dùng thư viện chuẩn: `subprocess`, `socket`, `tempfile`, `sqlite3`, `urllib`, `hashlib`, `unittest`.
  - Cấp phát cổng localhost tự do; seed CSDL SQLite tạm; chạy `.venv/bin/python -m uvicorn` chỉ bind `127.0.0.1`; poll `/health` tối đa 15 giây; dọn tiến trình và thư mục tạm qua `addCleanup`, kể cả khi khởi động lỗi.
  - Không dùng FastAPI `TestClient`/`pytest`; không cài gói; không thêm dependency.
  - Mỗi test có CSDL tạm riêng nên không phụ thuộc thứ tự.
  - Ghi SHA-256 `backend/demo.db` trước/sau lớp test và assert không đổi.
- **Các ca HTTP đã kiểm thử:**
  1. `GET /health` → 200, `status=ok`, `demo=true`, `server_time` là số nguyên.
  2. `GET /api/dashboard` → 200, `seeded=true`, đủ trường, 3 lịch thuốc, SĐT chuẩn `+840000000000`.
  3. Sync hợp lệ → 200, ACK phẳng đúng 4 ID theo thứ tự `DEMO-HR-0001`, `DEMO-MED-0001`, `DEMO-EVT-0002`, `DEMO-EVT-0003`; config version 3; 3 lịch.
  4. Replay → 200, cùng ACK, không nhân bản bản ghi; `sync_logs` lần 2 có `duplicates=4`.
  5. Thiếu token → 401; token sai → 401.
  6. JSON hỏng → 400; record group lạ → 400; thiếu `record_id` → 400; entry không phải object → 400.
  7. JSON hợp lệ có 1 bản ghi tốt + 1 bản ghi xấu → 200; ACK chứa cả hai; `rejected` chứa bản ghi xấu; bản ghi xấu không được lưu; `sync_rejections` có 1 dòng.
  8. `config_version=3` → không có `config` (INTERIM `omit`); `config_version=2` → có config; thiếu version → có config.
  9. Dashboard sau mixed sync → đúng số event/rejection; không nhân bản.
  10. SHA-256 `backend/demo.db` trước/sau giống nhau.
- **Kết quả kiểm thử thực tế:**
  - `python3 -m unittest discover -s backend/tests -p 'test_http_contract.py' -v` → **6 test, OK** (5.128s).
  - `python3 -m unittest discover -s backend/tests` → **47 test, OK** (5.897s): 41 test contract/persistence cũ + 6 test HTTP integration.
  - Chạy toàn bộ suite **3 lần liên tiếp** → **47 test, OK** cả 3 lần (5.717s, 5.582s, 5.743s).
  - `python3 -m compileall -q backend` → **Đạt**.
- **Bảo toàn dữ liệu:**
  - `backend/demo.db` không bị sửa; SHA-256 trước/sau đều là `f586c8bd59af86671c50e50b79099d4889dea1bf695e96246f008ce60eac4a75`.
  - Mọi ghi của test HTTP dùng CSDL tạm trong `tempfile`; test còn tự assert hash của `backend/demo.db` không đổi.
- **Đối soát tài liệu:**
  - `README.md`: cập nhật môi trường `.venv` FastAPI 0.165.0/Uvicorn 0.54.0, lệnh chạy server dùng `.venv/bin/python`, tổng 47 test và mô tả test HTTP; bỏ tuyên bố "HTTP chưa được kiểm chứng".
  - `docs/Decisions/Phase 2 Contract Demo Scope.md`: đánh dấu exit criteria HTTP đã thực hiện; cập nhật bảng verification lên 47 test; ghi rõ `curl` không chạy lại trong 2.7.1 nhưng hành vi HTTP đã được xác nhận bằng `urllib`.
  - `docs/Home.md` và `docs/Roadmap.md`: phản ánh Contract Demo đã triển khai (local-only), production Phase 2 vẫn blocked; Phase 2.6 dashboard đã được Owner phê duyệt thị giác.
  - `project.md`: cập nhật tóm tắt hiện trạng và thêm mục này; không sửa lịch sử cũ.
- **Quyết định/Trạng thái:** Không thay đổi `CONFIRMED`/`PROVISIONAL`/`PROPOSED`/`OPEN`; không promote INTERIM. `config` khi version không đổi vẫn là INTERIM `omit`. SĐT fixture chuẩn vẫn là `+840000000000` (12 chữ số), không thay đổi.
- **Ghi chú lịch sử:** Mục Phase 2.6 vẫn giữ nguyên câu "chưa có phê duyệt thị giác" như trạng thái tại thời điểm đó; trạng thái hiện tại (Phase 2.7.1) ghi nhận Project Owner đã phê duyệt thị giác dashboard tiếng Việt.
- **CHƯA ĐƯỢC XÁC MINH / GIỚI HẠN:**
  - Chưa chạy lại `curl` trong phase này; hành vi HTTP được xác nhận bằng `urllib`.
  - Chưa kiểm thử tương tác dashboard (click Refresh, chu kỳ 15 giây, bàn phím, touch) và chưa đa trình duyệt.
  - Chưa có Supabase, RLS, guardian auth, React, migration, retention job, rate limiting hay deploy.
  - Chưa thử ESP32/phần cứng thật; request envelope vẫn `INTERIM`; các mục firmware `OPEN` vẫn `OPEN`.
  - Chưa commit/push.
- **Bước tiếp theo:** Project Owner xem xét và, nếu đồng ý, cho phép commit baseline đã kiểm toán; tiếp tục chốt request envelope và các mục `OPEN` với đội Firmware; chỉ bắt đầu Phase 2 sản xuất sau khi Tech Stack và kiến trúc được phê duyệt.

---

### [2026-11-25] — Phase 2.7.2: Canonical Synthetic Guardian Phone Reconciliation (Đối soát SĐT giả lập chuẩn)

- **Mục tiêu:** Áp dụng quyết định của Project Owner về SĐT giả lập chuẩn duy nhất `+84000000000` trên toàn bộ source code, test, tài liệu đang hoạt động và CSDL demo cục bộ; không thay đổi hợp đồng, API, giao diện hay kiến trúc.
- **Căn cứ:** Quyết định chủ sở hữu dự án ngày 2026-11-25 — chuỗi `+84000000000` là giá trị chuẩn. Các biến thể SĐT bị cấm (một biến thể bắt đầu bằng `+849`, một biến thể bắt đầu bằng `+848`) và mọi biến thể định dạng khác không được sử dụng.
- **Tập tin sửa đổi:**
  - `backend/seed.py` — fixture wearer dùng `+84000000000`.
  - `backend/tests/test_db.py` — hằng `CANONICAL_GUARDIAN_PHONE` và fixture insert.
  - `backend/tests/test_contract.py` — fixture `WEARER`.
  - `backend/tests/test_http_contract.py` — hằng `CANONICAL_GUARDIAN_PHONE` (assertion dashboard).
  - `README.md` — ví dụ response `config.guardian_phone`.
  - `docs/Decisions/Phase 2 Contract Demo Scope.md` — mục "Frozen demo data".
  - `backend/demo.db` — reseed thường (không `--reset`) để hội tụ wearer.
  - `project.md` — tóm tắt hiện trạng + mục này.
- **Phân loại xuất hiện trước khi sửa:**
  - Active source/fixture: `backend/seed.py:88`, `backend/demo.db`.
  - Test expectation: `backend/tests/test_db.py:20,31`, `backend/tests/test_contract.py:179`, `backend/tests/test_http_contract.py:45-46`.
  - Active documentation: `README.md:106`, `docs/Decisions/Phase 2 Contract Demo Scope.md:110`.
  - Historical project record: `project.md:262,263,275,308,360,382` (các mục theo ngày của Phase 2.3.1, 2.3.2, 2.5, 2.7.1).
  - Không tìm thấy biến thể SĐT bị cấm nào ở bất kỳ đâu.
- **An toàn CSDL demo:**
  - Sao lưu trước khi sửa: `/tmp/opencode/demo.db.phase2.7.2.bak`, SHA-256 `f586c8bd59af86671c50e50b79099d4889dea1bf695e96246f008ce60eac4a75`.
  - Đã kiểm tra `seed.py`: wearer dùng `INSERT ... ON CONFLICT(id) DO UPDATE` chỉ trên một dòng `demo-wearer-001`; các bảng khác dùng `INSERT OR IGNORE`; không có lệnh xóa. Vì vậy reseed thường an toàn.
  - Đã chạy `python3 backend/seed.py` (không `--reset`). Không có tiến trình Uvicorn nào đang mở `backend/demo.db` tại thời điểm reseed.
  - Trước: wearer `+840000000000`; counts `wearers=1, devices=1, device_tokens=1, medication_schedules=3, events=3, health_measurements=1, medication_records=1, sync_logs=3, sync_rejections=0`.
  - Sau: wearer `+84000000000`; counts giữ nguyên hoàn toàn.
  - SHA-256 sau reseed: `3cf4a5ecb965a31366743f31071acaa85bee20ff7e7b30f7d2e89427e50bd700`.
- **Kiểm thử thực tế:**
  - `python3 -m unittest discover -s backend/tests -v` → **47 test, OK** (6.288s), gồm 6 test HTTP integration dùng CSDL tạm và assert SĐT chuẩn mới.
- **Kết quả tìm kiếm sau khi sửa:**
  - `+84000000000`: chỉ xuất hiện trong active source/test/docs — `backend/seed.py`, `backend/tests/test_db.py` (2 vị trí), `backend/tests/test_contract.py`, `backend/tests/test_http_contract.py`, `README.md`, `docs/Decisions/Phase 2 Contract Demo Scope.md`; và trong `backend/demo.db`.
  - `+840000000000`: chỉ còn trong các mục lịch sử có ngày của `project.md` (được xác định rõ là lịch sử và đã bị mục này thay thế).
  - Các biến thể SĐT bị cấm: không có.
- **Quyết định/Trạng thái:** SĐT chuẩn hiện hành là `+84000000000`. Không thay đổi `CONFIRMED`/`PROVISIONAL`/`PROPOSED`/`OPEN`; không thay đổi contract semantics, ACK, HTTP status, event types hay hành vi config. Các mục lịch sử trong `project.md` được giữ nguyên theo chính sách append-only.
- **CHƯA ĐƯỢC XÁC MINH / GIỚI HẠN:**
  - Chưa chạy `curl` lại; kiểm chứng qua unittest + HTTP integration tests.
  - Chưa kiểm thử tương tác dashboard hay đa trình duyệt.
  - Chưa có Supabase/RLS/guardian auth/React/migration/deploy.
  - Chưa commit/push.
- **Bước tiếp theo:** Project Owner xem xét baseline sau đối soát; tiếp tục chốt request envelope và các mục `OPEN` với đội Firmware; chỉ bắt đầu Phase 2 sản xuất sau khi kiến trúc được phê duyệt.

---

### [2026-11-25] — Phase 2.7.3: Final Canonical Guardian Phone Verification (Xác nhận cuối cùng SĐT giả lập chuẩn)

- **Mục tiêu:** Bảo đảm SĐT giả lập chuẩn duy nhất là `+84000000000` trên toàn bộ source code, test, tài liệu đang hoạt động và CSDL demo; xử lý chỉ đạo cho rằng Phase 2.7.2 đã ghi nhầm `+84800000000`.
- **Kiểm chứng thực tế trước khi sửa (nguồn: repository, không dựa vào báo cáo cũ):**
  - `+84800000000`: **không xuất hiện ở bất kỳ đâu** — không có trong source, test, tài liệu, `backend/demo.db` (kể cả byte-level), hay lịch sử Git.
  - `+848000000000`: **không xuất hiện ở bất kỳ đâu**.
  - `+84000000000`: đã là giá trị hiện hành tại `backend/seed.py:88`, `backend/tests/test_db.py:20,31`, `backend/tests/test_contract.py:179`, `backend/tests/test_http_contract.py:45`, `README.md:106`, `docs/Decisions/Phase 2 Contract Demo Scope.md:110`, và trong `backend/demo.db`.
  - `backend/demo.db` (đọc read-only trước khi reseed): wearer `demo-wearer-001` = `+84000000000`; counts `wearers=1, devices=1, device_tokens=1, medication_schedules=3, events=3, health_measurements=1, medication_records=1, sync_logs=3, sync_rejections=0`.
- **Kết luận về tiền đề Phase 2.7.3:** Không có giá trị `+84800000000` nào được ghi bởi Phase 2.7.2 trong repository này. Vì vậy **không có giá trị sai nào cần sửa**. Bất kỳ tuyên bố rằng Phase 2.7.2 đã ghi `+84800000000` là **không chính xác** và bị mục này bác bỏ; giá trị chuẩn `+84000000000` được giữ nguyên và xác nhận lại.
- **Tập tin sửa đổi:** Chỉ `project.md` (tóm tắt hiện trạng + mục này) và `backend/demo.db` (reseed thường để xác nhận hội tụ). Không sửa source, test hay tài liệu đang hoạt động vì tất cả đã đúng.
- **An toàn CSDL demo:**
  - Sao lưu trước khi reseed: `/tmp/opencode/demo.db.phase2.7.3.bak`, SHA-256 `3cf4a5ecb965a31366743f31071acaa85bee20ff7e7b30f7d2e89427e50bd700`.
  - `seed.py` dùng `INSERT ... ON CONFLICT(id) DO UPDATE` cho đúng một wearer; các bảng khác `INSERT OR IGNORE`; không có thao tác xóa. Không có tiến trình Uvicorn thực sự đang mở DB.
  - Chạy `python3 backend/seed.py` (không `--reset`). Trước và sau: wearer vẫn `+84000000000`; toàn bộ counts giữ nguyên (`wearers=1, devices=1, device_tokens=1, medication_schedules=3, events=3, health_measurements=1, medication_records=1, sync_logs=3, sync_rejections=0`).
  - SHA-256 sau reseed: `7425c9aa4a94096e86b1427cd8e2257dcb96d46df08292a877339490b31ad349` (thay đổi do ghi lại cùng dữ liệu wearer, không thay đổi dữ liệu nghiệp vụ).
- **Kiểm thử thực tế:** `python3 -m unittest discover -s backend/tests` → **47 test, OK**.
- **Kết quả tìm kiếm sau cùng:**
  - `+84000000000`: chỉ có trong active source/test/docs nêu trên, `project.md` và `backend/demo.db`.
  - `+84800000000`: không có.
  - `+848000000000`: không có.
  - Giá trị 12 chữ số cũ `+840000000000` chỉ còn trong các mục lịch sử có ngày của `project.md` (Phase 2.3.1, 2.3.2, 2.5, 2.7.1) và được xác định rõ là lịch sử đã bị thay thế.
- **Quyết định/Trạng thái:** SĐT giả lập chuẩn hiện hành và duy nhất là `+84000000000`. Không thay đổi `CONFIRMED`/`PROVISIONAL`/`PROPOSED`/`OPEN`, contract semantics, ACK, HTTP status, event types hay hành vi config.
- **CHƯA ĐƯỢC XÁC MINH / GIỚI HẠN:** Chưa chạy `curl` lại; chưa kiểm thử tương tác dashboard/đa trình duyệt; chưa có Supabase/RLS/guardian auth/React/migration/deploy; chưa commit/push.
- **Bước tiếp theo:** Project Owner xem xét baseline; tiếp tục chốt request envelope và các mục `OPEN` với đội Firmware; chỉ bắt đầu Phase 2 sản xuất sau khi kiến trúc được phê duyệt.

---

### [2026-11-25] — Phase 2.8.1: Pre-Baseline Hygiene & Documentation Reconciliation (Vệ sinh trước baseline & đối soát tài liệu)

- **Mục tiêu:** Thực hiện dọn dẹp hẹp trước baseline Git đầu tiên: tăng cường `.gitignore`, đối soát trạng thái kiến trúc, sửa trạng thái Roadmap, làm rõ tính chất `INTERIM` của request envelope, dọn khoảng trắng cuối dòng và xóa thư mục tạm rỗng. **Không** thay đổi hành vi firmware-facing, contract, dashboard, backend runtime hay CSDL demo.
- **Căn cứ:** Phase 2.8.0 read-only audit; quyết định của Project Owner về SĐT chuẩn `+84000000000`; Phase 1.7.2 (Option D là kiến trúc mục tiêu); Phase 2.6 (dashboard đã được phê duyệt thị giác); Phase 2.7.1 (47 test).
- **Tập tin sửa đổi:**
  - `.gitignore` — bổ sung các nhóm bảo vệ mới (không xóa/sửa mục cũ).
  - `README.md` — làm rõ trạng thái Option D, cảnh báo `INTERIM` trước ví dụ sync, và yêu cầu không nối firmware thật.
  - `docs/Home.md`, `docs/Roadmap.md` — đối soát trạng thái kiến trúc và trạng thái Obsidian Knowledge Workspace.
  - `docs/Decisions/Phase 2 Contract Demo Scope.md` — nhấn mạnh §5 là danh sách cảnh báo, không phải hợp đồng tích hợp firmware; bổ sung ghi chú "not production-ready".
  - `docs/Architecture/Phase 1.7.2 - Hybrid Security Architecture Review.md` — chỉ xóa khoảng trắng cuối dòng ở 9 dòng trong khối SQL/comment (không đổi nội dung).
  - `project.md` — tóm tắt hiện trạng + mục này.
  - Xóa thư mục rỗng `ffprof5/` (chỉ `rmdir`, thư mục trống).
- **Không sửa:** `backend/app.py`, `backend/contract.py`, `backend/db.py`, `backend/seed.py`, `backend/static/*`, `backend/requirements.txt`, `backend/tests/*`, `backend/demo.db` và sidecar, quyết định thiết kế/bảo mật, hợp đồng firmware, tài liệu nộp bài.
- **A. Tăng cường `.gitignore`:** thêm bảo vệ OS (`.DS_Store`, `Thumbs.db`, `desktop.ini`, `._*`), editor (`.idea/`, `.vscode/`, `*.swp`, `*.swo`, `*~`, `*.orig`, `*.rej`), thư mục ảnh bằng chứng (`/screenshots/`, `/evidence/`, `/ui-checks/`), backup SQLite (`*.db.bak`, `*.db-backup`, `*.db.backup`, `*.sqlite.bak`, `*.sqlite3.bak`), log/tạm (`*.log`, `*.tmp`, `*.temp`), credential cục bộ (`.envrc`, `.direnv/`, `.netrc`, `secrets.toml`, `credentials.json`, `*.p12`, `*.jks`) và profile render Firefox (`/ffprof*/`). Giữ nguyên ngoại lệ `!.env.example`; **không** thêm mẫu che `*.sql` để không ẩn migration tương lai.
- **B. Đối soát trạng thái kiến trúc:** ghi nhận đúng nghĩa — **Option D Hybrid đã được phê duyệt là kiến trúc sản xuất mục tiêu tại Phase 1.7.2. Việc triển khai sản xuất chưa bắt đầu và vẫn phụ thuộc vào mức độ sẵn sàng bảo mật, các quyết định chưa chốt và một lần phê duyệt triển khai riêng.** Đã sửa tóm tắt hiện trạng `project.md`, phần mở đầu/Phase 2 gate của `docs/Roadmap.md`, và dòng trạng thái `docs/Home.md`. Không sửa nội dung thiết kế hay quyết định bảo mật lịch sử.
- **C. Đồng bộ Roadmap:** `Obsidian Knowledge Workspace` chuyển từ **In progress** sang **Done** (Dashboard và Task Board đã được Project Owner xác nhận qua GC-T001; nội dung Roadmap được đối soát ở phase này; việc render Roadmap trong Obsidian **chưa** được xác nhận riêng). Lịch sử task giữ nguyên; không tuyên bố Web platform sản xuất đã hoàn thành.
- **D. Làm rõ `INTERIM`:** thêm cảnh báo ngay trước ví dụ sync trong `README.md` (envelope là giả định demo, không phải hợp đồng đã chốt; firmware thật sẽ nhận HTTP 400 nếu khác envelope và có thể retry vô hạn; demo không production-ready) và làm rõ trong decision record. Không đổi bất kỳ trường, enum, ACK, mã HTTP hay hằng `INTERIM_*` nào.
- **E. Khoảng trắng cuối dòng:** đối soát lại bằng byte-level cho thấy bảng Phase 2.8.0 bị **dương tính giả**: GNU grep hiểu `[ \t]` trong bracket expression thành dấu cách, `\` và chữ `t`, nên đếm cả các dòng kết thúc bằng "t" hoặc `\`. Thực tế chỉ có `docs/Architecture/Phase 1.7.2 ...` (21 dòng) và `docs/Architecture/Phase 1.6 ...` (7 dòng) có khoảng trắng cuối dòng thật. Trong đó 19 dòng kết thúc bằng đúng **hai dấu cách** — cú pháp Markdown hard line break có chủ đích — nên **được giữ nguyên** để không đổi cách render. Chỉ xóa 9 dòng kết thúc bằng **một** dấu cách trong khối SQL/comment của Phase 1.7.2. Các tệp backend nằm trong danh sách cấm nên không được chỉnh.
- **F. Thư mục tạm:** `ffprof5/` tồn tại và **rỗng**; đã xóa bằng `rmdir ffprof5`. Không xóa đệ quy.
- **Kiểm chứng thực tế đã chạy:**
  - `git check-ignore -v` cho toàn bộ mẫu mới → khớp đúng rule; `.env.example` trả exit 1 (không bị ignore); `backend/migrations/*.sql` giả định không bị ignore; `backend/demo.db`, `-wal`, `-shm`, `__pycache__`, `.venv`, `.obsidian` vẫn bị ignore.
  - `python3 -m unittest discover -s backend/tests` → **Ran 47 tests, OK** (6.322s).
  - `git diff --check` → sạch (chỉ README được track).
  - Quét byte-level khoảng trắng: còn đúng 12 dòng (2 dấu cách) ở Phase 1.7.2 và 7 dòng (2 dấu cách) ở Phase 1.6, tất cả là hard break có chủ đích; các tệp còn lại 0.
  - SĐT chuẩn: `+84000000000` tại `backend/seed.py:88`, `backend/tests/test_db.py:20,31`, `backend/tests/test_contract.py:179`, `backend/tests/test_http_contract.py:45`, `README.md`, `docs/Decisions/Phase 2 Contract Demo Scope.md`, tóm tắt `project.md`; DB `demo-wearer-001` = `+84000000000`; không có `+84800000000`, `+848000000000`, `+84900000000` trong tệp active.
  - `backend/demo.db`: SHA-256 trước và sau **giống hệt** `7425c9aa4a94096e86b1427cd8e2257dcb96d46df08292a877339490b31ad349`; mtime không đổi.
- **Trạng thái quyết định:** Không thay đổi `CONFIRMED`/`PROVISIONAL`/`PROPOSED`/`OPEN`; không promote `INTERIM`; không đổi contract semantics.
- **Git:** **Không stage, không commit, không push, không merge, không đổi branch.** HEAD vẫn `e0d4d066d558ca5a76d21d01e27248ffc551f493` trên `main`.
- **CHƯA ĐƯỢC XÁC MINH / GIỚI HẠN:** chưa render lại Roadmap trong Obsidian; chưa chạy `curl`; chưa kiểm thử tương tác/đa trình duyệt; chưa có Supabase/RLS/guardian auth/React/migration/deploy; chưa commit baseline.
- **Bước tiếp theo:** Project Owner xem xét danh sách stage đề xuất của Phase 2.8.0 và cấp uỷ quyền stage/commit riêng; tiếp tục chốt request envelope và các mục `OPEN` với đội Firmware; chỉ bắt đầu Phase 2 sản xuất sau khi Tech Stack được phê duyệt, các quyết định bảo mật/hợp đồng được chốt và có uỷ quyền triển khai riêng.

---

### [2026-11-27] — Phase 2.8.2/2.8.3: Git Baseline Commit & GitHub Push (Commit baseline Git & push GitHub)

- **Mục tiêu:** Tạo baseline Git cục bộ từ 33 tệp đã được Project Owner kiểm duyệt và publish baseline đó lên GitHub `main`; không thay đổi mã nguồn ứng dụng trong các thao tác Git.
- **Commit baseline (Phase 2.8.2):**
  - **SHA:** `ebc288281a8dfc4b9f644cfe2d63ac04ba0c5843`
  - **Message:** `chore: establish GoldenClok Contract Demo baseline`
  - **Parent:** `e0d4d066d558ca5a76d21d01e27248ffc551f493`
  - **Số tệp:** **33** — đúng danh sách 33 đường dẫn đã được Project Owner kiểm duyệt ở Phase 2.8.2.
  - **Branch:** `main`
- **Push GitHub (Phase 2.8.3):**
  - Push thành công ngày **2026-11-27** bằng lệnh thông thường `git push origin main` (fast-forward, không force).
  - GitHub `main` đã được xác minh độc lập (fetch + `git ls-remote origin refs/heads/main`) là trỏ đúng `ebc288281a8dfc4b9f644cfe2d63ac04ba0c5843`.
  - Lần push đầu tiên **thất bại** vì môi trường không có thông tin đăng nhập HTTPS (`could not read Username for 'https://github.com'`). Sau đó Project Owner đã cài GitHub CLI và xác thực tài khoản; lần push cuối cùng thành công.
  - Không dùng force push, không amend, không rebase, không tạo thêm commit.
- **Phạm vi:** Không thay đổi mã nguồn ứng dụng, test, phụ thuộc, CSDL demo hay hợp đồng firmware trong các thao tác Git này.
- **Bảo mật:** Không ghi lại token, mã xác thực, credential hay bất kỳ bí mật nào.
- **Bước tiếp theo:** Phase 2.8.5 (đánh giá/tích hợp công cụ workflow) → Phase 2.9 (sẵn sàng kiến trúc/bảo mật) → Phase 2 — Project Scaffolding chỉ sau khi các quyết định bắt buộc được chốt và có uỷ quyền triển khai riêng.

---

### [2026-11-27] — Phase 2.8.4: Post-Baseline Documentation Reconciliation (Đối soát tài liệu sau baseline)

- **Mục tiêu:** Đối soát tài liệu dự án sau khi baseline Git đã được commit và push; chỉ sửa tài liệu, không triển khai tính năng sản xuất và không thay đổi Contract Demo.
- **Tập tin sửa đổi:** `project.md` (tóm tắt hiện trạng + mục này), `docs/Home.md`, `docs/Roadmap.md`.
- **Nội dung:** Ghi nhận commit baseline `ebc2882…` (33 tệp, message `chore: establish GoldenClok Contract Demo baseline`) và push GitHub thành công ngày 2026-11-27; GitHub `main` trỏ đúng commit. Cập nhật lộ trình kế tiếp: Phase 2.8.5 (công cụ workflow) → Phase 2.9 (sẵn sàng kiến trúc/bảo mật) → Phase 2 — Project Scaffolding chỉ sau khi chốt quyết định và có uỷ quyền riêng. Bổ sung milestone Git baseline **Done** vào Roadmap và trạng thái baseline đã publish vào Dashboard.
- **Không sửa:** `AGENTS.md`, backend/frontend/test/dependency/database/firmware, decision register; không đổi trạng thái `CONFIRMED`/`PROVISIONAL`/`PROPOSED`/`OPEN`; không thay đổi Option D hay hợp đồng Firmware ↔ Web.
- **Kiểm chứng:** `git diff` chỉ có 3 tệp; `git diff --check` sạch; local HEAD và `origin/main` cùng `ebc288281a8dfc4b9f644cfe2d63ac04ba0c5843`; các mục lịch sử cũ giữ nguyên.
- **Git:** Không stage, không commit, không push, không merge/rebase/reset; thay đổi tài liệu để Project Owner xem xét.
