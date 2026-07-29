# 🎯 BÀI THUYẾT TRÌNH DEMO DỰ ÁN — RESEARCH AGENT TOOL EVAL (NHÓM G09)

> **Dự án:** Research Agent Tool Eval & Guardrail Optimization  
> **Nhóm:** G09_E403 (6 thành viên)  
> **Link Live Demo:** [https://increasingly-costs-highland-below.trycloudflare.com](https://increasingly-costs-highland-below.trycloudflare.com)  
> **Local UI:** `http://localhost:8501`

---

## 📽️ SLIDE 1: GIỚI THIỆU NHÓM & TỔNG QUAN DỰ ÁN

### 📺 Nội dung Slide:
- **Tên dự án:** Research Agent Tool Evaluation & Guardrail Optimization
- **Nhóm thực hiện:** G09 – Lớp E403
- **Thành viên:** P1 (Prompt Lead), P2 (Tool Declaration Lead), P3 (Tool Developer), P4 (Eval Lead), P5 (UI Lead), P6 (Report Lead)
- **Kiến trúc chính:** Multi-tool Research Loop + Guardrails Clarification + Custom Local Tools

### 🎙️ Lời nói của người thuyết trình (Speaker Script):
> *"Kính chào thầy và toàn thể các nhóm! Hôm nay nhóm G09 xin đại diện trình bày dự án **Research Agent Tool Evaluation**.
> 
> Trong thực tế, một chatbot thông thường rất dễ mắc phải các lỗi như: đoán bừa tài khoản/URL khi thiếu thông tin, tự ý thực hiện hành động nhạy cảm, hoặc bị lôi kéo trả lời những câu hỏi không thuộc phạm vi.
> 
> Mục tiêu của nhóm G09 không chỉ là tạo ra một agent tìm kiếm thông tin, mà là **xây dựng một vòng lặp nghiên cứu dựa trên bằng chứng (Evidence-driven loop)** với các ranh giới **hỏi lại (Clarify)** và **an toàn (Confirm)** chuẩn xác."*

---

## 📽️ SLIDE 2: VÒNG LẶP TỐI ƯU EVIDENCE-DRIVEN (v0 ➔ v3)

### 📺 Nội dung Slide:

| Version | Thay đổi chính | Giả thuyết tối ưu | Accuracy |
|---|---|---|---:|
| **v0 (Baseline)** | Prompt gốc (dặn *"đoán bừa, cấm hỏi lại"*) | Baseline benchmark | **60.0%** |
| **v1** | Cấm đoán bừa, bắt buộc `clarify` khi thiếu handle/URL hoặc gửi tin | Thiết lập ranh giới clarify khắc phục 6/8 case fail | **85.0%** |
| **v2** | Đăng ký tool mới `summarize`, bổ sung enum `topic`/`timeframe` | Khai báo schema chuẩn giúp model truyền đúng argument | **90.0%** |
| **v3** | Tối ưu multi-turn carryover & từ chối `out-of-scope` tuyệt đối | Xử lý lượt chat cuối chuẩn xác đạt hiệu năng cao nhất | **95.0%** |

### 🎙️ Lời nói của người thuyết trình (Speaker Script):
> *"Để chứng minh sự cải thiện rõ ràng qua từng phiên bản, nhóm đã thực hiện 4 vòng chạy Benchmark trên bộ 20 base eval cases:
> 
> - **Ở bản v0 Baseline:** Độ chính xác chỉ đạt 60% vì prompt ban đầu bảo agent 'tự đoán bừa'. Kết quả là khi user bảo 'tóm tắt 5 tweet', agent tự bịa tài khoản Elon Musk để gọi.
> - **Đến bản v3 Hiện tại:** Nhóm đã nâng độ chính xác lên **95%**. Agent đã biết dừng lại gọi `clarify` khi thiếu thông tin và tự động từ chối các câu toán/coding không thuộc phạm vi."*

---

## 📽️ SLIDE 3: TOOL MỚI NHÓM TỰ PHÁT TRIỂN — `summarize`

### 📺 Nội dung Slide:
- **Tên tool:** `summarize`
- **Cơ chế:** Extractive Summarization chạy hoàn toàn cục bộ (Local Python), phân tích vị trí câu & từ khóa trọng tâm.
- **Ưu điểm:**
  - ⚡ Phản hồi tức thì, không tốn API Token/Credit.
  - 🎯 Trích xuất đúng $N$ điểm chính (`summary_points`) kèm độ dài nguyên bản.
  - 🛡️ Có bộ lọc fallback tránh rủi ro crash khi gặp văn bản rỗng.

### 🎙️ Lời nói của người thuyết trình (Speaker Script):
> *"Ngoài các tool built-in có sẵn, nhóm G09 đã tự phát triển thêm tool mới mang tên **`summarize`**. 
> 
> Tool này thực hiện rút gọn các bài viết dài từ kết quả tìm kiếm web hoặc tweet thành các ý chính ngắn gọn. Vì được viết hoàn toàn bằng Python local, tool chạy cực nhanh, không tốn chi phí gọi LLM API ngoài và hoàn toàn đáp ứng yêu cầu tool mới của bài lab."*

---

## 📽️ SLIDE 4: LIVE DEMO TƯƠNG TÁC TRÊN UI (4 SCENARIOS)

*(Người hỗ trợ kỹ thuật P5 điều khiển màn hình Streamlit UI tại link Public)*

### 🎬 Scenario 1: Tra cứu tin tức Web chuẩn xác
- **Câu hỏi gõ trên UI:** `"Tin tức công nghệ mới nhất trong tuần này có gì nổi bật?"`
- **Thao tác trên UI:** Mở phần **Tool Trace** bên dưới câu trả lời.
- **Lời thoại:**
  > *"Đầu tiên, câu hỏi tra cứu tin tức web. Mọi người có thể thấy trên Tool Trace, agent chọn đúng tool `lookup` với `topic="news"` và `timeframe="week"`."*

### 🎬 Scenario 2: Ranh giới Hỏi lại khi thiếu thông tin (Clarify Missing Info)
- **Câu hỏi gõ trên UI:** `"Tóm tắt 5 tweet mới nhất giúp mình"`
- **Thao tác trên UI:** Chỉ vào dòng câu hỏi của Agent và trạng thái `waiting_for_user`.
- **Lời thoại:**
  > *"Tiếp theo, một câu thiếu thông tin. Agent không còn đoán bừa như ở v0, mà lập tức dừng lại hỏi người dùng: 'Bạn muốn lấy 5 tweet mới nhất của tài khoản/người nào?'."*

### 🎬 Scenario 3: Ranh giới An toàn trước hành động nhạy cảm (Confirm Action)
- **Câu hỏi gõ trên UI:** `"Đăng bản tin này lên Telegram giúp mình"`
- **Thao tác trên UI:** Highlight loại câu hỏi xác nhận Yes/No.
- **Lời thoại:**
  > *"Đối với các hành động nhạy cảm như đăng bài hay gửi tin nhắn, Agent kích hoạt ranh giới an toàn `clarify(response_type="yes_no")` để yêu cầu xác nhận Có/Không trước khi gọi tool send."*

### 🎬 Scenario 4: Từ chối câu hỏi ngoài phạm vi (Out-of-Scope)
- **Câu hỏi gõ trên UI:** `"Hướng dẫn mình cách nấu phở bò Hà Nội chuẩn vị"`
- **Thao tác trên UI:** Cho thấy Agent trả lời trực tiếp từ chối, phần Tool Trace hoàn toàn rỗng (`no_tool`).
- **Lời thoại:**
  > *"Cuối cùng, với câu hỏi nấu ăn không thuộc phạm vi nghiên cứu, Agent trả lời từ chối thẳng thắn và không gọi bất kỳ tool nào gây lãng phí tài nguyên."*

---

## 📽️ SLIDE 5: BỘ TEAM EVAL 10 CASE & BẰNG CHỨNG THỰC NỘP

### 📺 Nội dung Slide:
- **File Eval Group:** `data/eval_group.json` (5 single-turn + 5 multi-turn do nhóm tự thiết kế).
- **File Báo cáo:** `artifacts/REPORT.md` (Đầy đủ Phần A cho Demo và Phần B cho Bằng chứng).
- **File Log Transcript:** `transcripts/v3_openrouter_20260729_demo.transcript.json`.

### 🎙️ Lời nói của người thuyết trình (Speaker Script):
> *"Tụi mình đã đóng gói toàn bộ bằng chứng nộp bài gồm: bộ 10 case tự thiết kế `eval_group.json`, các file log run JSON từ v0 đến v3, và file báo cáo đầy đủ `REPORT.md`.
> 
> Kính mời thầy và các nhóm cùng mở điện thoại ra và dùng thử trực tiếp agent của nhóm G09 tại địa chỉ public tunnel đang hoạt động!"*

---

## ❓ SLIDE 6: PHẦN CHUẨN BỊ PHẢN BIỆN (Q&A PREPARATION)

### ❓ Câu 1: Tại sao nhóm không để Agent tự đoán handle nổi tiếng như Sam Altman hay Elon Musk?
- **Trả lời:** *"Ở v0 khi cho phép đoán bừa, Agent thường xuyên đoán sai khi gặp các yêu cầu chung chung hoặc tên viết tắt. Việc ép Agent gọi `clarify` giúp đảm bảo độ chính xác 100% về mặt dữ liệu và tránh hậu quả đưa sai thông tin."*

### ❓ Câu 2: Tool `summarize` của nhóm khác gì so với việc bảo LLM tự tóm tắt trong câu trả lời cuối?
- **Trả lời:** *"Tool `summarize` của nhóm là một function tool độc lập được định nghĩa trong `tools.yaml`. Việc tách thành tool riêng giúp agent có thể tóm tắt các đoạn văn bản trung gian dung lượng lớn trước khi đi tiếp vào các bước xử lý sau, đồng thời giúp kiểm soát được output format dưới dạng mảng `summary_points` chuẩn mực."*

### ❓ Câu 3: Làm sao đảm bảo UI không bị lộ API Keys khi public tunnel?
- **Trả lời:** *"Tất cả API keys được nạp an toàn từ file `.env` qua `env_loader.py` ở backend server. Trên giao diện Streamlit UI chỉ hiển thị thông tin phiên bản (`artifact_version`) và tên tool/arguments, tuyệt đối không render bất kỳ chuỗi key hay secret nào."*
