# Day 04 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. Xong trước 16:30 để làm tài liệu phụ trợ khi demo.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. Có thể hoàn thiện sau buổi debate để nộp bài.

## Team

- Team: G09_E403
- Members:
| Trần Văn Thi | 2A202601548 | Nhóm trưởng |
| Vũ Thế Lực | 2A202602008 | Thành Viên |
| Đinh Quốc Việt | 2A202601891 | Thành Viên |
| Ngô Văn Linh | 2A202601929 | Thành Viên |
| Hoàng Tuấn Hưng | 2A202601911 | Thành Viên |
| Nghiêm Quốc Huy | 2A202601923 | Thành Viên |

- Provider/model: openai/gpt-4o-mini

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì.

1. "Research agent: tìm tin thể thao rổi tổng hợp"
2. "Research agent: đọc cho tôi 1 tin tức thể thao hot nhất hôm nay"
3. "Research agent:Giá vàng thị trường hôm nay"

**Link dùng thử (truy cập được trong showdown):**

> Dán public URL nếu người khác cần mở từ máy riêng; localhost cũng được nếu demo trực tiếp trên máy trình chiếu. Streamlit được khuyến nghị, nhưng nhóm có thể dùng bất kỳ framework nào.
>
> URL: https://assistance-westminster-singer-accept.trycloudflare.com

## A2. Tool agent có

> Liệt kê các tool agent đang dùng. Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
| fetch | Dùng để đọc nội dung của một URL cụ thể. | không |
| timeline | Dùng để lấy các bài đăng gần đây của một tài khoản nhất định. | không |
| social_search | Dùng để tìm bài đăng theo chủ đề hoặc từ khóa trên mạng xã hội. | không |
| lookup | Dùng để tìm thông tin trên web theo từ khóa, thường cho các câu hỏi tin tức hoặc tìm tài liệu. | không |
| send | Dùng để gửi một nội dung nào đó đi (ví dụ gửi thông báo qua Telegram). | không |
| summarize | Dùng để tóm tắt nội dung dài thành bullet ngắn gọn. | không |
| policy | Dùng để tra cứu tài liệu nội bộ trong company policy. | không |
| format | Dùng để trình bày kết quả thành định dạng markdown/sections | không |

## A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1. Tìm tin tức thể thao để tổng hợp
2. Đọc cho tôi 1 tin tức thể thao hot nhất hôm nay
3. Giá vàng thị trường hôm nay 

## A4. Kịch bản demo đã rehearse

> Chuẩn bị 3–5 scenario. Mỗi scenario cần cho thấy tool đã làm gì và một thay đổi cụ thể giữa các version.

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback run/transcript |
|---|---|---|---|
| 1. Tìm tin thể thao nóng hôm nay | looKup | Ở v0 agent có thể gọi sai tool hoặc không biết nên đọc URL; ở v1/v2/v3 agent chọn đúng tool và tổng hợp tốt hơn | C:\Users\ADMIN\Documents\AI_20K\Lab\Thang7\29_7\Day04_G09_E403\starter_v0\runs\v0_B_base_gemini_20260729T152225949189.json, starter_v0\runs\v1_B_base_openrouter_20260729T155008861797.json |
| 2. Lấy tweet của một tài khoản cụ thể | clarify | Ở v0 agent có thể tự đoán tài khoản mà không hỏi; ở các version sau, agent biết phải gọi clarify khi thiếu thông tin | starter_v0\runs\v0_B_base_gemini_20260729T152225949189.json, starter_v0\runs\v2_B_base_openrouter_20260729T155504125335.json  |
| 3. Tìm tin tức theo chủ đề | clarify | Hỏi lại để tìm kiếm đúng hơn | starter_v0\runs\v0_B_base_gemini_20260729T152225949189.json, starter_v0\runs\v3_B_base_openrouter_20260729T155914087333.json |
| 4. Đọc một URL đã có sẵn | fetch -> lookup -> summarize  | tóm tắt tin tức cải thiện từ v1| starter_v0\runs\v0_B_base_openrouter_20260729T154521816526.json, starter_v0\runs\v3_B_base_openrouter_20260729T155914087333.json |
| 5. Xác nhận trước khi gửi nội dung | policy | Ở các version sau agent biết phải hỏi xác nhận trước khi gọi send, tránh hành động nhạy cảm | starter_v0\runs\v0_B_base_openrouter_20260729T155308736009.json, starter_v0\runs\v3_B_group_openrouter_20260729T161012984707.json |

---

# PHẦN B — Chi tiết / Bằng chứng

> Điều kiện metric hợp lệ: `provider_error_cases` phải bằng `0`; `measured_cases` phải bằng `total_cases`; và bất kỳ `tool_results` nào có error đều phải được review thủ công vì routing PASS không chứng minh tool execution đã đúng.

## B1. Version evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Prompt/tool change | Hypothesis | Metric name | Before | After | Run File |
|---|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |  |
| v1 |  |  |  |  |  |  |
| v2 |  |  |  |  |  |  |
| v3 |  |  |  |  |  |  |

## B2. Failure analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

## B3. Team eval cases

List the 10 cases added to `data/eval_group.json`:

- 5 single-turn
- 5 multi-turn

This section is for the mandatory team-authored eval set. Optional built-ins do
not belong here.

File template để trống có chủ đích; nhóm phải tự thiết kế đủ 10 case.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

## B4. Live chat evidence

Use `transcripts/*.transcript.json`.

| Scenario/Turn | Version | Tool Calls + Args | Transcript/Run | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Tool capability evidence

Phân loại rõ tool mới bắt buộc, optional built-in và tool đủ điều kiện bonus. Chỉ ghi Telegram/PDF nếu nhóm thực sự dùng; base report không cần chúng.

UI is core deliverable, not bonus. Do not list it here.

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Must-have: tool mới đầu tiên |  |  |  |
| Optional built-in |  |  |  |
| Bonus: tool mới thứ 4 trở đi |  |  |  |

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?
- Which fixes belonged in `tools.yaml`?
- Which failure needed manual review instead of automatic grading?
- What would you improve next?  
