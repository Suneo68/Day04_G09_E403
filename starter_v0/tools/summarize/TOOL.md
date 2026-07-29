# Tool: summarize

## Purpose
Tóm tắt một đoạn text dài thành các điểm chính (bullet points) ngắn gọn. Tool này hoạt động hoàn toàn locally, không gọi API bên ngoài.

## When to use
- Khi user yêu cầu tóm tắt nội dung từ kết quả tool khác (fetch, lookup, timeline, social_search, papers).
- Khi có một đoạn text dài cần rút gọn thành các ý chính.

## When NOT to use
- Khi user chưa có nội dung cần tóm tắt (cần gọi tool khác trước).
- Khi user yêu cầu tìm kiếm hoặc đọc URL — dùng lookup/fetch thay thế.

## Arguments
| Arg | Type | Required | Default | Description |
|---|---|---|---|---|
| text | string | yes | — | Đoạn text cần tóm tắt |
| max_points | integer | no | 5 | Số bullet points tối đa |
| language | string | no | "vi" | Ngôn ngữ output (vi/en) |

## Output contract
```json
{
  "summary_points": ["điểm 1", "điểm 2", ...],
  "original_length": 1234,
  "summary_length": 567,
  "language": "vi",
  "error": null
}
```

## Smoke test
```bash
python -c "from pathlib import Path; from env_loader import load_lab_env; load_lab_env(Path.cwd()); from tools import TOOL_FUNCTIONS as T; r=T['summarize'](text='Artificial intelligence is transforming every industry. From healthcare to finance, AI systems are being deployed at scale. Machine learning models can now process vast amounts of data and make predictions with high accuracy. However, ethical concerns remain about bias, privacy, and job displacement.', max_points=3); print({'error':r.get('error'), 'point_count':len(r.get('summary_points',[]))})"
```
