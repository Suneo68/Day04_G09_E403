# Phân chia công việc Lab Day04 — Research Agent Tool Eval (6 người)

> **Thời gian:** 14:00 – 18:00 | **Nhóm:** G09 – 6 thành viên
> 
> Mỗi người có **vai trò chính** xuyên suốt, nhưng sẽ **hỗ trợ nhau** tại từng checkpoint.

---

## Vai trò tổng quan

| Ký hiệu | Vai trò | Trách nhiệm chính |
|---|---|---|
| **P1** | **Lead Prompt Engineer** | Sửa `system_prompt.md`, phân tích failure, dẫn dắt v0→v3 |
| **P2** | **Tool Declaration Engineer** | Sửa `tools.yaml`, đồng bộ rename, thiết kế tool declaration |
| **P3** | **Tool Developer** | Viết tool mới (≥1 bắt buộc), `TOOL.md`, đăng ký `__init__.py` |
| **P4** | **Eval Case Writer** | Viết 10 eval case (`eval_group.json`), chạy eval, phân tích run JSON |
| **P5** | **UI Developer** | Tạo `app.py` (Streamlit), deploy tunnel, rehearse demo |
| **P6** | **Report & Evidence Lead** | Viết `REPORT.md`, `version_log.csv`, chuẩn bị demo scenario |

---

## CP0 — Kickoff (14:00 – 14:15) ⏱️ 15 phút

