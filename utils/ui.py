import streamlit as st
import os
from dotenv import load_dotenv

# Hot-reload environment variables on every page render
load_dotenv(override=True)

def setup_page(title: str):
    """
    Sets the page config, custom dark-theme stylesheets,
    and visual styles for a premium glassmorphic UI.
    """
    # Force custom font load (Inter) from Google Fonts
    st.markdown("""
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)
    
    # Custom CSS Inject
    st.markdown("""
    <style>
    /* Dark Theme Core */
    .stApp {
        background-color: #0a0a0a !important;
        color: #f3f4f6 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Remove default top margins */
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 3rem !important;
    }
    
    /* Sidebar override */
    section[data-testid="stSidebar"] {
        background-color: #0b0b0f !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Sidebar elements text color */
    section[data-testid="stSidebar"] .st-emotion-cache-10o5uqv {
        color: #f3f4f6;
    }
    
    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(22, 22, 28, 0.65);
        border-radius: 12px;
        padding: 24px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        margin-bottom: 20px;
    }
    
    .glass-card-title {
        color: #6366f1;
        font-weight: 700;
        font-size: 1.25rem;
        margin-bottom: 12px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        padding-bottom: 8px;
    }
    
    /* Custom Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
    }
    
    /* Paragraphs and texts */
    p, span, label, li {
        font-family: 'Inter', sans-serif !important;
        color: #cbd5e1 !important;
    }
    
    /* Accent styling */
    .accent-text {
        color: #6366f1 !important;
        font-weight: 600;
    }
    
    /* Buttons Custom Overrides */
    div.stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 12px 28px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3) !important;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5) !important;
        background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%) !important;
    }
    
    div.stButton > button:active {
        transform: translateY(1px) !important;
    }
    
    /* Progress and Metric styling */
    div[data-testid="stMetricValue"] {
        color: #6366f1 !important;
        font-weight: 700 !important;
    }
    
    /* Custom log lists */
    .message-container {
        border-left: 3px solid #6366f1;
        padding-left: 15px;
        margin-bottom: 15px;
        background-color: rgba(255, 255, 255, 0.02);
        padding-top: 10px;
        padding-bottom: 10px;
        border-radius: 0 8px 8px 0;
    }
    
    /* Form inputs overlay */
    input, textarea {
        background-color: #121216 !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    </style>
    """, unsafe_allow_html=True)
