# Day 04 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. Xong trước 16:30 để làm tài liệu phụ trợ khi demo.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. Có thể hoàn thiện sau buổi debate để nộp bài.

## Team

- Team: G09
- Members: P1 (Lead Prompt), P2 (Tool Declaration), P3 (Tool Developer), P4 (Eval Case Writer), P5 (UI Developer), P6 (Report Lead)
- Provider/model: Google Gemini (`gemini-2.5-flash` & `gemini-3.5-flash`) / OpenRouter (`openai/gpt-4o-mini`)

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Agent đa năng hỗ trợ tìm kiếm tin tức trực tuyến, theo dõi mạng xã hội Twitter/X, đọc & tóm tắt tài liệu web/khoa học arXiv, tra cứu chính sách nội bộ và tự động hỏi lại người dùng khi thiếu thông tin.

**Link dùng thử (truy cập được trong showdown):**
URL: https://assistance-westminster-singer-accept.trycloudflare.com

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại người dùng khi thiếu URL/username hoặc xin xác nhận trước khi gửi | Không |
| lookup | Tìm kiếm thông tin & tin tức thời sự trên Internet (Web Search) | Không |
| timeline | Lấy các bài đăng (tweets) mới nhất từ một tài khoản Twitter cụ thể | Không |
| social_search | Tìm kiếm bài đăng & xu hướng trên Twitter theo từ khóa/chủ đề | Không |
| fetch | Đọc nội dung chi tiết từ một địa chỉ URL | Không |
| format | Định dạng danh sách thông tin thu thập được thành bản tin/báo cáo | Không |
| policy | Tra cứu thông tin trong tài liệu chính sách nội bộ | Không |
| papers | Tìm kiếm bài báo khoa học trên arXiv | Không |
| paper_text | Trích xuất văn bản từ bài báo khoa học arXiv | Không |
| send | Gửi tin nhắn/báo cáo lên Telegram (cần xác nhận trước) | Không |
| summarize | Tóm tắt đoạn văn bản dài thành các gạch đầu dòng súc tích | Có (Nhóm phát triển) |

## A3. Câu hỏi mẫu để thử

1. "Tin tức AI hôm nay có gì nổi bật?" (Kích hoạt tool `lookup` với `topic="news"` và `timeframe="day"`)
2. "Lấy 5 tweet mới nhất của Elon Musk" (Kích hoạt tool `timeline` với `screenname="elonmusk"`)
3. "Tóm tắt bài viết này giúp mình" (Kích hoạt tool `clarify` để xin link URL)
4. "Tóm tắt bài toán tích phân: nguyên hàm của x^2 là gì?" (Agent từ chối trực tiếp vì Out of scope, không gọi tool thừa)

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback run/transcript |
|---|---|---|---|
| 1. Tra cứu tin tức AI hôm nay | `lookup(query="AI", topic="news", timeframe="day")` | Ở v0 ghép "news" vào query; ở v1-v3 query sạch và chọn đúng topic=news | `v1_B_base_gemini_20260729T165432293344.json` |
| 2. Thiếu URL bài viết | `clarify(question="...", response_type="text")` | Ở v0 tự bịa link; ở v1-v3 dừng lại hỏi URL chuẩn xác | `v1_B_base_gemini_20260729T165432293344.json` |
| 3. Xử lý câu ngoài phạm vi (Toán học) | `no_tool_call` (trả lời/từ chối trực tiếp) | Ở v0 gọi nhầm tool search/send; ở v1-v3 từ chối ngay lập tức | `v1_B_base_gemini_20260729T165432293344.json` |

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric name | Before | After | Run File |
|---|---|---|---|---:|---:|---|
| v0 | baseline | N/A - baseline | case_accuracy | N/A | 0.60 | `v0_B_base_gemini_20260729T152225949189.json` |
| v1 | optimize prompt & tools schema | strict clarify rules for URL/handle and clean search query | case_accuracy | 0.60 | 0.80 | `v1_B_base_gemini_20260729T165432293344.json` |
| v2 | telegram confirmation rule | explicit yes_no clarification before telegram send | case_accuracy | 0.65 | 0.70 | `v2_B_base_openrouter_20260729T155504125335.json` |
| v3 | add summarize tool & multi-turn rules | summarize tool routing and multi-turn context preservation | case_accuracy | 0.70 | 0.75 | `v3_B_base_gemini_20260729T165919200429.json` |

