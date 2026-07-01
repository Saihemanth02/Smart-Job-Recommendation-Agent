import streamlit as st
from utils.ui import setup_page
from utils.db import get_messages_for_trace

setup_page("Agent Pipeline Monitor")

st.title("A2A Agent Pipeline Activity Tracker 🔄")
st.write("This monitor logs the structured Agent-to-Agent (A2A) message communications, latencies, and output payloads during a pipeline run.")

# Check Active Session Trace
trace_id = st.session_state.get("active_trace_id")

if not trace_id:
    st.warning("⚠️ No active analysis trace loaded. Please upload a resume first in the **Upload Resume** page.")
else:
    st.write(f"Showing communication traces for Run: `{trace_id}`")
    
    # Retrieve messages from DB
    messages = get_messages_for_trace(trace_id)
    
    if not messages:
        st.info("No logs captured for this trace yet.")
    else:
        # Pipeline Performance Metrics
        # Filter for messages representing the replies from specialist agents to the Orchestrator
        agent_replies = [m for m in messages if m["from_agent"] != "Career Advisor"]
        
        total_latency = sum(m["latency_ms"] for m in agent_replies if m["latency_ms"] is not None)
        success_count = sum(1 for m in agent_replies if m["status"] == "success")
        error_count = sum(1 for m in agent_replies if m["status"] == "error")
        total_agents = len(agent_replies)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Cumulative Latency", f"{total_latency:,} ms")
        with col2:
            st.metric("Successful Transitions", f"{success_count} / {total_agents}")
        with col3:
            st.metric("Failed Operations", error_count)
            
        st.markdown("### Pipeline Execution Status Checklist")
        st.write("This lists the consolidated state of each agent in the multi-agent DAG sequence:")
        
        # Define the sequential steps in the DAG
        dag_steps = [
            {"task": "parse_resume", "agent": "Resume Intelligence Agent", "title": "1. Resume Parsing & Structuring"},
            {"task": "extract_skills", "agent": "Skill Extraction Agent", "title": "2. Skill Extraction & Taxonomy Matching"},
            {"task": "predict_jobs", "agent": "Job Prediction Agent", "title": "3. Job Fit Ensembles (NB & RF Classifier)"},
            {"task": "get_market_intel", "agent": "Market Intelligence Agent", "title": "4. Labor Market Analytics"},
            {"task": "predict_salary", "agent": "Salary Prediction Agent", "title": "5. Salary Estimation (RF Regressor)"},
            {"task": "generate_roadmap", "agent": "Skill Gap & Roadmap Agent", "title": "6. 90-Day Curriculum Design"}
        ]
        
        for idx, step in enumerate(dag_steps, 1):
            # Find all messages related to this task
            task_msgs = [m for m in messages if m["task"] == step["task"]]
            
            if not task_msgs:
                status = "NOT STARTED"
                status_color = "#64748b" # gray
                latency = None
                payload = {}
                result = {}
            else:
                # Find terminal response (returned from agent to Career Advisor)
                response_msg = next((m for m in task_msgs if m["from_agent"] == step["agent"]), None)
                request_msg = next((m for m in task_msgs if m["to_agent"] == step["agent"]), None)
                
                payload = request_msg["payload"] if request_msg else {}
                result = response_msg["result"] if response_msg else {}
                
                if response_msg:
                    status = response_msg["status"].upper() # SUCCESS or ERROR
                    status_color = "#10b981" if status == "SUCCESS" else "#ef4444"
                    latency = response_msg["latency_ms"]
                else:
                    status = "PENDING"
                    status_color = "#f59e0b" # orange
                    latency = None
            
            # Display step card
            st.markdown(
                f"""
                <div class="message-container" style="border-left: 4px solid {status_color};">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight:700; color:#ffffff; font-size:1.05rem;">
                            {step['title']}
                        </span>
                        <span style="background-color:{status_color}; color:white; padding:3px 10px; border-radius:12px; font-size:0.72rem; font-weight:700; letter-spacing: 0.5px;">
                            {status}
                        </span>
                    </div>
                    <div style="font-size:0.85rem; color:#94a3b8; margin-top:4px;">
                        <b>Agent Class:</b> <code>{step['agent']}</code> | 
                        <b>Execution Latency:</b> {f"{latency:,} ms" if latency is not None else "N/A"}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Expandable payload viewer
            if task_msgs:
                with st.expander(f"Inspect Packet Details - {step['task']}"):
                    col_left, col_right = st.columns(2)
                    with col_left:
                        st.markdown("**Request Payload (Input):**")
                        st.json(payload)
                    with col_right:
                        st.markdown("**Response Result (Output):**")
                        st.json(result if result else {"status": "Processing"})
            st.write("")
