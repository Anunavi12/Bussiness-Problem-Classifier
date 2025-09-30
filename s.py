import streamlit as st
import requests, json, os, re, time
import random
import hashlib
from datetime import datetime, timedelta
from io import BytesIO
from fpdf import FPDF
import unicodedata
import pandas as pd

# -----------------------------
# Config - Page Setup
# -----------------------------
st.set_page_config(
    page_title="Business Problem Level Classifier",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .main {
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        background-attachment: fixed;
        min-height: 100vh;
    }
    
    .stApp {
        background: transparent;
    }
    
    .page-title {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.2);
    }
    
    .page-title h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    
    /* Updated for non-clickable display boxes */
    .dimension-display-box {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
        min-height: 120px;
        margin-bottom: 1rem;
        border: none;
        width: 100%;
        cursor: default;
    }
    
    .dimension-display-box:hover {
        transform: none;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
    }
    
    .dimension-score {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0.5rem 0;
    }
    
    .dimension-label {
        font-size: 1.1rem;
        font-weight: 500;
        opacity: 0.95;
    }
    
    .hardness-badge-hard {
        background: linear-gradient(135deg, #ff6b6b, #ff5252);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 20px;
        font-size: 1.5rem;
        font-weight: 700;
        text-align: center;
        box-shadow: 0 10px 25px rgba(255, 107, 107, 0.4);
        min-height: 150px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .hardness-badge-moderate {
        background: linear-gradient(135deg, #ffa726, #ffb74d);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 20px;
        font-size: 1.5rem;
        font-weight: 700;
        text-align: center;
        box-shadow: 0 10px 25px rgba(255, 167, 38, 0.4);
        min-height: 150px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .hardness-badge-easy {
        background: linear-gradient(135deg, #66bb6a, #4caf50);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 20px;
        font-size: 1.5rem;
        font-weight: 700;
        text-align: center;
        box-shadow: 0 10px 25px rgba(102, 187, 106, 0.4);
        min-height: 150px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .score-badge {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        min-height: 150px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        font-family: 'Poppins', sans-serif;
        padding: 0.7rem 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 30px rgba(102, 126, 234, 0.5);
    }
    
    .primary-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-family: 'Poppins', sans-serif !important;
        padding: 1rem 2.5rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3) !important;
        font-size: 1.2rem !important;
        height: auto !important;
        min-height: 60px !important;
    }
    
    .primary-button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 30px rgba(102, 126, 234, 0.5) !important;
    }
    
    .qa-box {
        background: rgba(255, 255, 255, 0.95);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .qa-question {
        font-weight: 600;
        color: #667eea;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
    }
    
    .qa-answer {
        color: #4a5568;
        line-height: 1.6;
    }
    
    .section-title {
        color: #667eea;
        font-size: 1.3rem;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #667eea;
    }
    
    .problem-display {
        background: rgba(255, 255, 255, 0.95);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    .problem-display h4 {
        color: #667eea;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .content-text {
        background: rgba(255, 255, 255, 0.95);
        padding: 1.5rem;
        border-radius: 12px;
        line-height: 1.8;
        color: #4a5568;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .main-issue-box {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
    }
    
    .main-issue-title {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: white;
    }
    
    .main-issue-content {
        line-height: 1.6;
        color: white;
    }
    
    .dimension-button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
        min-height: 120px;
        margin-bottom: 1rem;
        border: none;
        width: 100%;
        cursor: pointer;
        font-family: 'Poppins', sans-serif;
    }
    
    .dimension-button:hover {
        transform: translateY(-5px) scale(1.05);
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.5);
    }
    
    /* New styles for restructured page 2 */
    .current-system-section {
        background: rgba(255, 255, 255, 0.95);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .io-section {
        background: rgba(255, 255, 255, 0.95);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        height: 100%;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Config - Data & Auth
# -----------------------------
TENANT_ID = "talos"
AUTH_TOKEN = None
HEADERS_BASE = {"Content-Type": "application/json"}

ACCOUNTS = [
    "Select Account",
    "Abbive", "BMS", "BLR Airport", "Chevron", "Coles", "DELL", "Microsoft", 
    "Mu Labs", "Nike", "Skill Development", "Southwest Airlines", "THD", "Tmobile", "Walmart"
]

INDUSTRIES = [
    "Select Industry",
    "Airlines", "Automotive", "Consumer Goods", "E-commerce", "Education", "Energy", 
    "Finance", "Healthcare", "Hospitality", "Logistics", "Other", "Pharma", "Retail", "Technology"
]

# === API CONFIGURATION ===
API_CONFIGS = [
    # Vocabulary
    {
        "name": "vocabulary",
        "url": "https://eoc.mu-sigma.com/talos-engine/agency/reasoning_api?society_id=1757657318406&agency_id=1758548233201&level=1",
        "multiround_convo":3,
        "description": "vocabulary",
        "prompt": lambda problem, outputs: (
            f"{problem}\n\nExtract the vocabulary from this problem statement."
        )
    },
    # Current System
    {
        "name": "current_system",
        "url": "https://eoc.mu-sigma.com/talos-engine/agency/reasoning_api?society_id=1757657318406&agency_id=1758549095254&level=1",
        "multiround_convo": 2,
        "description": "Current System in Place",
        "prompt": lambda problem, outputs: (
            f"Problem statement - {problem}\n\nContext from vocabulary:\n{outputs.get('vocabulary','')}\n\n"
            "Describe the current system, inputs, outputs, and pain points."
        )
    },
    {
        "name": "Q1. What is the frequency and pace of change in the key inputs driving the business?",
        "url": "https://eoc.mu-sigma.com/talos-engine/agency/reasoning_api?society_id=1757657318406&agency_id=1758555344231&level=1",
        "multiround_convo": 2,
        "description": "Q1. What is the frequency and pace of change in the key inputs driving the business?",
        "prompt": lambda problem, outputs: (
            f"Problem statement - {problem}\n\nContext from Current System:\n{outputs.get('current_system','')}\n\n"
            "Q1. What is the frequency and pace of change in the key inputs driving the business?\n"
            "Provide detailed answers/explanations grounded in business and functional realities.\n"
            "Act as an evaluator for this question based on the answer you provide.\n"
            "Score the problem statement between 0–5 (0 = no conflicts, 5 = significant conflicts).\n"
            "Do not consider technical aspects or implementation; rate only by the characteristics of the problem.\n"
            "Provide a detailed justification for the score."
        )
    },
    {
        "name": "Q2. To what extent are these changes cyclical and predictable versus sporadic and unpredictable?",
        "url": "https://eoc.mu-sigma.com/talos-engine/agency/reasoning_api?society_id=1757657318406&agency_id=1758549615986&level=1",
        "multiround_convo": 2,
        "description": "Q2. To what extent are these changes cyclical and predictable versus sporadic and unpredictable?",
        "prompt": lambda problem, outputs: (
            f"Problem statement - {problem}\n\nContext from Current System:\n{outputs.get('current_system','')}\n\n"
            "Q2. To what extent are these changes cyclical and predictable vs sporadic and unpredictable?\nScore 0–5. Provide justification."
            "Provide detailed answers/explanations grounded in business and functional realities.\n"
            "Act as an evaluator for this question based on the answer you provide.\n"
            "Score the problem statement between 0–5 (0 = no conflicts, 5 = significant conflicts).\n"
            "Do not consider technical aspects or implementation; rate only by the characteristics of the problem.\n"
            "Provide a detailed justification for the score."
        )
    },
    {
        "name": "Q3. How resilient is the current system in absorbing these changes without requiring significant rework or disruption?",
        "url": "https://eoc.mu-sigma.com/talos-engine/agency/reasoning_api?society_id=1757657318406&agency_id=1758614550482&level=1",
        "multiround_convo": 2,
        "description": "Q3. How resilient is the current system in absorbing these changes without requiring significant rework or disruption?",
        "prompt": lambda problem, outputs: (
            f"Problem statement - {problem}\n\nContext from Current System:\n{outputs.get('current_system','')}\n\n"
            "Q3. How resilient is the current system in absorbing these changes? Score 0–5. Provide justification."
            "Provide detailed answers/explanations grounded in business and functional realities.\n"
            "Act as an evaluator for this question based on the answer you provide.\n"
            "Score the problem statement between 0–5 (0 = no conflicts, 5 = significant conflicts).\n"
            "Do not consider technical aspects or implementation; rate only by the characteristics of the problem.\n"
            "Provide a detailed justification for the score."
        )
    },
    {
        "name": "Q4. To what extent do stakeholders share a common understanding of the key terms and concepts?",
        "url": "https://eoc.mu-sigma.com/talos-engine/agency/reasoning_api?society_id=1757657318406&agency_id=1758614809984&level=1",
        "multiround_convo": 2,
        "description": "Q4. To what extent do stakeholders share a common understanding of the key terms and concepts?",
        "prompt": lambda problem, outputs: (
            f"Problem statement - {problem}\n\nContext from Current System:\n{outputs.get('current_system','')}\n\n"
            "Q4. To what extent do stakeholders share a common understanding and goals about the problem? Score 0–5. Provide justification."
            "Provide detailed answers/explanations grounded in business and functional realities.\n"
            "Act as an evaluator for this question based on the answer you provide.\n"
            "Score the problem statement between 0–5 (0 = no conflicts, 5 = significant conflicts).\n"
            "Do not consider technical aspects or implementation; rate only by the characteristics of the problem.\n"
            "Provide a detailed justification for the score."
        )
    },
    {
        "name": "Q5. Are there any conflicting definitions or interpretations that could create confusion?",
        "url": "https://eoc.mu-sigma.com/talos-engine/agency/reasoning_api?society_id=1757657318406&agency_id=1758615038050&level=1",
        "multiround_convo": 2,
        "description": "Q5. Are there any conflicting definitions or interpretations that could create confusion",
        "prompt": lambda problem, outputs: (
            f"Problem statement - {problem}\n\nContext from Current System:\n{outputs.get('current_system','')}\n\n"
            "Q5. Are there significant conflicts or tradeoffs between stakeholders or system elements? Score 0–5. Provide justification."
            "Provide detailed answers/explanations grounded in business and functional realities.\n"
            "Act as an evaluator for this question based on the answer you provide.\n"
            "Score the problem statement between 0–5 (0 = no conflicts, 5 = significant conflicts).\n"
            "Do not consider technical aspects or implementation; rate only by the characteristics of the problem.\n"
            "Provide a detailed justification for the score."
        )
    },
    {
        "name": "Q6. Are objectives, priorities, and constraints clearly communicated and well-defined?",
        "url": "https://eoc.mu-sigma.com/talos-engine/agency/reasoning_api?society_id=1757657318406&agency_id=1758615386880&level=1",
        "multiround_convo": 2,
        "description": "Q6. Are objectives, priorities, and constraints clearly communicated and well-defined?",
        "prompt": lambda problem, outputs: (
            f"Problem statement - {problem}\n\nContext from Current System:\n{outputs.get('current_system','')}\n\n"
            "Q6. How clear is the problem definition and scope? Score 0–5. Provide justification."
            "Provide detailed answers/explanations grounded in business and functional realities.\n"
            "Act as an evaluator for this question based on the answer you provide.\n"
            "Score the problem statement between 0–5 (0 = no conflicts, 5 = significant conflicts).\n"
            "Do not consider technical aspects or implementation; rate only by the characteristics of the problem.\n"
            "Provide a detailed justification for the score."
        )
    },
    {
        "name": "Q7. To what extent are key inputs interdependent?",
        "url": "https://eoc.mu-sigma.com/talos-engine/agency/reasoning_api?society_id=1757657318406&agency_id=1758615778653&level=1",
        "multiround_convo": 2,
        "description": "Q7. To what extent are key inputs interdependent?",
        "prompt": lambda problem, outputs: (
            f"Problem statement - {problem}\n\nContext from Current System:\n{outputs.get('current_system','')}\n\n"
            "Q7. How adequate are current resources (people, budget, technology) to handle the issue? Score 0–5. Provide justification."
            "Provide detailed answers/explanations grounded in business and functional realities.\n"
            "Act as an evaluator for this question based on the answer you provide.\n"
            "Score the problem statement between 0–5 (0 = no conflicts, 5 = significant conflicts).\n"
            "Do not consider technical aspects or implementation; rate only by the characteristics of the problem.\n"
            "Provide a detailed justification for the score."
        )
    },
    {
        "name": "Q8. How well are the governing rules, functions, and relationships between inputs understood?",
        "url": "https://eoc.mu-sigma.com/talos-engine/agency/reasoning_api?society_id=1757657318406&agency_id=1758616081630&level=1",
        "multiround_convo": 2,
        "description": "Q8. How well are the governing rules, functions, and relationships between inputs understood?",
        "prompt": lambda problem, outputs: (
            f"Problem statement - {problem}\n\nContext from Current System:\n{outputs.get('current_system','')}\n\n"
            "Q8. How complex is the problem in terms of stakeholders, processes, or technology involved? Score 0–5. Provide justification."
            "Provide detailed answers/explanations grounded in business and functional realities.\n"
            "Act as an evaluator for this question based on the answer you provide.\n"
            "Score the problem statement between 0–5 (0 = no conflicts, 5 = significant conflicts).\n"
            "Do not consider technical aspects or implementation; rate only by the characteristics of the problem.\n"
            "Provide a detailed justification for the score."
        )
    },
    {
        "name": "Q9. Are there any hidden or latent dependencies that could impact outcomes?",
        "url": "https://eoc.mu-sigma.com/talos-engine/agency/reasoning_api?society_id=1757657318406&agency_id=1758616793510&level=1",
        "multiround_convo": 2,
        "description": "Q9. Are there any hidden or latent dependencies that could impact outcomes?",
        "prompt": lambda problem, outputs: (
            f"Problem statement - {problem}\n\nContext from Current System:\n{outputs.get('current_system','')}\n\n"
            "Q9. How dependent is the problem on external factors or third parties? Score 0–5. Provide justification."
            "Provide detailed answers/explanations grounded in business and functional realities.\n"
            "Act as an evaluator for this question based on the answer you provide.\n"
            "Score the problem statement between 0–5 (0 = no conflicts, 5 = significant conflicts).\n"
            "Do not consider technical aspects or implementation; rate only by the characteristics of the problem.\n"
            "Provide a detailed justification for the score."
        )
    },
    {
        "name": "Q10. Are there hidden or latent dependencies that could affect outcomes?",
        "url": "https://eoc.mu-sigma.com/talos-engine/agency/reasoning_api?society_id=1757657318406&agency_id=1758617140479&level=1",
        "multiround_convo": 2,
        "description": "Q10. Are there hidden or latent dependencies that could affect outcomes?",
        "prompt": lambda problem, outputs: (
            f"Problem statement - {problem}\n\nContext from Current System:\n{outputs.get('current_system','')}\n\n"
            "Q10. What is the risk/impact if this problem remains unresolved? Score 0–5. Provide justification."
            "Provide detailed answers/explanations grounded in business and functional realities.\n"
            "Act as an evaluator for this question based on the answer you provide.\n"
            "Score the problem statement between 0–5 (0 = no conflicts, 5 = significant conflicts).\n"
            "Do not consider technical aspects or implementation; rate only by the characteristics of the problem.\n"
            "Provide a detailed justification for the score."
        )
    },
    {
        "name": "Q11. Are feedback loops insufficient or missing, limiting our ability to adapt?",
        "url": "https://eoc.mu-sigma.com/talos-engine/agency/reasoning_api?society_id=1757657318406&agency_id=1758618137301&level=1",
        "multiround_convo": 2,
        "description": "Q11. Are feedback loops insufficient or missing, limiting our ability to adapt?",
        "prompt": lambda problem, outputs: (
            f"Problem statement - {problem}\n\nContext from Current System:\n{outputs.get('current_system','')}\n\n"
            "Q11. How urgent is it to address this problem? Score 0–5. Provide justification."
            "Provide detailed answers/explanations grounded in business and functional realities.\n"
            "Act as an evaluator for this question based on the answer you provide.\n"
            "Score the problem statement between 0–5 (0 = no conflicts, 5 = significant conflicts).\n"
            "Do not consider technical aspects or implementation; rate only by the characteristics of the problem.\n"
            "Provide a detailed justification for the score."
        )
    },
    {
        "name": "Q12. Do we lack established benchmarks or \"gold standards\" to validate results?",
        "url": "https://eoc.mu-sigma.com/talos-engine/agency/reasoning_api?society_id=1757657318406&agency_id=1758619317968&level=1",
        "multiround_convo": 2,
        "description": "Q12. Do we lack established benchmarks or \"gold standards\" to validate results?",
        "prompt": lambda problem, outputs: (
            f"Problem statement - {problem}\n\nContext from Current System:\n{outputs.get('current_system','')}\n\n"
            "Q12. How well does solving this problem align with organizational strategy or goals? Score 0–5. Provide justification."
            "Provide detailed answers/explanations grounded in business and functional realities.\n"
            "Act as an evaluator for this question based on the answer you provide.\n"
            "Score the problem statement between 0–5 (0 = no conflicts, 5 = significant conflicts).\n"
            "Do not consider technical aspects or implementation; rate only by the characteristics of the problem.\n"
            "Provide a detailed justification for the score."
        )
    },
    # === HARDNESS / SUMMARY ===
    {
        "name": "hardness_summary",
        "url": "https://eoc.mu-sigma.com/talos-engine/agency/reasoning_api?society_id=1757657318406&agency_id=1758619658634&level=1",
        "multiround_convo": 2,
        "description": "Hardness Level, Summary & Key Takeaways",
        "prompt": lambda problem, outputs: (
            f"Problem statement - {problem}\n\n"
            "Context from all previous analysis:\n"
            f"Current System:\n{outputs.get('current_system','')}\n"
            f"Q1:\n{outputs.get('Q1. What is the frequency and pace of change in the key inputs driving the business?','')}\n"
            f"Q2:\n{outputs.get('Q2. To what extent are these changes cyclical and predictable versus sporadic and unpredictable?','')}\n"
            f"Q3:\n{outputs.get('Q3. How resilient is the current system in absorbing these changes without requiring significant rework or disruption?','')}\n"
            f"Q4:\n{outputs.get('Q4. To what extent do stakeholders share a common understanding of the key terms and concepts?','')}\n"
            f"Q5:\n{outputs.get('Q5. Are there any conflicting definitions or interpretations that could create confusion?','')}\n"
            f"Q6:\n{outputs.get('Q6. Are objectives, priorities, and constraints clearly communicated and well-defined?','')}\n"
            f"Q7:\n{outputs.get('Q7. To what extent are key inputs interdependent?','')}\n"
            f"Q8:\n{outputs.get('Q8. How well are the governing rules, functions, and relationships between inputs understood?','')}\n"
            f"Q9:\n{outputs.get('Q9. Are there any hidden or latent dependencies that could impact outcomes?','')}\n"
            f"Q10:\n{outputs.get('Q10. Are there hidden or latent dependencies that could affect outcomes?','')}\n"
            f"Q11:\n{outputs.get('Q11. Are feedback loops insufficient or missing, limiting our ability to adapt?','')}\n"
            f"Q12:\n{outputs.get('Q12. Do we lack established benchmarks or \"gold standards\" to validate results?','')}\n\n"
            "Provide Hardness Score, Level, Summary & Key Takeaways."
        )
    }
]

# Dimension mapping
DIMENSION_QUESTIONS = {
    "Volatility": ["Q1. What is the frequency and pace of change in the key inputs driving the business?",
                   "Q2. To what extent are these changes cyclical and predictable versus sporadic and unpredictable?",
                   "Q3. How resilient is the current system in absorbing these changes without requiring significant rework or disruption?"],
    "Ambiguity": ["Q4. To what extent do stakeholders share a common understanding of the key terms and concepts?",
                  "Q5. Are there any conflicting definitions or interpretations that could create confusion?",
                  "Q6. Are objectives, priorities, and constraints clearly communicated and well-defined?"],
    "Interconnectedness": ["Q7. To what extent are key inputs interdependent?",
                           "Q8. How well are the governing rules, functions, and relationships between inputs understood?",
                           "Q9. Are there any hidden or latent dependencies that could impact outcomes?"],
    "Uncertainty": ["Q10. Are there hidden or latent dependencies that could affect outcomes?",
                    "Q11. Are feedback loops insufficient or missing, limiting our ability to adapt?",
                    "Q12. Do we lack established benchmarks or \"gold standards\" to validate results?"]
}

# -----------------------------
# Utility Functions
# -----------------------------
def json_to_text(data):
    if data is None: 
        return ""
    if isinstance(data, str): 
        return data
    if isinstance(data, dict):
        for key in ("result", "output", "content", "text"):
            if key in data and data[key]: 
                return json_to_text(data[key])
        if "data" in data: 
            return json_to_text(data["data"])
        return "\n".join(f"{k}: {json_to_text(v)}" for k, v in data.items() if v)
    if isinstance(data, list): 
        return "\n".join(json_to_text(x) for x in data if x)
    return str(data)

def sanitize_text(text):
    """Remove markdown artifacts and clean up text, including Q# Answer Explanation prefixes"""
    if not text:
        return ""
    
    # Remove Q# Answer Explanation prefixes (Q1 Answer Explanation:, Q2 Answer Explanation:, etc.)
    text = re.sub(r'Q\d+\s*Answer\s*Explanation\s*:', '', text, flags=re.IGNORECASE)
    
    # Remove markdown formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # **bold** -> bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # *italic* -> italic
    text = re.sub(r'`(.*?)`', r'\1', text)        # `code` -> code
    text = re.sub(r'#+\s*', '', text)             # # headers -> remove
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)   # remove images
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)  # [link](url) -> link
    
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    
    # Clean up bullet points - convert to proper formatting
    text = re.sub(r'^\s*[-*]\s+', '• ', text, flags=re.MULTILINE)
    
    # Remove any remaining markdown artifacts
    text = re.sub(r'<\/?[^>]+>', '', text)  # Remove any HTML tags
    
    # Clean up specific patterns like "& Key Takeaway:"
    text = re.sub(r'& Key Takeaway:', 'Key Takeaway:', text)
    text = re.sub(r'&amp;', '&', text)
    
    return text.strip()

def call_api(api_cfg, problem_text, outputs, tenant_id=TENANT_ID, auth_token=AUTH_TOKEN, tries=3):
    # Build prompt based on API
    if api_cfg["name"] == "vocabulary":
        prompt = f"{problem_text}\n\nExtract the vocabulary from this problem statement."
    elif api_cfg["name"] == "current_system":
        prompt = f"Problem statement - {problem_text}\n\nContext from vocabulary:\n{outputs.get('vocabulary','')}\n\nDescribe the current system, inputs, outputs, and pain points."
    elif api_cfg["name"] in [f"Q{i}" for i in range(1, 13)]:
        prompt = f"Problem statement - {problem_text}\n\nContext from Current System:\n{outputs.get('current_system','')}\n\n{api_cfg.get('question', '')} Provide detailed analysis, score 0–5, and justification."
    elif api_cfg["name"] == "hardness_summary":
        # Build comprehensive context for hardness summary
        context_parts = []
        if outputs.get('vocabulary'):
            context_parts.append(f"Vocabulary:\n{outputs['vocabulary']}")
        if outputs.get('current_system'):
            context_parts.append(f"Current System Analysis:\n{outputs['current_system']}")
        
        # Add all Q&A responses
        for i in range(1, 13):
            q_key = f"Q{i}"
            if outputs.get(q_key):
                context_parts.append(f"{q_key}:\n{outputs[q_key]}")
        
        context = "\n\n".join(context_parts)
        prompt = f"""Problem statement: {problem_text}

Based on the following comprehensive analysis, provide:
1. Overall Hardness Level (Hard/Moderate/Easy)
2. Overall Difficulty Score (0-5)
3. Individual dimension scores for Volatility, Ambiguity, Interconnectedness, and Uncertainty (0-5 scale)
4. Detailed summary and key takeaways

Analysis Context:
{context}

Please structure your response clearly with the scores and classification."""
    else:
        prompt = problem_text
    
    headers_list = []
    base = HEADERS_BASE.copy()
    if tenant_id:
        headers_list = [
            dict(base, **{"Tenant-ID": tenant_id}), 
            dict(base, **{"X-Tenant-ID": tenant_id})
        ]
    else:
        headers_list = [base]
    
    if auth_token:
        headers_list = [dict(h, **{"Authorization": f"Bearer {auth_token}"}) for h in headers_list]

    last_err = None
    for attempt in range(1, tries + 1):
        for headers in headers_list:
            try:
                resp = requests.post(
                    api_cfg["url"], 
                    headers=headers, 
                    json={"prompt": prompt}, 
                    timeout=60
                )
                if resp.status_code == 200:
                    res = json_to_text(resp.json())
                    # Sanitize the response
                    res = sanitize_text(res)
                    for r in range(1, api_cfg.get("multiround_convo", 1)):
                        resp2 = requests.post(
                            api_cfg["url"], 
                            headers=headers, 
                            json={"prompt": res}, 
                            timeout=60
                        )
                        if resp2.status_code == 200: 
                            res = json_to_text(resp2.json())
                            res = sanitize_text(res)
                    return res
                else:
                    last_err = f"{resp.status_code}-{resp.text}"
            except Exception as e:
                last_err = str(e)
        time.sleep(1 + attempt * 0.5)
    
    return f"API failed after {tries} attempts. Last error: {last_err}"

def extract_score_from_text(text, dimension):
    """Extract dimension score from hardness_summary API output"""
    if not text:
        return 0.0
    
    # Multiple patterns to catch different formats
    patterns = [
        # Pattern 1: **Volatility Score**: 4.2/5
        rf"\*\*{dimension}\s+Score\*\*:\s*(\d+(?:\.\d+)?)\s*\/\s*5",
        # Pattern 2: Volatility: 4.2/5
        rf"{dimension}:\s*(\d+(?:\.\d+)?)\s*\/\s*5",
        # Pattern 3: **Volatility**: 4.2
        rf"\*\*{dimension}\*\*:\s*(\d+(?:\.\d+)?)",
        # Pattern 4: Volatility - 4.2
        rf"{dimension}\s*[-\—]\s*(\d+(?:\.\d+)?)",
        # Pattern 5: Look for scores in tables or lists
        rf"{dimension}.*?(\d+(?:\.\d+)?)\s*(?=\/|$)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            try:
                score = float(match.group(1))
                if 0 <= score <= 5:
                    return score
            except:
                continue
    
    # Fallback: Look for any number between 0-5 near the dimension name
    fallback_pattern = rf"{dimension}.*?(\d+(?:\.\d+)?)"
    matches = re.findall(fallback_pattern, text, re.IGNORECASE | re.MULTILINE)
    for match in matches:
        try:
            num_match = re.search(r"(\d+(?:\.\d+)?)", match)
            if num_match:
                score = float(num_match.group(1))
                if 0 <= score <= 5:
                    return score
        except:
            continue
    
    return 0.0

def extract_overall_score(text):
    """Extract overall difficulty score from hardness_summary API"""
    if not text:
        return 0.0
    
    patterns = [
        # Pattern 1: Overall Difficulty Score: 4.2/5
        r"Overall\s+Difficulty\s+Score[:\s]*(\d+(?:\.\d+)?)\s*\/\s*5",
        # Pattern 2: Overall Score: 4.2
        r"Overall\s+Score[:\s]*(\d+(?:\.\d+)?)",
        # Pattern 3: **Overall**: 4.2
        r"\*\*Overall\*\*[:\s]*(\d+(?:\.\d+)?)",
        # Pattern 4: Hardness Score: 4.2
        r"Hardness\s+Score[:\s]*(\d+(?:\.\d+)?)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            try:
                score = float(match.group(1))
                if 0 <= score <= 5:
                    return score
            except:
                continue
    
    # Calculate from dimension scores if not found directly
    dimensions = ["Volatility", "Ambiguity", "Interconnectedness", "Uncertainty"]
    scores = []
    for dim in dimensions:
        score = extract_score_from_text(text, dim)
        if score > 0:
            scores.append(score)
    
    if len(scores) >= 2:  # Require at least 2 valid scores
        return sum(scores) / len(scores)
    
    return 0.0

def extract_hardness_level(text):
    """Extract hardness level from hardness_summary API"""
    if not text:
        return "Unknown"
    
    text_lower = text.lower()
    
    # Explicit classifications
    if re.search(r"\bhard\b", text_lower) and not re.search(r"\bnot\s+hard\b", text_lower):
        return "Hard"
    elif re.search(r"\bmoderate\b", text_lower):
        return "Moderate"
    elif re.search(r"\beasy\b|\bnot\s+hard\b|\blow\b", text_lower):
        return "Easy"
    
    # Score-based classification
    overall_score = extract_overall_score(text)
    if overall_score >= 3.5:
        return "Hard"
    elif overall_score >= 2.0:
        return "Moderate"
    elif overall_score > 0:
        return "Easy"
    
    return "Unknown"

def extract_current_system_full(text):
    """Extract the full current system description from current_system API"""
    if not text:
        return "No current system information available"
    
    # If the text is already clean and substantial, return it
    if len(text.strip()) > 100:
        return text.strip()
    
    return "Current system analysis not available."

def extract_input(text):
    """Extract Input section from current_system API"""
    if not text:
        return "No input information available"
    
    # Look for input-related content
    patterns = [
        r'input[s]?[:\s]*(.*?)(?=output|pain|system|$)',
        r'Input[s]?[:\s]*(.*?)(?=Output|Pain|System|$)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            content = match.group(1).strip()
            if content and len(content) > 20:
                return content
    
    return "Input analysis not available."

def extract_output(text):
    """Extract Output section from current_system API"""
    if not text:
        return "No output information available"
    
    # Look for output-related content
    patterns = [
        r'output[s]?[:\s]*(.*?)(?=input|pain|system|$)',
        r'Output[s]?[:\s]*(.*?)(?=Input|Pain|System|$)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            content = match.group(1).strip()
            if content and len(content) > 20:
                return content
    
    return "Output analysis not available."

def extract_pain_points(text):
    """Extract Pain Points section from current_system API"""
    if not text:
        return "No pain points information available"
    
    # Look for pain points related content
    patterns = [
        r'pain[s]?[:\s]*(.*?)(?=input|output|system|$)',
        r'Pain[s]?[:\s]*(.*?)(?=Input|Output|System|$)',
        r'challenge[s]?[:\s]*(.*?)(?=input|output|system|$)',
        r'Challenge[s]?[:\s]*(.*?)(?=Input|Output|System|$)',
        r'issue[s]?[:\s]*(.*?)(?=input|output|system|$)',
        r'Issue[s]?[:\s]*(.*?)(?=Input|Output|System|$)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            content = match.group(1).strip()
            if content and len(content) > 20:
                return content
    
    return "Pain points analysis not available."

def extract_summary_and_takeaways(text):
    """Extract Summary from hardness_summary API"""
    if not text:
        return ""
    
    # Clean the text first
    text = sanitize_text(text)
    
    # Look for summary or conclusion
    patterns = [
        r'(?:summary|key takeaway|conclusion)[:\s]*(.*?)(?=hardness|score|overall|$)',
        r'(?:Summary|Key Takeaway|Conclusion)[:\s]*(.*?)(?=Hardness|Score|Overall|$)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            content = match.group(1).strip()
            if content and len(content) > 20:
                return content
    
    # If no specific section found, return first substantial paragraph
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    for para in paragraphs:
        if len(para) > 50 and not any(word in para.lower() for word in ['score', 'rating', 'hardness', 'volatility', 'ambiguity']):
            return para
    
    return "Summary not available."

def extract_main_issue_for_dimension(dimension, hardness_summary_text, qa_outputs):
    """Extract main issue analysis for a specific dimension"""
    if not hardness_summary_text:
        return f"Main issue analysis for {dimension} not available."
    
    # Try to find dimension-specific content
    patterns = [
        rf"{dimension}.*?(?:issue|problem|challenge)[:\s]*(.*?)(?=(?:{dimension}|Volatility|Ambiguity|Interconnectedness|Uncertainty|Overall|\Z))",
        rf"{dimension}.*?:\s*(.*?)(?=\n\n|\Z)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, hardness_summary_text, re.IGNORECASE | re.DOTALL)
        if match:
            content = match.group(1).strip()
            if content and len(content) > 30:
                return content[:400] + "..." if len(content) > 400 else content
    
    # Fallback to first question answer
    dimension_questions = DIMENSION_QUESTIONS.get(dimension, [])
    if dimension_questions and qa_outputs.get(dimension_questions[0]):
        first_answer = qa_outputs[dimension_questions[0]]
        paragraphs = [p.strip() for p in first_answer.split('\n\n') if p.strip()]
        for para in paragraphs:
            if len(para) > 50:
                return para[:400] + "..." if len(para) > 400 else para
    
    return f"Main issue analysis for {dimension} not available."

# -----------------------------
# Session State Initialization
# -----------------------------
def init_session_state():
    defaults = {
        "current_page": "page1",
        "problem_text": "",
        "industry": "Select Industry",
        "account": "Select Account",
        "outputs": {},
        "analysis_complete": False,
        "dimension_scores": {
            "Volatility": 0.0,
            "Ambiguity": 0.0, 
            "Interconnectedness": 0.0,
            "Uncertainty": 0.0
        },
        "hardness_level": None,
        "overall_score": 0.0,
        "summary": "",
        "current_system_full": "",
        "input_text": "",
        "output_text": "",
        "pain_points_text": "",
        "hardness_summary_text": "",
        "main_issues": {
            "Volatility": "",
            "Ambiguity": "",
            "Interconnectedness": "",
            "Uncertainty": ""
        }
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

init_session_state()

# -----------------------------
# PAGE 1: Business Problem Input & Analysis
# -----------------------------
if st.session_state.current_page == "page1":
    st.markdown('<div class="page-title"><h1>Business Problem Level Classifier</h1></div>', unsafe_allow_html=True)
    
    # Industry & Account Selection
    col1, col2 = st.columns(2)
    
    with col1:
        st.session_state.industry = st.selectbox(
            "Select Industry",
            INDUSTRIES,
            index=INDUSTRIES.index(st.session_state.industry) if st.session_state.industry in INDUSTRIES else 0
        )
    
    with col2:
        st.session_state.account = st.selectbox(
            "Select Account",
            ACCOUNTS,
            index=ACCOUNTS.index(st.session_state.account) if st.session_state.account in ACCOUNTS else 0
        )
    
    # Business Problem Description
    st.markdown("### Business Problem Description")
    st.session_state.problem_text = st.text_area(
        "Describe your business problem in detail:",
        value=st.session_state.problem_text,
        height=200,
        placeholder="Enter a detailed description of your business challenge..."
    )
    
    # Analysis Button and Vocabulary Button
    col1, col2 = st.columns([3, 1])
    
    with col1:
        analyze_btn = st.button(
            "Analyze Problem",
            type="primary",
            use_container_width=True,
            disabled=not (st.session_state.problem_text.strip() and 
                         st.session_state.industry != "Select Industry" and 
                         st.session_state.account != "Select Account")
        )
    
    with col2:
        if st.session_state.analysis_complete:
            with st.expander("📚 Vocabulary"):
                vocab_text = st.session_state.outputs.get('vocabulary', 'No vocabulary data available')
                st.write(sanitize_text(vocab_text))
    
    if analyze_btn:
        with st.spinner("Analyzing your business problem..."):
            progress_bar = st.progress(0)
            st.session_state.outputs = {}
            
            # Process all APIs including hardness_summary
            total_apis = len(API_CONFIGS)
            for i, api_config in enumerate(API_CONFIGS):
                progress = (i / total_apis)
                progress_bar.progress(progress)
                
                result = call_api(api_config, st.session_state.problem_text, st.session_state.outputs)
                st.session_state.outputs[api_config['name']] = result
                
                time.sleep(0.5)
            
            progress_bar.progress(1.0)
            
            # Extract data from hardness_summary API
            hardness_summary = st.session_state.outputs.get('hardness_summary', '')
            st.session_state.hardness_summary_text = hardness_summary
            
            # Extract hardness level
            st.session_state.hardness_level = extract_hardness_level(hardness_summary)
            
            # Extract overall score
            st.session_state.overall_score = extract_overall_score(hardness_summary)
            
            # Extract dimension scores from hardness_summary
            for dimension in ["Volatility", "Ambiguity", "Interconnectedness", "Uncertainty"]:
                score = extract_score_from_text(hardness_summary, dimension)
                st.session_state.dimension_scores[dimension] = score
            
            # Extract summary
            st.session_state.summary = extract_summary_and_takeaways(hardness_summary)
            
            # Extract main issues for each dimension
            for dimension in ["Volatility", "Ambiguity", "Interconnectedness", "Uncertainty"]:
                st.session_state.main_issues[dimension] = extract_main_issue_for_dimension(
                    dimension, hardness_summary, st.session_state.outputs
                )
            
            # Extract current system components from current_system API
            current_system_text = st.session_state.outputs.get('current_system', '')
            st.session_state.current_system_full = extract_current_system_full(current_system_text)
            st.session_state.input_text = extract_input(current_system_text)
            st.session_state.output_text = extract_output(current_system_text)
            st.session_state.pain_points_text = extract_pain_points(current_system_text)
            
            st.session_state.analysis_complete = True
            st.success("Analysis complete!")
            st.rerun()
    
    # Display Results if analysis is complete
    if st.session_state.analysis_complete:
        st.markdown("---")
        
        # Hardness Level Section
        col1, col2 = st.columns(2)
        
        with col1:
            hardness = st.session_state.hardness_level
            if hardness == "Hard":
                badge_class = "hardness-badge-hard"
            elif hardness == "Moderate":
                badge_class = "hardness-badge-moderate"
            else:
                badge_class = "hardness-badge-easy"
            
            st.markdown(f'<div class="{badge_class}">{hardness}</div>', unsafe_allow_html=True)
        
        with col2:
            overall = st.session_state.overall_score
            st.markdown(f'''
            <div class="score-badge">
                <div style="font-size: 1.2rem; font-weight: 600; opacity: 0.95; margin-bottom: 0.5rem;">Overall Difficulty Score</div>
                <div style="font-size: 2.5rem; font-weight: 800;">{overall:.2f}/5</div>
            </div>
            ''', unsafe_allow_html=True)
        
        # Dimension Scores - Four NON-CLICKABLE display boxes in 2x2 grid
        st.markdown("---")
        st.markdown("### Dimension Scores")
        
        col1, col2 = st.columns(2)
        dimensions = ["Volatility", "Ambiguity", "Interconnectedness", "Uncertainty"]
        
        for i, dimension in enumerate(dimensions):
            with col1 if i < 2 else col2:
                score = st.session_state.dimension_scores.get(dimension, 0.0)
                # Changed from button to static display box
                st.markdown(f'''
                <div class="dimension-display-box">
                    <div class="dimension-label">{dimension}</div>
                    <div class="dimension-score">{score:.2f}/5</div>
                </div>
                ''', unsafe_allow_html=True)
        
        # Summary & Key Takeaways
        st.markdown("---")
        st.markdown("### Summary & Key Takeaways")
        
        if st.session_state.summary:
            st.markdown(f'<div class="content-text">{st.session_state.summary}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="content-text">{sanitize_text(st.session_state.hardness_summary_text)}</div>', unsafe_allow_html=True)
        
        # Navigation Buttons - Only "In Detail" button
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("In Detail →", key="in_detail_main", use_container_width=True, type="primary"):
                st.session_state.current_page = "page2"
                st.rerun()

# -----------------------------
# PAGE 2: Current System & Pain Points
# -----------------------------
# -----------------------------
# PAGE 2: Current System & Pain Points
# -----------------------------
elif st.session_state.current_page == "page2":
    import re

    def extract_section(text, start_marker, end_marker=None):
        """Extract text between start_marker and end_marker (if given)."""
        pattern = rf"{start_marker}(.*?){end_marker if end_marker else '$'}"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            content = match.group(1).strip()
            # Clean up redundant prefixes
            content = re.sub(r"^The key inputs that feed into.*?:\s*", "", content, flags=re.IGNORECASE)
            content = re.sub(r"^The outputs currently generated.*?:\s*", "", content, flags=re.IGNORECASE)
            content = re.sub(r"^The current system.*?:\s*", "", content, flags=re.IGNORECASE)
            return content.strip()
        return ""

    # Extract sections from current_system_full
    full_text = st.session_state.current_system_full

    current_system_text = extract_section(full_text, r"Current System", r"Inputs")
    input_text = extract_section(full_text, r"Inputs", r"Outputs")
    output_text = extract_section(full_text, r"Outputs", r"Pain Points")
    pain_points_text = extract_section(full_text, r"Pain Points")

    # Save into session state
    st.session_state.current_system_text = current_system_text
    st.session_state.input_text = input_text
    st.session_state.output_text = output_text
    st.session_state.pain_points_text = pain_points_text

    # ---------------- UI Layout ----------------
    st.markdown('<div class="page-title"><h1>Current System & Pain Points</h1></div>', unsafe_allow_html=True)

    # Business Problem
    st.markdown('<div class="problem-display">', unsafe_allow_html=True)
    st.markdown("<h4>Business Problem</h4>", unsafe_allow_html=True)
    st.write(st.session_state.problem_text)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("← Back to Analysis", use_container_width=False):
        st.session_state.current_page = "page1"
        st.rerun()

    st.markdown('<div class="main-content-container">', unsafe_allow_html=True)

    # Current System
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">Current System</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="content-text">{st.session_state.current_system_text}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Inputs & Outputs (side by side)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="content-section">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">Input</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="content-text">{st.session_state.input_text}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="content-section">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">Output</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="content-text">{st.session_state.output_text}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Pain Points
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">Pain Points</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="content-text">{st.session_state.pain_points_text}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Dimension Scores
    st.markdown('<p class="section-title">Dimension Scores - Click to view details</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    dimensions = ["Volatility", "Ambiguity", "Interconnectedness", "Uncertainty"]

    for i, dimension in enumerate(dimensions):
        with col1 if i < 2 else col2:
            score = st.session_state.dimension_scores.get(dimension, 0.0)
            st.markdown(f"""
            <div class="dimension-box">
                <div class="dimension-label">{dimension}</div>
                <div class="dimension-score">{score:.2f}/5</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"View {dimension} Details", key=f"dim_{dimension}", use_container_width=True):
                st.session_state.current_page = f"dimension_{dimension.lower()}"
                st.rerun()

    # Hardness Summary navigation
    st.markdown("---")
    if st.button("View Hardness Summary →", use_container_width=True):
        st.session_state.current_page = "hardness_summary"
        st.rerun()
# -----------------------------
# DIMENSION DETAIL PAGES
# -----------------------------
elif st.session_state.current_page.startswith("dimension_"):
    dimension_name = st.session_state.current_page.replace("dimension_", "").title()
    
    st.markdown(f'<div class="page-title"><h1>{dimension_name} Analysis</h1></div>', unsafe_allow_html=True)
    
    # Display Business Problem
    st.markdown('<div class="problem-display">', unsafe_allow_html=True)
    st.markdown("<h4>Business Problem</h4>", unsafe_allow_html=True)
    st.write(st.session_state.problem_text)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Back button
    if st.button("← Back to System Overview", use_container_width=False):
        st.session_state.current_page = "page2"
        st.rerun()
    
    # Display dimension score
    score = st.session_state.dimension_scores.get(dimension_name, 0.0)
    st.markdown(f"""
    <div class="score-badge" style="margin-bottom: 2rem;">
        <div style="font-size: 1.5rem; font-weight: 600; margin-bottom: 0.5rem;">{dimension_name} Score</div>
        <div style="font-size: 3rem; font-weight: 800;">{score:.2f}/5</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display Q&A for this dimension (with sanitized text removing Q# Answer Explanation prefixes)
    st.markdown("### Detailed Analysis")
    questions = DIMENSION_QUESTIONS.get(dimension_name, [])
    
    for q_name in questions:
        answer_text = st.session_state.outputs.get(q_name, "No analysis available")
        # The sanitize_text function now automatically removes Q# Answer Explanation prefixes
        clean_answer = sanitize_text(answer_text)
        
        st.markdown('<div class="qa-box">', unsafe_allow_html=True)
        st.markdown(f'<div class="qa-question">Q: {q_name}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="qa-answer">{clean_answer}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Navigation buttons based on current dimension
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    if dimension_name == "Volatility":
        with col3:
            if st.button("Next → Ambiguity", use_container_width=True, type="primary"):
                st.session_state.current_page = "dimension_ambiguity"
                st.rerun()
    elif dimension_name == "Ambiguity":
        with col3:
            if st.button("Next → Interconnectedness", use_container_width=True, type="primary"):
                st.session_state.current_page = "dimension_interconnectedness"
                st.rerun()
    elif dimension_name == "Interconnectedness":
        with col3:
            if st.button("Next → Uncertainty", use_container_width=True, type="primary"):
                st.session_state.current_page = "dimension_uncertainty"
                st.rerun()
    elif dimension_name == "Uncertainty":
        # ADDED: "View Hardness Summary" button on Uncertainty page
        with col3:
            if st.button("View Hardness Summary →", use_container_width=True, type="primary"):
                st.session_state.current_page = "hardness_summary"
                st.rerun()

# -----------------------------
# HARDNESS SUMMARY PAGE (UPDATED - Summary only, no extracted scores)
# -----------------------------
elif st.session_state.current_page == "hardness_summary":
    st.markdown('<div class="page-title"><h1>Hardness Summary Analysis</h1></div>', unsafe_allow_html=True)
    
    # Display Business Problem
    st.markdown('<div class="problem-display">', unsafe_allow_html=True)
    st.markdown("<h4>Business Problem</h4>", unsafe_allow_html=True)
    st.write(st.session_state.problem_text)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Back button
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("← Back to Uncertainty Analysis", use_container_width=False):
            st.session_state.current_page = "dimension_uncertainty"
            st.rerun()
    
    # UPDATED: Display only the summary, no extracted scores
    st.markdown('<p class="section-title">Hardness Summary Analysis</p>', unsafe_allow_html=True)
    
    if st.session_state.hardness_summary_text:
        # Use sanitize_text to clean the summary (removes Q# prefixes and other artifacts)
        clean_summary = sanitize_text(st.session_state.hardness_summary_text)
        st.markdown(f'<div class="content-text">{clean_summary}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="content-text">No hardness summary available. Please run the analysis first.</div>', unsafe_allow_html=True)
