# GOLDENCLOCK — AGENT WORKING RULES & GOVERNANCE (AGENTS.MD)

Tài liệu quy định nguyên tắc hoạt động thường trực cho AI Agent và nhà phát triển trong workspace WebGoldenClock. Mọi phiên làm việc bắt buộc phải tuân thủ nghiêm ngặt các điều khoản này.

---

## 1. PROJECT IDENTITY & RESPONSIBILITIES (NHẬN DIỆN DỰ ÁN & PHÂN ĐỊNH TRÁCH NHIỆM)

- **Phạm vi dự án:** Nền tảng Web toàn diện (Full-Stack Web Platform) cho GoldenClok bao gồm: Giao diện người giám hộ (Frontend), API và nghiệp vụ máy chủ (Backend), Quản lý CSDL (Database), Xác thực người dùng và Tích hợp thiết bị đeo.
- **Trách nhiệm của nhóm Web:** Phát triển toàn bộ ứng dụng web, REST API, CSDL và phân hệ tích hợp.
- **Ranh giới với đội Firmware:** Đội ngũ khác phụ trách vi điều khiển ESP32-32D, mô-đun A7680C, cảm biến, phát hiện ngã, đo nhịp tim, nhắc thuốc cục bộ và gửi SMS qua SIM.
- **Quy tắc tuyệt đối:** **Không lập trình firmware nhúng**. Tích hợp với thiết bị duy nhất thông qua Hợp đồng giao tiếp Firmware ↔ Web đã được phê duyệt.

---

## 2. CONTEXT BEFORE WORK (NẮM BẮT NGỮ CẢNH TRƯỚC KHI THỰC HIỆN)

Trước khi thực hiện bất kỳ nhiệm vụ có ý nghĩa nào, bắt buộc phải:
1. Đọc kỹ file này (`AGENTS.md`).
2. Đọc kỹ nhật ký tiến độ [project.md](project.md) để nắm rõ trạng thái hiện tại và các việc dang dở.
3. Kiểm tra các tập tin mã nguồn và tài liệu kỹ thuật liên quan trực tiếp.
4. Kiểm tra trạng thái Git (`git status`, `git diff`).
5. Phân định rõ các yêu cầu đã chốt (`CONFIRMED`) và các vấn đề còn mở (`OPEN`).

*Không bao giờ suy diễn hay mặc định chi tiết triển khai trước đó nếu chưa kiểm tra thực tế trong repository.*

---

## 3. TASK SCOPE CONTROL (KIỂM SOÁT PHẠM VI NHIỆM VỤ)

Đối với mỗi nhiệm vụ:
1. Hiểu rõ kết quả mong đợi của người dùng.
2. Xác định tiêu chí nghiệm thu (Acceptance Criteria).
3. Xác định chính xác các tập tin và thành phần cần chỉnh sửa.
4. Chỉ lập kế hoạch những gì thực sự cần thiết.
5. Chỉ thực thi đúng phạm vi được yêu cầu; không thêm tính năng ngoài phạm vi.
6. Không thực hiện tái cấu trúc cơ hội (Opportunistic Refactoring).
7. Không tự ý thay đổi framework, kiến trúc, dependencies hoặc hợp đồng API khi chưa được phép.
8. Dừng lại ngay khi các tiêu chí nghiệm thu đã đạt.

*Nếu một nhiệm vụ phát sinh quy mô lớn hơn đáng kể so với yêu cầu ban đầu, phải dừng lại và giải thích rõ ràng sự thay đổi phạm vi trước khi tiếp tục.*

---

## 4. GOLDENCLOK CONTRACT PROTECTION (BẢO VỆ HỢP ĐỒNG FIRMWARE BẤT BIẾN)

Hợp đồng Firmware ↔ Web là tài liệu có tính pháp lệnh kỹ thuật cao nhất.

**Tuyệt đối không tự ý thay đổi:**
- Tên trường trong JSON (JSON field names).
- Kiểu dữ liệu trong JSON (JSON data types).
- Định dạng ACK (Bắt buộc là mảng phẳng ID: `{"ack": ["ID1", "ID2"]}`) và ngữ nghĩa của ACK.
- Xử lý mã trạng thái HTTP (400 cho JSON hỏng, 200 cho JSON hợp lệ dù có bản ghi rejected).
- Các loại sự kiện (`FALL`, `FALL_CANCELLED`, `HR_HIGH`, `HR_LOW`, `MED_MISSED`, `SOS`, `LOW_BATTERY`).
- Ý nghĩa trạng thái thiết bị (`paired`, `unpaired`).
- Quy ước mốc thời gian (Unix epoch seconds UTC; giờ lịch thuốc UTC+7).
- Chu kỳ đồng bộ (Có WiFi sync ngay, duy trì WiFi sync ~15 phút/lần, sau SMS khẩn cấp sync ngay, trước 1 ngày hết hạn lịch thuốc sync kiểm tra).
- Quyền quyết định trạng thái uống thuốc (`TAKEN` / `MISSED` thuộc về firmware, Web không được ghi đè).

