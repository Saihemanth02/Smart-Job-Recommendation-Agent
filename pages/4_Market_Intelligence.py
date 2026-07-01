import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from utils.ui import setup_page
from utils.db import get_session_context
from config.settings import DATA_DIR

setup_page("Market Intelligence")

st.title("Market Intelligence Dashboard 📈")
st.write("Examine hiring trends, salary distribution models, and experience ratios across Indian entry-level engineering profiles.")

# Load seed datasets
resumes_path = DATA_DIR / "resumes_seed.csv"
salary_path = DATA_DIR / "salary_seed.csv"

if not resumes_path.exists() or not salary_path.exists():
    st.error("⚠️ Synthetic seed datasets not found. Please run the training pipeline first.")
else:
    # Read files
    df_res = pd.read_csv(resumes_path)
    df_sal = pd.read_csv(salary_path)
    
    # Get active session matched role if exists
    trace_id = st.session_state.get("active_trace_id")
    default_role = "Frontend Developer"
    
    if trace_id:
        context = get_session_context(trace_id)
        if context:
            default_role = context.get("primary_target_role", "Frontend Developer")
            st.info(f"💡 Visuals currently filtered for your matched target role: **{default_role}**")
            
    # Role Selection dropdown
    all_roles = sorted(df_sal['job_role'].unique())
    selected_role = st.selectbox(
        "Select Job Role to Inspect:", 
        options=all_roles, 
        index=all_roles.index(default_role) if default_role in all_roles else 0
    )
    
    # Filter datasets
    role_res = df_res[df_res['job_role'] == selected_role]
    role_sal = df_sal[df_sal['job_role'] == selected_role]
    
    # Show summary metric cards for selected role
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Hiring Market Size (Seed Resumes)", f"{len(role_res)} candidates")
    with col2:
        st.metric("Average Salary Range", f"{role_sal['salary'].mean():.2f} LPA")
    with col3:
        st.metric("Top Compensation Cap", f"{role_sal['salary'].max():.1f} LPA")
        
    st.markdown("---")
    
    # Render Analyst Comments
    st.markdown("### Labor Market Analyst Insights")
    if trace_id and selected_role == default_role:
        st.info(context.get("market_data", {}).get("trend_summary", "Hiring demand remains robust for this segment."))
    else:
        # Generate quick offline insight
        skills_list = []
        for s in role_res['skills'].dropna():
            skills_list.extend([x.strip() for x in s.split(",")])
        common_skills = pd.Series(skills_list).value_counts().head(3).index.tolist()
        
        st.markdown(
            f"""
            <div class="glass-card">
                <p style="margin:0;">
                    <b> Hires targeting '{selected_role}' show strong competencies in:</b> {', '.join(common_skills)}. 
                    Compensation ranges typically expand based on location tier and credentials, 
                    with average starting figures around <b>{role_sal['salary'].mean():.2f} LPA</b>.
                </p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    # --- VISUALIZATIONS SECTION ---
    st.markdown("### Market Analytics Charts")
    
    col_chart1, col_chart2 = st.columns(2)
    
    plt.style.use('dark_background')
    
    with col_chart1:
        # Chart 1: Top Trending Skills
        st.markdown("##### Trending Skills Frequency")
        all_skills = []
        for s in role_res['skills'].dropna():
            all_skills.extend([x.strip() for x in s.split(",")])
            
        if all_skills:
            df_skills = pd.Series(all_skills).value_counts().head(8).reset_index()
            df_skills.columns = ['skill', 'count']
            
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.barplot(
                x='count', y='skill', data=df_skills, ax=ax, 
                palette='Purples_r', hue='skill', legend=False
            )
            ax.set_xlabel("Number of Resume Profiles", color='#94a3b8')
            ax.set_ylabel("", color='#94a3b8')
            ax.tick_params(colors='#94a3b8', labelsize=9)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.info("No skill records found.")
            
    with col_chart2:
        # Chart 2: Salary Distribution Histogram
        st.markdown("##### Salary Distribution Density")
        if not role_sal.empty:
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.histplot(role_sal['salary'], kde=True, color='#f43f5e', ax=ax, edgecolor='none')
            ax.set_xlabel("Salary (LPA - INR)", color='#94a3b8')
            ax.set_ylabel("Profile Density", color='#94a3b8')
            ax.tick_params(colors='#94a3b8', labelsize=9)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.info("No salary records found.")
            
    st.write("")
    
    # Chart 3: Experience vs Salary Regplot
    st.markdown("##### Compensation Trajectory (Experience vs Salary)")
    if not role_sal.empty:
        fig, ax = plt.subplots(figsize=(10, 4.5))
        
        # Add jitter to make experience levels discrete points readable
        sns.regplot(
            x='years_experience', y='salary', data=role_sal, ax=ax,
            x_jitter=0.1, color='#6366f1',
            scatter_kws={'alpha':0.4, 's':40, 'color':'#f43f5e'},
            line_kws={'color':'#6366f1', 'linewidth':2}
        )
        
        ax.set_xlabel("Years of Work Experience", color='#94a3b8')
        ax.set_ylabel("Compensation (LPA - INR)", color='#94a3b8')
        ax.set_xticks([0, 1, 2, 3])
        ax.tick_params(colors='#94a3b8', labelsize=9)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.info("No salary correlation metrics.")
