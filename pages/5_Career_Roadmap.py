import streamlit as st
from utils.ui import setup_page
from utils.db import get_session_context
from utils.report_generator import generate_pdf_report

setup_page("Career Roadmap")

st.title("90-Day Skill Gap & Learning Roadmap 🗺️")
st.write("Construct an actionable curriculum to bridge skill gaps and reach target competency standards.")

# Get session context
trace_id = st.session_state.get("active_trace_id")

if not trace_id:
    st.warning("⚠️ No active analysis trace loaded. Please upload a resume first in the **Upload Resume** page.")
else:
    context = get_session_context(trace_id)
    
    if not context:
        st.error("Could not fetch session data. Try running the analyzer again.")
    else:
        roadmap_data = context.get("roadmap_data", {})
        prioritized_gaps = roadmap_data.get("prioritized_gaps", {"high": [], "medium": [], "low": []})
        roadmap_text = roadmap_data.get("roadmap", "No roadmap generated.")
        primary_role = context.get("primary_target_role", "Target Role")
        
        # --- PDF Export Button ---
        st.markdown("### Export Full Profile Assessment")
        try:
            pdf_bytes = generate_pdf_report(context)
            candidate_name = context.get("parsed_resume", {}).get("name", "Candidate").replace(" ", "_")
            st.download_button(
                label="📥 Download Full PDF Assessment Report",
                data=pdf_bytes,
                file_name=f"Career_Advisor_Report_{candidate_name}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Error compiling PDF: {str(e)}")
            
        st.write("")
        
        # --- Section 1: Skill Gaps priority columns ---
        st.markdown("### Identified Skill Gaps & Priority")
        st.write(f"The following gaps represent required competencies for **{primary_role}** not identified on your profile:")
        
        col_h, col_m, col_l = st.columns(3)
        
        with col_h:
            st.markdown(
                """
                <div style="border:1px solid #ef4444; border-radius:8px; padding:15px; background-color:rgba(239,68,68,0.02); height:100%;">
                    <div style="font-weight:700; color:#ef4444; margin-bottom:10px; font-size:1.05rem;">🔴 High Priority (Core Gaps)</div>
                """,
                unsafe_allow_html=True
            )
            gaps_high = prioritized_gaps.get("high", [])
            if gaps_high:
                for skill in gaps_high:
                    st.markdown(f"- **{skill}**")
            else:
                st.write("No major gaps found! Core capabilities are covered.")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_m:
            st.markdown(
                """
                <div style="border:1px solid #f59e0b; border-radius:8px; padding:15px; background-color:rgba(245,158,11,0.02); height:100%;">
                    <div style="font-weight:700; color:#f59e0b; margin-bottom:10px; font-size:1.05rem;">🟡 Medium Priority (Tools & Support)</div>
                """,
                unsafe_allow_html=True
            )
            gaps_med = prioritized_gaps.get("medium", [])
            if gaps_med:
                for skill in gaps_med:
                    st.markdown(f"- {skill}")
            else:
                st.write("No intermediate gaps identified.")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_l:
            st.markdown(
                """
                <div style="border:1px solid #10b981; border-radius:8px; padding:15px; background-color:rgba(16,185,129,0.02); height:100%;">
                    <div style="font-weight:700; color:#10b981; margin-bottom:10px; font-size:1.05rem;">🟢 Low Priority (Nice to Have)</div>
                """,
                unsafe_allow_html=True
            )
            gaps_low = prioritized_gaps.get("low", [])
            if gaps_low:
                for skill in gaps_low:
                    st.markdown(f"- {skill}")
            else:
                st.write("No secondary gaps identified.")
            st.markdown("</div>", unsafe_allow_html=True)
            
        # --- Section 2: 90-Day Roadmap Display ---
        st.markdown("---")
        st.markdown(f"### Phased Study Curriculum for {primary_role}")
        
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="glass-card-title">Structured Study Plan</div>
                <div style="font-size:1rem; line-height:1.6; color:#cbd5e1; white-space: pre-wrap;">{roadmap_text}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # Interactive Study Progress Checklist
        st.markdown("### Interactive Progress Checklist")
        st.write("Tick off missing competencies as you study to track your path:")
        
        all_missing = gaps_high + gaps_med + gaps_low
        if all_missing:
            for skill in all_missing:
                st.checkbox(f"I have mastered **{skill}**", key=f"chk_{skill.lower()}")
        else:
            st.success("🎉 You match 100% of the target requirements! No missing skills to track.")