*Không tự chế các endpoint bootstrap hoặc quy trình ghép nối chưa được duyệt. Luôn phân định rõ: `CONFIRMED`, `PROVISIONAL`, `PROPOSED`, `OPEN`.*

---

## 5. CODING DISCIPLINE (KỶ LUẬT LẬP TRÌNH)

- **Mô hình thực thi:** Mặc định sử dụng **Single Agent** và thực thi tuần tự. Multi-Agent chỉ được phép khi có chỉ đạo rõ ràng từ người dùng.
- **Chất lượng mã:** Viết mã ngắn gọn, rõ ràng, dễ bảo trì; tránh trừu tượng hóa và dependencies không cần thiết.
- **Tiết kiệm tài nguyên:** Tôn trọng môi trường máy tính Linux Mint có dung lượng RAM hạn chế (~3.3 GB RAM vật lý, áp lực swap cao).
- **Kiểm thử có mục tiêu:** Ưu tiên các bài test tập trung, kiểm tra đúng ca biên và hợp đồng.
- **Bảo tồn tính năng:** Giữ nguyên các chức năng đang hoạt động tốt; không chỉnh sửa các tệp không liên quan.

---

## 6. PUBLIC REPOSITORY SECURITY (AN TOÀN BẢO MẬT GITHUB CÔNG KHAI)

Repository `WebGoldenClock` là công khai. Bắt buộc tuân thủ:
- Không bao giờ commit bí mật, API key, mật khẩu CSDL hoặc file `.env`.
- Không bao giờ để lộ `SERVICE_ROLE_KEY` hoặc chuỗi kết nối đặc quyền xuống frontend hay git.
- Không bao giờ đưa số điện thoại thật, tên thật hoặc dữ liệu bệnh án thật vào tài liệu/mã nguồn (chỉ dùng dữ liệu giả lập - Synthetic Data).
- Luôn kiểm tra `git diff` trước khi kết thúc phiên làm việc để đảm bảo không rò rỉ bí mật.

---

## 7. MANDATORY PROJECT.MD POLICY (QUY TẮC BẮT BUỘC VỚI PROJECT.MD)

Tập tin [project.md](project.md) là nhật ký tiến độ phát triển chính thức và duy nhất của dự án.

- **Đầu mỗi phiên làm việc có ý nghĩa:** Bắt buộc đọc `project.md` để nắm hiện trạng; không giả định công việc trước đó đã xong nếu chưa kiểm tra.
- **Cuối mỗi phiên làm việc có ý nghĩa:**
  - Bắt buộc cập nhật `project.md` trước khi gửi câu trả lời kết thúc.
  - Không tạo ra các file tiến độ cạnh tranh khác.
  - Nối tiếp mục nhật ký mới theo trình tự thời gian (Append only), không xóa lịch sử cũ.
  - Cập nhật phần tóm tắt hiện trạng ở đầu file.
  - Ghi nhận trung thực: Công việc hoàn thành, tệp sửa đổi, quyết định kỹ thuật, kiểm thử thực tế đã chạy, vấn đề tồn đọng và bước tiếp theo.
  - Không bao giờ bịa đặt kết quả kiểm thử hay tuyên bố việc đã xong khi mới chỉ ở mức đề xuất.
- Đối với các trao đổi giải thích đơn thuần không làm thay đổi trạng thái dự án: Không ghi log rác vào `project.md`.

---

## 8. MANDATORY COMPLETION WORKFLOW (QUY TRÌNH NGHIỆM THU HOÀN THÀNH TASK)

Trước khi báo cáo một nhiệm vụ đã hoàn thành:
1. Rà soát danh sách các tập tin đã thay đổi.
2. Kiểm tra toàn bộ `git diff` để đảm bảo sạch sẽ, đúng phạm vi.
3. Chạy các bài kiểm thử hoặc lệnh xác minh liên quan.
4. Đánh giá kết quả trung thực dựa trên bằng chứng thực thi.
5. Cập nhật [project.md](project.md).
6. Kiểm tra lại `git status`.
7. Báo cáo ngắn gọn cho người dùng: Nội dung đã đổi, kết quả xác minh và rủi ro còn lại (nếu có).
8. Dừng lại, không tự ý nhảy sang làm các việc ngoài phạm vi.
9. **Tuyệt đối không tự động `git commit`, `git push` hoặc `git merge`** trừ khi có yêu cầu trực tiếp từ người dùng.
