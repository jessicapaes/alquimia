import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import os
from pathlib import Path

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

DATA_FILE = "alquimia_data.json"
DEFAULT_RODA_SCORES = {
    'Saúde/Health': 5,
    'Carreira/Career': 5,
    'Finanças/Finances': 5,
    'Relacionamentos/Relationships': 5,
    'Família/Family': 5,
    'Espiritualidade/Spirituality': 5,
    'Diversão/Fun': 5,
    'Crescimento Pessoal/Growth': 5,
    'Ambiente Físico/Home': 5,
    'Criatividade/Creativity': 5
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_data():
    """Load data from JSON file if it exists"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
            return None
    return None

def save_data():
    """Save all session state data to JSON file"""
    try:
        data = {
            "roda_scores": st.session_state.roda_scores,
            "smart_goals": st.session_state.smart_goals,
            "reflections": {
                "conquistas_2025": st.session_state.get("conquistas_2025", ""),
                "desafios_2025": st.session_state.get("desafios_2025", ""),
                "aprendizados_2025": st.session_state.get("aprendizados_2025", ""),
                "gratidao_2025": st.session_state.get("gratidao_2025", ""),
                "feiticeira_presente": st.session_state.get("feiticeira_presente", ""),
                "archetypes_atencao": st.session_state.get("archetypes_atencao", ""),
                "rituais_2026": st.session_state.get("rituais_2026", ""),
                "eva_magia": st.session_state.get("eva_magia", "")
            },
            "vision_intentions": {
                area: st.session_state.get(f"vision_{area}", "")
                for area in [
                    "🌸 EVA - Minha Criação Sagrada",
                    "🌿 Saúde & Bem-Estar",
                    "🔮 Espiritualidade",
                    "🦋 Crescimento Pessoal",
                    "💕 Amor Próprio",
                    "🇮🇹 Italia & Aventuras",
                    "💰 Abundância",
                    "🎨 Criatividade"
                ]
            },
            "archetype_scores": {
                key: st.session_state.get(key, 5)
                for key in st.session_state.keys()
                if key.startswith("arch_")
            },
            "history": st.session_state.get("history", []),
            "last_updated": datetime.now().isoformat()
        }
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar dados: {e}")
        return False

def initialize_session_state():
    """Initialize or load session state from file"""
    data = load_data()
    
    if data:
        # Load saved data
        st.session_state.roda_scores = data.get("roda_scores", DEFAULT_RODA_SCORES)
        st.session_state.smart_goals = data.get("smart_goals", [])
        st.session_state.history = data.get("history", [])
        
        # Load reflections
        reflections = data.get("reflections", {})
        for key, value in reflections.items():
            if key not in st.session_state:
                st.session_state[key] = value
        
        # Load vision intentions
        vision_intentions = data.get("vision_intentions", {})
        for area, value in vision_intentions.items():
            key = f"vision_{area}"
            if key not in st.session_state:
                st.session_state[key] = value
        
        # Load archetype scores
        archetype_scores = data.get("archetype_scores", {})
        for key, value in archetype_scores.items():
            if key not in st.session_state:
                st.session_state[key] = value
    else:
        # Initialize with defaults
        st.session_state.roda_scores = DEFAULT_RODA_SCORES.copy()
        st.session_state.smart_goals = []
        st.session_state.history = []
        
        # Initialize reflection fields
        reflection_keys = [
            "conquistas_2025", "desafios_2025", "aprendizados_2025", "gratidao_2025",
            "feiticeira_presente", "archetypes_atencao", "rituais_2026", "eva_magia"
        ]
        for key in reflection_keys:
            if key not in st.session_state:
                st.session_state[key] = ""

def add_to_history():
    """Add current roda scores to history for progress tracking"""
    if "history" not in st.session_state:
        st.session_state.history = []
    
    entry = {
        "date": datetime.now().isoformat(),
        "roda_scores": st.session_state.roda_scores.copy(),
        "avg_score": sum(st.session_state.roda_scores.values()) / len(st.session_state.roda_scores)
    }
    st.session_state.history.append(entry)
    
    # Keep only last 12 entries (monthly check-ins for a year)
    if len(st.session_state.history) > 12:
        st.session_state.history = st.session_state.history[-12:]

def create_radar_chart(values, categories, name='2025', show_target=False, target_values=None):
    """Create a radar chart with purple gradient theme matching app design"""
    fig = go.Figure()
    
    # Main trace with purple gradient fill
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(102, 126, 234, 0.25)',  # Purple with transparency
        line=dict(
            color='#667eea',  # Purple line
            width=4,
            smoothing=1.3
        ),
        marker=dict(
            size=10,
            color='#764ba2',  # Darker purple for markers
            line=dict(width=2, color='white')
        ),
        name=name,
        hovertemplate='<b>%{theta}</b><br>Score: %{r}/10<extra></extra>'
    ))
    
    if show_target and target_values:
        fig.add_trace(go.Scatterpolar(
            r=target_values,
            theta=categories,
            fill='toself',
            fillcolor='rgba(236, 72, 153, 0.15)',  # Pink for target
            line=dict(
                color='#ec4899',  # Pink line
                width=3,
                dash='dash',
                smoothing=1.3
            ),
            marker=dict(
                size=8,
                color='#ec4899',
                line=dict(width=2, color='white')
            ),
            name='Target 2026',
            hovertemplate='<b>%{theta}</b><br>Target: %{r}/10<extra></extra>'
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                tickmode='linear',
                tick0=0,
                dtick=2,
                tickfont=dict(
                    size=13,
                    color='#64748b',
                    family='Inter'
                ),
                gridcolor='rgba(102, 126, 234, 0.15)',
                gridwidth=1,
                linecolor='rgba(102, 126, 234, 0.3)',
                linewidth=2,
                showline=True,
                layer='below traces'
            ),
            angularaxis=dict(
                tickfont=dict(
                    size=13,
                    color='#334155',
                    family='Inter',
                    weight=600
                ),
                gridcolor='rgba(102, 126, 234, 0.1)',
                gridwidth=1,
                linecolor='rgba(102, 126, 234, 0.2)',
                linewidth=1,
                rotation=90,
                direction='counterclockwise'
            ),
            bgcolor='rgba(255, 255, 255, 0.95)',
            hole=0.1  # Add inner hole for modern look
        ),
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.15,
            xanchor='center',
            x=0.5,
            font=dict(
                size=14,
                color='#334155',
                family='Inter',
                weight=600
            ),
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='rgba(102, 126, 234, 0.2)',
            borderwidth=1
        ),
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent to match app background
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            color='#1a202c',
            family='Inter',
            size=14
        ),
        height=650,
        margin=dict(l=50, r=50, t=50, b=100),
        hovermode='closest',
        hoverlabel=dict(
            bgcolor='rgba(255, 255, 255, 0.95)',
            bordercolor='#667eea',
            font_size=13,
            font_family='Inter',
            font_color='#1a202c'
        )
    )
    
    return fig

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="🔮 ALQUIMIA - Year 7",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS
# ============================================================================

st.markdown("""
<style>
    .main {
        background: #ffffff;
    }
    .stApp {
        background: #ffffff;
    }
    h1 {
        font-family: 'Cinzel', serif;
        color: #667eea;
        text-align: center;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    h2 {
        font-family: 'Cormorant Garamond', serif;
        color: #764ba2;
    }
    h3 {
        color: #667eea;
    }
    /* TABS - Modern Design (Exact Bearable Format) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        padding: 15px;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        width: 100% !important;
        box-sizing: border-box !important;
        margin: 0 0 2rem 0 !important;
        max-width: none !important;
        border-bottom: none !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px !important;
        padding: 15px 30px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        border: none !important;
        border-bottom: none !important;
        background-color: transparent !important;
        color: #334155 !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(102, 126, 234, 0.1) !important;
        transform: translateY(-2px) !important;
        color: #667eea !important;
        border: none !important;
        border-bottom: none !important;
        text-decoration: none !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3) !important;
        border: none !important;
        border-bottom: none !important;
    }
    
    /* Ensure text stays white on selected tab - all child elements */
    .stTabs [aria-selected="true"] * {
        color: white !important;
    }
    
    /* Selected tab on click/active */
    .stTabs [aria-selected="true"]:active,
    .stTabs [aria-selected="true"]:focus,
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: white !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    .stTabs [aria-selected="true"]:active *,
    .stTabs [aria-selected="true"]:focus *,
    .stTabs [data-baseweb="tab"][aria-selected="true"] * {
        color: white !important;
    }
    
    /* Remove tab underline/indicator bar */
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: transparent !important;
        display: none !important;
    }
    
    .stTabs [data-baseweb="tab-border"] {
        background-color: transparent !important;
        display: none !important;
    }
    
    /* Remove any red default underlines on tabs */
    button[data-baseweb="tab"] {
        border: none !important;
        border-bottom: none !important;
        text-decoration: none !important;
    }
    
    button[data-baseweb="tab"]:hover {
        border: none !important;
        border-bottom: none !important;
        text-decoration: none !important;
    }
    
    button[data-baseweb="tab"]:focus {
        border: none !important;
        border-bottom: none !important;
        text-decoration: none !important;
        outline: none !important;
    }
    
    button[data-baseweb="tab"]:active {
        border: none !important;
        border-bottom: none !important;
        text-decoration: none !important;
    }
    /* Tab content area */
    [data-testid="stTabs"] > div:last-child {
        padding-top: 1.5rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2em;
        color: #667eea;
    }
    /* PREMIUM CARDS - Clean White Boxes (Bearable Style) */
    .glass-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 30px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
        position: relative;
        overflow: visible;
    }
    
    .glass-card::before {
        display: none;
    }
    
    .glass-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-color: #cbd5e1;
    }

    .glass-card:hover::before {
        display: none;
    }
    
    /* Section Headers - Gradient Background (From Bearable) */
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 2rem 0 1rem 0;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
    }
    
    .section-header h3 {
        color: white !important;
        margin: 0;
        font-size: 1.4rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    
    .section-header p {
        color: rgba(255,255,255,0.9);
        margin: 0.3rem 0 0 0;
        font-size: 0.9rem;
    }
    
    /* Archetype Card - Updated to match Bearable */
    .archetype-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        padding: 20px;
        border-radius: 20px;
        border-left: 6px solid #667eea;
        margin: 10px 0;
        box-shadow: 0 8px 30px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .archetype-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2);
    }
    
    /* Success/Info Messages - Updated */
    .success-message {
        background: rgba(16, 185, 129, 0.1);
        border-left: 4px solid #10b981;
        padding: 15px 20px;
        border-radius: 12px;
        margin: 10px 0;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.15);
    }
    
    /* Clean section spacing */
    .element-container {
        margin-bottom: 1.5rem;
    }
    
    /* BUTTONS - Modern sleek design (From Bearable) */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        font-size: 0.95rem !important;
        border: 2px solid #e2e8f0 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
        background: white !important;
        color: #334155 !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2) !important;
        border-color: #667eea !important;
        background: #f8f9ff !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Primary buttons - Purple gradient */
    .stButton > button[kind="primary"],
    button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
    }

    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
        background: linear-gradient(135deg, #5568d3 0%, #6a3f91 100%) !important;
    }
    
    /* FORMS - Light Grey Input Fields (Bearable Style) */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input {
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
        padding: 14px 16px !important;
        font-size: 15px !important;
        font-weight: 400 !important;
        transition: all 0.2s ease !important;
        background: #f8f9fa !important;
        color: #1a202c !important;
    }

    .stTextInput > div > div > input:hover,
    .stTextArea > div > div > textarea:hover,
    .stSelectbox > div > div > select:hover,
    .stNumberInput > div > div > input:hover {
        border-color: #cbd5e1 !important;
        background: #f1f5f9 !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        outline: none !important;
        background: #ffffff !important;
    }
    
    /* Input placeholders */
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #9ca3af !important;
        font-weight: 400 !important;
    }

    /* Form Labels */
    .stTextInput > label,
    .stTextArea > label,
    .stSelectbox > label,
    .stNumberInput > label {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #334155 !important;
        margin-bottom: 8px !important;
    }
    /* SLIDERS - FORCE PURPLE COLOR (Override Streamlit Red) - From Bearable App */
    .stSlider {
        padding: 10px 0 !important;
    }

    /* Slider track - FORCE PURPLE with multiple selectors */
    .stSlider > div > div > div > div,
    div[data-testid="stSlider"] > div > div > div > div,
    .stSlider [data-baseweb="slider"] > div:first-child > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        height: 10px !important;
        border-radius: 10px !important;
    }

    /* Slider thumb (handle) - Smaller with gradient fill */
    .stSlider > div > div > div > div > div,
    div[data-testid="stSlider"] > div > div > div > div > div,
    .stSlider [data-baseweb="slider"] [role="slider"],
    .stSlider div[role="slider"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        width: 20px !important;
        height: 20px !important;
        box-shadow: 0 3px 10px rgba(102, 126, 234, 0.4) !important;
        border-radius: 50% !important;
        transition: all 0.2s ease !important;
    }

    .stSlider > div > div > div > div > div:hover,
    div[data-testid="stSlider"] [role="slider"]:hover {
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.6) !important;
    }
    
    /* Override Streamlit's accent-color (this controls slider/checkbox colors) */
    input, select, textarea {
        accent-color: #667eea !important;
    }
    
    /* Force all range inputs to be purple */
    input[type="range"],
    input[type="checkbox"],
    input[type="radio"] {
        accent-color: #667eea !important;
    }
    
    input[type="range"]::-webkit-slider-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        width: 20px !important;
        height: 20px !important;
        border-radius: 50% !important;
        box-shadow: 0 3px 10px rgba(102, 126, 234, 0.4) !important;
        cursor: pointer !important;
    }
    
    input[type="range"]::-webkit-slider-runnable-track {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        height: 10px !important;
        border-radius: 10px !important;
    }
    
    input[type="range"]::-moz-range-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        width: 20px !important;
        height: 20px !important;
        border-radius: 50% !important;
        box-shadow: 0 3px 10px rgba(102, 126, 234, 0.4) !important;
        cursor: pointer !important;
    }
    
    input[type="range"]::-moz-range-track {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        height: 10px !important;
        border-radius: 10px !important;
    }
    
    /* Checkbox - Force purple */
    input[type="checkbox"]:checked {
        accent-color: #667eea !important;
        background-color: #667eea !important;
    }

    /* Show slider value - simple number above handle */
    .stSlider [data-baseweb="slider"] [role="slider"] > div {
        background: none !important;
        background-color: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        color: #667eea !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        padding: 0 !important;
        margin: 0 !important;
        box-shadow: none !important;
        width: auto !important;
        height: auto !important;
    }

    /* Style min/max labels - keep visible */
    .stSlider [data-baseweb="slider"] [data-testid="stTickBarMin"],
    .stSlider [data-baseweb="slider"] [data-testid="stTickBarMax"] {
        font-weight: 600 !important;
        color: #64748b !important;
        font-size: 13px !important;
    }

    /* FIXED: Remove purple dot at end of slider */
    .stSlider > div > div > div::after,
    .stSlider > div > div > div > div::after,
    .stSlider [data-baseweb="slider"]::after {
        display: none !important;
    }

    /* Remove any extra elements at slider ends */
    .stSlider [data-baseweb="slider"] > div:last-child:not([role="slider"]) {
        display: none !important;
    }

    /* FIXED: Ensure only ONE circle on slider handle */
    .stSlider [role="slider"]::before,
    .stSlider [role="slider"]::after {
        display: none !important;
    }

    /* Hide any duplicate slider thumbs */
    .stSlider [data-baseweb="slider"] > div[aria-hidden="true"] {
        display: none !important;
    }
    /* Override any red colors in tabs */
    .stTabs [data-baseweb="tab"][aria-selected="true"],
    .stTabs [data-baseweb="tab"]:focus-visible,
    .stTabs [data-baseweb="tab"]:active {
        color: #667eea !important;
        border-color: #667eea !important;
    }
    /* Remove any red box-shadow or outline */
    .stTabs [data-baseweb="tab"]:focus {
        outline: 2px solid #667eea !important;
        outline-offset: 2px;
    }
    /* EXPANDER - Stylish (From Bearable) */
    .streamlit-expanderHeader {
        border-radius: 12px !important;
        background: rgba(255, 255, 255, 0.9) !important;
        backdrop-filter: blur(10px) !important;
        padding: 18px 24px !important;
        font-weight: 700 !important;
        font-size: 18px !important;
        border: 2px solid #e2e8f0 !important;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #667eea !important;
        background: rgba(102, 126, 234, 0.05) !important;
    }
    
    [data-testid="stExpander"] {
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        margin-bottom: 1rem;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    [data-testid="stExpander"]:hover {
        border-color: #667eea;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.15);
    }
    
    /* Container styling - Apply glass card effect (removed to prevent unwanted white boxes) */
    /* [data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 20px !important;
        padding: 2rem !important;
        box-shadow: 0 8px 30px rgba(0,0,0,0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
    } */
    
    /* Remove white boxes from empty Streamlit containers */
    [data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"]:empty,
    [data-testid="element-container"]:empty {
        display: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Remove background and styling from plotly chart containers */
    [data-testid="stPlotlyChart"] {
        background: transparent !important;
    }
    
    /* Remove white background from containers holding plotly charts */
    div:has([data-testid="stPlotlyChart"]) {
        background: transparent !important;
        padding: 0 !important;
        border: none !important;
        box-shadow: none !important;
        border-radius: 0 !important;
    }
    
    /* Alternative selector for browsers that don't support :has() */
    [data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] > div:first-child:has([data-testid="stPlotlyChart"]) {
        background: transparent !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Metrics styling */
    [data-testid="stMetricValue"] {
        font-size: 48px !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 16px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #64748b !important;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 18px !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# Add JavaScript to force slider colors (runs after CSS)
st.markdown("""
<script>
    // Ultra-aggressive function to change ALL red colors to purple in sliders
    function forcePurpleSliders() {
        const purpleColor = '#667eea';
        const purpleRGB = 'rgb(102, 126, 234)';
        
        // Find all sliders
        const sliders = document.querySelectorAll('[data-baseweb="slider"], .stSlider, [data-testid="stSlider"]');
        
        sliders.forEach(slider => {
            // Get ALL elements inside slider
            const allInside = slider.querySelectorAll('*');
            
            allInside.forEach(el => {
                // Check computed style
                const computed = window.getComputedStyle(el);
                const bgColor = computed.backgroundColor;
                const bgImage = computed.backgroundImage;
                
                // Check if it's any shade of red
                const isRed = bgColor && (
                    bgColor.includes('rgb(255') || 
                    bgColor.includes('rgb(239') || 
                    bgColor.includes('rgb(244') ||
                    bgColor.includes('rgb(220') ||
                    bgColor.includes('rgb(211') ||
                    bgColor.includes('rgb(248') ||
                    bgColor.includes('rgb(254')
                );
                
                // Force change to purple if red
                if (isRed) {
                    el.style.setProperty('background-color', purpleColor, 'important');
                    el.style.setProperty('background', purpleColor, 'important');
                }
                
                // Check inline style attribute
                const inlineStyle = el.getAttribute('style');
                if (inlineStyle) {
                    // Check for red RGB values in inline style
                    const redPatterns = [
                        /rgb\(255,\s*\d+,\s*\d+\)/g,
                        /rgb\(239,\s*\d+,\s*\d+\)/g,
                        /rgb\(244,\s*\d+,\s*\d+\)/g,
                        /rgb\(220,\s*\d+,\s*\d+\)/g,
                        /#ff[0-9a-f]{4}/gi,
                        /#f[34][0-9a-f]{4}/gi
                    ];
                    
                    let newStyle = inlineStyle;
                    redPatterns.forEach(pattern => {
                        newStyle = newStyle.replace(pattern, purpleColor);
                    });
                    
                    if (newStyle !== inlineStyle) {
                        el.setAttribute('style', newStyle);
                        el.style.setProperty('background-color', purpleColor, 'important');
                    }
                }
                
                // Check background-image for gradients with red
                if (bgImage && (bgImage.includes('rgb(255') || bgImage.includes('rgb(239') || bgImage.includes('rgb(244'))) {
                    el.style.setProperty('background-image', `linear-gradient(to right, ${purpleColor}, ${purpleColor})`, 'important');
                }
            });
        });
        
        // Also inject a global style rule for slider tracks (more targeted)
        if (!document.getElementById('slider-purple-override')) {
            const style = document.createElement('style');
            style.id = 'slider-purple-override';
            style.textContent = `
                /* Target only elements with red backgrounds inside sliders */
                [data-baseweb="slider"] div[style*="rgb(255"],
                [data-baseweb="slider"] div[style*="rgb(239"],
                [data-baseweb="slider"] div[style*="rgb(244"],
                [data-baseweb="slider"] div[style*="#ff"],
                [data-baseweb="slider"] div[style*="#f3"],
                [data-baseweb="slider"] div[style*="#f4"] {
                    background-color: ${purpleColor} !important;
                    background: ${purpleColor} !important;
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    // Run immediately and repeatedly
    forcePurpleSliders();
    
    // Run on various events
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', forcePurpleSliders);
    }
    
    // Run after delays
    [100, 300, 500, 1000, 2000, 3000].forEach(delay => {
        setTimeout(forcePurpleSliders, delay);
    });
    
    // Continuous monitoring
    const observer = new MutationObserver(() => {
        forcePurpleSliders();
    });
    observer.observe(document.body, { 
        childList: true, 
        subtree: true,
        attributes: true,
        attributeFilter: ['style']
    });
    
    // Also run on any slider interaction
    document.addEventListener('mousedown', () => setTimeout(forcePurpleSliders, 10));
    document.addEventListener('mouseup', () => setTimeout(forcePurpleSliders, 10));
    document.addEventListener('input', () => setTimeout(forcePurpleSliders, 10));
</script>
""", unsafe_allow_html=True)

# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================

initialize_session_state()

# ============================================================================
# HEADER
# ============================================================================

st.title("🔮 ALQUIMIA ✨")
st.markdown("### Transformando 2025 em 2026 | The Sorceress Year")

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("### 👤 Informação Pessoal")
    st.markdown("""
    **Nome:** Jessica  
    **Nascimento:** 05 Novembro 1989, 16:40  
    **Local:** Brasília, Brasil  
    
    **☀️ Sol:** Escorpião ♏  
    **🌙 Lua:** Câncer ♋  
    **⬆️ Ascendente:** Áries ♈  
    
    ---
    
    **✨ Ano Pessoal 2025-2026:** 7  
    (05/11/2025 → 04/11/2026)
    
    **🔮 Arquétipo Principal:** Sorceress/Feiticeira  
    **🪐 Tema Astrológico:** Retorno de Saturno (Integração)
    
    ---
    
    **Período:** Novembro 5, 2025 - Novembro 4, 2026  
    **Energia:** Espiritualidade • Introspecção • Sabedoria Interior
    """)
    
    st.markdown("---")
    st.markdown("### 📅 Hoje")
    st.markdown(f"**{datetime.now().strftime('%d de %B, %Y')}**")
    
    st.markdown("---")
    st.markdown("### 💾 Gerenciamento de Dados")
    
    if st.button("💾 Salvar Dados", use_container_width=True):
        if save_data():
            st.success("✅ Dados salvos com sucesso!")
        else:
            st.error("❌ Erro ao salvar dados")
    
    if st.button("🔄 Recarregar Dados", use_container_width=True):
        initialize_session_state()
        st.success("✅ Dados recarregados!")
        st.rerun()
    
    if os.path.exists(DATA_FILE):
        file_size = os.path.getsize(DATA_FILE) / 1024  # KB
        st.caption(f"📁 Arquivo: {DATA_FILE} ({file_size:.1f} KB)")
        mod_time = datetime.fromtimestamp(os.path.getmtime(DATA_FILE))
        st.caption(f"🕒 Última atualização: {mod_time.strftime('%d/%m/%Y %H:%M')}")

# ============================================================================
# MAIN TABS
# ============================================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🎯 Roda da Vida 2025", 
    "🔮 Arquétipos", 
    "🌟 Vision Board 2026",
    "📋 SMART Goals 2026",
    "📊 Dashboard",
    "📈 Progresso"
])

# ============================================================================
# TAB 1: RODA DA VIDA 2025
# ============================================================================

with tab1:
    st.markdown("""
    <div class="section-header">
        <h2 style="color: white; margin: 0; font-size: 2rem; font-weight: 800; letter-spacing: -0.5px;">
            🎯 Roda da Vida 2025
        </h2>
        <p style="color: rgba(255,255,255,0.95); margin: 0.5rem 0 0 0; font-size: 1rem;">
            Reflita sobre 2025 que está terminando. Avalie cada área de 0-10
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: rgba(102, 126, 234, 0.05); padding: 1rem 1.5rem; border-radius: 12px; margin: 1.5rem 0;">
        <p style="margin: 0; color: #334155; font-size: 0.95rem; line-height: 1.8;">
            <strong>0-3:</strong> Precisa atenção urgente • 
            <strong>4-6:</strong> Área em desenvolvimento • 
            <strong>7-8:</strong> Indo bem • 
            <strong>9-10:</strong> Excelente!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Roda da Vida Chart at the top (full width)
    st.markdown("""
    <div class="section-header" style="margin: 0 0 0.5rem 0;">
        <h3 style="color: white; margin: 0; font-size: 1.4rem; font-weight: 700;">
            🎨 Sua Roda da Vida
        </h3>
    </div>
    <div style="background: transparent; padding: 0; margin: 0; border: none; box-shadow: none;">
    """, unsafe_allow_html=True)
    
    categories = list(st.session_state.roda_scores.keys())
    values = list(st.session_state.roda_scores.values())
    
    fig = create_radar_chart(values, categories)
    st.plotly_chart(fig, use_container_width=True, config={
        'displayModeBar': False,
        'staticPlot': False
    })
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Metrics row below chart - wrapped in white box with minimal padding
    st.markdown('<div class="glass-card" style="padding: 20px; margin-bottom: 1.5rem;">', unsafe_allow_html=True)
    
    col_metric1, col_metric2, col_metric3 = st.columns(3)
    
    with col_metric1:
        avg_score = sum(values) / len(values)
        st.metric("Pontuação Média", f"{avg_score:.1f}/10")
    
    with col_metric2:
        max_area = max(st.session_state.roda_scores.items(), key=lambda x: x[1])
        st.metric("Área Mais Forte", max_area[0].split('/')[0])
    
    with col_metric3:
        min_area = min(st.session_state.roda_scores.items(), key=lambda x: x[1])
        st.metric("Área para Crescer", min_area[0].split('/')[0])
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Progress indicator
    if avg_score < 5:
        st.warning("💡 Há espaço para crescimento em várias áreas!")
    elif avg_score < 7:
        st.info("✨ Você está no caminho certo!")
    else:
        st.success("🌟 Excelente! Você está prosperando!")
    
    st.markdown("---")
    
    # Sliders below in two columns - wrapped in white box
    st.markdown("""
    <div class="section-header" style="margin: 0 0 1.5rem 0;">
        <h3 style="color: white; margin: 0; font-size: 1.4rem; font-weight: 700;">
            📊 Avalie cada área
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="glass-card" style="padding: 25px; margin-bottom: 2rem;">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    # Split areas into two columns
    areas_list = list(st.session_state.roda_scores.keys())
    mid_point = len(areas_list) // 2
    
    with col1:
        for area in areas_list[:mid_point]:
            st.session_state.roda_scores[area] = st.slider(
                area,
                min_value=0,
                max_value=10,
                value=st.session_state.roda_scores[area],
                key=f"slider_{area}"
            )
    
    with col2:
        for area in areas_list[mid_point:]:
            st.session_state.roda_scores[area] = st.slider(
                area,
                min_value=0,
                max_value=10,
                value=st.session_state.roda_scores[area],
                key=f"slider_{area}"
            )
    
    # Save button centered
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button("💾 Salvar Avaliação", use_container_width=True, type="primary"):
            if save_data():
                st.success("✅ Avaliação salva!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Reflection questions - wrapped in white box
    st.markdown("---")
    st.markdown("""
    <div class="section-header">
        <h3 style="color: white; margin: 0; font-size: 1.4rem; font-weight: 700;">
            💭 Perguntas de Reflexão 2025
        </h3>
        <p style="color: rgba(255,255,255,0.9); margin: 0.3rem 0 0 0; font-size: 0.9rem;">
            Reflita sobre suas experiências e aprendizados
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="glass-card" style="padding: 25px; margin-bottom: 2rem;">', unsafe_allow_html=True)
    
    reflection_col1, reflection_col2 = st.columns(2)
    
    with reflection_col1:
        st.text_area(
            "🌟 Quais foram suas maiores conquistas em 2025?",
            value=st.session_state.get("conquistas_2025", ""),
            height=150,
            key="conquistas_2025"
        )
        st.text_area(
            "💪 Que desafios você superou?",
            value=st.session_state.get("desafios_2025", ""),
            height=150,
            key="desafios_2025"
        )
    
    with reflection_col2:
        st.text_area(
            "📚 O que você aprendeu sobre si mesma?",
            value=st.session_state.get("aprendizados_2025", ""),
            height=150,
            key="aprendizados_2025"
        )
        st.text_area(
            "🙏 Pelo que você é grata em 2025?",
            value=st.session_state.get("gratidao_2025", ""),
            height=150,
            key="gratidao_2025"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# TAB 2: ARQUÉTIPOS
# ============================================================================

with tab2:
    st.markdown("""
    <div class="section-header">
        <h2 style="color: white; margin: 0; font-size: 2rem; font-weight: 800; letter-spacing: -0.5px;">
            🔮 Roda dos Arquétipos Femininos
        </h2>
        <p style="color: rgba(255,255,255,0.95); margin: 0.5rem 0 0 0; font-size: 1rem;">
            Explore os arquétipos que habitam em você
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="glass-card" style="margin: 2rem 0;">
        <h3 style="color: #1a202c; margin: 0 0 15px 0; font-size: 1.5rem; font-weight: 800;">
            A Feiticeira/Sorceress - Seu Arquétipo Principal 2025-2026
        </h3>
        <p style="color: #334155; margin: 0 0 15px 0; font-size: 1rem; line-height: 1.8;">
            A Feiticeira é a alquimista da própria vida, transformando dor em sabedoria, 
            escuridão em luz. Ela conhece as ervas, os ciclos lunares, o timing sagrado. 
            Ela confia na intuição acima de tudo e trabalha com forças invisíveis para 
            manifestar seus desejos.
        </p>
        <div style="background: rgba(102, 126, 234, 0.1); padding: 12px; border-radius: 8px; border-left: 4px solid #667eea;">
            <p style="margin: 0; color: #334155; font-size: 0.95rem; font-weight: 600;">
                <strong>Keywords:</strong> Magic • Transformation • Intuition • Alchemy • Power • Sovereignty • Mystery • Healing
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🌟 Arquétipos Principais")
        
        archetypes = {
            "🔮 Sorceress/Feiticeira": "Magia, transformação, alquimia, poder",
            "🌸 Maiden/Donzela": "Novos começos, curiosidade, inocência",
            "💕 Lover/Amante": "Paixão, prazer, conexão, auto-amor",
            "🤱 Mother/Mãe": "Nutrição, criação, cuidado",
            "👑 Queen/Rainha": "Soberania, liderança, autoridade",
            "🐺 Wild Woman/Selvagem": "Instinto, liberdade, autenticidade",
            "⚔️ Warrior/Guerreira": "Coragem, ação, proteção",
            "🦉 Wise Woman/Sábia": "Sabedoria, finais, liberação",
            "🌙 Mystic/Mística": "Espiritualidade, mundo interior"
        }
        
        archetype_scores = {}
        for archetype, desc in archetypes.items():
            with st.expander(archetype):
                st.write(desc)
                key = f"arch_{archetype}"
                current_value = st.session_state.get(key, 5)
                st.slider(
                    "Quão presente está este arquétipo em sua vida agora?",
                    0, 10, current_value,
                    key=key
                )
                archetype_scores[archetype] = st.session_state[key]
        
        # Archetype visualization
        if archetype_scores:
            st.markdown("#### 📊 Visualização dos Arquétipos")
            # Convert to lists to avoid pyarrow issues
            archetypes_list = list(archetype_scores.keys())
            presenca_list = [float(v) for v in archetype_scores.values()]
            
            df_arch = pd.DataFrame({
                'Arquétipo': archetypes_list,
                'Presença': presenca_list
            })
            
            # Use go.Figure instead of px.bar to avoid pyarrow dependency
            fig_arch = go.Figure()
            
            # Create horizontal bar chart with purple gradient
            fig_arch.add_trace(go.Bar(
                x=presenca_list,
                y=archetypes_list,
                orientation='h',
                marker=dict(
                    color=presenca_list,
                    colorscale='Viridis',
                    cmin=0,
                    cmax=10,
                    line=dict(color='white', width=1)
                ),
                text=[f'{v:.1f}' for v in presenca_list],
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Presença: %{x}/10<extra></extra>'
            ))
            
            fig_arch.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(
                    color='#1a202c',
                    family='Inter',
                    size=14
                ),
                height=400,
                xaxis=dict(
                    title='Presença',
                    range=[0, 10],
                    gridcolor='rgba(102, 126, 234, 0.1)',
                    linecolor='rgba(102, 126, 234, 0.3)'
                ),
                yaxis=dict(
                    title='',
                    gridcolor='rgba(102, 126, 234, 0.1)',
                    linecolor='rgba(102, 126, 234, 0.3)'
                ),
                margin=dict(l=150, r=50, t=20, b=50)
            )
            st.plotly_chart(fig_arch, use_container_width=True)
    
    with col2:
        st.markdown("#### 💭 Reflexões sobre Arquétipos")
        
        st.text_area(
            "Como a Feiticeira já está presente na sua vida?",
            value=st.session_state.get("feiticeira_presente", ""),
            height=100,
            key="feiticeira_presente"
        )
        
        st.text_area(
            "Quais arquétipos precisam de mais atenção?",
            value=st.session_state.get("archetypes_atencao", ""),
            height=100,
            key="archetypes_atencao"
        )
        
        st.text_area(
            "Que rituais você quer criar em 2026 para honrar seu poder de Feiticeira?",
            value=st.session_state.get("rituais_2026", ""),
            height=100,
            key="rituais_2026"
        )
        
        st.text_area(
            "Como Eva é uma expressão do seu poder mágico e transformador?",
            value=st.session_state.get("eva_magia", ""),
            height=100,
            key="eva_magia"
        )

# ============================================================================
# TAB 3: VISION BOARD 2026
# ============================================================================

with tab3:
    st.markdown("""
    <div class="section-header">
        <h2 style="color: white; margin: 0; font-size: 2rem; font-weight: 800; letter-spacing: -0.5px;">
            🌟 Vision Board 2026
        </h2>
        <p style="color: rgba(255,255,255,0.95); margin: 0.5rem 0 0 0; font-size: 1rem;">
            Visualize e manifeste seus desejos para o próximo ano
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="glass-card" style="margin: 2rem 0;">
        <h3 style="color: #1a202c; margin: 0 0 15px 0; font-size: 1.5rem; font-weight: 800;">
            Ano Pessoal 7 (Nov 2025 - Nov 2026)
        </h3>
        <p style="color: #334155; margin: 0 0 10px 0; font-size: 1rem; line-height: 1.8;">
            <strong>Tema:</strong> Espiritualidade • Sabedoria Interior • Mysticism • Introspecção
        </p>
        <p style="color: #334155; margin: 0; font-size: 1rem; line-height: 1.8;">
            <strong>Transição em Novembro 2026:</strong> Ano Pessoal 8 (Poder • Abundância • Manifestação)
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    vision_areas = {
        "🌸 EVA - Minha Criação Sagrada": {
            "keywords": ["AI Health Tech", "Women's Wellness", "Brazilian Market", "Holistic Care"],
            "affirmation": "Eu estou criando Eva com a sabedoria da Mãe e a magia da Feiticeira."
        },
        "🌿 Saúde & Bem-Estar": {
            "keywords": ["Pain Management", "Holistic Healing", "Gentle Movement", "Self-Care"],
            "affirmation": "Eu honro a sabedoria do meu corpo e confio no processo de cura."
        },
        "🔮 Espiritualidade": {
            "keywords": ["Rituais", "Moon Work", "Intuição", "Astrologia"],
            "affirmation": "Eu confio na minha intuição e na magia que flui através de mim."
        },
        "🦋 Crescimento Pessoal": {
            "keywords": ["Saturn Return", "Autenticidade", "Boundaries", "Self-Discovery"],
            "affirmation": "Eu abraço minha transformação e entro no meu poder autêntico."
        },
        "💕 Amor Próprio": {
            "keywords": ["Cellibatical Year", "Self-Love", "Clareza", "Healing Patterns"],
            "affirmation": "Eu sou completa e inteira dentro de mim mesma."
        },
        "🇮🇹 Italia & Aventuras": {
            "keywords": ["Italian Language", "Cultural Immersion", "Travel", "Adventure"],
            "affirmation": "Eu abraço a beleza e magia de viver na Itália."
        },
        "💰 Abundância": {
            "keywords": ["Financial Growth", "Eva Success", "Smart Investments", "Prosperity"],
            "affirmation": "Dinheiro flui para mim facilmente enquanto crio valor para outros."
        },
        "🎨 Criatividade": {
            "keywords": ["AI Learning", "Tech Skills", "Innovation", "Problem-Solving"],
            "affirmation": "Eu confio no meu gênio criativo e capacidade de aprender qualquer coisa."
        }
    }
    
    cols = st.columns(2)
    
    for idx, (area, details) in enumerate(vision_areas.items()):
        with cols[idx % 2]:
            st.markdown(f"""
            <div class="glass-card">
                <h3 style="color: #1a202c; margin: 0 0 15px 0; font-size: 1.3rem; font-weight: 800;">{area}</h3>
                <p style="color: #64748b; margin: 0 0 15px 0; font-size: 0.95rem; font-weight: 600;">
                    <strong>Keywords:</strong> {', '.join(details['keywords'])}
                </p>
                <div style="background: rgba(102, 126, 234, 0.1); padding: 15px; border-radius: 10px; border-left: 4px solid #667eea; margin-bottom: 15px;">
                    <p style="margin: 0; color: #334155; font-size: 0.95rem; font-style: italic;">
                        💭 {details['affirmation']}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            key = f"vision_{area}"
            current_value = st.session_state.get(key, "")
            st.text_area(
                "Suas intenções para esta área:",
                value=current_value,
                height=100,
                key=key
            )
            
            st.markdown("---")

# ============================================================================
# TAB 4: SMART GOALS 2026
# ============================================================================

with tab4:
    st.markdown("""
    <div class="section-header">
        <h2 style="color: white; margin: 0; font-size: 2rem; font-weight: 800; letter-spacing: -0.5px;">
            📋 SMART Goals 2026
        </h2>
        <p style="color: rgba(255,255,255,0.95); margin: 0.5rem 0 0 0; font-size: 1rem;">
            Crie metas específicas, mensuráveis e alcançáveis
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: rgba(102, 126, 234, 0.05); padding: 1rem 1.5rem; border-radius: 12px; margin: 1.5rem 0;">
        <p style="margin: 0; color: #334155; font-size: 0.95rem; line-height: 1.8;">
            <strong>S</strong>pecific • <strong>M</strong>easurable • <strong>A</strong>chievable • <strong>R</strong>elevant • <strong>T</strong>ime-bound
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add new goal
    with st.expander("➕ Adicionar Nova Meta SMART", expanded=False):
        with st.form("new_goal_form"):
            goal_area = st.selectbox(
                "Área da Vida",
                list(st.session_state.roda_scores.keys())
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                specific = st.text_area("📍 Specific - O que exatamente você quer alcançar?")
                measurable = st.text_area("📊 Measurable - Como você vai medir o progresso?")
                achievable = st.text_area("✅ Achievable - É realista? Você tem recursos?")
            
            with col2:
                relevant = st.text_area("🎯 Relevant - Por que isso é importante para você?")
                time_bound = st.text_area("⏰ Time-bound - Qual o prazo?")
            
            archetype = st.selectbox(
                "🔮 Arquétipo que apoia esta meta",
                ["Sorceress", "Maiden", "Lover", "Mother", "Queen", "Wild Woman", "Warrior", "Wise Woman", "Mystic"]
            )
            
            priority = st.select_slider(
                "⭐ Prioridade",
                options=["Baixa", "Média", "Alta", "Crítica"],
                value="Média"
            )
            
            submit_goal = st.form_submit_button("Adicionar Meta")
            
            if submit_goal and specific:
                new_goal = {
                    "area": goal_area,
                    "specific": specific,
                    "measurable": measurable,
                    "achievable": achievable,
                    "relevant": relevant,
                    "time_bound": time_bound,
                    "archetype": archetype,
                    "priority": priority,
                    "completed": False,
                    "created_date": datetime.now().isoformat()
                }
                st.session_state.smart_goals.append(new_goal)
                save_data()
                st.success("✨ Meta adicionada com sucesso!")
                st.rerun()
    
    # Display existing goals
    if st.session_state.smart_goals:
        st.markdown("### 🎯 Suas Metas 2026")
        
        # Filter options
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        with filter_col1:
            filter_area = st.selectbox("Filtrar por área", ["Todas"] + list(st.session_state.roda_scores.keys()))
        with filter_col2:
            filter_status = st.selectbox("Filtrar por status", ["Todas", "Completadas", "Pendentes"])
        with filter_col3:
            filter_priority = st.selectbox("Filtrar por prioridade", ["Todas", "Crítica", "Alta", "Média", "Baixa"])
        
        filtered_goals = st.session_state.smart_goals.copy()
        
        if filter_area != "Todas":
            filtered_goals = [g for g in filtered_goals if g['area'] == filter_area]
        if filter_status == "Completadas":
            filtered_goals = [g for g in filtered_goals if g.get('completed', False)]
        elif filter_status == "Pendentes":
            filtered_goals = [g for g in filtered_goals if not g.get('completed', False)]
        if filter_priority != "Todas":
            filtered_goals = [g for g in filtered_goals if g.get('priority', 'Média') == filter_priority]
        
        for idx, goal in enumerate(filtered_goals):
            # Find original index
            original_idx = st.session_state.smart_goals.index(goal)
            
            status_icon = "✅" if goal.get('completed', False) else "⏳"
            priority_icon = {"Crítica": "🔴", "Alta": "🟠", "Média": "🟡", "Baixa": "🟢"}.get(goal.get('priority', 'Média'), "🟡")
            
            with st.expander(f"{status_icon} {priority_icon} {goal['area']} - {goal['specific'][:50]}..."):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**📍 Específico:** {goal['specific']}")
                    st.markdown(f"**📊 Mensurável:** {goal['measurable']}")
                    st.markdown(f"**✅ Alcançável:** {goal['achievable']}")
                    st.markdown(f"**🎯 Relevante:** {goal['relevant']}")
                    st.markdown(f"**⏰ Prazo:** {goal['time_bound']}")
                    st.markdown(f"**🔮 Arquétipo:** {goal['archetype']}")
                    st.markdown(f"**⭐ Prioridade:** {goal.get('priority', 'Média')}")
                    if 'created_date' in goal:
                        created = datetime.fromisoformat(goal['created_date'])
                        st.caption(f"📅 Criada em: {created.strftime('%d/%m/%Y')}")
                
                with col2:
                    completed = st.checkbox(
                        "Completada",
                        value=goal.get('completed', False),
                        key=f"goal_complete_{original_idx}"
                    )
                    st.session_state.smart_goals[original_idx]['completed'] = completed
                    
                    if completed != goal.get('completed', False):
                        save_data()
                    
                    if st.button("🗑️ Deletar", key=f"delete_{original_idx}"):
                        st.session_state.smart_goals.pop(original_idx)
                        save_data()
                        st.rerun()
    else:
        st.info("Nenhuma meta adicionada ainda. Use o formulário acima para criar sua primeira meta SMART!")

# ============================================================================
# TAB 5: DASHBOARD
# ============================================================================

with tab5:
    st.markdown("""
    <div class="section-header">
        <h2 style="color: white; margin: 0; font-size: 2rem; font-weight: 800; letter-spacing: -0.5px;">
            📊 Dashboard Completo
        </h2>
        <p style="color: rgba(255,255,255,0.95); margin: 0.5rem 0 0 0; font-size: 1rem;">
            Visão geral do seu progresso e realizações
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_roda = sum(st.session_state.roda_scores.values()) / len(st.session_state.roda_scores)
        st.metric("Roda da Vida Média", f"{avg_roda:.1f}/10")
    
    with col2:
        total_goals = len(st.session_state.smart_goals)
        st.metric("Total de Metas", total_goals)
    
    with col3:
        completed_goals = sum(1 for g in st.session_state.smart_goals if g.get('completed', False))
        st.metric("Metas Completadas", completed_goals)
    
    with col4:
        completion_rate = (completed_goals / total_goals * 100) if total_goals > 0 else 0
        st.metric("Taxa de Conclusão", f"{completion_rate:.0f}%")
    
    st.markdown("---")
    
    # Visual comparisons
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Distribuição da Roda da Vida")
        
        # Convert to lists to avoid pyarrow issues
        areas_list = list(st.session_state.roda_scores.keys())
        scores_list = [float(v) for v in st.session_state.roda_scores.values()]
        
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=scores_list,
            y=areas_list,
            orientation='h',
            marker=dict(
                color=scores_list,
                colorscale='Viridis',
                cmin=0,
                cmax=10,
                line=dict(color='white', width=1)
            ),
            text=[f'{v:.1f}' for v in scores_list],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Pontuação: %{x}/10<extra></extra>'
        ))
        
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(
                color='#1a202c',
                family='Inter',
                size=14
            ),
            height=500,
            xaxis=dict(
                title='Pontuação',
                range=[0, 10],
                gridcolor='rgba(102, 126, 234, 0.1)',
                linecolor='rgba(102, 126, 234, 0.3)'
            ),
            yaxis=dict(
                title='',
                gridcolor='rgba(102, 126, 234, 0.1)',
                linecolor='rgba(102, 126, 234, 0.3)'
            ),
            margin=dict(l=150, r=50, t=20, b=50)
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Metas por Área")
        
        if st.session_state.smart_goals:
            goals_by_area = {}
            for goal in st.session_state.smart_goals:
                area = goal['area']
                if area not in goals_by_area:
                    goals_by_area[area] = {'total': 0, 'completed': 0}
                goals_by_area[area]['total'] += 1
                if goal.get('completed', False):
                    goals_by_area[area]['completed'] += 1
            
            # Convert to lists to avoid pyarrow issues
            areas_list = list(goals_by_area.keys())
            totals_list = [v['total'] for v in goals_by_area.values()]
            
            # Purple gradient colors for pie chart
            colors = ['#667eea', '#764ba2', '#8b5cf6', '#a78bfa', '#c4b5fd', '#ddd6fe', '#ede9fe']
            
            fig_pie = go.Figure()
            fig_pie.add_trace(go.Pie(
                labels=areas_list,
                values=totals_list,
                marker=dict(
                    colors=colors[:len(areas_list)],
                    line=dict(color='white', width=2)
                ),
                textinfo='label+percent',
                hovertemplate='<b>%{label}</b><br>Total: %{value} metas<br>Percentual: %{percent}<extra></extra>'
            ))
            
            fig_pie.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(
                    color='#1a202c',
                    family='Inter',
                    size=14
                ),
                height=500,
                showlegend=True,
                legend=dict(
                    font=dict(size=12),
                    orientation='v',
                    yanchor='middle',
                    y=0.5,
                    xanchor='left',
                    x=1.1
                )
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Adicione metas na aba SMART Goals para ver a distribuição")
    
    # Goals by priority
    if st.session_state.smart_goals:
        st.markdown("---")
        st.subheader("⭐ Metas por Prioridade")
        
        priority_counts = {}
        for goal in st.session_state.smart_goals:
            priority = goal.get('priority', 'Média')
            if priority not in priority_counts:
                priority_counts[priority] = {'total': 0, 'completed': 0}
            priority_counts[priority]['total'] += 1
            if goal.get('completed', False):
                priority_counts[priority]['completed'] += 1
        
        # Convert to lists to avoid pyarrow issues
        priorities_list = list(priority_counts.keys())
        totals_list = [v['total'] for v in priority_counts.values()]
        completed_list = [v['completed'] for v in priority_counts.values()]
        
        fig_priority = go.Figure()
        fig_priority.add_trace(go.Bar(
            name='Total',
            x=priorities_list,
            y=totals_list,
            marker=dict(
                color='rgba(102, 126, 234, 0.6)',
                line=dict(color='#667eea', width=1)
            ),
            hovertemplate='<b>%{x}</b><br>Total: %{y} metas<extra></extra>'
        ))
        fig_priority.add_trace(go.Bar(
            name='Completadas',
            x=priorities_list,
            y=completed_list,
            marker=dict(
                color='rgba(102, 126, 234, 1)',
                line=dict(color='#764ba2', width=1)
            ),
            hovertemplate='<b>%{x}</b><br>Completadas: %{y} metas<extra></extra>'
        ))
        
        fig_priority.update_layout(
            barmode='group',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(
                color='#1a202c',
                family='Inter',
                size=14
            ),
            height=400,
            xaxis=dict(
                title='Prioridade',
                gridcolor='rgba(102, 126, 234, 0.1)',
                linecolor='rgba(102, 126, 234, 0.3)'
            ),
            yaxis=dict(
                title='Número de Metas',
                gridcolor='rgba(102, 126, 234, 0.1)',
                linecolor='rgba(102, 126, 234, 0.3)'
            ),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            ),
            margin=dict(l=50, r=50, t=50, b=50)
        )
        st.plotly_chart(fig_priority, use_container_width=True)
    
    # Export section
    st.markdown("---")
    st.subheader("💾 Exportar Seus Dados")
    
    export_data = {
        "roda_da_vida_2025": st.session_state.roda_scores,
        "smart_goals_2026": st.session_state.smart_goals,
        "reflections": {
            "conquistas_2025": st.session_state.get("conquistas_2025", ""),
            "desafios_2025": st.session_state.get("desafios_2025", ""),
            "aprendizados_2025": st.session_state.get("aprendizados_2025", ""),
            "gratidao_2025": st.session_state.get("gratidao_2025", "")
        },
        "data_criacao": datetime.now().isoformat()
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="📥 Download JSON",
            data=json.dumps(export_data, indent=2, ensure_ascii=False),
            file_name=f"alquimia_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )
    
    with col2:
        df_export = pd.DataFrame({
            'Área': list(st.session_state.roda_scores.keys()),
            'Pontuação 2025': list(st.session_state.roda_scores.values())
        })
        
        csv = df_export.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"alquimia_roda_vida_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# ============================================================================
# TAB 6: PROGRESS TRACKING
# ============================================================================

with tab6:
    st.header("📈 Acompanhamento de Progresso")
    
    st.markdown("""
    ### Registre seu progresso ao longo do tempo
    Use esta aba para fazer check-ins mensais e ver como sua Roda da Vida evolui.
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("📝 Registrar Check-in Mensal", use_container_width=True, type="primary"):
            add_to_history()
            save_data()
            st.success("✅ Check-in registrado com sucesso!")
    
    with col2:
        if st.button("🗑️ Limpar Histórico", use_container_width=True):
            st.session_state.history = []
            save_data()
            st.success("✅ Histórico limpo!")
    
    if st.session_state.history:
        st.markdown("### 📊 Evolução da Roda da Vida")
        
        # Create timeline chart
        history_dates = [datetime.fromisoformat(h['date']) for h in st.session_state.history]
        history_avgs = [h['avg_score'] for h in st.session_state.history]
        
        df_history = pd.DataFrame({
            'Data': history_dates,
            'Média': history_avgs
        })
        
        # Convert to lists to avoid pyarrow issues
        dates_list = df_history['Data'].tolist()
        medias_list = [float(v) for v in df_history['Média'].tolist()]
        
        fig_timeline = go.Figure()
        fig_timeline.add_trace(go.Scatter(
            x=dates_list,
            y=medias_list,
            mode='lines+markers',
            name='Pontuação Média',
            line=dict(
                color='#667eea',
                width=4,
                smoothing=1.3
            ),
            marker=dict(
                size=12,
                color='#764ba2',
                line=dict(width=2, color='white')
            ),
            fill='tonexty',
            fillcolor='rgba(102, 126, 234, 0.1)',
            hovertemplate='<b>%{x}</b><br>Pontuação Média: %{y:.1f}/10<extra></extra>'
        ))
        
        fig_timeline.update_layout(
            title=dict(
                text='Evolução da Pontuação Média',
                font=dict(size=18, family='Inter', color='#1a202c')
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(
                color='#1a202c',
                family='Inter',
                size=14
            ),
            height=400,
            xaxis=dict(
                title='Data do Check-in',
                showgrid=True,
                gridcolor='rgba(102, 126, 234, 0.15)',
                linecolor='rgba(102, 126, 234, 0.3)'
            ),
            yaxis=dict(
                title='Pontuação Média',
                showgrid=True,
                gridcolor='rgba(102, 126, 234, 0.15)',
                linecolor='rgba(102, 126, 234, 0.3)',
                range=[0, 10]
            ),
            margin=dict(l=60, r=50, t=60, b=50),
            hovermode='x unified'
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Show detailed history
        st.markdown("### 📋 Histórico de Check-ins")
        
        for idx, entry in enumerate(reversed(st.session_state.history[-10:])):  # Show last 10
            entry_date = datetime.fromisoformat(entry['date'])
            with st.expander(f"📅 {entry_date.strftime('%d/%m/%Y %H:%M')} - Média: {entry['avg_score']:.1f}/10"):
                # Convert to lists to avoid pyarrow issues
                areas_list = list(entry['roda_scores'].keys())
                scores_list = [float(v) for v in entry['roda_scores'].values()]
                
                # Create markdown table to avoid pyarrow dependency
                markdown_table = "| Área | Pontuação |\n|------|----------|\n"
                for area, score in zip(areas_list, scores_list):
                    markdown_table += f"| {area} | {score:.1f} |\n"
                
                st.markdown(markdown_table)
    else:
        st.info("""
        📝 Nenhum check-in registrado ainda.
        
        Clique no botão "Registrar Check-in Mensal" para salvar sua avaliação atual da Roda da Vida.
        Isso permitirá que você acompanhe seu progresso ao longo do tempo!
        """)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #667eea; padding: 20px;'>
    <h3>🔮 ALQUIMIA ✨</h3>
    <p>Transformando chumbo em ouro | Turning lead into gold</p>
    <p>2026: O Ano da Feiticeira</p>
    <p style='margin-top: 15px; font-style: italic;'>A magia está em você 💜</p>
</div>
""", unsafe_allow_html=True)
