from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version
from chat import run_model_tool_loop, write_transcript, now_iso

# Load environment
ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
load_lab_env(ROOT)

# Set Streamlit Page Config
st.set_page_config(
    page_title="Research Agent Tool Eval - UI",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 Research Agent Tool Eval Dashboard")

# ---------------------------------------------------------
# Sidebar: Settings & Artifact Versioning
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")
    
    provider_choice = st.selectbox(
        "Model Provider",
        options=["gemini", "openrouter", "openai", "anthropic"],
        index=0,
    )
    
    model_override = st.text_input(
        "Model Override (Optional)",
        value="",
        help="Leave blank to use provider default.",
    )
    
    version_name = st.text_input(
        "Prompt / Tool Version Label",
        value="v0",
        help="Label used in versioning logs.",
    )
    
    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_yaml_path = ARTIFACTS_DIR / "tools.yaml"

    # Compute Artifact Version SHA
    try:
        art_ver = build_artifact_version(version_name, system_prompt_path, tools_yaml_path)
        ver_info = artifact_version_dict(art_ver)
        
        st.subheader("📦 Artifact Version")
        st.code(
            f"Version: {ver_info['artifact_version']}\n"
            f"Prompt SHA: {ver_info['prompt_hash'][:8]}\n"
            f"Tools SHA:  {ver_info['tools_hash'][:8]}",
            language="yaml",
        )
    except Exception as e:
        st.error(f"Error loading artifacts: {e}")

    st.markdown("---")
    
    if st.button("🗑️ Clear Session & Start New Chat"):
        st.session_state["messages"] = []
        st.session_state["chat_history"] = []
        st.session_state["session_id"] = str(uuid.uuid4())[:8]
        st.rerun()

# ---------------------------------------------------------
# Initialize Session State
# ---------------------------------------------------------
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())[:8]

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Load system prompt and tool declarations
if system_prompt_path.exists():
    system_prompt_content = system_prompt_path.read_text(encoding="utf-8")
else:
    system_prompt_content = "You are a helpful research assistant with tools."

try:
    tool_declarations = load_tool_declarations(tools_yaml_path)
    openai_tools = to_openai_tools(tool_declarations)
except Exception as e:
    tool_declarations = []
    openai_tools = []
    st.error(f"Failed to load tools.yaml: {e}")

# Render Chat History
for item in st.session_state["chat_history"]:
    role = item["role"]
    content = item["content"]
    tool_events = item.get("tool_events", [])

    with st.chat_message(role):
        if tool_events:
            with st.expander(f"🛠️ Tool Execution Trace ({len(tool_events)} event(s))", expanded=False):
                for idx, ev in enumerate(tool_events, 1):
                    st.markdown(f"**Event #{idx} - Tool:** `{ev.get('tool')}`")
                    st.json({"args": ev.get("args"), "result": ev.get("result")})
        st.markdown(content)

# ---------------------------------------------------------
# Chat Input & Processing
# ---------------------------------------------------------
user_input = st.chat_input("Nhập câu hỏi hoặc yêu cầu nghiên cứu...")

if user_input:
    # 1. Display User Message
    st.chat_message("user").markdown(user_input)
    
    # Update state messages
    st.session_state["chat_history"].append({"role": "user", "content": user_input})
    
    # Build payload for agent loop
    full_messages = [{"role": "system", "content": system_prompt_content}]
    for msg in st.session_state["chat_history"]:
        full_messages.append({"role": msg["role"], "content": msg["content"]})
        
    # 2. Assistant Response & Tool Loop
    with st.chat_message("assistant"):
        with st.spinner("Agent đang suy nghĩ & thực thi tools..."):
            try:
                provider_inst = make_provider(provider_choice)
                model_arg = model_override.strip() if model_override.strip() else None
                
                loop_result = run_model_tool_loop(
                    provider=provider_inst,
                    messages=full_messages,
                    tools=openai_tools,
                    model=model_arg,
                    max_tool_rounds=5,
                )
                
                status = loop_result.get("status")
                assistant_text = loop_result.get("assistant_text") or ""
                tool_events = loop_result.get("tool_events") or []
                
                # Render Tool Traces if any
                if tool_events:
                    with st.expander(f"🛠️ Tool Execution Trace ({len(tool_events)} event(s))", expanded=True):
                        for idx, ev in enumerate(tool_events, 1):
                            st.markdown(f"**Event #{idx} - Tool:** `{ev.get('tool')}`")
                            st.json({"args": ev.get("args"), "result": ev.get("result")})
                
                # Render Text Result
                if assistant_text:
                    st.markdown(assistant_text)
                
                # Update Session State
                st.session_state["chat_history"].append({
                    "role": "assistant",
                    "content": assistant_text,
                    "tool_events": tool_events,
                })
                
                # Save Transcript JSON
                transcript_data = {
                    "transcript_id": f"ui_{st.session_state['session_id']}",
                    "version": version_name,
                    **ver_info,
                    "provider": provider_choice,
                    "model": model_arg or getattr(provider_inst, "default_model", None),
                    "status": status,
                    "history": st.session_state["chat_history"],
                    "rounds": loop_result.get("rounds", []),
                    "created_at": now_iso(),
                }
                
                transcript_file = TRANSCRIPTS_DIR / f"ui_session_{st.session_state['session_id']}.json"
                write_transcript(transcript_file, transcript_data)
                
            except Exception as exc:
                st.error(f"Lỗi khi thực thi Agent: {exc}")