## B2. Failure analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08_out_of_scope | out_of_scope | `lookup(query="nguyên hàm của x^2")` | Gọi nhầm tool tra cứu cho câu hỏi toán học | Bổ sung luật cấm gọi tool cho câu hỏi Toán/Code trong `system_prompt.md` |
| R10_missing_handle | missing_info | `timeline(screenname="sama")` | Tự đoán bừa handle Twitter của Sam Altman | Thêm quy tắc bắt buộc dùng `clarify(response_type="text")` khi thiếu username |
| R11_missing_url | missing_info | `fetch(url="https://ia.samaltman.com/")` | Tự bịa link URL khi user không cung cấp | Bắt buộc dùng `clarify(response_type="text")` hỏi URL |
| R12_confirm_before_send | wrong_boundary | `clarify(response_type="text")` | Dùng sai `response_type="text"` thay vì `yes_no` | Quy định rõ trước khi `send` Telegram phải dùng `response_type="yes_no"` |

## B3. Team eval cases

10 case do nhóm viết trong `data/eval_group.json`:

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_summarize_routing | Routing tóm tắt văn bản có sẵn | `summarize(text=...)` | PASS |
| G02_single_lookup_timeframe | Trích xuất timeframe='month' | `lookup(topic="news", timeframe="month")` | PASS |
| G03_missing_url_read | Đọc bài thiếu URL | `clarify(response_type="text")` | PASS |
| G04_out_of_scope_cooking | Câu hỏi công thức nấu ăn ngoài phạm vi | `no_tool` (refuse) | PASS |
| G05_confirm_before_send_telegram | Xác nhận trước khi gửi tin Telegram | `clarify(response_type="yes_no")` | PASS |
| G06_multiturn_clarify_text_summarize | Multi-turn: Cung cấp text sau khi được hỏi | `summarize(text=...)` | PASS |
| G07_multiturn_carryover_search_tweets | Multi-turn: Giữ ngữ cảnh từ khóa tìm kiếm | `social_search(query=...)` | PASS |
| G08_multiturn_switch_from_search_to_summarize | Multi-turn: Chuyển từ tìm kiếm sang tóm tắt | `summarize(text=...)` | PASS |
| G09_multiturn_correction_limit | Multi-turn: Sửa số lượng limit ở lượt sau | `timeline(limit=10)` | PASS |
| G10_multiturn_confirm_send | Multi-turn: Xác nhận gửi tin nhắn | `send(confirmed=True)` | PASS |

## B4. Live chat evidence

| Scenario/Turn | Version | Tool Calls + Args | Transcript/Run | Outcome |
|---|---|---|---|---|
| Turn 1: Hỏi tin tức AI | v1 | `lookup(query="AI", topic="news", timeframe="day")` | `ui_session_87641e14.json` | Agent tìm kiếm thành công tin thời sự AI |
| Turn 2: Tóm tắt bài viết | v1 | `clarify(question="...", response_type="text")` | `ui_session_87641e14.json` | Agent chủ động hỏi URL của bài viết |

## B5. Tool capability evidence

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Must-have: tool mới đầu tiên (`summarize`) | `tools/summarize/tool.py` | Tóm tắt súc tích đoạn văn bản dài thành các bullet points bằng thuật toán nén câu | Cần đảm bảo độ dài văn bản tối thiểu > 10 ký tự |
| Optional built-in (`lookup`, `timeline`) | `tools/lookup/`, `tools/timeline/` | Tra cứu web và Twitter đúng tham số | Giới hạn số lượng results/limit để tránh token explosion |

## B6. Reflection

- **Sửa trong `system_prompt.md`**: Quy định ranh giới Out-of-scope (bài toán/lập trình), nguyên tắc làm sạch query và phân biệt giữa `timeline` vs `social_search`.
- **Sửa trong `tools.yaml`**: Siết chặt mô tả các tool, bổ sung enum cho `response_type` và biến `response_type` thành tham số bắt buộc trong `clarify`.
- **Lỗi cần review thủ công**: Các case gọi tool song song (multi-tool call) cần kiểm tra thủ công xem dữ liệu từ nguồn 1 có bị trùng lặp với nguồn 2 hay không.
- **Hướng cải thiện tiếp theo**: Tích hợp thêm bộ nhớ tự động (Vector Memory) để lưu giữ thông tin người dùng qua các phiên trò chuyện lâu dài.
