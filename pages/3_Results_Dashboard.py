import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from utils.ui import setup_page
from utils.db import get_session_context

setup_page("Results Dashboard")

st.title("Career FIT Assessment Dashboard 📊")
st.write("Review recommendations, model metrics, compensation ranges, and profile feature weights driving predictions.")

# Get session context
trace_id = st.session_state.get("active_trace_id")

if not trace_id:
    st.warning("⚠️ No active analysis trace loaded. Please upload a resume first in the **Upload Resume** page.")
else:
    context = get_session_context(trace_id)
    
    if not context:
        st.error("Could not fetch session data. Try running the analyzer again.")
    else:
        parsed_resume = context.get("parsed_resume", {})
        top_roles = context.get("top_roles", [])
        salary_data = context.get("salary_data", {})
        features = context.get("candidate_features", [])
        coarse_cat = context.get("coarse_category", "Unknown")
        exec_summary = context.get("executive_summary", "")
        
        # --- Section 1: Executive Briefing ---
        st.markdown("### Career Advisor Summary Report")
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="glass-card-title">Executive Briefing</div>
                <p style="font-size:1.05rem; line-height:1.6; color:#e2e8f0;">
                    {exec_summary}
                </p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # --- Section 2: Recommendation & Compensation Cards ---
        col_rec, col_sal = st.columns([3, 2])
        
        with col_rec:
            st.markdown("### Predicted Job Roles")
            
            # Show top recommended roles with visual confidence meters
            for idx, role in enumerate(top_roles):
                border_color = "#6366f1" if idx == 0 else "rgba(255, 255, 255, 0.1)"
                match_tag = '<span style="color:#10b981; font-weight:600; font-size:0.85rem;">[Coarse Category Match Boosted]</span>' if role.get("category_match") else ""
                
                st.markdown(
                    f"""
                    <div style="border: 1px solid {border_color}; border-radius:8px; padding:16px; margin-bottom:12px; background-color:rgba(255,255,255,0.015);">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-weight:700; font-size:1.15rem; color:#ffffff;">#{idx+1} {role['role']}</span>
                            <span style="font-weight:700; color:#6366f1; font-size:1.1rem;">{role['confidence']*100:.1f}% Match</span>
                        </div>
                        <div style="font-size:0.85rem; color:#94a3b8; margin: 4px 0 8px 0;">
                            Category: <b>{role.get('category')}</b> | {match_tag}
                        </div>
                        <p style="margin: 0; color:#cbd5e1; font-size:0.95rem;">{role.get('explanation')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
        with col_sal:
            st.markdown("### Compensation Analysis")
            
            # Predict std range
            low_sal = salary_data.get("salary_low", 3.0)
            high_sal = salary_data.get("salary_high", 6.0)
            mean_sal = salary_data.get("predicted_salary_mean", 4.5)
            std_sal = salary_data.get("predicted_salary_std", 0.5)
            
            st.markdown(
                f"""
                <div class="glass-card" style="text-align:center; padding:30px 10px;">
                    <div style="font-size:0.9rem; text-transform:uppercase; color:#94a3b8; letter-spacing:1px; margin-bottom:5px;">Estimated Annual Salary</div>
                    <div style="font-size:2.5rem; font-weight:800; color:#6366f1; margin-bottom:10px;">
                        {low_sal:.2f}L - {high_sal:.2f}L
                    </div>
                    <div style="font-size:1rem; color:#f3f4f6; margin-bottom:10px;">INR Per Annum (LPA)</div>
                    <hr style="margin: 15px auto; border:0; border-top: 1px solid rgba(255,255,255,0.08); width:70%;">
                    <div style="font-size:0.85rem; color:#94a3b8; text-align:left; padding: 0 15px;">
                        • <b>Ensemble mean:</b> {mean_sal:.2f} LPA<br>
                        • <b>Uncertainty band (1σ):</b> ±{std_sal:.2f} LPA<br>
                        • <b>Location Factor Applied:</b> Tier {context.get('location_tier', 1)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown("##### Compensation Insights")
            st.info(salary_data.get("market_note", "Estimated based on profile parameters."))
            
        # --- Section 3: Feature Weights Explainability ---
        st.markdown("---")
        st.markdown("### Feature Importance Explainability")
        
        if not features:
            st.info("No predictive features tracked for this run.")
        else:
            col_chart, col_desc = st.columns([5, 3])
            
            with col_chart:
                # Render beautiful seaborn chart
                try:
                    df_feat = pd.DataFrame(features)
                    # Sort ascending for horizontal bar chart
                    df_feat = df_feat.sort_values(by='importance', ascending=True)
                    
                    plt.style.use('dark_background')
                    fig, ax = plt.subplots(figsize=(7, 4.5))
                    
                    # Gradient color mapping
                    colors_list = sns.color_palette("plasma", len(df_feat))
                    
                    ax.barh(df_feat['feature'], df_feat['importance'], color=colors_list, edgecolor='none')
                    
                    ax.set_title("Random Forest Signal Strengths (Your Profile)", fontsize=11, color='#e2e8f0', fontweight='bold')
                    ax.set_xlabel("Predictive Impact Weight", fontsize=9, color='#94a3b8')
                    ax.tick_params(colors='#94a3b8', labelsize=8)
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    ax.spines['left'].set_color('#334155')
                    ax.spines['bottom'].set_color('#334155')
                    plt.tight_layout()
                    
                    st.pyplot(fig)
                except Exception as ex:
                    st.error(f"Failed to display matplotlib chart: {str(ex)}")
                    
            with col_desc:
                st.markdown(
                    """
                    <div class="glass-card" style="height:100%;">
                        <div class="glass-card-title">How to Read this Chart</div>
                        <p style="font-size:0.9rem; line-height:1.5;">
                            This chart displays the specific data points from your resume (skills, degree level, projects, etc.) 
                            that carried the <b>highest feature importances</b> inside our Random Forest Classification ensemble.
                        </p>
                        <p style="font-size:0.9rem; line-height:1.5;">
                            Signals with larger bars represent the primary elements that pushed the classifier toward matching 
                            you with <b>{top_roles[0]['role'] if top_roles else 'the target role'}</b>. 
                            If you wish to pivot roles, your learning roadmap will detail what new signals to construct.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
