# Day 04 Lab v2 Report — Research Agent

## Team

- Team: G09_Ẻ403
- Members:
- Provider/model:

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research agent thông minh hỗ trợ tự động tìm kiếm tin tức trên web/mạng xã hội, trích xuất bài viết từ URL, tra cứu tài liệu khoa học arXiv và chính sách nội bộ, tóm tắt dữ liệu dài (via `summarize` tool mới), và gửi bản tin có kiểm soát xác nhận an toàn.

**Link dùng thử (truy cập được trong showdown):**

> Streamlit UI chạy local tại `http://localhost:8501`. Để truy cập từ thiết bị khác trong buổi demo, chạy: `cloudflared tunnel --url http://localhost:8501`
>
> URL Public Demo: https://increasingly-costs-highland-below.trycloudflare.com

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
|  |  |  |
|  |  |  |

## A3. Câu hỏi mẫu để thử

1. **Research tin tức web:** "Tin tức công nghệ mới nhất trong tuần này có gì nổi bật?"
2. **Kiểm tra ranh giới Hỏi lại (Clarify - missing info):** "Tóm tắt 5 tweet mới nhất giúp mình" (Agent sẽ hỏi lại: *Tài khoản nào?*)
3. **Kiểm tra ranh giới An toàn (Confirm before action):** "Đăng bản tin này lên Telegram giúp mình" (Agent sẽ hỏi lại xác nhận Có/Không)
4. **Tra cứu bài báo arXiv:** "Tìm 3 bài báo khoa học về LLM agent evaluation trên arXiv"
5. **Ngoài phạm vi (Out of scope):** "Hướng dẫn mình cách nấu phở bò Hà Nội" (Agent từ chối không gọi tool)

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback run/transcript |
|---|---|---|---|
|  |  |  |  |

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric name | Before | After | Run File |
|---|---|---|---|---:|---:|---|
| v0 | Baseline (vẫn dùng prompt gốc có dặn "tự đoán, đừng hỏi lại") | N/A - baseline | case_accuracy | N/A | 0.60 | `runs/v0_B_base_gemini_20260729T152225949189.json` |
| v1 | Sửa `system_prompt.md`: Cấm đoán bừa, bắt buộc clarify khi thiếu handle/URL hoặc cần confirm send; định nghĩa scope rõ ràng. | Prompt nghiêm ngặt về ranh giới clarify và scope sẽ sửa được 6/8 case fail ở v0. | case_accuracy | 0.60 | 0.85 | `runs/v1_B_base_openrouter_20260729T163330.json` |
| v2 | Sửa `tools.yaml`: Thêm declaration cho tool `summarize` mới, bổ sung mô tả và enum rõ ràng cho các argument (`topic`, `timeframe`, `search_type`). | Khai báo tool chi tiết giúp model truyền đúng argument giá trị chính xác. | case_accuracy | 0.85 | 0.90 | `runs/v2_B_base_openrouter_20260729T163500.json` |
| v3 | Tối ưu prompt cho multi-turn context carryover & bổ sung rule xử lý out-of-scope tuyệt đối. | Hướng dẫn rõ cách xử lý lượt chat cuối trong multi-turn giúp đạt độ chính xác tối đa. | case_accuracy | 0.90 | 0.95 | `runs/v3_B_base_openrouter_20260729T163600.json` |

## B2. Failure analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | wrong_arg_value | `lookup(query="AI news")` | Model thêm từ "news" vào query thay vì để trong field topic | Sửa `tools.yaml` & `system_prompt.md` hướng dẫn trích query gọn |
| R08_out_of_scope | out_of_scope | `send(text=...)` | Câu toán nguyên hàm ngoài phạm vi nhưng model vẫn cố gọi tool send | Bổ sung rule từ chối out-of-scope trong `system_prompt.md` |
| R09_no_tool_capability | unnecessary_tool | `send(text=...)` | Câu hỏi meta "Bạn làm được gì" bị model gọi nhầm tool send | Thêm instruction: "Nếu user hỏi khả năng agent, trả lời trực tiếp không gọi tool" |
| R10_missing_handle | missing_info | `timeline(screenname="elonmusk")` | Prompt v0 bảo "make a sensible guess" nên model tự đoán Elon Musk | Sửa prompt bắt buộc gọi `clarify(response_type="text")` khi thiếu handle |
| R11_missing_url | missing_info | `fetch(url="https://...")` | Yêu cầu "tóm tắt bài này" không có URL bị model tự bịa URL | Sửa prompt bắt buộc gọi `clarify(response_type="text")` khi thiếu URL |
| R12_confirm_before_send | wrong_boundary | `policy(...)` / `send(...)` | Yêu cầu đăng Telegram không được hỏi xác nhận trước | Sửa prompt bắt buộc gọi `clarify(response_type="yes_no")` trước action ghi |
| R13_parallel_web_and_tweets | wrong_arg_value | `lookup(query="AI news today")` | Model ghép tin nhắn user thành query string rườm rà | Hướng dẫn trích keyword chuẩn |
| R14_out_of_scope_coding | out_of_scope | `send(text=...)` | Yêu cầu viết code Python ngoài phạm vi bị gọi nhầm tool | Thêm rule từ chối coding/math |

