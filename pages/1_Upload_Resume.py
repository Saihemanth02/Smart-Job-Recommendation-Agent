import streamlit as st
import time
from utils.ui import setup_page
from utils.pdf_parser import extract_text_from_file
from agents.orchestrator import Orchestrator
from utils.db import get_all_sessions, get_session_context

setup_page("Upload Resume")

st.title("Resume Upload & Analysis Portal 📤")
st.write("Upload a candidate profile to initiate the multi-agent career assessment, or compare multiple profiles side-by-side.")

# Setup Orchestrator
orchestrator = Orchestrator()

# Settings Sidebar Input
location_tier = st.sidebar.selectbox(
    "Select Target Job Location Tier",
    options=[1, 2, 3],
    format_func=lambda x: {
        1: "Tier 1 Metro (Bangalore, Hyd, Pune, Mumbai)",
        2: "Tier 2 Hub (Vizag, Kochi, Coimbatore, Jaipur)",
        3: "Tier 3 City (Vijayawada, Kakinada, Warangal)"
    }.get(x),
    index=0
)
st.session_state.location_tier = location_tier

# Option: Single Upload vs Batch Comparison
mode = st.radio("Analysis Mode", ["Single Candidate Assessment", "Multi-Resume Batch Comparison"], horizontal=True)