| Người | Việc cần làm |
|---|---|
| **Tất cả** | Đọc [README.md](file:///d:/Vin_Lab/Day04_G09_E403/README.md) và [TOOL-SETUP.md](file:///d:/Vin_Lab/Day04_G09_E403/TOOL-SETUP.md) |
| **Tất cả** | Thống nhất phân vai P1–P6, thống nhất provider (khuyến nghị OpenRouter) |
| **P1** | Đọc kỹ [system_prompt.md](file:///d:/Vin_Lab/Day04_G09_E403/starter_v0/artifacts/system_prompt.md) để hiểu prompt hiện tại |
| **P2** | Đọc kỹ [tools.yaml](file:///d:/Vin_Lab/Day04_G09_E403/starter_v0/artifacts/tools.yaml) để hiểu tool declarations |
| **P3** | Brainstorm ý tưởng tool mới (ví dụ: `summarize`, `translate`, `sentiment`, `compare`...) |
| **P5** | Đọc phần UI trong README, chọn framework (khuyến nghị Streamlit) |

> **✅ Gate:** Mọi người hiểu vai trò, biết deliverable của mình.

---

## CP1 — Setup (14:15 – 14:40) ⏱️ 25 phút

| Người | Việc cần làm |
|---|---|
| **P1 + P2** | Setup `.env` với API keys (OpenRouter, Tavily, Firecrawl, RapidAPI) |
| **P1** | Chạy `python scripts/preflight_provider.py --provider openrouter` → phải PASS |
| **P2** | Chạy smoke test cho từng core tool: `lookup`, `fetch`, `timeline`, `social_search` |
| **P3** | Setup môi trường riêng, bắt đầu tạo folder tool mới: `tools/<new_tool>/TOOL.md` + `tool.py` |
| **P4** | Đọc kỹ [eval_base.json](file:///d:/Vin_Lab/Day04_G09_E403/starter_v0/data/eval_base.json) (20 case), hiểu cấu trúc eval case |
| **P4** | Đọc [eval_group.schema.example.json](file:///d:/Vin_Lab/Day04_G09_E403/starter_v0/samples/eval_group.schema.example.json) để hiểu format cần viết |
| **P5** | `pip install "streamlit>=1.30.0"`, thêm vào `requirements.txt`, tạo khung `app.py` |
| **P6** | Mở [REPORT.md](file:///d:/Vin_Lab/Day04_G09_E403/starter_v0/artifacts/REPORT.md), điền Team info, chuẩn bị template |

> **✅ Gate:** Provider preflight PASS, ít nhất 2 core tool smoke test PASS, `.env` đầy đủ key.

---

## CP2 — Baseline v0 (14:40 – 15:15) ⏱️ 35 phút

| Người | Việc cần làm |
|---|---|
| **P1** | Chạy baseline: `python run_eval.py --provider openrouter --version v0 --suite base --eval-cases data/eval_base.json` |
| **P1** | Đọc run JSON → ghi lại 4 metric: `case_accuracy`, `tool_routing_accuracy`, `argument_accuracy`, `multiturn_accuracy` |
| **P1 + P2** | Mở `results[*].result.failures` → liệt kê case nào fail, vì sao (sai tool? sai arg? thiếu clarify?) |
| **P2** | Từ failure analysis → đặt giả thuyết đầu tiên để sửa ở v1 |
| **P3** | Tiếp tục code tool mới, viết `TOOL.md`, đăng ký trong `tools/__init__.py` |
| **P4** | Bắt đầu viết 5 single-turn eval case vào `data/eval_group.json` |
| **P5** | **Dựng UI local:** tạo `app.py` sử dụng `run_model_tool_loop` từ [chat.py](file:///d:/Vin_Lab/Day04_G09_E403/starter_v0/chat.py), hiển thị: request/response, tool trace (name + args + result/error), version info |
| **P5** | Chạy `streamlit run app.py` → xác nhận mở được `localhost:8501` |
| **P6** | Ghi v0 vào [version_log.csv](file:///d:/Vin_Lab/Day04_G09_E403/starter_v0/artifacts/version_log.csv): version, metric, run file |
| **P6** | Bắt đầu điền Phần B1 (Version evidence) trong REPORT.md |

> **✅ Gate:** v0 run JSON có trong `runs/`, 4 metric đã ghi, UI local mở được, failure list đã có.

---

## CP3 — v1 + Tool mới (15:15 – 15:50) ⏱️ 35 phút

| Người | Việc cần làm |
|---|---|
| **P1** | Sửa `artifacts/system_prompt.md` dựa trên giả thuyết từ CP2 (ví dụ: thêm rule "khi nói 'bài này' mà không có URL → clarify") |
| **P2** | Sửa `artifacts/tools.yaml` nếu giả thuyết liên quan đến tool description/schema |
| **P2** | Thêm declaration cho tool mới của P3 vào `tools.yaml` |
| **P1** | Chạy v1: `python run_eval.py --provider openrouter --version v1 --suite base --eval-cases data/eval_base.json` |
| **P1 + P2** | So sánh metric v0 vs v1, ghi nhận improvement/regression |
| **P3** | **Hoàn thiện tool mới bắt buộc:** code xong, smoke test PASS, đăng ký đủ (`TOOL.md` + `tool.py` + `__init__.py` + `tools.yaml`) |
| **P4** | Viết tiếp 5 multi-turn eval case → hoàn thành 10 case trong `eval_group.json` |
| **P5** | Cải thiện UI: thêm hiển thị transcript, cho phép chọn version, hiển thị tool events chi tiết |
| **P6** | Cập nhật `version_log.csv` với v1 data |
| **P6** | Ghi Phần B2 (Failure analysis) trong REPORT.md |

> **✅ Gate:** v1 chạy xong + metric cải thiện, tool mới smoke test PASS, 10 eval case đã viết.

---

## CP4 — Nghỉ (15:50 – 16:05) ⏱️ 15 phút

| Người | Việc cần làm |
|---|---|
| **Tất cả** | Nghỉ giải lao, review nhanh progress |
| **P1 + P2** | Trong lúc nghỉ, brainstorm giả thuyết cho v2 |

---

## CP5 — Eval + v2 + Demo prep (16:05 – 16:30) ⏱️ 25 phút

> [!IMPORTANT]
> **Deadline cứng 16:30:** Report Phần A phải xong, UI phải demo được, 3 kịch bản demo phải sẵn sàng.

| Người | Việc cần làm |
|---|---|
| **P1** | Sửa prompt/tool theo giả thuyết v2 |
| **P1** | Chạy v2: `python run_eval.py --provider openrouter --version v2 --suite base --eval-cases data/eval_base.json` |
| **P2** | Chạy group eval: `python run_eval.py --provider openrouter --version v2 --suite group --eval-cases data/eval_group.json` |
| **P4** | Review kết quả group eval, fix eval case nếu format sai |
| **P3** | Hỗ trợ P5 tích hợp tool mới vào UI, hoặc viết thêm tool bonus nếu kịp |
| **P5** | **Deploy link tạm:** `cloudflared tunnel --url http://localhost:8501` → lấy URL public |
| **P5** | Test UI từ device khác qua link tunnel |
| **P6** | **Hoàn thành Report Phần A** (trước 16:30): A1 (agent làm gì), A2 (bảng tool), A3 (câu hỏi mẫu), A4 (kịch bản demo) |
| **P6** | Dán URL tunnel vào Report Phần A |
| **P1 + P6** | Chuẩn bị 3 kịch bản demo: (1) request bình thường, (2) thiếu info → clarify → bổ sung, (3) action nhạy cảm → confirm |
| **P5 + P6** | Rehearse demo 1 lần trên UI |

> **✅ Gate:** Report Phần A xong, UI có URL public, 3 demo scenario sẵn sàng, v2 + group eval chạy xong.

---

## CP6 — Demo → Ship (16:30 – 17:40) ⏱️ 70 phút

### 6a. Showdown (16:30 – 17:15)

| Người | Việc cần làm |
|---|---|
| **P5 + P6** | Giới thiệu agent, demo live trên UI |
| **P1 + P2** | Trả lời câu hỏi technical (prompt design, tool routing) |
| **P3** | Trả lời câu hỏi về tool mới |
| **P4** | Sẵn sàng show eval evidence, run JSON nếu được hỏi |
| **Tất cả** | Ghi nhận feedback từ team khác để cải thiện ở v3 |

### 6b. v3 + Report B (17:15 – 17:35)

| Người | Việc cần làm |
|---|---|
| **P1** | Áp dụng feedback từ showdown → sửa prompt/tool cho v3 |
| **P1** | Chạy v3: `python run_eval.py --provider openrouter --version v3 --suite base --eval-cases data/eval_base.json` |
| **P2** | Chạy group eval v3: `python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json` |
| **P3** | Chạy live chat: `python chat.py --provider openrouter --version v3` → 3 turn tối thiểu |
| **P4** | So sánh metric v0→v3, tổng kết improvement |
| **P5** | Đảm bảo UI vẫn chạy ổn, tunnel vẫn sống |
| **P6** | **Hoàn thiện Report Phần B:** B1 (version evidence v0-v3), B2 (failure analysis), B3 (10 eval cases), B4 (live chat evidence), B5 (tool capability), B6 (reflection) |

### 6c. Final Gate (17:35 – 17:40)

| Người | Việc cần làm |
|---|---|
| **Tất cả** | Checklist nộp bài: |
| | ☐ `artifacts/system_prompt.md` |
| | ☐ `artifacts/tools.yaml` |
| | ☐ `artifacts/version_log.csv` (v0, v1, v2, v3) |
| | ☐ `artifacts/REPORT.md` (Phần A + B) |
| | ☐ `data/eval_group.json` (đúng 10 case) |
| | ☐ `runs/*.json` (ít nhất 4 file: v0, v1, v2, v3) |
| | ☐ `transcripts/*.transcript.json` |
| | ☐ Tool mới: `tools/<name>/TOOL.md` + `tool.py` |
| | ☐ `app.py` (UI code) |
| | ☐ **KHÔNG có** `.env`, `.venv/`, `__pycache__/` trong nộp bài |
| **P6** | Kiểm tra lần cuối, git commit & push |

---

## CP7 — Kahoot Recap (17:40 – 18:00)

| Người | Việc cần làm |
|---|---|
| **Tất cả** | Tham gia Kahoot recap |

---

## Tóm tắt deliverable theo người

| Người | Deliverable chính | File chịu trách nhiệm |
|---|---|---|
| **P1** | Prompt engineering, v0–v3 runs | `artifacts/system_prompt.md`, run commands |
| **P2** | Tool declarations, sync rename | `artifacts/tools.yaml` |
| **P3** | Tool mới bắt buộc (≥1) | `tools/<new_tool>/TOOL.md`, `tools/<new_tool>/tool.py`, `tools/__init__.py` |
| **P4** | 10 eval cases + analysis | `data/eval_group.json` |
| **P5** | UI + deploy | `app.py`, `requirements.txt` (streamlit) |
| **P6** | Report + version log | `artifacts/REPORT.md`, `artifacts/version_log.csv` |

> [!WARNING]
> **Lưu ý quan trọng:**
> - v1/v2/v3 phải là **3 vòng cải tiến KHÁC NHAU**, không phải copy-paste giống nhau
> - Mỗi version phải có **giả thuyết rõ ràng** về cái gì cần sửa
> - Eval case `eval_group.json` phải **tự viết**, không copy từ `eval_base.json`
> - UI phải hiển thị: request/response, tool trace, version info
> - **KHÔNG commit `.env` hay API keys**
