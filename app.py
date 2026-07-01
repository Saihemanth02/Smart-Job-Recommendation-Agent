import streamlit as st
import os
from dotenv import load_dotenv
from utils.db import init_db
from utils.ui import setup_page

# Load environment variables
load_dotenv()

# Initialize local sqlite database structure
init_db()

# Page config and stylesheet injectors
setup_page("Home")

# Header Section
st.title("Smart Job Recommendation Agent 💼")
st.subheader("Your AI Career Assessment & Personal Advisor Portal")

# Sidebar Status Segment
st.sidebar.markdown("### Agent Status Panel")
groq_key = os.getenv("GROQ_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")

if groq_key:
    st.sidebar.success("Groq Primary: Connected")
else:
    st.sidebar.warning("Groq Primary: Config missing")

if gemini_key:
    st.sidebar.success("Gemini Fallback: Connected")
else:
    st.sidebar.warning("Gemini Fallback: Config missing")

# Session State Setup
if "active_trace_id" not in st.session_state:
    st.session_state.active_trace_id = None
if "location_tier" not in st.session_state:
    st.session_state.location_tier = 1

# Welcome Panel
st.markdown(
    """
    <div class="glass-card">
        <div class="glass-card-title">Welcome to the Career Advisor System</div>
        <p>
            The <b>Smart Job Recommendation Agent</b> is a production-grade multi-agent orchestrator 
            designed to analyze candidate resumes, predict matching industry job roles using advanced 
            machine learning models, calculate uncertainty-calibrated salary bounds, and map complete 
            90-day curricula to bridge identified skill gaps.
        </p>
        <p>
            Instead of executing as a monolithic system, this platform delegates assessment tasks 
            across <b>eight specialized agents</b>, cooperating through a structured Agent-to-Agent (A2A) 
            message protocol.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Pipeline Flow Diagram (Visualizing the A2A DAG)
st.markdown("### System Architecture & Pipeline Flow")

st.markdown(
    """
    <div class="glass-card">
        <div class="glass-card-title">Multi-Agent DAG Execution Sequence</div>
        <p>Here is how the specialist agents collaborate to evaluate your profile in one unified pass:</p>
        <div style="padding: 10px; background-color: rgba(255, 255, 255, 0.02); border-radius: 8px; font-family: monospace; font-size: 0.9rem; line-height: 1.6;">
            [Resume Text] <br>
            &nbsp;&nbsp;&nbsp;│<br>
            &nbsp;&nbsp;&nbsp;▼<br>
            <b>1. Resume Intelligence Agent</b> (Parses raw doc structure to JSON)<br>
            &nbsp;&nbsp;&nbsp;│<br>
            &nbsp;&nbsp;&nbsp;▼<br>
            <b>2. Skill Extraction Agent</b> (Taxonomy match + implicit soft skill detection)<br>
            &nbsp;&nbsp;&nbsp;│<br>
            &nbsp;&nbsp;&nbsp;▼<br>
            <b>3. Job Prediction Agent</b> (NB Coarse Category + RF fine-grained role ensemble)<br>
            &nbsp;&nbsp;&nbsp;├───► <b>4. Market Intelligence Agent</b> (Aggregates relative trend statistics)<br>
            &nbsp;&nbsp;&nbsp;└───► <b>5. Salary Prediction Agent</b> (RF regression prediction & standard-deviation range)<br>
            &nbsp;&nbsp;&nbsp;│<br>
            &nbsp;&nbsp;&nbsp;▼<br>
            <b>6. Skill Gap & Roadmap Agent</b> (Builds custom 90-day learning path with phases)<br>
            &nbsp;&nbsp;&nbsp;│<br>
            &nbsp;&nbsp;&nbsp;▼<br>
            <b>7. Career Advisor Orchestrator</b> (Weaves outcomes into encouraging report)<br>
            &nbsp;&nbsp;&nbsp;├───► <b>[Resume Optimizer / ATS Agent]</b> (On-Demand bullet rewrites & cover letters)<br>
            &nbsp;&nbsp;&nbsp;└───► <b>[Interview Prep Agent]</b> (On-Demand technical and behavioral Q&As)<br>
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)

st.markdown("### How to Get Started")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="glass-card" style="min-height: 180px;">
            <div style="font-weight:700; color:#6366f1; margin-bottom:8px;">Step 1: Upload Resume</div>
            Navigate to the <b>Upload Resume</b> page in the sidebar and upload your PDF, Word doc, or text resume.
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class="glass-card" style="min-height: 180px;">
            <div style="font-weight:700; color:#6366f1; margin-bottom:8px;">Step 2: Watch Agents Run</div>
            The <b>Agent Pipeline</b> page lets you monitor agent message packets, latencies, and fallback steps in real time.
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """
        <div class="glass-card" style="min-height: 180px;">
            <div style="font-weight:700; color:#6366f1; margin-bottom:8px;">Step 3: Analyze Results</div>
            Examine your matched roles, feature weights, market metrics, roadmap steps, and practice interview coach questions.
        </div>
        """,
        unsafe_allow_html=True
    )
