"""Helper script to run 3 sample live turns and generate a valid transcript JSON."""

import sys
from pathlib import Path
import json
from datetime import datetime

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding='utf-8')


from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools, TOOL_FUNCTIONS
from chat import run_model_tool_loop, write_transcript, safe_slug, now_iso
from versioning import build_artifact_version, artifact_version_dict

load_lab_env(ROOT)

system_prompt_path = ROOT / "artifacts" / "system_prompt.md"
tools_path = ROOT / "artifacts" / "tools.yaml"

system_prompt = system_prompt_path.read_text(encoding="utf-8")
tool_declarations = load_tool_declarations(tools_path)
openai_tools = to_openai_tools(tool_declarations)
provider = make_provider("openrouter")
artifact_version = build_artifact_version("v3", system_prompt_path, tools_path)

timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
transcript_id = f"v3_openrouter_{timestamp}"
transcript_path = ROOT / "transcripts" / f"{transcript_id}.transcript.json"

transcript = {
    "transcript_id": transcript_id,
    **artifact_version_dict(artifact_version),
    "provider": "openrouter",
    "model": "openrouter/free",
    "system_prompt": str(system_prompt_path),
    "tools": str(tools_path),
    "history_window": 5,
    "max_tool_rounds": 4,
    "created_at": now_iso(),
    "updated_at": now_iso(),
    "turns": [],
}

test_turns = [
    "Tìm tin tức AI hôm nay nổi bật trên web.",
    "Tóm tắt 5 tweet mới nhất giúp mình nhưng quên không nói của ai.",
    "Đăng bản tin này lên Telegram channel giúp mình nhé."
]

history = []
for i, user_text in enumerate(test_turns, start=1):
    print(f"Running Turn {i}: {user_text}")
    messages = [
        {"role": "system", "content": system_prompt},
        *history,
        {"role": "user", "content": user_text},
    ]
    turn_record = {
        "turn_index": i,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }
    try:
        res = run_model_tool_loop(
            provider=provider,
            messages=messages,
            tools=openai_tools,
            model="openrouter/free",
            max_tool_rounds=4,
        )
        turn_record.update(res)
        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": res["assistant_text"]})
    except Exception as exc:
        turn_record.update({"status": "error", "error": str(exc)})
    
    turn_record["ended_at"] = now_iso()
    transcript["turns"].append(turn_record)

write_transcript(transcript_path, transcript)
print(f"Generated transcript: {transcript_path}")
