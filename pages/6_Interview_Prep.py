import streamlit as st
from utils.ui import setup_page
from utils.db import get_session_context, save_session_context
from agents.orchestrator import Orchestrator

setup_page("Interview Prep & ATS Optimizer")

st.title("Interview Coach & ATS Resume Optimizer 💬")
st.write("Access interactive mock interview prep, audit your resume against target JDs, or chat directly with the Career Advisor.")

# Get session context
trace_id = st.session_state.get("active_trace_id")

if not trace_id:
    st.warning("⚠️ No active analysis trace loaded. Please upload a resume first in the **Upload Resume** page.")
else:
    context = get_session_context(trace_id)
    
    if not context:
        st.error("Could not fetch session data. Try running the analyzer again.")
    else:
        orchestrator = Orchestrator()
        primary_role = context.get("primary_target_role", "Frontend Developer")
        
        # Tabs for grouping services
        tab_coach, tab_ats, tab_chat = st.tabs([
            "🎯 Interview Practice Coach", 
            "📄 ATS Audit & Resume Optimizer", 
            "💬 Chat with Career Advisor"
        ])
        
        # --- TAB 1: INTERVIEW COACH ---
        with tab_coach:
            st.markdown("### Calibrated Practice Interview Coach")
            st.write(f"Practice technical and behavioral questions calibrated for a fresher seeking a **{primary_role}** role.")
            
            interview_data = context.get("interview_prep_data")
            
            if not interview_data:
                st.info("No practice questions generated yet for this session.")
                if st.button("Generate Calibrated Questions"):
                    with st.spinner("Interview Coach Agent is generating calibrated questions..."):
                        try:
                            interview_data = orchestrator.run_interview_prep(trace_id)
                            # Reload context
                            context = get_session_context(trace_id)
                            st.success("Questions generated!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to generate questions: {str(e)}")
            
            if interview_data:
                col_tech, col_beh = st.columns(2)
                
                with col_tech:
                    st.markdown("##### Technical Interview Questions")
                    for idx, q in enumerate(interview_data.get("technical_questions", []), 1):
                        st.markdown(
                            f"""
                            <div class="glass-card" style="padding:15px; margin-bottom:10px; font-size:0.92rem;">
                                <b>Q{idx}:</b> {q}
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                        
                with col_beh:
                    st.markdown("##### Behavioral Questions & STAR Hints")
                    for idx, q_dict in enumerate(interview_data.get("behavioral_questions", []), 1):
                        st.markdown(
                            f"""
                            <div class="glass-card" style="padding:15px; margin-bottom:10px; font-size:0.92rem;">
                                <b>Q{idx}:</b> {q_dict.get('question')}<br>
                                <span style="color:#6366f1; font-size:0.8rem; font-style:italic;">
                                    💡 STAR Hint: {q_dict.get('star_hint')}
                                </span>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                        
        # --- TAB 2: ATS RESUME OPTIMIZER ---
        with tab_ats:
            st.markdown("### ATS Match Audit & Cover Letter Builder")
            st.write("Paste a target job description below to check keyword match, optimize bullet points, and draft a cover letter.")
            
            target_jd = st.text_area("Target Job Description (JD):", height=150, placeholder="Paste target requirements here...")
            
            optimizer_data = context.get("optimizer_data")
            
            if st.button("Audit and Optimize Profile"):
                if not target_jd.strip():
                    st.warning("Please paste a job description first.")
                else:
                    with st.spinner("Resume Optimizer Agent is evaluating keywords and rewrites..."):
                        try:
                            optimizer_data = orchestrator.run_resume_optimizer(trace_id, target_jd)
                            # Reload context
                            context = get_session_context(trace_id)
                            st.success("Optimization completed!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to run optimizer: {str(e)}")
                            
            if optimizer_data:
                score = optimizer_data.get("ats_score", 0.0)
                missing = optimizer_data.get("missing_keywords", [])
                rewrites = optimizer_data.get("rewrites", [])
                cov_let = optimizer_data.get("cover_letter", "")
                general_tips = optimizer_data.get("general_ats_tips", [])
                
                # Show score gauge/metric
                score_color = "#10b981" if score >= 75 else "#f59e0b" if score >= 50 else "#ef4444"
                
                col_score, col_kw = st.columns([1, 2])
                with col_score:
                    st.markdown(
                        f"""
                        <div class="glass-card" style="text-align:center; padding:35px 10px;">
                            <div style="font-size:0.9rem; text-transform:uppercase; color:#94a3b8; letter-spacing:1px; margin-bottom:5px;">Estimated ATS Score</div>
                            <div style="font-size:3.5rem; font-weight:800; color:{score_color}; margin-bottom:5px;">{score:.0f}%</div>
                            <div style="font-size:0.85rem; color:#94a3b8;">Threshold match target is 80%</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with col_kw:
                    st.markdown("##### Missing Target Keywords:")
                    if missing:
                        kw_html = " ".join([f'<span style="background-color:rgba(99,102,241,0.1); color:#6366f1; border: 1px solid rgba(99,102,241,0.2); padding: 4px 10px; border-radius: 12px; font-size:0.85rem; margin-right:8px; display:inline-block; margin-bottom:8px;">{k}</span>' for k in missing])
                        st.markdown(kw_html, unsafe_allow_html=True)
                    else:
                        st.success("Great keyword overlap! No major missing competencies.")
                        
                st.markdown("---")
                
                col_rew, col_letter = st.columns(2)
                with col_rew:
                    st.markdown("##### Suggested Resume Bullet Point Rewrites:")
                    if rewrites:
                        for rw in rewrites:
                            st.markdown(
                                f"""
                                <div style="background-color:rgba(255,255,255,0.015); border-left: 3px solid #ef4444; padding:10px; border-radius: 0 6px 6px 0; margin-bottom:10px; font-size:0.88rem;">
                                    <b>Original:</b><br><span style="color:#94a3b8;">{rw.get('original')}</span>
                                </div>
                                <div style="background-color:rgba(255,255,255,0.015); border-left: 3px solid #10b981; padding:10px; border-radius: 0 6px 6px 0; margin-bottom:20px; font-size:0.88rem;">
                                    <b>Suggested (quantified):</b><br><span style="color:#ffffff;">{rw.get('suggested')}</span>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                    else:
                        st.info("No bullet rewrites recommended. Keep standard formatting.")
                        
                    if general_tips:
                        st.markdown("##### ATS Optimization Tips:")
                        for tip in general_tips:
                            st.markdown(f"- {tip}")
                            
                with col_letter:
                    st.markdown("##### Drafted Cover Letter (150 Words):")
                    if cov_let:
                        st.markdown(
                            f"""
                            <div class="glass-card" style="font-size:0.9rem; line-height:1.6; font-family:monospace; background-color:#111116;">
                                {cov_let}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        st.info("Please provide a Job Description to generate a tailored cover letter.")
                        
        # --- TAB 3: CAREER ADVISOR CHAT ---
        with tab_chat:
            st.markdown("### Conversational Follow-Up with Career Advisor")
            st.write("Ask the Orchestrator free-form questions about your recommendations, salary predictions, or study roadmap.")
            
            # Setup Session Chat History
            chat_key = f"chat_history_{trace_id}"
            if chat_key not in st.session_state:
                st.session_state[chat_key] = [
                    {"role": "assistant", "content": "Hello! I am your Career Advisor. Feel free to ask me any questions about your job predictions, salary parameters, or study curriculum details."}
                ]
                
            # Render chat history
            for msg in st.session_state[chat_key]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    
            # User chat input
            if prompt := st.chat_input("Ask a follow-up question..."):
                # Append user query
                st.session_state[chat_key].append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                    
                # Call LLM Router with full context as prompt helper
                with st.chat_message("assistant"):
                    with st.spinner("Advisor is thinking..."):
                        try:
                            # Gather previous logs
                            chat_str = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state[chat_key][-4:]])
                            
                            system_prompt = (
                                "You are the Career Advisor, lead coordinator of a team of specialist career-analysis agents. "
                                "You have already analyzed the candidate's profile. Here is their full parsed analysis context:\n"
                                f"- Recommended Role: {primary_role}\n"
                                f"- Matching Category: {context.get('coarse_category', 'Software Development')}\n"
                                f"- Salary Estimation Range: {context.get('salary_data', {}).get('salary_low', 3.0):.2f}L - {context.get('salary_data', {}).get('salary_high', 6.0):.2f}L LPA\n"
                                f"- Missing Core Skills: {', '.join(context.get('roadmap_data', {}).get('missing_skills', []))}\n\n"
                                "Answer the candidate's follow-up questions in a professional, encouraging, supportive, and direct tone. "
                                "Never repeat raw JSON format. Keep answers concise (under 120 words)."
                            )
                            
                            response = orchestrator.call_llm(
                                user_prompt=f"Conversation History:\n{chat_str}\n\nCandidate Question: {prompt}",
                                json_mode=False,
                                task_size="small"
                            )
                            
                            st.markdown(response)
                            st.session_state[chat_key].append({"role": "assistant", "content": response})
                        except Exception as e:
                            st.error(f"Could not connect to Advisor: {str(e)}")
