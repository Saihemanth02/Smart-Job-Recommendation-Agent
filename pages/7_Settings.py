import streamlit as st
import pandas as pd
import os
from utils.ui import setup_page
from llm.llm_router import llm_call_history
from config.settings import MODEL_CONFIGS

setup_page("Settings & System Status")

st.title("System Settings & Performance Dashboard ⚙️")
st.write("Monitor LLM router performance, fallback history, and API configurations.")

st.markdown("### 🔌 API Authentication Status")
st.write("Ensure credentials are set up inside the local `.env` file in the workspace directory.")

# Read environmental variables
groq_key = os.getenv("GROQ_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")

col_groq, col_gem = st.columns(2)

with col_groq:
    if groq_key:
        st.success("✅ **Groq API Status: CONFIGURED**")
        st.write(f"Active Primary Models:")
        st.write(f"- Small: `{MODEL_CONFIGS['small']['groq']}`")
        st.write(f"- Large: `{MODEL_CONFIGS['large']['groq']}`")
    else:
        st.error("❌ **Groq API Status: MISSING**")
        st.write("Missing `GROQ_API_KEY` in environment. The system will fail back to Gemini immediately.")

with col_gem:
    if gemini_key:
        st.success("✅ **Gemini API Status: CONFIGURED**")
        st.write(f"Active Fallback Models:")
        st.write(f"- Small: `{MODEL_CONFIGS['small']['gemini']}`")
        st.write(f"- Large: `{MODEL_CONFIGS['large']['gemini']}`")
    else:
        st.error("❌ **Gemini API Status: MISSING**")
        st.write("Missing `GEMINI_API_KEY` in environment. Ensure this is set for Groq rate-limit recovery.")

st.markdown("---")

# Visualizing Router Fallbacks
st.markdown("### 🔄 Router Routing History (LLM Trace Logs)")
st.write("This table logs every LLM call made since application launch, demonstrating dynamic failovers and latencies:")

if not llm_call_history:
    st.info("No LLM operations recorded in this session. Initiate a resume analysis or interview query to start tracking.")
else:
    # Convert history log into pandas DataFrame
    df_calls = pd.DataFrame(llm_call_history)
    
    # Format and clean columns
    df_calls['timestamp'] = df_calls['timestamp'].str[11:19]
    df_calls['latency'] = df_calls['latency_ms'].apply(lambda x: f"{x:,} ms" if x is not None else "N/A")
    df_calls['json_mode'] = df_calls['json_mode'].apply(lambda x: "Yes" if x else "No")
    
    display_cols = {
        "timestamp": "Time",
        "task_size": "Task Size",
        "primary_model": "Target Model",
        "actual_backend": "Served Backend",
        "actual_model": "Served Model",
        "status": "Result Status",
        "latency": "Response Latency",
        "json_mode": "JSON Mode"
    }
    
    df_display = df_calls[list(display_cols.keys())].rename(columns=display_cols)
    
    # CSS Status formatting
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    # Detailed log selector
    st.markdown("##### Detailed Call Diagnostics")
    selected_log_idx = st.selectbox(
        "Select call index to inspect error metadata (if any):",
        options=range(len(llm_call_history)),
        format_func=lambda x: f"Call {x+1} - {llm_call_history[x]['actual_backend'].upper()} ({llm_call_history[x]['timestamp'][11:19]})"
    )
    
    diag_record = llm_call_history[selected_log_idx]
    if diag_record["status"] == "error" or diag_record["error_message"]:
        st.error(f"Error Message: {diag_record['error_message']}")
    else:
        st.success(f"Call {selected_log_idx+1} processed successfully with zero exceptions.")

st.markdown("---")
st.markdown("### 📘 About the Project")
st.write(
    """
    This prototype displays a multi-agent architectural capability built for scaling AI workflows. 
    By decoupling processing logic from model selection, the orchestrator guarantees execution persistence 
    even when upstream provider channels experience rate limits or sudden downtime.
    """
)
