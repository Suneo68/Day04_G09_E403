R08_out_of_scope(out_of_scope): Lỗi gọi tool thừa: Đề hỏi tích phân (toán học) mong đợi AI từ chối (expected no tool call), nhưng AI lại gọi lookup (tìm kiếm: "nguyên hàm của x^2").

R10_missing_handle(missing_info):Lỗi tự biên tự diễn: Đề yêu cầu "Tóm tắt 5 tweet" (không nói của ai) mong đợi AI gọi clarify để hỏi. Nhưng AI tự đoán mò là Sam Altman nên gọi timeline(screenname="sama").

R11_missing_url(missing_info): Lỗi thiếu Argument: Đề thiếu link, AI đã gọi đúng tool clarify để hỏi, nhưng lại quên truyền tham số response_type="text" (bị rơi vào giá trị None).

R12_confirm_before_send (wrong_boundary): Lỗi sai Argument: Đề yêu cầu gửi tin nhắn. AI đã biết gọi clarify để hỏi lại, nhưng lại dùng response_type: "text" (hỏi tự luận) thay vì bắt buộc phải là "yes_no" (hỏi xác nhận Có/Không).

R13_parallel_web_and_tweets(wrong_tool): Lỗi sai Tool: Đề yêu cầu tìm "tweet về AI" (chủ đề chung). Đáng lẽ phải dùng social_search, AI lại gọi nhầm thành timeline(screenname="sama").

M06_switch_tool(wrong_tool): Lỗi không hiểu Context: Ở turn trước AI tìm Twitter, turn này user bảo "Bỏ Twitter, chuyển sang tìm web". AI vẫn gọi cả 2 tool là lookup VÀ social_search (thừa tool social_search).