## B3. Team eval cases

Danh sách 10 test cases bắt buộc do nhóm thiết kế trong `data/eval_group.json`:

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_tech_news_week | Single-turn: map "tuần này" và "công nghệ" | `lookup(query="công nghệ", topic="news", timeframe="week")` | PASS |
| G02_papers_arxiv | Single-turn: tra cứu bài báo trên arXiv | `papers(query="LLM agent evaluation", max_results=3)` | PASS |
| G03_missing_clarify_topic | Single-turn: thiếu chủ đề tin tức | `clarify(response_type="text")` | PASS |
| G04_confirm_send_tg | Single-turn: đăng tin Telegram chưa xác nhận | `clarify(response_type="yes_no")` | PASS |
| G05_out_of_scope_cooking | Single-turn: yêu cầu nấu ăn ngoài phạm vi | `no_tool: true` (refuse) | PASS |
| M07_clarify_then_search | Multi-turn: carryover topic AI & timeframe month | `lookup(query="AI", topic="news", timeframe="month")` | PASS |
| M08_paper_text_extraction | Multi-turn: trích text bài báo arXiv 2 trang | `paper_text(arxiv_url="1706.03762", max_pages=2)` | PASS |
| M09_correction_topic_tweets | Multi-turn: sửa chủ đề Python -> Rust & search_type Top | `social_search(query="Rust", search_type="Top")` | PASS |
| M10_summarize_existing_text | Multi-turn: cung cấp URL ở lượt sau | `fetch(url="https://openai.com/index/gpt-4")` | PASS |
| M11_confirm_send_flow | Multi-turn: người dùng đã xác nhận gửi tin | `send(text="Báo cáo ngày 04 đã hoàn thành", confirmed=true)` | PASS |

## B4. Live chat evidence

Log trích từ `transcripts/v3_openrouter_20260729_demo.transcript.json`:

| Scenario/Turn | Version | Tool Calls + Args | Transcript/Run | Outcome |
|---|---|---|---|---|
| Turn 1: "Tìm tin tức AI mới nhất trên web hôm nay" | v3 | `lookup(query="AI", topic="news", timeframe="day")` | `transcripts/v3_openrouter_20260729_demo.transcript.json` | Agent gọi lookup đúng args, trả về kết quả tìm kiếm tin tức AI trong ngày |
| Turn 2: "Tóm tắt 5 tweet mới nhất giúp mình" | v3 | `clarify(question="...", response_type="text")` | `transcripts/v3_openrouter_20260729_demo.transcript.json` | Agent phát hiện thiếu tên tài khoản, chủ động hỏi lại user |
| Turn 3: "Đăng bản tin này lên Telegram giúp mình" | v3 | `clarify(question="...", response_type="yes_no")` | `transcripts/v3_openrouter_20260729_demo.transcript.json` | Agent phát hiện hành động nhạy cảm, dừng lại xin xác nhận Có/Không |

## B5. Tool capability evidence

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| **Must-have: tool mới đầu tiên** | `tools/summarize/` (`TOOL.md`, `tool.py`) | Tool `summarize` chạy extractive summarization cục bộ rà soát câu theo vị trí & từ khóa trọng tâm, trả về array `summary_points`. Smoke test PASS. | Tránh tóm tắt text rỗng hoặc quá ngắn (có fallback xử lý an toàn). |
| **Optional built-in** | `tools/papers/`, `tools/paper_text/` | Tra cứu arXiv bài báo khoa học và trích xuất text PDF. | arXiv có rate limit, khuyến nghị max_pages <= 5. |
| **UI Delivery** | `app.py` | UI Streamlit hiển thị full request/response, trace tool name, args, status, result/error và artifact version. | Đảm bảo không render secrets `.env` lên UI. |

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?
- Which fixes belonged in `tools.yaml`?
- Which failure needed manual review instead of automatic grading?
- What would you improve next?
