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
    page_title="Research Agent Tool Eval - UI Dashboard",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 Research Agent Tool Eval Dashboard")

# ---------------------------------------------------------
# Sidebar: Settings & Version Selection
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
    
    # Version Selector
    version_choice = st.selectbox(
        "Select Version Label",
        options=["v0", "v1", "v2", "v3", "custom"],
        index=0,
        help="Choose version label. Will look for matching prompt/tool files if available.",
    )
    
    if version_choice == "custom":
        version_name = st.text_input("Custom Version Name", value="v_custom")
    else:
        version_name = version_choice

    # Smart fallback for version-specific prompt/tool files
    prompt_filename = f"system_prompt_{version_name}.md" if (ARTIFACTS_DIR / f"system_prompt_{version_name}.md").exists() else "system_prompt.md"
    tools_filename = f"tools_{version_name}.yaml" if (ARTIFACTS_DIR / f"tools_{version_name}.yaml").exists() else "tools.yaml"
    
    system_prompt_path = ARTIFACTS_DIR / prompt_filename
    tools_yaml_path = ARTIFACTS_DIR / tools_filename

    # Compute Artifact Version SHA
    try:
        art_ver = build_artifact_version(version_name, system_prompt_path, tools_yaml_path)
        ver_info = artifact_version_dict(art_ver)
        
        st.subheader("📦 Artifact Version Info")
        st.code(
            f"Version: {ver_info['artifact_version']}\n"
            f"Prompt File: {prompt_filename}\n"
            f"Tools File:  {tools_filename}\n"
            f"Prompt SHA:  {ver_info['prompt_hash'][:8]}\n"
            f"Tools SHA:   {ver_info['tools_hash'][:8]}",
            language="yaml",
        )
    except Exception as e:
        st.error(f"Error loading artifacts: {e}")
        ver_info = {"artifact_version": version_name, "prompt_hash": "", "tools_hash": ""}

    st.markdown("---")
    
    if st.button("🗑️ Clear Session & Start New Chat"):
        st.session_state["messages"] = []
        st.session_state["chat_history"] = []
        st.session_state["session_id"] = str(uuid.uuid4())[:8]
        st.rerun()

# ---------------------------------------------------------
# Helper function: Detailed Tool Event Trace Renderer
# ---------------------------------------------------------
def render_detailed_tool_events(tool_events: list[dict[str, Any]], expanded: bool = False):
    if not tool_events:
        return
    with st.expander(f"🛠️ Detailed Tool Execution Trace ({len(tool_events)} event(s))", expanded=expanded):
        for idx, ev in enumerate(tool_events, 1):
            tool_name = ev.get("tool", "unknown")
            result = ev.get("result", {})
            is_error = isinstance(result, dict) and "error" in result
            
            status_badge = "🔴 ERROR" if is_error else "🟢 SUCCESS"
            st.markdown(f"##### Event #{idx}: `{tool_name}` — {status_badge}")
            
            tab_args, tab_res = st.tabs(["📥 Arguments", "📤 Output / Result"])
            with tab_args:
                st.json(ev.get("args", {}))
            with tab_res:
                if is_error:
                    st.error(f"**Error**: `{result.get('error')}`\n\n**Message**: {result.get('message')}")
                else:
                    st.json(result)
            st.markdown("---")

# ---------------------------------------------------------
# Main UI Tabs: Live Chat vs Transcript Viewer
# ---------------------------------------------------------
tab_chat, tab_transcripts = st.tabs(["💬 Live Chat Agent", "📜 Transcript History Viewer"])

# =========================================================
# TAB 1: LIVE CHAT AGENT
# =========================================================
with tab_chat:
    # Initialize Session State
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
                render_detailed_tool_events(tool_events, expanded=False)
            st.markdown(content)

    # Chat Input & Processing
    user_input = st.chat_input("Nhập câu hỏi hoặc yêu cầu nghiên cứu...")

    if user_input:
        # 1. Display User Message
        st.chat_message("user").markdown(user_input)
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
                    
                    # Render Detailed Tool Traces
                    if tool_events:
                        render_detailed_tool_events(tool_events, expanded=True)
                    
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
                    st.rerun()
                    
                except Exception as exc:
                    st.error(f"Lỗi khi thực thi Agent: {exc}")

# =========================================================
# TAB 2: TRANSCRIPT HISTORY VIEWER
# =========================================================
with tab_transcripts:
    st.subheader("📜 Saved Session Transcripts")
    
    if not TRANSCRIPTS_DIR.exists():
        st.info("Chưa có file transcript nào được lưu.")
    else:
        transcript_files = sorted(list(TRANSCRIPTS_DIR.glob("*.json")), reverse=True)
        if not transcript_files:
            st.info("Chưa có file transcript nào trong thư mục `transcripts/`.")
        else:
            file_options = {f.name: f for f in transcript_files}
            selected_filename = st.selectbox(
                "Chọn file transcript để xem lại bằng chứng (Evidence):",
                options=list(file_options.keys()),
            )
            
            if selected_filename:
                selected_file_path = file_options[selected_filename]
                try:
                    data = json.loads(selected_file_path.read_text(encoding="utf-8"))
                    
                    # Display Metadata Summary Card
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Version", data.get("version", "N/A"))
                    with col2:
                        st.metric("Provider", data.get("provider", "N/A"))
                    with col3:
                        st.metric("Status", data.get("status", "N/A"))
                    with col4:
                        st.metric("Created At", data.get("created_at", "")[:19].replace("T", " "))
                    
                    st.code(
                        f"Transcript ID: {data.get('transcript_id')}\n"
                        f"Artifact Version: {data.get('artifact_version')}\n"
                        f"Model: {data.get('model')}\n"
                        f"File Path: {selected_file_path}",
                        language="text",
                    )
                    
                    st.markdown("### 💬 Session Chat History")
                    history = data.get("history", [])
                    for msg in history:
                        role = msg.get("role", "user")
                        content = msg.get("content", "")
                        events = msg.get("tool_events", [])
                        
                        with st.chat_message(role):
                            if events:
                                render_detailed_tool_events(events, expanded=False)
                            st.markdown(content)
                            
                except Exception as err:
                    st.error(f"Lỗi khi đọc file transcript: {err}")