if mode == "Single Candidate Assessment":
    uploaded_file = st.file_uploader("Upload Resume (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])
    
    if uploaded_file is not None:
        file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
        st.write(f"📁 Loaded: `{uploaded_file.name}` ({uploaded_file.size / 1024:.1f} KB)")
        
        if st.button("Execute AI Analysis"):
            try:
                # 1. Parse raw text
                with st.spinner("Extracting text from document..."):
                    file_bytes = uploaded_file.read()
                    raw_text = extract_text_from_file(file_bytes, uploaded_file.name)
                
                if not raw_text.strip():
                    st.error("The uploaded file did not contain any extractable text.")
                else:
                    # 2. Run orchestrator step-by-step with custom spinners naming agents
                    progress_text = st.empty()
                    
                    with st.spinner("Resume Intelligence Agent is structuring the candidate profile..."):
                        # We trigger the run pipeline method, which handles the agent flow internally.
                        # Since we want to update the UI, we can let it run. But wait, how do we show individual spinners?
                        # We can mock the stages or run them step-by-step in app page, but let's let Orchestrator run
                        # and write progress logs. We can show simulated steps that map to actual agent calls:
                        progress_text.info("🤖 Resume Intelligence Agent is structuring the candidate profile...")
                        time.sleep(0.5)
                        
                        progress_text.info("🔍 Skill Extraction Agent is parsing taxonomy keywords...")
                        time.sleep(0.5)
                        
                        progress_text.info("🧠 Job Prediction Agent is executing Random Forest classification...")
                        time.sleep(0.5)
                        
                        progress_text.info("📊 Market Intelligence Agent is aggregating job distribution stats...")
                        time.sleep(0.5)
                        
                        progress_text.info("💸 Salary Prediction Agent is running regressor uncertainty bands...")
                        time.sleep(0.5)
                        
                        progress_text.info("🗺️ Skill Gap & Roadmap Agent is compiling 90-day learning curriculum...")
                        time.sleep(0.5)
                        
                        progress_text.info("💼 Career Advisor Orchestrator is writing the final executive summary...")
                        
                        context = orchestrator.run_pipeline(
                            raw_resume_text=raw_text,
                            filename=uploaded_file.name,
                            location_tier=location_tier
                        )
                        
                    progress_text.empty()
                    st.success("✅ Analysis completed successfully!")
                    
                    # Update active session trace ID
                    st.session_state.active_trace_id = context["trace_id"]
                    
                    st.write("Navigate to the **Results Dashboard** or **Agent Pipeline** page to explore results.")
                    
                    # Show quick summary card
                    st.markdown(
                        f"""
                        <div class="glass-card">
                            <div class="glass-card-title">Quick Fit Assessment</div>
                            <p><b>Candidate:</b> {context['parsed_resume'].get('name', 'Applicant')}</p>
                            <p><b>Primary Recommended Role:</b> <span class="accent-text">{context['primary_target_role']}</span></p>
                            <p><b>Confidence Rating:</b> {context['top_roles'][0]['confidence']*100:.1f}%</p>
                            <p><b>Estimated Compensation Range:</b> {context['salary_data']['salary_low']:.2f}L - {context['salary_data']['salary_high']:.2f}L LPA</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            except Exception as e:
                st.error(f"An error occurred during pipeline run: {str(e)}")

else:
    # Multi-Resume Batch Comparison Mode
    uploaded_files = st.file_uploader("Upload 2-3 Resumes (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"], accept_multiple_files=True)
    
    if uploaded_files:
        st.write(f"📁 Loaded `{len(uploaded_files)}` profiles.")
        if len(uploaded_files) > 3:
            st.warning("⚠️ Recommended limit is 3 resumes for optimal comparison visibility.")
            
        if st.button("Execute Batch Comparison"):
            comparison_results = []
            
            for file in uploaded_files:
                try:
                    with st.spinner(f"Analyzing {file.name}..."):
                        file_bytes = file.read()
                        raw_text = extract_text_from_file(file_bytes, file.name)
                        
                        if not raw_text.strip():
                            st.warning(f"No text extracted from {file.name}.")
                            continue
                            
                        context = orchestrator.run_pipeline(
                            raw_resume_text=raw_text,
                            filename=file.name,
                            location_tier=location_tier
                        )
                        comparison_results.append(context)
                except Exception as e:
                    st.error(f"Error processing {file.name}: {str(e)}")
                    
            if comparison_results:
                st.success("✅ Batch Comparison Complete!")
                
                # Render Comparison Table
                st.markdown("### Side-by-Side Comparison")
                
                cols = st.columns(len(comparison_results))
                for idx, ctx in enumerate(comparison_results):
                    with cols[idx]:
                        parsed_p = ctx.get("parsed_resume", {})
                        sal = ctx.get("salary_data", {})
                        top_r = ctx.get("top_roles", [{}])[0]
                        skills_lst = ctx.get("skills", {})
                        all_sk = skills_lst.get("technical", []) + skills_lst.get("tools", [])
                        
                        st.markdown(
                            f"""
                            <div class="glass-card">
                                <div class="glass-card-title" style="font-size:1.1rem;">{parsed_p.get('name', 'Candidate ' + str(idx+1))}</div>
                                <p><b>File:</b> <code>{ctx.get('filename')}</code></p>
                                <hr style="margin: 10px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.05);">
                                <p><b>Job Fit:</b> <span class="accent-text">{top_r.get('role')}</span></p>
                                <p><b>Confidence:</b> {top_r.get('confidence', 0)*100:.1f}%</p>
                                <p><b>Salary Range:</b> {sal.get('salary_low', 0):.2f}L - {sal.get('salary_high', 0):.2f}L LPA</p>
                                <p><b>Education:</b> {', '.join(parsed_p.get('education', ['N/A']))}</p>
                                <p><b>Identified Skills:</b> {', '.join(all_sk[:6])}...</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

# Select Past Sessions
st.markdown("---")
st.markdown("### Recall Historical Session Logs")
sessions = get_all_sessions()

if sessions:
    session_options = {s["trace_id"]: f"{s['filename']} ({s['timestamp'][:16].replace('T', ' ')})" for s in sessions}
    selected_trace = st.selectbox(
        "Load previous analysis session:",
        options=list(session_options.keys()),
        format_func=lambda x: session_options[x]
    )
    
    if st.button("Load Session"):
        st.session_state.active_trace_id = selected_trace
        st.success(f"Loaded session `{session_options[selected_trace]}`! Navigate to the dashboard pages to inspect.")
else:
    st.info("No past sessions found in history. Run your first analysis above!")
